"""Build dimension-specific evaluation prompts with few-shot examples."""

from config import (
    ENTITY_TYPES, ASSERTION_TYPES, TEMPORALITY_TYPES, SUBJECT_TYPES,
)

# ── Dimension-specific criteria and few-shot examples ────────────────────────

_DIMENSION_CONFIGS = {
    "entity_type": {
        "criteria": (
            "You are a clinical NLP quality evaluator. Score how correctly the entity_type "
            "label was assigned to a medical entity extracted from a clinical note.\n\n"
            "Scoring rubric:\n"
            "1 = Completely wrong (e.g., UI noise labeled as a medical entity, or a drug "
            "misclassified as PROBLEM)\n"
            "2 = Wrong category but in the medical domain\n"
            "3 = Ambiguous or borderline classification\n"
            "4 = Mostly correct, minor quibble possible\n"
            "5 = Perfectly correct entity type assignment\n\n"
            f"Valid entity types: {', '.join(ENTITY_TYPES)}"
        ),
        "examples": [
            {
                "role": "user",
                "content": (
                    "Section: Cover Page\n"
                    "Entities in section: [\"Quick Search\", \"Fax Inbox\"]\n"
                    "Score entity: \"Quick Search\" | entity_type: PROCEDURE"
                ),
            },
            {"role": "assistant", "content": "1"},
            {
                "role": "user",
                "content": (
                    "Section: Current Medications\n"
                    "Entities in section: [\"metformin 500mg\", \"lisinopril 10mg\"]\n"
                    "Score entity: \"metformin 500mg\" | entity_type: MEDICINE"
                ),
            },
            {"role": "assistant", "content": "5"},
            {
                "role": "user",
                "content": (
                    "Section: Assessment and Plan\n"
                    "Entities in section: [\"ibuprofen\", \"knee pain\"]\n"
                    "Score entity: \"ibuprofen\" | entity_type: PROBLEM"
                ),
            },
            {"role": "assistant", "content": "1"},
        ],
    },
    "assertion": {
        "criteria": (
            "You are a clinical NLP quality evaluator. Score how correctly the assertion "
            "status was assigned to a medical entity extracted from a clinical note.\n\n"
            "Scoring rubric:\n"
            "1 = Completely wrong assertion (e.g., clearly negated finding marked POSITIVE)\n"
            "2 = Likely wrong, strong evidence against this assertion\n"
            "3 = Ambiguous, context does not clearly support either way\n"
            "4 = Mostly correct, minor ambiguity\n"
            "5 = Perfectly correct assertion assignment\n\n"
            f"Valid assertion types: {', '.join(ASSERTION_TYPES)}"
        ),
        "examples": [
            {
                "role": "user",
                "content": (
                    "Section: Review of Systems\n"
                    "Text: \"Patient denies chest pain, shortness of breath, or palpitations.\"\n"
                    "Entities in section: [\"chest pain\", \"shortness of breath\", \"palpitations\"]\n"
                    "Score entity: \"chest pain\" | assertion: POSITIVE"
                ),
            },
            {"role": "assistant", "content": "1"},
            {
                "role": "user",
                "content": (
                    "Section: Assessment and Plan\n"
                    "Text: \"Patient presents with acute bronchitis, started on azithromycin.\"\n"
                    "Entities in section: [\"acute bronchitis\", \"azithromycin\"]\n"
                    "Score entity: \"acute bronchitis\" | assertion: POSITIVE"
                ),
            },
            {"role": "assistant", "content": "5"},
            {
                "role": "user",
                "content": (
                    "Section: Assessment and Plan\n"
                    "Text: \"Chest X-ray shows possible pneumonia, will start empiric antibiotics.\"\n"
                    "Entities in section: [\"pneumonia\", \"antibiotics\"]\n"
                    "Score entity: \"pneumonia\" | assertion: UNCERTAIN"
                ),
            },
            {"role": "assistant", "content": "5"},
        ],
    },
    "temporality": {
        "criteria": (
            "You are a clinical NLP quality evaluator. Score how correctly the temporality "
            "label was assigned to a medical entity extracted from a clinical note.\n\n"
            "Scoring rubric:\n"
            "1 = Completely wrong temporality (e.g., a historical condition marked CURRENT)\n"
            "2 = Likely wrong temporal assignment\n"
            "3 = Ambiguous temporal context\n"
            "4 = Mostly correct, minor ambiguity\n"
            "5 = Perfectly correct temporality assignment\n\n"
            f"Valid temporality types: {', '.join(TEMPORALITY_TYPES)}"
        ),
        "examples": [
            {
                "role": "user",
                "content": (
                    "Section: Past Medical History\n"
                    "Text: \"History of appendectomy in 2005, cholecystectomy in 2010.\"\n"
                    "Entities in section: [\"appendectomy\", \"cholecystectomy\"]\n"
                    "Score entity: \"appendectomy\" | temporality: CURRENT"
                ),
            },
            {"role": "assistant", "content": "1"},
            {
                "role": "user",
                "content": (
                    "Section: Active Problems\n"
                    "Text: \"Hypertension, well controlled on current medications.\"\n"
                    "Entities in section: [\"hypertension\"]\n"
                    "Score entity: \"hypertension\" | temporality: CURRENT"
                ),
            },
            {"role": "assistant", "content": "5"},
            {
                "role": "user",
                "content": (
                    "Section: Discharge Plan\n"
                    "Text: \"Schedule follow-up colonoscopy in 6 months.\"\n"
                    "Entities in section: [\"colonoscopy\"]\n"
                    "Score entity: \"colonoscopy\" | temporality: UPCOMING"
                ),
            },
            {"role": "assistant", "content": "5"},
        ],
    },
    "subject": {
        "criteria": (
            "You are a clinical NLP quality evaluator. Score how correctly the subject "
            "label was assigned to a medical entity extracted from a clinical note.\n\n"
            "Scoring rubric:\n"
            "1 = Completely wrong subject (e.g., family member's condition labeled as PATIENT)\n"
            "2 = Likely wrong subject assignment\n"
            "3 = Ambiguous subject context\n"
            "4 = Mostly correct, minor ambiguity\n"
            "5 = Perfectly correct subject assignment\n\n"
            f"Valid subject types: {', '.join(SUBJECT_TYPES)}"
        ),
        "examples": [
            {
                "role": "user",
                "content": (
                    "Section: Family History\n"
                    "Text: \"Mother with breast cancer, father with type 2 diabetes.\"\n"
                    "Entities in section: [\"breast cancer\", \"type 2 diabetes\"]\n"
                    "Score entity: \"breast cancer\" | subject: PATIENT"
                ),
            },
            {"role": "assistant", "content": "1"},
            {
                "role": "user",
                "content": (
                    "Section: Assessment and Plan\n"
                    "Text: \"Patient diagnosed with stage 2 hypertension.\"\n"
                    "Entities in section: [\"stage 2 hypertension\"]\n"
                    "Score entity: \"stage 2 hypertension\" | subject: PATIENT"
                ),
            },
            {"role": "assistant", "content": "5"},
            {
                "role": "user",
                "content": (
                    "Section: Family History\n"
                    "Text: \"Father had MI at age 55, paternal grandfather had CAD.\"\n"
                    "Entities in section: [\"MI\", \"CAD\"]\n"
                    "Score entity: \"MI\" | subject: FAMILY_MEMBER"
                ),
            },
            {"role": "assistant", "content": "5"},
        ],
    },
}


def build_evaluation_prompt(
    entity: dict,
    section_entities: list,
    heading: str,
    text: str,
    dimension: str,
) -> list:
    """
    Build a messages list for evaluating a single entity on a single dimension.

    Args:
        entity: The entity dict being scored (must have 'entity_name' and the dimension key).
        section_entities: All entities in the same section for context.
        heading: The section heading the entity was found under.
        text: The source text of the section.
        dimension: One of 'entity_type', 'assertion', 'temporality', 'subject'.

    Returns:
        A list of message dicts suitable for the OpenRouter chat completions API.
    """
    config = _DIMENSION_CONFIGS[dimension]

    # System message with criteria and output format instruction
    system_content = (
        f"{config['criteria']}\n\n"
        "IMPORTANT: Respond with ONLY a single digit from 1 to 5. "
        "No explanation, no punctuation, no other text."
    )

    messages = [{"role": "system", "content": system_content}]

    # Few-shot examples
    messages.extend(config["examples"])

    # Build the actual user query
    entity_name = entity.get("entity", "")
    dimension_value = entity.get(dimension, entity.get("entity_type", "UNKNOWN"))

    entity_names = [e.get("entity", "") for e in section_entities]
    entity_list_str = ", ".join(f'"{n}"' for n in entity_names)

    # Truncate text to keep prompt size reasonable
    truncated_text = text[:500] if len(text) > 500 else text

    user_content = (
        f"Section: {heading}\n"
        f"Text: \"{truncated_text}\"\n"
        f"Entities in section: [{entity_list_str}]\n"
        f"Score entity: \"{entity_name}\" | {dimension}: {dimension_value}"
    )

    messages.append({"role": "user", "content": user_content})

    return messages
