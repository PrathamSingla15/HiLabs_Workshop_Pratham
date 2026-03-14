"""Detect UI noise, admin text, and template boilerplate entities."""
import re
from config import (
    UI_NOISE_ENTITY_PATTERNS, UI_NOISE_HEADING_PATTERNS,
    ADMIN_ENTITY_PATTERNS,
)

def is_ui_noise(entity: dict, heading_info: dict) -> tuple:
    """
    Returns (is_noise: bool, confidence: float, reason: str)
    """
    ent_name = entity.get("entity", "").lower().strip()
    heading = heading_info.get("full_normalized", "")
    text = entity.get("text", "").lower()

    # 1. Heading starts with "x" alone or "cover page"
    if heading_info.get("primary", "") in ("x", ""):
        return (True, 0.95, "cover_page_heading")

    # 2. Heading-based noise
    for pattern in UI_NOISE_HEADING_PATTERNS:
        if pattern in heading:
            return (True, 0.90, f"noise_heading:{pattern}")

    # 3. Entity name matches UI noise patterns
    for pattern in UI_NOISE_ENTITY_PATTERNS:
        if pattern in ent_name:
            return (True, 0.95, f"noise_entity:{pattern}")

    # 4. Admin entity patterns
    for pattern in ADMIN_ENTITY_PATTERNS:
        if pattern in ent_name:
            return (True, 0.85, f"admin_entity:{pattern}")

    # 5. Entity is a PHI placeholder like [PATIENT_NAME]
    if re.match(r'^\[.*\]$', ent_name):
        return (True, 0.95, "phi_placeholder")

    # 6. Entity is just "x" or single character
    if len(ent_name) <= 1:
        return (True, 0.90, "single_char")

    # 7. Text context is clearly UI/navigation
    ui_text_indicators = [
        "quick search", "fax inbox", "click here to view",
        "info hub", "ask eva", "web mode", "patient documents",
        "if content is not visible", "external viewer",
        "132%", "add description",
    ]
    for indicator in ui_text_indicators:
        if indicator in text and len(text) < 500:
            return (True, 0.80, f"ui_text:{indicator}")

    # 8. Template/boilerplate detection
    boilerplate = [
        "internally validated risk model",
        "patients with a score of",
        "specific patient level drivers",
        "readmission risk score",
        "please click here",
    ]
    for bp in boilerplate:
        if bp in text:
            return (True, 0.85, f"boilerplate:{bp}")

    # 9. Truncated entities (end with "...")
    if ent_name.endswith("...") or ent_name.endswith("/h"):
        return (True, 0.75, "truncated")

    # 10. "No Heading Found" with suspicious entity
    if "no heading found" in heading:
        # Not necessarily noise, but check entity
        if any(p in ent_name for p in ["rcvd", "pg:", "job:", "ct1"]):
            return (True, 0.90, "fax_header")

    return (False, 0.0, "")
