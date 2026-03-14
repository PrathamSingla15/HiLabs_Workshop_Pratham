"""NegEx-style assertion scoring."""
import re
from config import (
    NEGEX_PRE_TRIGGERS, NEGEX_POST_TRIGGERS,
    NEGEX_TERMINATION, NEGEX_PSEUDO,
    UNCERTAINTY_TRIGGERS,
)

# Sort pre-triggers by length DESC so longer matches are found first
# e.g., "no evidence of" before "no "
_SORTED_PRE_TRIGGERS = sorted(NEGEX_PRE_TRIGGERS, key=len, reverse=True)
_SORTED_POST_TRIGGERS = sorted(NEGEX_POST_TRIGGERS, key=len, reverse=True)
_SORTED_PSEUDO = sorted(NEGEX_PSEUDO, key=len, reverse=True)
_SORTED_UNCERTAINTY = sorted(UNCERTAINTY_TRIGGERS, key=len, reverse=True)
_SORTED_TERMINATION = sorted(NEGEX_TERMINATION, key=len, reverse=True)

# Pre-context window size (characters before entity)
_PRE_CONTEXT_CHARS = 80
# Post-context window size (characters after entity)
_POST_CONTEXT_CHARS = 80


def _find_entity_in_text(entity_text: str, full_text: str, alignment: dict | None = None) -> tuple[int, int] | None:
    """Find entity position in text using alignment info or direct search.

    Returns (start, end) character offsets or None if not found.
    """
    if alignment:
        start = alignment.get("start_char")
        end = alignment.get("end_char")
        if start is not None and end is not None:
            return (int(start), int(end))

    # Fallback: case-insensitive search
    lower_text = full_text.lower()
    lower_entity = entity_text.lower().strip()
    idx = lower_text.find(lower_entity)
    if idx >= 0:
        return (idx, idx + len(lower_entity))
    return None


def _is_pseudo_negation(context: str) -> bool:
    """Check if context contains a pseudo-negation pattern (not true negation)."""
    ctx = context.lower()
    return any(p in ctx for p in _SORTED_PSEUDO)


def _has_termination_between(text_segment: str) -> bool:
    """Check if a termination term exists in the text segment between trigger and entity."""
    seg = text_segment.lower()
    return any(t in seg for t in _SORTED_TERMINATION)


def _detect_assertion(entity_text: str, full_text: str, alignment: dict | None = None) -> str:
    """Detect assertion status from text context around entity.

    Returns one of: "NEGATIVE", "UNCERTAIN", "POSITIVE"
    """
    pos = _find_entity_in_text(entity_text, full_text, alignment)
    if pos is None:
        return "POSITIVE"  # can't find entity, assume positive

    ent_start, ent_end = pos

    # Extract pre- and post-context
    pre_start = max(0, ent_start - _PRE_CONTEXT_CHARS)
    pre_context = full_text[pre_start:ent_start].lower()
    post_end = min(len(full_text), ent_end + _POST_CONTEXT_CHARS)
    post_context = full_text[ent_end:post_end].lower()

    # Check for pseudo-negation first (these override negation triggers)
    if _is_pseudo_negation(pre_context):
        # Still check uncertainty
        if any(u in pre_context or u in post_context for u in _SORTED_UNCERTAINTY):
            return "UNCERTAIN"
        return "POSITIVE"

    # Scan pre-context for negation triggers
    for trigger in _SORTED_PRE_TRIGGERS:
        trig_pos = pre_context.rfind(trigger)
        if trig_pos >= 0:
            # Check that no termination term sits between trigger and entity
            between = pre_context[trig_pos + len(trigger):]
            if not _has_termination_between(between):
                return "NEGATIVE"

    # Scan post-context for post-negation triggers
    for trigger in _SORTED_POST_TRIGGERS:
        if trigger in post_context:
            return "NEGATIVE"

    # Scan for uncertainty triggers in both pre and post context
    for trigger in _SORTED_UNCERTAINTY:
        if trigger in pre_context or trigger in post_context:
            return "UNCERTAIN"

    return "POSITIVE"


def score_assertion(entity: dict, full_text: str, heading_info: dict, is_noise: bool) -> float:
    """Score assertion correctness on 1-5 scale.

    Args:
        entity: Entity dict with 'entity', 'assertion', and optionally alignment info.
        full_text: The full source text containing the entity.
        heading_info: Dict with heading context information.
        is_noise: Whether this entity is UI noise.

    Returns:
        Score from 1.0 to 5.0.
    """
    if is_noise:
        return 1.0

    assigned = (entity.get("assertion") or "").upper().strip()
    ent_text = entity.get("entity", "")

    # Empty/missing assertion field
    if not assigned:
        return 2.0

    # Get alignment info if available
    alignment = entity.get("alignment")

    # Detect assertion from text context
    detected = _detect_assertion(ent_text, full_text, alignment)

    # Compare detected vs assigned
    if detected == assigned:
        return 5.0

    # Major mismatches
    if detected == "NEGATIVE" and assigned == "POSITIVE":
        return 1.0
    if detected == "POSITIVE" and assigned == "NEGATIVE":
        return 1.0

    # Partial mismatches involving UNCERTAIN
    if detected == "UNCERTAIN" and assigned == "POSITIVE":
        return 3.0  # uncertain marked as positive -- mild mismatch
    if detected == "UNCERTAIN" and assigned == "NEGATIVE":
        return 2.0  # uncertain marked as negative -- more concerning
    if detected == "POSITIVE" and assigned == "UNCERTAIN":
        return 3.0  # positive marked as uncertain -- mild
    if detected == "NEGATIVE" and assigned == "UNCERTAIN":
        return 2.0  # negative marked as uncertain -- worse

    # Fallback for any other combinations
    return 3.5
