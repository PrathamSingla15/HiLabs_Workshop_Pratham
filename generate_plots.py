"""Generate evaluation plots for report."""
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = "output"
ASSETS_DIR = "assets"

ENTITY_TYPES = [
    "MEDICINE", "PROBLEM", "PROCEDURE", "TEST", "VITAL_NAME",
    "IMMUNIZATION", "MEDICAL_DEVICE", "MENTAL_STATUS", "SDOH", "SOCIAL_HISTORY",
]
ASSERTION_TYPES = ["POSITIVE", "NEGATIVE", "UNCERTAIN"]
TEMPORALITY_TYPES = ["CURRENT", "CLINICAL_HISTORY", "UPCOMING", "UNCERTAIN"]
SUBJECT_TYPES = ["PATIENT", "FAMILY_MEMBER"]


def load_outputs():
    outputs = []
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith(".json"):
            with open(os.path.join(OUTPUT_DIR, f)) as fh:
                outputs.append(json.load(fh))
    return outputs


def plot_error_heatmap(outputs):
    """Generate the main error heatmap: entity_types x dimensions."""
    dimensions = ["Entity Type", "Assertion\n(avg)", "Temporality\n(avg)", "Subject\n(avg)"]

    # Build matrix: rows = entity types, cols = dimensions
    matrix = np.zeros((len(ENTITY_TYPES), 4))

    for i, etype in enumerate(ENTITY_TYPES):
        et_rates = [o["entity_type_error_rate"].get(etype, 0.0) for o in outputs]
        matrix[i, 0] = np.mean(et_rates)

        # For assertion/temporality/subject we use overall average across categories
        # since we don't have per-entity-type breakdown in output
        assert_rates = [np.mean([o["assertion_error_rate"].get(a, 0.0) for a in ASSERTION_TYPES]) for o in outputs]
        matrix[i, 1] = np.mean(assert_rates)

        temp_rates = [np.mean([o["temporality_error_rate"].get(t, 0.0) for t in TEMPORALITY_TYPES]) for o in outputs]
        matrix[i, 2] = np.mean(temp_rates)

        subj_rates = [np.mean([o["subject_error_rate"].get(s, 0.0) for s in SUBJECT_TYPES]) for o in outputs]
        matrix[i, 3] = np.mean(subj_rates)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        matrix,
        annot=True, fmt=".2f",
        xticklabels=dimensions,
        yticklabels=ENTITY_TYPES,
        cmap="RdYlGn_r",
        vmin=0, vmax=1,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Error Rate (0 = perfect, 1 = all wrong)"},
        ax=ax,
    )
    ax.set_title("Error Rate Heatmap Across Entity Types and Evaluation Dimensions", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("")
    ax.set_xlabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "error_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: assets/error_heatmap.png")


def plot_dimension_breakdown(outputs):
    """Bar chart showing error rates per category within each dimension."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Entity Type
    ax = axes[0, 0]
    et_means = {et: np.mean([o["entity_type_error_rate"].get(et, 0.0) for o in outputs]) for et in ENTITY_TYPES}
    colors = ["#2ecc71" if v < 0.25 else "#f39c12" if v < 0.45 else "#e74c3c" for v in et_means.values()]
    bars = ax.barh(list(et_means.keys()), list(et_means.values()), color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xlim(0, 1)
    ax.set_title("Entity Type Error Rates", fontweight="bold")
    ax.set_xlabel("Error Rate")
    ax.invert_yaxis()
    for bar, val in zip(bars, et_means.values()):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2, f"{val:.2f}", va="center", fontsize=9)

    # 2. Assertion
    ax = axes[0, 1]
    as_means = {a: np.mean([o["assertion_error_rate"].get(a, 0.0) for o in outputs]) for a in ASSERTION_TYPES}
    colors = ["#2ecc71" if v < 0.25 else "#f39c12" if v < 0.45 else "#e74c3c" for v in as_means.values()]
    bars = ax.barh(list(as_means.keys()), list(as_means.values()), color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xlim(0, 1)
    ax.set_title("Assertion Error Rates", fontweight="bold")
    ax.set_xlabel("Error Rate")
    ax.invert_yaxis()
    for bar, val in zip(bars, as_means.values()):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2, f"{val:.2f}", va="center", fontsize=9)

    # 3. Temporality
    ax = axes[1, 0]
    tp_means = {t: np.mean([o["temporality_error_rate"].get(t, 0.0) for o in outputs]) for t in TEMPORALITY_TYPES}
    colors = ["#2ecc71" if v < 0.25 else "#f39c12" if v < 0.45 else "#e74c3c" for v in tp_means.values()]
    bars = ax.barh(list(tp_means.keys()), list(tp_means.values()), color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xlim(0, 1)
    ax.set_title("Temporality Error Rates", fontweight="bold")
    ax.set_xlabel("Error Rate")
    ax.invert_yaxis()
    for bar, val in zip(bars, tp_means.values()):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2, f"{val:.2f}", va="center", fontsize=9)

    # 4. Subject
    ax = axes[1, 1]
    su_means = {s: np.mean([o["subject_error_rate"].get(s, 0.0) for o in outputs]) for s in SUBJECT_TYPES}
    colors = ["#2ecc71" if v < 0.25 else "#f39c12" if v < 0.45 else "#e74c3c" for v in su_means.values()]
    bars = ax.barh(list(su_means.keys()), list(su_means.values()), color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xlim(0, 1)
    ax.set_title("Subject Error Rates", fontweight="bold")
    ax.set_xlabel("Error Rate")
    ax.invert_yaxis()
    for bar, val in zip(bars, su_means.values()):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2, f"{val:.2f}", va="center", fontsize=9)

    plt.suptitle("Error Rate Breakdown by Evaluation Dimension", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "dimension_breakdown.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: assets/dimension_breakdown.png")


def plot_per_chart_overview(outputs):
    """Scatter plot: per-chart avg error rate vs attribute completeness."""
    fig, ax = plt.subplots(figsize=(12, 6))

    chart_names = []
    avg_errors = []
    attr_comps = []
    date_accs = []

    for o in outputs:
        name = o["file_name"]
        short = name.split("_")[0]
        chart_names.append(short)

        all_err = (
            list(o["entity_type_error_rate"].values())
            + list(o["assertion_error_rate"].values())
            + list(o["temporality_error_rate"].values())
            + list(o["subject_error_rate"].values())
        )
        avg_errors.append(np.mean(all_err))
        attr_comps.append(o["attribute_completeness"])
        date_accs.append(o["event_date_accuracy"])

    x = np.arange(len(chart_names))
    width = 0.35

    bars1 = ax.bar(x - width/2, avg_errors, width, label="Avg Error Rate", color="#e74c3c", alpha=0.85)
    bars2 = ax.bar(x + width/2, attr_comps, width, label="Attr Completeness", color="#3498db", alpha=0.85)

    ax.set_ylabel("Score (0-1)")
    ax.set_title("Per-Chart: Average Error Rate vs Attribute Completeness", fontweight="bold", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(chart_names, rotation=45, ha="right", fontsize=8)
    ax.legend(loc="upper right")
    ax.set_ylim(0, 1)
    ax.axhline(y=np.mean(avg_errors), color="#e74c3c", linestyle="--", alpha=0.5, linewidth=1)
    ax.axhline(y=np.mean(attr_comps), color="#3498db", linestyle="--", alpha=0.5, linewidth=1)

    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "per_chart_overview.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: assets/per_chart_overview.png")


if __name__ == "__main__":
    os.makedirs(ASSETS_DIR, exist_ok=True)
    outputs = load_outputs()
    print(f"Loaded {len(outputs)} output files")
    plot_error_heatmap(outputs)
    plot_dimension_breakdown(outputs)
    plot_per_chart_overview(outputs)
    print("All plots generated.")
