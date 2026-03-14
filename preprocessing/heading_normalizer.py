"""Normalize heading fields from entity JSON."""
import re

def normalize_heading(heading: str) -> dict:
    """
    Normalize a heading string like "History of Present Illness :: 2. Diabetes__page_no__1"
    Returns dict with: raw, page_no, parts, primary, full_normalized
    """
    raw = heading

    # Extract page number
    page_match = re.search(r'__page_no__(\d+)', heading)
    page_no = int(page_match.group(1)) if page_match else None
    heading_clean = re.sub(r'__page_no__\d+', '', heading).strip()

    # Remove " - Table" suffix
    is_table = heading_clean.endswith(' - Table')
    heading_clean = re.sub(r'\s*-\s*Table$', '', heading_clean).strip()

    # Split by :: separator
    parts = [p.strip().lower() for p in heading_clean.split('::') if p.strip()]

    # Primary = last meaningful part (most specific)
    primary = parts[-1] if parts else ""

    # Full normalized = joined
    full_normalized = ' :: '.join(parts)

    return {
        "raw": raw,
        "page_no": page_no,
        "parts": parts,
        "primary": primary,
        "full_normalized": full_normalized,
        "is_table": is_table,
    }
