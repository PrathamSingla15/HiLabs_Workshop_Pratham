"""Score entity_type correctness."""
import re
from config import (
    DRUG_SUFFIXES, KNOWN_DRUG_NAMES,
    DISEASE_SUFFIXES, KNOWN_PROBLEM_TERMS,
    PROCEDURE_SUFFIXES, KNOWN_PROCEDURE_TERMS,
    KNOWN_TEST_TERMS, KNOWN_VITAL_TERMS, KNOWN_IMMUNIZATION_TERMS,
)


def _matches_type(entity_text: str, entity_type: str) -> bool:
    """Check if entity text matches the given type."""
    text = entity_text.lower().strip()
    words = set(text.split())

    if entity_type == "MEDICINE":
        if text in KNOWN_DRUG_NAMES or any(w in KNOWN_DRUG_NAMES for w in words):
            return True
        return any(text.endswith(s) or any(w.endswith(s) for w in words) for s in DRUG_SUFFIXES)

    elif entity_type == "PROBLEM":
        if text in KNOWN_PROBLEM_TERMS or any(w in KNOWN_PROBLEM_TERMS for w in words):
            return True
        return any(text.endswith(s) or any(w.endswith(s) for w in words) for s in DISEASE_SUFFIXES)

    elif entity_type == "PROCEDURE":
        if text in KNOWN_PROCEDURE_TERMS or any(w in KNOWN_PROCEDURE_TERMS for w in words):
            return True
        return any(text.endswith(s) or any(w.endswith(s) for w in words) for s in PROCEDURE_SUFFIXES)

    elif entity_type == "TEST":
        return text in KNOWN_TEST_TERMS or any(w in KNOWN_TEST_TERMS for w in words)

    elif entity_type == "VITAL_NAME":
        return text in KNOWN_VITAL_TERMS or any(w in KNOWN_VITAL_TERMS for w in words)

    elif entity_type == "IMMUNIZATION":
        return (
            text in KNOWN_IMMUNIZATION_TERMS
            or any(w in KNOWN_IMMUNIZATION_TERMS for w in words)
            or "vaccine" in text
            or "immunization" in text
            or "vaccination" in text
        )

    return False


def _infer_type_from_heading(heading: str) -> str | None:
    """Infer expected entity type from heading."""
    h = heading.lower()
    if any(k in h for k in ["medication", "medicine", "drug", "prescription", "rx"]):
        return "MEDICINE"
    if any(k in h for k in ["vital", "vitals"]):
        return "VITAL_NAME"
    if any(k in h for k in ["lab", "laboratory", "result", "blood work"]):
        return "TEST"
    if any(k in h for k in ["immunization", "vaccine", "vaccination"]):
        return "IMMUNIZATION"
    if any(k in h for k in ["diagnosis", "diagnoses", "problem", "assessment"]):
        return "PROBLEM"
    if any(k in h for k in ["procedure", "surgical", "operative"]):
        return "PROCEDURE"
    if any(k in h for k in ["family history", "fhx"]):
        return "PROBLEM"  # family history items are usually problems
    if any(k in h for k in ["social history", "social hx", "shx"]):
        return "SOCIAL_HISTORY"
    return None


def _detect_best_type(entity_text: str) -> str | None:
    """Determine the most likely correct type for an entity."""
    for check_type in ["MEDICINE", "PROBLEM", "PROCEDURE", "TEST", "VITAL_NAME", "IMMUNIZATION"]:
        if _matches_type(entity_text, check_type):
            return check_type
    return None


def score_entity_type(entity: dict, heading_info: dict, is_noise: bool) -> float:
    """Score entity_type correctness on 1-5 scale."""
    if is_noise:
        return 1.0

    ent_name = entity.get("entity", "").lower().strip()
    ent_type = entity.get("entity_type", "")
    heading = heading_info.get("full_normalized", "")

    # Check if entity matches its assigned type
    type_confirmed = _matches_type(ent_name, ent_type)

    # Check if entity matches a DIFFERENT type better
    best_type = _detect_best_type(ent_name)
    cross_type_mismatch = best_type is not None and best_type != ent_type

    # Check heading context
    heading_expected = _infer_type_from_heading(heading)
    heading_match = heading_expected == ent_type if heading_expected else None

    # Scoring logic
    if type_confirmed and (heading_match is True or heading_match is None):
        return 5.0
    elif type_confirmed and heading_match is False:
        return 3.5  # entity looks right but heading suggests different
    elif cross_type_mismatch:
        return 2.0  # entity matches a different type better
    elif not type_confirmed and best_type is None:
        return 3.5  # ambiguous, defer to LLM
    else:
        return 3.0
