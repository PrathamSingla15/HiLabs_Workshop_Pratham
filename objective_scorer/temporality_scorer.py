"""Score temporality correctness."""
import re
from datetime import datetime, date
from config import (
    HISTORY_HEADINGS, CURRENT_HEADINGS, UPCOMING_HEADINGS,
    HISTORY_TEXT_TRIGGERS, CURRENT_TEXT_TRIGGERS, UPCOMING_TEXT_TRIGGERS,
)

# Chronic condition keywords -- these can legitimately be both CURRENT and CLINICAL_HISTORY
_CHRONIC_KEYWORDS = [
    "chronic", "long-standing", "longstanding", "ongoing",
    "stable", "maintained", "controlled", "uncontrolled",
    "diabetes", "hypertension", "copd", "chf", "cad", "ckd",
    "asthma", "epilepsy", "hiv", "hepatitis", "cirrhosis",
    "osteoporosis", "rheumatoid", "lupus",
]


def _infer_temporality_from_heading(heading: str) -> str | None:
    """Infer temporality from heading text."""
    h = heading.lower()
    for pattern in HISTORY_HEADINGS:
        if pattern in h:
            return "CLINICAL_HISTORY"
    for pattern in CURRENT_HEADINGS:
        if pattern in h:
            return "CURRENT"
    for pattern in UPCOMING_HEADINGS:
        if pattern in h:
            return "UPCOMING"
    return None


def _infer_temporality_from_text(entity_text: str, surrounding_text: str) -> str | None:
    """Infer temporality from text triggers around entity."""
    combined = f"{surrounding_text} {entity_text}".lower()

    # Count matches per category
    history_count = sum(1 for t in HISTORY_TEXT_TRIGGERS if t in combined)
    current_count = sum(1 for t in CURRENT_TEXT_TRIGGERS if t in combined)
    upcoming_count = sum(1 for t in UPCOMING_TEXT_TRIGGERS if t in combined)

    max_count = max(history_count, current_count, upcoming_count)
    if max_count == 0:
        return None

    if upcoming_count == max_count and upcoming_count > 0:
        return "UPCOMING"
    if history_count == max_count and history_count > 0:
        return "CLINICAL_HISTORY"
    if current_count == max_count and current_count > 0:
        return "CURRENT"
    return None


def _check_date_temporality(metadata: dict, encounter_date: str | None) -> str | None:
    """Infer temporality from dates in metadata vs encounter date."""
    if not encounter_date:
        return None

    try:
        enc_date = datetime.strptime(encounter_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

    # Check exact_date or derived_date in metadata
    for date_key in ["exact_date", "derived_date"]:
        date_val = metadata.get(date_key, "")
        if not date_val or not isinstance(date_val, str):
            continue
        try:
            entity_date = datetime.strptime(date_val.strip(), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        delta = (entity_date - enc_date).days
        if delta < -30:
            return "CLINICAL_HISTORY"
        elif delta > 7:
            return "UPCOMING"
        else:
            return "CURRENT"

    return None


def _is_chronic(entity_text: str, surrounding_text: str) -> bool:
    """Check if entity likely represents a chronic condition."""
    combined = f"{surrounding_text} {entity_text}".lower()
    return any(kw in combined for kw in _CHRONIC_KEYWORDS)


def score_temporality(
    entity: dict,
    full_text: str,
    heading_info: dict,
    is_noise: bool,
    encounter_date: str | None = None,
) -> float:
    """Score temporality correctness on 1-5 scale.

    Args:
        entity: Entity dict with 'entity', 'temporality', 'metadata_from_qa'.
        full_text: The full source text.
        heading_info: Dict with heading context info.
        is_noise: Whether entity is UI noise.
        encounter_date: Encounter date string (YYYY-MM-DD) if available.

    Returns:
        Score from 1.0 to 5.0.
    """
    if is_noise:
        return 1.0

    assigned = (entity.get("temporality") or "").upper().strip()
    ent_text = entity.get("entity", "")
    metadata = entity.get("metadata_from_qa", {}) or {}
    heading = heading_info.get("full_normalized", "")

    # Empty/missing temporality
    if not assigned:
        return 2.0

    # Gather evidence from multiple sources
    heading_temp = _infer_temporality_from_heading(heading)
    text_temp = _infer_temporality_from_text(ent_text, full_text)
    date_temp = _check_date_temporality(metadata, encounter_date)

    # Build a list of non-None inferences
    inferences = [t for t in [heading_temp, text_temp, date_temp] if t is not None]

    if not inferences:
        # No evidence either way -- ambiguous
        return 3.5

    # Check if assigned matches any inference
    assigned_matches_any = assigned in inferences

    # Check for chronic conditions: CURRENT and CLINICAL_HISTORY are both acceptable
    is_chronic = _is_chronic(ent_text, full_text)
    if is_chronic and assigned in ("CURRENT", "CLINICAL_HISTORY"):
        chronic_acceptable = {"CURRENT", "CLINICAL_HISTORY"}
        if any(inf in chronic_acceptable for inf in inferences):
            return 5.0

    if assigned_matches_any:
        return 5.0

    # Check if all inferences agree on something different
    unique_inferences = set(inferences)

    # If assigned is UNCERTAIN, partial credit
    if assigned == "UNCERTAIN":
        return 3.0

    # If any inference is UNCERTAIN, give some benefit
    if "UNCERTAIN" in unique_inferences:
        return 3.0

    # Major mismatch: all inferences agree on one value, assigned is different
    if len(unique_inferences) == 1:
        expected = unique_inferences.pop()
        # CURRENT vs CLINICAL_HISTORY is less severe than UPCOMING vs CLINICAL_HISTORY
        if {assigned, expected} == {"CURRENT", "CLINICAL_HISTORY"}:
            return 3.0  # moderate mismatch
        else:
            return 2.0  # major mismatch

    # Mixed inferences, assigned doesn't match any
    return 2.5
