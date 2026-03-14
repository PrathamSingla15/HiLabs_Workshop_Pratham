"""Orchestrate LLM-based subjective evaluation with tiered filtering."""
import asyncio
import logging
from collections import defaultdict
from config import PASS_K, LLM_SEED, EARLY_STOP_LOGPROB_THRESHOLD, AMBIGUOUS_LOW, AMBIGUOUS_HIGH
from subjective_scorer.llm_client import OpenRouterClient
from subjective_scorer.prompt_builder import build_evaluation_prompt
from subjective_scorer.logprobs_calculator import (
    extract_weighted_score, get_top_logprob, average_pass_k_scores,
)

logger = logging.getLogger(__name__)

DIMENSIONS = ["entity_type", "assertion", "temporality", "subject"]


class BatchEvaluator:
    def __init__(self):
        self.client = OpenRouterClient()

    async def evaluate_chart(
        self,
        entities: list,
        objective_scores: list,  # list of dicts {dim: score}
        heading_infos: list,
        noise_flags: list,  # list of (is_noise, confidence, reason)
    ) -> dict:
        """
        Evaluate entities that need LLM judgment.
        Returns dict: {entity_idx: {dimension: score}}
        """
        # Identify what needs LLM evaluation
        tasks = []
        for idx, entity in enumerate(entities):
            if noise_flags[idx][0]:  # Skip UI noise
                continue
            for dim in DIMENSIONS:
                obj_score = objective_scores[idx].get(dim, 3.5)
                if AMBIGUOUS_LOW < obj_score < AMBIGUOUS_HIGH:
                    tasks.append((idx, dim))

        logger.info(f"LLM evaluation needed for {len(tasks)} entity-dimension pairs")

        if not tasks:
            return {}

        # Group by section for context
        section_groups = defaultdict(list)
        for idx, dim in tasks:
            key = (entities[idx].get("heading", ""), entities[idx].get("text", "")[:200])
            section_groups[key].append((idx, dim))

        # Build and execute LLM calls
        all_coros = []
        for (heading, text_prefix), items in section_groups.items():
            # Get all entities in this section
            section_entity_indices = list(set(i for i, _ in items))
            section_entities = [entities[i] for i in section_entity_indices]
            full_text = entities[section_entity_indices[0]].get("text", "")

            # Group by dimension
            dim_groups = defaultdict(list)
            for idx, dim in items:
                dim_groups[dim].append(idx)

            for dim, entity_indices in dim_groups.items():
                for entity_idx in entity_indices:
                    all_coros.append(
                        self._score_entity(
                            entities[entity_idx], section_entities,
                            heading, full_text, dim, entity_idx,
                        )
                    )

        # Run all with concurrency control
        results_list = await asyncio.gather(*all_coros, return_exceptions=True)

        # Collect results
        results = {}
        for result in results_list:
            if isinstance(result, Exception):
                logger.error(f"LLM evaluation error: {result}")
                continue
            if result is None:
                continue
            idx, dim, score = result
            if idx not in results:
                results[idx] = {}
            results[idx][dim] = score

        return results

    async def _score_entity(
        self, entity, section_entities, heading, text, dimension, entity_idx
    ):
        """Score a single entity for a single dimension with pass@k."""
        messages = build_evaluation_prompt(
            entity, section_entities, heading, text, dimension
        )

        scores = []
        for pass_num in range(PASS_K):
            seed = LLM_SEED + pass_num
            response = await self.client.call_with_retry(messages, seed=seed)

            if response is None:
                continue

            score = extract_weighted_score(response)
            scores.append(score)

            # Early stopping on high confidence
            if pass_num == 0 and len(scores) == 1:
                top_lp = get_top_logprob(response)
                if top_lp > EARLY_STOP_LOGPROB_THRESHOLD:
                    break

        if not scores:
            return None

        avg_score = average_pass_k_scores(scores)
        return (entity_idx, dimension, avg_score)

    async def close(self):
        await self.client.close()
