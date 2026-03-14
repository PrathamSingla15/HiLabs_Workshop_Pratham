"""Score subject correctness (PATIENT vs FAMILY_MEMBER)."""
import re
from config import (
    FAMILY_HEADINGS_LIST, FAMILY_TRIGGERS,
    SOCIAL_CONTEXT_EXCLUSIONS,
)

# Pre-context window size for proximity scanning
_PROXIMITY_CHARS = 120


def _heading_indicates_family(heading: str) -> bool:
    """Check if heading indicates family history context."""
    h = heading.lower()
    return any(pattern in h for pattern in FAMILY_HEADINGS_LIST)


def _text_indicates_family(entity_text: str, full_text: str, alignment: dict | None = None) -> bool:
    """Check if surrounding text indicates family member context.

    Scans proximity around entity for family triggers, filtering out
    social context exclusions (lives with, married to, etc.).
    """
    # Find entity position
    ent_start = None
    if alignment:
        ent_start = alignment.get("start_char")

    if ent_start is None:
        lower_text = full_text.lower()
        lower_entity = entity_text.lower().strip()
        idx = lower_text.find(lower_entity)
        if idx >= 0:
            ent_start = idx
        else:
            return False

    ent_start = int(ent_start)

    # Extract surrounding context
    ctx_start = max(0, ent_start - _PROXIMITY_CHARS)
    ctx_end = min(len(full_text), ent_start + len(entity_text) + _PROXIMITY_CHARS)
    context = full_text[ctx_start:ctx_end].lower()

    # First check: is this a social context exclusion?
    if any(excl in context for excl in SOCIAL_CONTEXT_EXCLUSIONS):
        return False

    # Check for family triggers in proximity
    return any(trigger in context for trigger in FAMILY_TRIGGERS)


def score_subject(
    entity: dict,
    full_text: str,
    heading_info: dict,
    is_noise: bool,
) -> float:
    """Score subject correctness on 1-5 scale.

    Subject is binary: PATIENT or FAMILY_MEMBER.
    Match = 5.0, mismatch = 1.0, empty = 2.0.

    Args:
        entity: Entity dict with 'entity', 'subject', optional alignment.
        full_text: The full source text.
        heading_info: Dict with heading context info.
        is_noise: Whether entity is UI noise.

    Returns:
        Score from 1.0 to 5.0.
    """
    if is_noise:
        return 1.0

    assigned = (entity.get("subject") or "").upper().strip()
    ent_text = entity.get("entity", "")
    heading = heading_info.get("full_normalized", "")
    alignment = entity.get("alignment")

    # Empty/missing subject field
    if not assigned:
        return 2.0

    # Determine expected subject from heading and text
    heading_family = _heading_indicates_family(heading)
    text_family = _text_indicates_family(ent_text, full_text, alignment)

    # If either heading or text indicates family context
    expected_family = heading_family or text_family

    if expected_family:
        expected = "FAMILY_MEMBER"
    else:
        expected = "PATIENT"

    # Binary scoring
    if assigned == expected:
        return 5.0
    else:
        return 1.0
