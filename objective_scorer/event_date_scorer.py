"""Score event_date accuracy. Purely objective, no LLM needed."""
import re
from datetime import datetime, date


_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_TEXT_DATE_PATTERNS = [
    re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"),
    re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"),
    re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2})\b"),
    re.compile(
        r"\b(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b",
        re.IGNORECASE,
    ),
]

_MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def _parse_date(date_str: str) -> date | None:
    """Parse a YYYY-MM-DD date string."""
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = date_str.strip()
    if not _DATE_PATTERN.match(date_str):
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def _extract_dates_from_relations(metadata: dict) -> list[tuple[str, str]]:
    """Extract (date_string, date_type) from metadata_from_qa.relations.

    Relations structure:
    [{"entity": "2024-12-13", "entity_type": "exact_date", ...}, ...]
    """
    relations = metadata.get("relations", [])
    if not isinstance(relations, list):
        return []

    dates = []
    for rel in relations:
        if not isinstance(rel, dict):
            continue
        rel_type = rel.get("entity_type", "")
        if rel_type in ("exact_date", "derived_date"):
            dates.append((rel.get("entity", ""), rel_type))
    return dates


def _extract_dates_from_text(text: str) -> list[date]:
    """Extract all parseable dates from text."""
    found = []
    for pattern in _TEXT_DATE_PATTERNS:
        for match in pattern.finditer(text):
            groups = match.groups()
            try:
                if pattern == _TEXT_DATE_PATTERNS[0]:
                    d = date(int(groups[0]), int(groups[1]), int(groups[2]))
                elif pattern == _TEXT_DATE_PATTERNS[1]:
                    d = date(int(groups[2]), int(groups[0]), int(groups[1]))
                elif pattern == _TEXT_DATE_PATTERNS[2]:
                    yr = int(groups[2])
                    yr = yr + 2000 if yr < 50 else yr + 1900
                    d = date(yr, int(groups[0]), int(groups[1]))
                elif pattern == _TEXT_DATE_PATTERNS[3]:
                    month = _MONTH_MAP.get(groups[0].lower())
                    if month:
                        d = date(int(groups[2]), month, int(groups[1]))
                    else:
                        continue
                else:
                    continue
                found.append(d)
            except (ValueError, TypeError):
                continue
    return found


def score_event_date(
    entity: dict,
    full_text: str,
    heading_info: dict,
    is_noise: bool,
    encounter_date: str | None = None,
) -> float | None:
    """Score event_date accuracy on 1-5 scale.

    Returns None for entities without dates (they don't contribute).
    """
    if is_noise:
        return 1.0

    metadata = entity.get("metadata_from_qa", {}) or {}
    temporality = (entity.get("temporality") or "").upper().strip()

    # Extract dates from relations list
    date_entries = _extract_dates_from_relations(metadata)
    if not date_entries:
        return None  # No date to evaluate

    enc_date = _parse_date(encounter_date) if encounter_date else None

    scores = []
    for date_str, date_type in date_entries:
        parsed = _parse_date(date_str)
        if parsed is None:
            scores.append(1.0)  # Invalid format
            continue

        score = 5.0

        # Plausibility check
        if parsed.year < 1900 or parsed.year > 2100:
            scores.append(1.0)
            continue

        if enc_date:
            delta = (parsed - enc_date).days
            if delta > 730:
                scores.append(1.5)
                continue

        # Cross-reference against text
        text_dates = _extract_dates_from_text(full_text)
        if text_dates:
            if parsed in text_dates:
                score = min(score, 5.0)
            elif any(abs((parsed - td).days) <= 3 for td in text_dates):
                score = min(score, 4.0)

        # Consistency with temporality
        if enc_date:
            delta = (parsed - enc_date).days
            if temporality == "CLINICAL_HISTORY" and delta > 7:
                score = min(score, 2.0)
            elif temporality == "UPCOMING" and delta < -30:
                score = min(score, 2.0)
            elif temporality == "CURRENT" and abs(delta) > 365:
                score = min(score, 2.5)

        # Derived dates are inherently less certain
        if date_type == "derived_date":
            score = min(score, 4.0)

        scores.append(score)

    if not scores:
        return None
    return sum(scores) / len(scores)
