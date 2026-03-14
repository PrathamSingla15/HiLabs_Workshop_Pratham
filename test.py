#!/usr/bin/env python3
"""
Clinical NLP Entity Extraction Evaluation Pipeline.

Usage:
    python test.py input.json output.json
    python test.py --all                      # Process all charts + generate report
    python test.py --report                   # Generate report from existing outputs
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from preprocessing.heading_normalizer import normalize_heading
from preprocessing.ui_noise_detector import is_ui_noise
from preprocessing.text_aligner import align_entity_to_text
from preprocessing.encounter_date import parse_encounter_date

from objective_scorer.entity_type_scorer import score_entity_type
from objective_scorer.assertion_scorer import score_assertion
from objective_scorer.temporality_scorer import score_temporality
from objective_scorer.subject_scorer import score_subject
from objective_scorer.event_date_scorer import score_event_date
from objective_scorer.attribute_scorer import score_attributes

from subjective_scorer.batch_evaluator import BatchEvaluator

from combiner.score_combiner import combine_scores, build_output

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class EvaluationPipeline:
    """Main evaluation pipeline orchestrator."""

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.evaluator = BatchEvaluator() if use_llm else None

    async def evaluate(
        self,
        entities: list,
        folder_name: str,
        encounter_date: str | None,
        markdown_text: str = "",
    ) -> dict:
        """Run the full evaluation pipeline on a list of entities.

        Returns the output JSON dict.
        """
        n = len(entities)
        logger.info(f"Evaluating {n} entities from {folder_name}")

        # ── Step 1: Preprocessing ──────────────────────────────────────────
        heading_infos = []
        noise_flags = []
        alignments = []

        for entity in entities:
            heading = entity.get("heading", "")
            h_info = normalize_heading(heading)
            heading_infos.append(h_info)

            noise = is_ui_noise(entity, h_info)
            noise_flags.append(noise)

            ent_text = entity.get("entity", "")
            full_text = entity.get("text", "")
            alignment = align_entity_to_text(ent_text, full_text)
            alignments.append(alignment)

        noise_count = sum(1 for f in noise_flags if f[0])
        logger.info(f"Preprocessing complete: {noise_count}/{n} UI noise entities")

        # ── Step 2: Objective Scoring ──────────────────────────────────────
        objective_scores = []
        for i, entity in enumerate(entities):
            is_noise_flag = noise_flags[i][0]
            h_info = heading_infos[i]
            full_text = entity.get("text", "")

            obj = {
                "entity_type": score_entity_type(entity, h_info, is_noise_flag),
                "assertion": score_assertion(entity, full_text, h_info, is_noise_flag),
                "temporality": score_temporality(
                    entity, full_text, h_info, is_noise_flag, encounter_date
                ),
                "subject": score_subject(entity, full_text, h_info, is_noise_flag),
                "event_date": score_event_date(
                    entity, full_text, h_info, is_noise_flag, encounter_date
                ),
                "attribute_completeness": score_attributes(entity, h_info, is_noise_flag),
            }
            objective_scores.append(obj)

        logger.info("Objective scoring complete")

        # ── Step 3: Subjective Scoring (LLM) ──────────────────────────────
        subjective_scores = {}
        if self.use_llm and self.evaluator:
            try:
                subjective_scores = await self.evaluator.evaluate_chart(
                    entities, objective_scores, heading_infos, noise_flags,
                )
                logger.info(
                    f"Subjective scoring complete: {len(subjective_scores)} entities evaluated"
                )
            except Exception as e:
                logger.error(f"Subjective scoring failed, using objective only: {e}")
                subjective_scores = {}

        # ── Step 4: Combine Scores ─────────────────────────────────────────
        combined_scores = []
        for i in range(n):
            obj = objective_scores[i]
            subj = subjective_scores.get(i, {})

            combined = {
                "entity_type": combine_scores(
                    obj["entity_type"], subj.get("entity_type")
                ),
                "assertion": combine_scores(
                    obj["assertion"], subj.get("assertion")
                ),
                "temporality": combine_scores(
                    obj["temporality"], subj.get("temporality")
                ),
                "subject": combine_scores(
                    obj["subject"], subj.get("subject")
                ),
                "event_date": obj["event_date"],  # Purely objective
                "attribute_completeness": obj["attribute_completeness"],  # Purely objective
            }
            combined_scores.append(combined)

        # ── Step 5: Aggregate to Output ────────────────────────────────────
        output = build_output(entities, combined_scores, folder_name)
        logger.info(f"Evaluation complete for {folder_name}")

        return output

    async def close(self):
        if self.evaluator:
            await self.evaluator.close()


def _infer_folder_name(input_path: str) -> str:
    """Infer folder name from input file path."""
    p = Path(input_path)
    # If the file is inside a folder with the same name, use the folder name
    if p.parent.name == p.stem:
        return p.parent.name
    return p.stem


def _find_markdown(input_path: str, folder_name: str) -> str | None:
    """Find the corresponding .md file for a JSON input."""
    p = Path(input_path)

    # Try same directory
    md_path = p.parent / f"{folder_name}.md"
    if md_path.exists():
        return str(md_path)

    # Try parent directory pattern
    md_path = p.parent / f"{p.stem}.md"
    if md_path.exists():
        return str(md_path)

    return None


async def process_single_chart(input_path: str, output_path: str, use_llm: bool = True):
    """Process a single chart JSON and produce evaluation output."""
    with open(input_path) as f:
        entities = json.load(f)

    folder_name = _infer_folder_name(input_path)
    encounter_date = parse_encounter_date(folder_name)

    md_path = _find_markdown(input_path, folder_name)
    markdown_text = ""
    if md_path:
        with open(md_path) as f:
            markdown_text = f.read()

    pipeline = EvaluationPipeline(use_llm=use_llm)
    try:
        output = await pipeline.evaluate(entities, folder_name, encounter_date, markdown_text)
    finally:
        await pipeline.close()

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Evaluation complete: {output_path}")


async def process_all_charts(use_llm: bool = True):
    """Process all charts in workshop_test_data/."""
    project_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    data_dir = project_dir / "workshop_test_data"
    output_dir = project_dir / "output"
    output_dir.mkdir(exist_ok=True)

    if not data_dir.exists():
        print(f"Error: {data_dir} not found")
        sys.exit(1)

    folders = sorted([f for f in data_dir.iterdir() if f.is_dir()])
    print(f"Found {len(folders)} chart folders")

    pipeline = EvaluationPipeline(use_llm=use_llm)

    try:
        for i, folder in enumerate(folders, 1):
            json_file = folder / f"{folder.name}.json"
            if not json_file.exists():
                print(f"  [{i}/{len(folders)}] Skipping {folder.name} (no JSON)")
                continue

            output_file = output_dir / f"{folder.name}.json"
            print(f"  [{i}/{len(folders)}] Processing {folder.name}...")

            with open(json_file) as f:
                entities = json.load(f)

            encounter_date = parse_encounter_date(folder.name)
            md_file = folder / f"{folder.name}.md"
            markdown_text = md_file.read_text() if md_file.exists() else ""

            output = await pipeline.evaluate(
                entities, folder.name, encounter_date, markdown_text
            )

            with open(output_file, "w") as f:
                json.dump(output, f, indent=2)

        print(f"\nAll charts processed. Outputs in: {output_dir}")
    finally:
        await pipeline.close()

    # Generate report
    from reporting.report_generator import generate_report
    report_path = project_dir / "report.md"
    generate_report(str(output_dir), str(report_path))
    print(f"Report generated: {report_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test.py input.json output.json")
        print("       python test.py --all [--no-llm]")
        print("       python test.py --report")
        sys.exit(1)

    use_llm = "--no-llm" not in sys.argv

    if sys.argv[1] == "--all":
        asyncio.run(process_all_charts(use_llm=use_llm))
    elif sys.argv[1] == "--report":
        from reporting.report_generator import generate_report
        project_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        generate_report(str(project_dir / "output"), str(project_dir / "report.md"))
        print("Report generated: report.md")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        if output_path is None or output_path.startswith("--"):
            base = Path(input_path).stem
            output_path = f"output/{base}.json"

        asyncio.run(process_single_chart(input_path, output_path, use_llm=use_llm))


if __name__ == "__main__":
    main()
