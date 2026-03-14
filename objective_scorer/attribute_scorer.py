"""Score attribute completeness. Purely objective."""
from config import EXPECTED_ATTRIBUTES

# Weights for attribute priority tiers
_WEIGHT_CRITICAL = 1.0
_WEIGHT_IMPORTANT = 0.75
_WEIGHT_OPTIONAL = 0.5


def _get_present_qa_types(metadata: dict) -> set:
    """Extract the set of QA entity_type values present in metadata_from_qa.relations.

    metadata_from_qa structure:
    {
        "relations": [
            {"entity": "40", "entity_type": "STRENGTH", ...},
            {"entity": "mg", "entity_type": "UNIT", ...},
        ],
        "count": 2
    }
    """
    relations = metadata.get("relations", [])
    if not isinstance(relations, list):
        return set()
    return {r.get("entity_type", "") for r in relations if isinstance(r, dict)}


def score_attributes(entity: dict, heading_info: dict, is_noise: bool) -> float:
    """Score attribute completeness on 1-5 scale. Purely objective.

    Args:
        entity: Entity dict with 'entity_type' and 'metadata_from_qa'.
        heading_info: Dict with heading context info.
        is_noise: Whether entity is UI noise.

    Returns:
        Score from 1.0 to 5.0.
    """
    if is_noise:
        return 1.0

    ent_type = entity.get("entity_type", "")
    metadata = entity.get("metadata_from_qa", {}) or {}

    # Get expected attributes for this entity type
    expected = EXPECTED_ATTRIBUTES.get(ent_type)
    if expected is None:
        return 3.5

    critical_attrs = expected.get("critical", [])
    important_attrs = expected.get("important", [])
    optional_attrs = expected.get("optional", [])

    requires_metadata = ent_type in ("MEDICINE", "TEST", "VITAL_NAME")

    # Get the set of present QA entity types
    present_types = _get_present_qa_types(metadata)
    has_any_metadata = len(present_types) > 0

    # Count present attributes per tier
    critical_present = sum(1 for a in critical_attrs if a in present_types)
    important_present = sum(1 for a in important_attrs if a in present_types)
    optional_present = sum(1 for a in optional_attrs if a in present_types)

    critical_total = len(critical_attrs)
    important_total = len(important_attrs)
    optional_total = len(optional_attrs)

    # Calculate total weight
    total_weight = (
        critical_total * _WEIGHT_CRITICAL
        + important_total * _WEIGHT_IMPORTANT
        + optional_total * _WEIGHT_OPTIONAL
    )

    if total_weight == 0:
        return 4.0  # No expected attributes

    # Check for empty metadata when attributes are expected
    if not has_any_metadata:
        if requires_metadata:
            return 1.5
        if critical_total == 0 and important_total == 0:
            return 4.0
        return 2.0

    # Calculate weighted completeness
    achieved_weight = (
        critical_present * _WEIGHT_CRITICAL
        + important_present * _WEIGHT_IMPORTANT
        + optional_present * _WEIGHT_OPTIONAL
    )
    completeness = achieved_weight / total_weight

    # Map completeness [0, 1] to score [1, 5]
    score = 1.0 + completeness * 4.0

    # Penalize missing critical attributes
    if critical_total > 0 and critical_present == 0:
        score = min(score, 2.0)
    elif critical_total > 0 and critical_present < critical_total:
        score = min(score, 3.5)

    return round(score, 1)
