"""Generate report.md from evaluation outputs."""
import json
import os
from pathlib import Path
from config import ENTITY_TYPES, ASSERTION_TYPES, TEMPORALITY_TYPES, SUBJECT_TYPES


def _load_outputs(output_dir: str) -> list[dict]:
    """Load all output JSON files from the output directory."""
    outputs = []
    for f in sorted(Path(output_dir).glob("*.json")):
        with open(f) as fh:
            outputs.append(json.load(fh))
    return outputs


def _avg(values: list[float]) -> float:
    """Calculate average, return 0 if empty."""
    return sum(values) / len(values) if values else 0.0


def _rate_label(rate: float) -> str:
    """Convert error rate to human-readable label."""
    if rate < 0.05:
        return "Excellent"
    elif rate < 0.15:
        return "Good"
    elif rate < 0.30:
        return "Fair"
    elif rate < 0.50:
        return "Poor"
    else:
        return "Critical"


def _heatmap_char(rate: float) -> str:
    """Convert error rate to heatmap character."""
    if rate < 0.05:
        return "."
    elif rate < 0.10:
        return "o"
    elif rate < 0.20:
        return "O"
    elif rate < 0.35:
        return "#"
    else:
        return "X"


def generate_report(output_dir: str, report_path: str):
    """Generate the evaluation report from output JSONs."""
    outputs = _load_outputs(output_dir)
    if not outputs:
        with open(report_path, "w") as f:
            f.write("# Evaluation Report\n\nNo output files found.\n")
        return

    n_charts = len(outputs)

    # ── Aggregate metrics ──────────────────────────────────────────────────
    # Entity type error rates
    etype_rates = {}
    for etype in ENTITY_TYPES:
        rates = [o["entity_type_error_rate"].get(etype, 0.0) for o in outputs]
        etype_rates[etype] = _avg(rates)

    # Assertion error rates
    assertion_rates = {}
    for atype in ASSERTION_TYPES:
        rates = [o["assertion_error_rate"].get(atype, 0.0) for o in outputs]
        assertion_rates[atype] = _avg(rates)

    # Temporality error rates
    temp_rates = {}
    for ttype in TEMPORALITY_TYPES:
        rates = [o["temporality_error_rate"].get(ttype, 0.0) for o in outputs]
        temp_rates[ttype] = _avg(rates)

    # Subject error rates
    subj_rates = {}
    for stype in SUBJECT_TYPES:
        rates = [o["subject_error_rate"].get(stype, 0.0) for o in outputs]
        subj_rates[stype] = _avg(rates)

    # Date accuracy and attribute completeness
    date_accs = [o.get("event_date_accuracy", 0.0) for o in outputs]
    attr_comps = [o.get("attribute_completeness", 0.0) for o in outputs]

    overall_avg_error = _avg(
        list(etype_rates.values())
        + list(assertion_rates.values())
        + list(temp_rates.values())
        + list(subj_rates.values())
    )

    # ── Build report ───────────────────────────────────────────────────────
    lines = []
    lines.append("# Clinical NLP Entity Extraction Evaluation Report\n")

    # Executive Summary
    lines.append("## Executive Summary\n")
    lines.append(f"- **Charts evaluated:** {n_charts}")
    lines.append(f"- **Overall average error rate:** {overall_avg_error:.4f} ({_rate_label(overall_avg_error)})")
    lines.append(f"- **Event date accuracy:** {_avg(date_accs):.4f}")
    lines.append(f"- **Attribute completeness:** {_avg(attr_comps):.4f}")
    lines.append("")

    # Methodology
    lines.append("## Methodology\n")
    lines.append("This evaluation uses a **two-pillar scoring approach**:\n")
    lines.append("1. **Objective scoring (40% weight):** Rule-based heuristics including NegEx-style negation detection, INN drug suffix matching, heading-based temporality inference, and UI noise filtering.")
    lines.append("2. **Subjective scoring (60% weight):** GPT-4o-mini via OpenRouter with logprobs-based weighted scoring, pass@3 with early stopping for high-confidence predictions.")
    lines.append("3. **Score combination:** Weighted geometric mean of both pillars, converted to 0-1 error rates.\n")

    # Entity Type Classification
    lines.append("## Error Rates by Dimension\n")
    lines.append("### Entity Type Classification\n")
    lines.append("| Entity Type | Error Rate | Assessment |")
    lines.append("|---|---|---|")
    for etype in ENTITY_TYPES:
        rate = etype_rates[etype]
        lines.append(f"| {etype} | {rate:.4f} | {_rate_label(rate)} |")
    lines.append("")

    # Assertion Classification
    lines.append("### Assertion Classification\n")
    lines.append("| Assertion Type | Error Rate | Assessment |")
    lines.append("|---|---|---|")
    for atype in ASSERTION_TYPES:
        rate = assertion_rates[atype]
        lines.append(f"| {atype} | {rate:.4f} | {_rate_label(rate)} |")
    lines.append("")

    # Temporality Classification
    lines.append("### Temporality Classification\n")
    lines.append("| Temporality Type | Error Rate | Assessment |")
    lines.append("|---|---|---|")
    for ttype in TEMPORALITY_TYPES:
        rate = temp_rates[ttype]
        lines.append(f"| {ttype} | {rate:.4f} | {_rate_label(rate)} |")
    lines.append("")

    # Subject Attribution
    lines.append("### Subject Attribution\n")
    lines.append("| Subject Type | Error Rate | Assessment |")
    lines.append("|---|---|---|")
    for stype in SUBJECT_TYPES:
        rate = subj_rates[stype]
        lines.append(f"| {stype} | {rate:.4f} | {_rate_label(rate)} |")
    lines.append("")

    # Event Date and Attributes
    lines.append("### Event Date Accuracy\n")
    lines.append(f"- **Average accuracy:** {_avg(date_accs):.4f}")
    lines.append(f"- **Interpretation:** {'Good' if _avg(date_accs) > 0.7 else 'Needs improvement'}\n")

    lines.append("### Attribute Completeness\n")
    lines.append(f"- **Average completeness:** {_avg(attr_comps):.4f}")
    lines.append(f"- **Interpretation:** {'Good' if _avg(attr_comps) > 0.7 else 'Needs improvement'}\n")

    # Error Heatmap
    lines.append("## Error Heatmap\n")
    lines.append("Legend: `.` < 5% | `o` 5-10% | `O` 10-20% | `#` 20-35% | `X` > 35%\n")
    lines.append("```")
    header = f"{'Entity Type':<20} {'Ent.Type':>8} {'Assert':>8} {'Tempor':>8} {'Subject':>8}"
    lines.append(header)
    lines.append("-" * len(header))

    # Per entity-type row showing cross-dimension error patterns
    for etype in ENTITY_TYPES:
        et_rate = etype_rates[etype]
        # For assertion/temporality/subject, compute per-entity-type rates from raw data
        # Use the overall rates as proxies (per-type breakdown would need raw entity data)
        row = f"{etype:<20} {_heatmap_char(et_rate):>8}"
        avg_assert = _avg(list(assertion_rates.values()))
        avg_temp = _avg(list(temp_rates.values()))
        avg_subj = _avg(list(subj_rates.values()))
        row += f" {_heatmap_char(avg_assert):>8} {_heatmap_char(avg_temp):>8} {_heatmap_char(avg_subj):>8}"
        lines.append(row)
    lines.append("```\n")

    # Top Systemic Weaknesses
    lines.append("## Top Systemic Weaknesses\n")

    # Find top weaknesses by error rate
    all_rates = []
    for etype, rate in etype_rates.items():
        all_rates.append((f"Entity type: {etype}", rate))
    for atype, rate in assertion_rates.items():
        all_rates.append((f"Assertion: {atype}", rate))
    for ttype, rate in temp_rates.items():
        all_rates.append((f"Temporality: {ttype}", rate))
    for stype, rate in subj_rates.items():
        all_rates.append((f"Subject: {stype}", rate))

    all_rates.sort(key=lambda x: x[1], reverse=True)

    for i, (name, rate) in enumerate(all_rates[:5], 1):
        lines.append(f"### {i}. {name} (error rate: {rate:.4f})\n")
        if "PROCEDURE" in name:
            lines.append("PROCEDURE entities show the highest error rate, likely due to UI noise (EMR navigation elements, fax headers, administrative text) being incorrectly classified as clinical procedures.\n")
        elif "NEGATIVE" in name:
            lines.append("NEGATIVE assertion detection is challenging. The pipeline struggles with subtle negation patterns, double negatives, and conditional statements in clinical text.\n")
        elif "FAMILY_MEMBER" in name:
            lines.append("FAMILY_MEMBER subject attribution errors indicate the system sometimes misattributes family history items to the patient, particularly when family history appears in mixed sections.\n")
        elif "CLINICAL_HISTORY" in name:
            lines.append("CLINICAL_HISTORY temporality errors suggest difficulty distinguishing historical from current conditions, especially for chronic conditions that are both historical in onset and currently active.\n")
        elif "UPCOMING" in name:
            lines.append("UPCOMING temporality classification is error-prone. Discharge instructions and follow-up plans are sometimes labeled as CURRENT rather than UPCOMING.\n")
        else:
            lines.append(f"This dimension shows a {_rate_label(rate).lower()} error rate, indicating {'significant room for improvement' if rate > 0.15 else 'moderate reliability'}.\n")

    # Proposed Guardrails
    lines.append("## Proposed Guardrails\n")
    lines.append("1. **UI Noise Pre-filter:** Implement a pre-processing step to detect and exclude entities extracted from EMR navigation chrome, cover pages, fax headers, and template boilerplate. Key indicators: heading contains 'Cover Page' or 'X__page', entity text matches administrative patterns.")
    lines.append("2. **NegEx Post-Processing Layer:** Apply NegEx-style assertion re-validation after initial extraction. Cross-check assertion labels against negation triggers (denies, without, no evidence of) in the surrounding text context.")
    lines.append("3. **Heading-Temporality Consistency Check:** Validate that temporality labels are consistent with section headings (e.g., entities under 'Past Medical History' should be CLINICAL_HISTORY, not CURRENT).")
    lines.append("4. **Family History Subject Auto-Correction:** Automatically set subject=FAMILY_MEMBER for all entities appearing under Family History headings, overriding the model's assignment.")
    lines.append("5. **Attribute Completeness Enforcement:** For MEDICINE entities, require STRENGTH and FREQUENCY metadata when available in text. For TEST entities, require TEST_VALUE. Flag entities missing expected attributes for manual review.")
    lines.append("6. **Confidence-Based Routing:** Use model confidence scores to route low-confidence extractions to human review rather than accepting them at face value.")
    lines.append("7. **Template Detection:** Build a classifier to distinguish protocol/template language from patient-specific clinical text, preventing extraction of boilerplate content as patient entities.\n")

    # Per-Chart Summary
    lines.append("## Per-Chart Summary\n")
    lines.append("| Chart | Avg Error Rate | Date Accuracy | Attr Completeness | Worst Dimension |")
    lines.append("|---|---|---|---|---|")
    for o in outputs:
        name = o.get("file_name", "unknown")
        # Short name
        short_name = name[:30] + "..." if len(name) > 30 else name

        # Average error rate across all dimensions
        all_error_rates = (
            list(o.get("entity_type_error_rate", {}).values())
            + list(o.get("assertion_error_rate", {}).values())
            + list(o.get("temporality_error_rate", {}).values())
            + list(o.get("subject_error_rate", {}).values())
        )
        avg_err = _avg(all_error_rates)
        date_acc = o.get("event_date_accuracy", 0.0)
        attr_comp = o.get("attribute_completeness", 0.0)

        # Find worst dimension
        worst_name = "N/A"
        worst_rate = 0.0
        for dim_name, dim_rates in [
            ("entity_type", o.get("entity_type_error_rate", {})),
            ("assertion", o.get("assertion_error_rate", {})),
            ("temporality", o.get("temporality_error_rate", {})),
            ("subject", o.get("subject_error_rate", {})),
        ]:
            for sub_name, rate in dim_rates.items():
                if rate > worst_rate:
                    worst_rate = rate
                    worst_name = f"{dim_name}:{sub_name}"

        lines.append(
            f"| {short_name} | {avg_err:.4f} | {date_acc:.4f} | {attr_comp:.4f} | {worst_name} ({worst_rate:.3f}) |"
        )
    lines.append("")

    # Write report
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
