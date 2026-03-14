"""Align entity text to its source context."""
import re

def align_entity_to_text(entity_name: str, text: str) -> dict:
    """
    Find entity position in text and extract surrounding context.
    Returns dict with: found, start_idx, end_idx, pre_context, post_context, context_window
    """
    ent_lower = entity_name.lower().strip()
    text_lower = text.lower()

    # Try exact match
    idx = text_lower.find(ent_lower)

    if idx == -1:
        # Try without extra whitespace
        ent_collapsed = re.sub(r'\s+', ' ', ent_lower)
        text_collapsed = re.sub(r'\s+', ' ', text_lower)
        idx_collapsed = text_collapsed.find(ent_collapsed)
        if idx_collapsed >= 0:
            idx = idx_collapsed
            text_lower = text_collapsed

    if idx == -1:
        # Try first word match as fallback
        first_word = ent_lower.split()[0] if ent_lower.split() else ""
        if first_word and len(first_word) > 3:
            idx = text_lower.find(first_word)

    if idx >= 0:
        end_idx = idx + len(ent_lower)
        pre_start = max(0, idx - 80)
        post_end = min(len(text_lower), end_idx + 80)

        return {
            "found": True,
            "start_idx": idx,
            "end_idx": end_idx,
            "pre_context": text_lower[pre_start:idx],
            "post_context": text_lower[end_idx:post_end],
            "context_window": text_lower[pre_start:post_end],
        }

    # Not found - return full text as context (truncated)
    return {
        "found": False,
        "start_idx": -1,
        "end_idx": -1,
        "pre_context": "",
        "post_context": "",
        "context_window": text_lower[:300],
    }
