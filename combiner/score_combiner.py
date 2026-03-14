"""Combine objective and subjective scores into final error rates."""
import math
from config import (
    OBJECTIVE_WEIGHT, SUBJECTIVE_WEIGHT,
    ENTITY_TYPES, ASSERTION_TYPES, TEMPORALITY_TYPES, SUBJECT_TYPES,
)


def combine_scores(objective: float, subjective: float | None) -> float:
    """Combine objective and subjective scores using weighted geometric mean.

    Both scores are on 1-5 scale. Returns combined score on 1-5 scale.
    """
    if subjective is None:
        return objective

    obj = max(objective, 1.0)
    subj = max(subjective, 1.0)

    # Weighted geometric mean: (obj^w1 * subj^w2)^(1/(w1+w2))
    combined = math.exp(
        (OBJECTIVE_WEIGHT * math.log(obj) + SUBJECTIVE_WEIGHT * math.log(subj))
        / (OBJECTIVE_WEIGHT + SUBJECTIVE_WEIGHT)
    )
    return max(1.0, min(5.0, combined))


def score_to_error_rate(score: float) -> float:
    """Convert 1-5 score to 0-1 error rate.

    Score 5 → error rate 0.0 (perfect)
    Score 1 → error rate 1.0 (all wrong)
    """
    rate = 1.0 - (score - 1.0) / 4.0
    return max(0.0, min(1.0, round(rate, 4)))


def score_to_accuracy(score: float) -> float:
    """Convert 1-5 score to 0-1 accuracy/completeness.

    Score 5 → accuracy 1.0 (perfect)
    Score 1 → accuracy 0.0 (all wrong)
    """
    acc = (score - 1.0) / 4.0
    return max(0.0, min(1.0, round(acc, 4)))


def build_output(
    entities: list,
    combined_scores: list,
    file_name: str,
) -> dict:
    """Aggregate per-entity combined scores into the output JSON schema.

    Args:
        entities: List of entity dicts.
        combined_scores: List of dicts with per-entity combined scores.
            Each dict has keys: entity_type, assertion, temporality, subject,
            event_date (float|None), attribute_completeness (float).
        file_name: Name for the output file_name field.

    Returns:
        Output dict matching the required JSON schema.
    """
    output = {
        "file_name": file_name,
        "entity_type_error_rate": {},
        "assertion_error_rate": {},
        "temporality_error_rate": {},
        "subject_error_rate": {},
        "event_date_accuracy": 0.0,
        "attribute_completeness": 0.0,
    }

    # entity_type_error_rate: group by entity_type, average, convert to error rate
    for etype in ENTITY_TYPES:
        scores = [
            combined_scores[i]["entity_type"]
            for i, e in enumerate(entities)
            if e.get("entity_type") == etype
        ]
        if scores:
            avg = sum(scores) / len(scores)
            output["entity_type_error_rate"][etype] = score_to_error_rate(avg)
        else:
            output["entity_type_error_rate"][etype] = 0.0

    # assertion_error_rate: group by assertion value
    for atype in ASSERTION_TYPES:
        scores = [
            combined_scores[i]["assertion"]
            for i, e in enumerate(entities)
            if (e.get("assertion") or "").upper().strip() == atype
        ]
        if scores:
            avg = sum(scores) / len(scores)
            output["assertion_error_rate"][atype] = score_to_error_rate(avg)
        else:
            output["assertion_error_rate"][atype] = 0.0

    # temporality_error_rate: group by temporality value
    for ttype in TEMPORALITY_TYPES:
        scores = [
            combined_scores[i]["temporality"]
            for i, e in enumerate(entities)
            if (e.get("temporality") or "").upper().strip() == ttype
        ]
        if scores:
            avg = sum(scores) / len(scores)
            output["temporality_error_rate"][ttype] = score_to_error_rate(avg)
        else:
            output["temporality_error_rate"][ttype] = 0.0

    # subject_error_rate: group by subject value
    for stype in SUBJECT_TYPES:
        scores = [
            combined_scores[i]["subject"]
            for i, e in enumerate(entities)
            if (e.get("subject") or "").upper().strip() == stype
        ]
        if scores:
            avg = sum(scores) / len(scores)
            output["subject_error_rate"][stype] = score_to_error_rate(avg)
        else:
            output["subject_error_rate"][stype] = 0.0

    # event_date_accuracy: average of non-None date scores → accuracy
    date_scores = [
        combined_scores[i]["event_date"]
        for i in range(len(entities))
        if combined_scores[i].get("event_date") is not None
    ]
    if date_scores:
        avg = sum(date_scores) / len(date_scores)
        output["event_date_accuracy"] = score_to_accuracy(avg)
    else:
        output["event_date_accuracy"] = 0.0

    # attribute_completeness: average of all attribute scores → accuracy
    attr_scores = [
        combined_scores[i]["attribute_completeness"]
        for i in range(len(entities))
    ]
    if attr_scores:
        avg = sum(attr_scores) / len(attr_scores)
        output["attribute_completeness"] = score_to_accuracy(avg)
    else:
        output["attribute_completeness"] = 0.0

    return output
