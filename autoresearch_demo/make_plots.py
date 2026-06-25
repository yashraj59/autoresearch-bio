"""Generate plots for the MoFNet autoresearch demonstration."""

from __future__ import annotations

from pathlib import Path
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

DEMO_DIR = Path(__file__).resolve().parent
EXP_DIR = DEMO_DIR / "outputs" / "experiments"
PLOT_DIR = DEMO_DIR / "outputs" / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(EXP_DIR / "results.tsv", sep="\t")
registry = json.loads((EXP_DIR / "BASELINE_REGISTRY.json").read_text())
baseline_mean = registry["baseline_mean"]
baseline_std = registry["baseline_std"]

# ============================================================
# Plot 1: Improvement chart (Tier 1 single-seed vs Tier 2 multi-seed)
# ============================================================
fig, ax = plt.subplots(figsize=(11, 6))
baseline_auc = baseline_mean["val_auc"]
baseline_auc_std = baseline_std["val_auc"]

ax.axhspan(
    baseline_auc - baseline_auc_std, baseline_auc + baseline_auc_std,
    alpha=0.15, color="gray", label="Baseline 1σ band"
)
ax.axhline(baseline_auc, color="black", linestyle="--", linewidth=1.5,
           label=f"Baseline mean = {baseline_auc:.4f}")

colors = {
    "TIER1_KEEP_CONTROLLED_SIGNAL": "#2ca02c",
    "TIER1_DISCARD_NO_SIGNAL": "#d62728",
    "TIER1_DISCARD_METRIC_REGRESSION": "#d62728",
    "TIER1_DISCARD_PROTECTED_DOMAIN_REGRESSION": "#9467bd",
    "TIER2_PASS_CLEAN": "#1f77b4",
    "TIER2_FAIL_HIGH_VARIANCE": "#ff7f0e",
    "BASELINE_COMPLETE": "#7f7f7f",
}

for _, row in df.iterrows():
    if row["experiment_num"] == 0:
        continue
    color = colors.get(row["status"], "gray")
    xpos = row["experiment_num"]
    yval = row["primary_metric"]
    if row["tier_reached"] == 2:
        yerr = row["secondary_metric"]  # std of replay seeds
        ax.errorbar(xpos, yval, yerr=yerr, fmt="s", color=color, capsize=5,
                    markersize=12, elinewidth=2, label=row["status"] if row["status"] not in [r.get_label() for r in ax.get_lines()] else "")
    else:
        ax.scatter(xpos, yval, c=color, s=120, marker="o", edgecolors="black", linewidths=1)

    label_y = yval + 0.0025 if row["tier_reached"] < 2 else yval + (row["secondary_metric"] + 0.0015)
    ax.text(xpos, label_y, row["family"], ha="center", fontsize=9, rotation=15)

ax.set_xlabel("Experiment number", fontsize=12)
ax.set_ylabel("Validation AUC", fontsize=12)
ax.set_title("MoFNet Autoresearch: Validation AUC by Experiment (Tier 1 = circle, Tier 2 = square with error bars)",
             fontsize=13)
ax.set_xticks(df["experiment_num"].tolist())

handles = [
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#2ca02c", markersize=11, markeredgecolor="black", label="Tier 1 keep"),
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#d62728", markersize=11, markeredgecolor="black", label="Tier 1 discard"),
    plt.Line2D([0], [0], marker="s", color="#ff7f0e", markersize=11, label="Tier 2 fail (high variance)"),
    plt.Line2D([0], [0], color="black", linestyle="--", label=f"Baseline ({baseline_auc:.4f})"),
    patches.Patch(color="gray", alpha=0.15, label="Baseline 1σ band"),
]
ax.legend(handles=handles, loc="lower right", fontsize=10)
ax.grid(alpha=0.3)

# Annotate the headline result
ax.annotate(
    "Single-seed Tier 1 'keep' on gating\nlooked like improvement",
    xy=(4, df.loc[df["experiment_num"] == 4, "primary_metric"].iloc[0]), xytext=(2.3, baseline_auc + 0.017),
    fontsize=9, color="#2ca02c",
    arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.5),
)
ax.annotate(
    "Tier 2 multi-seed revealed\nimprovement was within noise.\nNo promotion.",
    xy=(5, df.loc[df["experiment_num"] == 5, "primary_metric"].iloc[0]), xytext=(5.3, baseline_auc - 0.014),
    fontsize=9, color="#ff7f0e",
    arrowprops=dict(arrowstyle="->", color="#ff7f0e", lw=1.5),
)

plt.tight_layout()
plt.savefig(PLOT_DIR / "mofnet_autoresearch_improvement.png", dpi=150, bbox_inches="tight")
print(f"Saved {PLOT_DIR / 'mofnet_autoresearch_improvement.png'}")

# ============================================================
# Plot 2: Search tree (DAG) with status colors
# ============================================================
fig, ax = plt.subplots(figsize=(13, 7))

node_status_color = {
    "expanded": "#1f77b4",
    "active_leaf": "#2ca02c",
    "pruned": "#d62728",
    "promoted": "#ff7f0e",
    "retired_subtree": "#7f7f7f",
}

# Layout: root at top center, families fan out
positions = {
    0: (5.0, 5.0),  # baseline root
    1: (2.0, 3.5),  # calibration
    2: (3.5, 3.5),  # sparsity 2e-2
    3: (5.0, 3.5),  # sparsity 5e-2
    4: (7.5, 3.5),  # gating
    5: (7.5, 1.5),  # tier 2 replay of gating
}

# Draw edges first (so they're under the nodes)
for _, row in df.iterrows():
    pe = row["parent_experiment_ids"]
    if pd.isna(pe) or str(pe).strip() == "" or str(pe).strip().lower() == "nan":
        continue
    parents = []
    for p in str(pe).split(","):
        p = p.strip()
        if not p or p.lower() == "nan":
            continue
        try:
            parents.append(int(float(p)))
        except ValueError:
            continue
    for p in parents:
        if p not in positions:
            continue
        x1, y1 = positions[p]
        x2, y2 = positions[row["experiment_num"]]
        # Style edges by branch type
        style = "-"
        if row["branch_type"] == "fork":
            style = "--"
        elif row["branch_type"] == "combine":
            style = ":"
        elif row["branch_type"] == "replay":
            style = "-."
        arrow = FancyArrowPatch(
            (x1, y1 - 0.25), (x2, y2 + 0.25),
            arrowstyle="->", mutation_scale=15, linewidth=1.5,
            color="gray", linestyle=style,
        )
        ax.add_patch(arrow)

# Draw nodes
for _, row in df.iterrows():
    x, y = positions[row["experiment_num"]]
    color = node_status_color.get(row["subtree_status"], "white")
    box = FancyBboxPatch(
        (x - 1.0, y - 0.35), 2.0, 0.7,
        boxstyle="round,pad=0.05", linewidth=1.5,
        facecolor=color, edgecolor="black", alpha=0.85,
    )
    ax.add_patch(box)
    label = f"exp {row['experiment_num']}\n{row['family']}"
    ax.text(x, y + 0.05, label, ha="center", va="center", fontsize=10, fontweight="bold", color="white")
    ax.text(x, y - 0.22, f"AUC {row['primary_metric']:.4f}", ha="center", va="center", fontsize=8, color="white")

# Legend
status_handles = [patches.Patch(color=c, label=s) for s, c in node_status_color.items() if s in ["expanded", "active_leaf", "pruned"]]
branch_handles = [
    plt.Line2D([0], [0], color="gray", linestyle="-", label="linear"),
    plt.Line2D([0], [0], color="gray", linestyle="--", label="fork"),
    plt.Line2D([0], [0], color="gray", linestyle="-.", label="replay"),
    plt.Line2D([0], [0], color="gray", linestyle=":", label="combine (none here)"),
]
leg1 = ax.legend(handles=status_handles, title="Subtree status", loc="upper left", fontsize=9)
ax.add_artist(leg1)
ax.legend(handles=branch_handles, title="Branch type (edge style)", loc="upper right", fontsize=9)

ax.set_xlim(0, 10)
ax.set_ylim(0.5, 6)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("MoFNet Autoresearch: Lineage DAG\n(parent_experiment_ids → branch_type → subtree_status)",
             fontsize=13, pad=20)

# Caption
caption = (
    "Search tree from one autoresearch cycle on MoFNet v1.1.0.\n"
    "Exp 0 (root): published baseline. Exps 1-4: smoke tests across three architectural families.\n"
    "Exp 4 (gating) passed single-seed Tier 1; exp 5 was Tier 2 replay across 3 seeds and failed,\n"
    "showing the apparent improvement was within seed variance. No new baseline promoted."
)
ax.text(5, 0.4, caption, ha="center", va="top", fontsize=9, style="italic")

plt.tight_layout()
plt.savefig(PLOT_DIR / "mofnet_autoresearch_tree.png", dpi=150, bbox_inches="tight")
print(f"Saved {PLOT_DIR / 'mofnet_autoresearch_tree.png'}")

# ============================================================
# Plot 3: Combined summary
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Panel A: AUC comparison
ax1.axhspan(baseline_auc - baseline_auc_std, baseline_auc + baseline_auc_std,
            alpha=0.15, color="gray", label="Baseline ±1σ")
ax1.axhline(baseline_auc, color="black", linestyle="--", linewidth=1.5)

x_positions = [0, 1, 2, 3, 4, 5]
labels = ["baseline\n(3 seeds)", "calib\nT1", "L1=2e-2\nT1", "L1=5e-2\nT1", "gating\nT1", "gating\nT2 (3 seeds)"]
aucs = df["primary_metric"].tolist()
stds = [baseline_auc_std, 0, 0, 0, 0, df.iloc[5]["secondary_metric"]]
bar_colors = ["#7f7f7f", "#d62728", "#d62728", "#d62728", "#2ca02c", "#ff7f0e"]
bars = ax1.bar(x_positions, aucs, yerr=stds, color=bar_colors, edgecolor="black",
               capsize=6, alpha=0.85)
ax1.set_xticks(x_positions)
ax1.set_xticklabels(labels, fontsize=10)
ax1.set_ylabel("Validation AUC", fontsize=12)
ax1.set_title("A. Tier-by-Tier AUC Comparison", fontsize=12)
ax1.set_ylim(0.86, 0.92)
ax1.grid(axis="y", alpha=0.3)
for bar, auc in zip(bars, aucs):
    ax1.text(bar.get_x() + bar.get_width() / 2, auc + 0.003,
             f"{auc:.4f}", ha="center", fontsize=9)

# Panel B: Status counts pie
status_counts = df["status"].value_counts()
colors_pie = [colors.get(s, "gray") for s in status_counts.index]
wedges, texts, autotexts = ax2.pie(
    status_counts.values, labels=[s.replace("_", "\n") for s in status_counts.index],
    autopct="%d", colors=colors_pie, startangle=90, textprops={"fontsize": 9},
)
ax2.set_title("B. Experiment Outcomes by Status", fontsize=12)

plt.suptitle("MoFNet Autoresearch Summary: Protocol Caught a Single-Seed False Positive",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(PLOT_DIR / "mofnet_autoresearch_summary.png", dpi=150, bbox_inches="tight")
print(f"Saved {PLOT_DIR / 'mofnet_autoresearch_summary.png'}")

print("\nAll plots saved.")
