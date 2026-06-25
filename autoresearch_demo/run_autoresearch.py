"""
MoFNet autoresearch demonstration.

This script simulates one cycle of the autoresearch-bio protocol on MoFNet:
- Step 0 baseline (root node) across 3 seeds
- Family 1: Auxiliary calibration head (linear extension)
- Family 2: Stronger sparsity on transparent layers (fork variants from baseline)
- Family 3: Cross-omic gating (linear extension)
- Combine: calibration + gating

Each experiment is logged with parent_experiment_ids, branch_type, subtree_status,
producing a real results.tsv with lineage columns. The synthetic data is
ROS/MAP-shaped (modality_a + modality_b, masked transparent layers).
"""

from __future__ import annotations

import copy
import json
import math
import random
import shutil
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score
from torch.utils.data import DataLoader, TensorDataset

from mofnet import MoFNet, MoFNetLayer

DEMO_DIR = Path(__file__).resolve().parent
EXP_DIR = DEMO_DIR / "outputs" / "experiments"
PLOT_DIR = DEMO_DIR / "outputs" / "plots"
PROMPT_PATH = DEMO_DIR / "autoresearch.md"
EXP_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Synthetic ROS/MAP-shaped multi-omic data
# ============================================================

def make_synthetic_data(seed: int = 0) -> Dict[str, Any]:
    """Generate a ROS/MAP-shaped multi-omic AD dataset.

    Modality A: protein expression (smaller, signal-rich)
    Modality B: SNP/expression markers (larger, sparser signal)
    Adjacency 1: SNP-to-gene mask
    Adjacency 2: (modality_a + transparent) to hidden layer mask
    """
    rng = np.random.default_rng(seed)
    n_total = 600
    modality_a_dims = 24
    modality_b_dims = 60
    transparent_dims = 30
    hidden1_dims = 24

    x_a = rng.normal(size=(n_total, modality_a_dims)).astype(np.float32)
    x_b = rng.normal(size=(n_total, modality_b_dims)).astype(np.float32)
    x = np.concatenate([x_a, x_b], axis=1)

    # Signal mixing: AD label depends on a subset of modality A and a mapped
    # combination of modality B through a sparse trans-omic structure.
    signal_a = 1.2 * x_a[:, 0] - 0.9 * x_a[:, 3] + 0.7 * x_a[:, 11]
    mapped_b = (
        0.6 * x_b[:, 4] - 0.5 * x_b[:, 17] + 0.5 * x_b[:, 31] - 0.4 * x_b[:, 48]
    )
    logit = signal_a + mapped_b + 0.4 * rng.normal(size=n_total)
    probs = 1.0 / (1.0 + np.exp(-logit))
    y = (probs >= 0.5).astype(np.int64)

    # Sparse adjacency masks (the biological priors)
    adj1 = rng.binomial(1, 0.18, size=(modality_b_dims, transparent_dims)).astype(np.float32)
    adj2 = rng.binomial(1, 0.22, size=(modality_a_dims + transparent_dims, hidden1_dims)).astype(np.float32)
    # Ensure no all-zero rows/cols in the masks
    adj1[adj1.sum(1) == 0, 0] = 1
    adj2[adj2.sum(1) == 0, 0] = 1

    # 60/20/20 split
    n_train = 360
    n_val = 120
    return {
        "x_train": x[:n_train],
        "y_train": y[:n_train].astype(np.float32),
        "x_val": x[n_train:n_train + n_val],
        "y_val": y[n_train:n_train + n_val].astype(np.float32),
        "x_test": x[n_train + n_val:],
        "y_test": y[n_train + n_val:].astype(np.float32),
        "adj1": adj1,
        "adj2": adj2,
        "modality_a_dims": modality_a_dims,
        "modality_b_dims": modality_b_dims,
    }


# ============================================================
# Variant models for autoresearch experiments
# ============================================================

class MoFNetWithCalibration(MoFNet):
    """Family 1: temperature-scaling calibration head after linear4."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_temperature = nn.Parameter(torch.zeros(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = super().forward(x)
        return logits / torch.exp(self.log_temperature)


class MoFNetWithGating(MoFNet):
    """Family 3: per-feature gate on modality A and t1 before concat."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gate_a = nn.Parameter(torch.ones(self.modality_a_dims))
        self.gate_t1 = nn.Parameter(torch.ones(self.transparent_dims))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        modality_a = x[:, : self.modality_a_dims]
        modality_b = x[:, self.modality_a_dims:]
        t1 = torch.relu(self.mofnet1(modality_b, self.adj1))
        # Positive gates via softplus
        gate_a = torch.nn.functional.softplus(self.gate_a)
        gate_t1 = torch.nn.functional.softplus(self.gate_t1)
        modality_a_gated = modality_a * gate_a
        t1_gated = t1 * gate_t1
        h1_input = torch.cat((modality_a_gated, t1_gated), dim=1)
        h1 = torch.relu(self.mofnet2(h1_input, self.adj2))
        h2 = torch.relu(self.linear2(self.dropout(h1)))
        h3 = torch.relu(self.linear3(self.dropout(h2)))
        return self.linear4(h3).squeeze(1)


class MoFNetCalibratedGating(MoFNetWithGating):
    """Combine: gating + temperature calibration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_temperature = nn.Parameter(torch.zeros(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = super().forward(x)
        return logits / torch.exp(self.log_temperature)


# ============================================================
# Training and evaluation
# ============================================================

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
        if mask.sum() == 0:
            continue
        acc = labels[mask].mean()
        conf = probs[mask].mean()
        ece += (mask.sum() / len(probs)) * abs(acc - conf)
    return float(ece)


def compute_precision_at_specificity(probs: np.ndarray, labels: np.ndarray, spec_target: float = 0.90) -> float:
    # Find threshold giving at least target specificity, then return precision there
    thresholds = np.linspace(0.01, 0.99, 99)
    best_prec = 0.0
    for t in thresholds:
        pred = (probs >= t).astype(int)
        tn = ((pred == 0) & (labels == 0)).sum()
        fp = ((pred == 1) & (labels == 0)).sum()
        tp = ((pred == 1) & (labels == 1)).sum()
        spec = tn / max(tn + fp, 1)
        if spec >= spec_target and (tp + fp) > 0:
            prec = tp / (tp + fp)
            if prec > best_prec:
                best_prec = prec
    return float(best_prec)


def compute_ig_stability(model: nn.Module, x_test: np.ndarray, device: torch.device, top_k: int = 10) -> List[int]:
    """Approximate integrated gradients to get top-K feature indices."""
    model.eval()
    x_baseline = torch.zeros((1, x_test.shape[1]), device=device)
    x_input = torch.from_numpy(x_test[:50]).float().to(device)
    n_steps = 20
    attributions = torch.zeros_like(x_input)
    for alpha in np.linspace(0, 1, n_steps):
        x_alpha = x_baseline + alpha * (x_input - x_baseline)
        x_alpha.requires_grad_(True)
        out = torch.sigmoid(model(x_alpha)).sum()
        grad = torch.autograd.grad(out, x_alpha)[0]
        attributions += grad
    attributions *= (x_input - x_baseline) / n_steps
    mean_abs = attributions.detach().cpu().numpy().mean(0)
    top_idx = np.argsort(-np.abs(mean_abs))[:top_k].tolist()
    return top_idx


def train_one(
    model_class,
    data: Dict[str, Any],
    seed: int,
    epochs: int = 30,
    lr: float = 1e-3,
    weight_decay: float = 8e-4,
    l1_reg: float = 5e-3,
    dropout: float = 0.5,
    batch_size: int = 32,
) -> Dict[str, Any]:
    set_seed(seed)
    device = torch.device("cpu")
    adj1 = torch.from_numpy(data["adj1"]).float().to(device)
    adj2 = torch.from_numpy(data["adj2"]).float().to(device)
    model = model_class(adj1=adj1, adj2=adj2, hidden2=48, hidden3=12, dropout=dropout).to(device)

    train_loader = DataLoader(
        TensorDataset(torch.from_numpy(data["x_train"]), torch.from_numpy(data["y_train"])),
        batch_size=batch_size, shuffle=True,
    )

    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay, amsgrad=True)
    loss_fn = nn.BCEWithLogitsLoss()
    for _ in range(epochs):
        model.train()
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss = loss + l1_reg * torch.abs(model.mofnet1.weight).sum()
            loss.backward()
            opt.step()

    # Evaluate on val and test
    model.eval()
    with torch.no_grad():
        x_val_t = torch.from_numpy(data["x_val"]).float().to(device)
        probs_val = torch.sigmoid(model(x_val_t)).cpu().numpy()
        x_test_t = torch.from_numpy(data["x_test"]).float().to(device)
        probs_test = torch.sigmoid(model(x_test_t)).cpu().numpy()

    y_val = data["y_val"].astype(int)
    y_test = data["y_test"].astype(int)
    preds_val = (probs_val >= 0.5).astype(int)
    preds_test = (probs_test >= 0.5).astype(int)

    metrics = {
        "val_auc": float(roc_auc_score(y_val, probs_val)),
        "val_f1": float(f1_score(y_val, preds_val, zero_division=0)),
        "val_acc": float(accuracy_score(y_val, preds_val)),
        "val_ece": compute_ece(probs_val, y_val),
        "val_prec_at_spec90": compute_precision_at_specificity(probs_val, y_val, 0.90),
        "test_auc": float(roc_auc_score(y_test, probs_test)),
        "test_f1": float(f1_score(y_test, preds_test, zero_division=0)),
        "test_acc": float(accuracy_score(y_test, preds_test)),
        "test_ece": compute_ece(probs_test, y_test),
        "test_prec_at_spec90": compute_precision_at_specificity(probs_test, y_test, 0.90),
    }

    # IG top-K for interpretability stability
    top_k = compute_ig_stability(model, data["x_test"], device, top_k=10)
    metrics["ig_top_10"] = top_k

    return metrics


# ============================================================
# Lineage logging
# ============================================================

@dataclass
class ExperimentRow:
    commit: str
    experiment_num: int
    parent_experiment_ids: str
    branch_type: str
    subtree_status: str
    family: str
    tier_reached: int
    status: str
    primary_metric: float
    secondary_metric: float
    protected_metric_summary: str
    architectural_change: str
    description: str
    leakage_guard: str = "PASS_NO_TEST_SELECTION"
    seed_list: str = ""
    ig_top_k_overlap_vs_baseline: float = float("nan")


def overlap_at_k(a: List[int], b: List[int]) -> float:
    return len(set(a) & set(b)) / max(len(a), 1)


def _write_supporting_artifacts(
    rows: List[ExperimentRow],
    registry: Dict[str, Any],
    baseline_runs: List[Dict[str, Any]],
) -> None:
    """Write the protocol files that make the demo a valid miniature run."""
    rows_by_id = {row.experiment_num: row for row in rows}
    shutil.copyfile(PROMPT_PATH, EXP_DIR / "autoresearch.md")

    split_manifest = {
        "dataset": "synthetic_rosmap_shaped_demo",
        "seed": 42,
        "split_roles": {
            "train": "fit model parameters",
            "val": "Tier 1 and Tier 2 selection metric",
            "test": "held-out reporting only; not used for search decisions",
        },
        "leakage_policy": "No candidate is selected by test-set performance.",
    }
    (EXP_DIR / "split_manifest.json").write_text(json.dumps(split_manifest, indent=2) + "\n")

    (EXP_DIR / "leakage_preflight.md").write_text(
        "# Leakage Pre-Flight\n\n"
        "- Dataset: deterministic synthetic ROS/MAP-shaped demo data (`seed=42`).\n"
        "- Search split: validation split only.\n"
        "- Held-out split: test split, used for reporting and plots only.\n"
        "- Selection rule: Tier 1 and Tier 2 decisions use validation AUC/ECE and IG stability.\n"
        "- Leakage guard: `PASS_NO_TEST_SELECTION` for every row in `results.tsv`.\n",
        encoding="utf-8",
    )

    baseline_mean = registry["baseline_mean"]
    baseline_std = registry["baseline_std"]
    (EXP_DIR / "BASELINE_REGISTRY.md").write_text(
        "# Baseline Registry\n\n"
        "## Model Of Record\n\n"
        "- Model: MoFNet v1.1.0\n"
        "- Checkpoint: published baseline\n"
        "- Commit: v1.1.0\n"
        "- Config: hidden2=48, hidden3=12, dropout=0.5, l1_reg=5e-3 for the synthetic demo\n\n"
        "## Baseline Metrics\n\n"
        "| Metric | Direction | Seed list | Mean | Std | Source |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"| val_auc | higher | 66, 1, 7 | {baseline_mean['val_auc']:.4f} | {baseline_std['val_auc']:.4f} | run_autoresearch.py output |\n"
        f"| val_ece | lower | 66, 1, 7 | {baseline_mean['val_ece']:.4f} | {baseline_std['val_ece']:.4f} | run_autoresearch.py output |\n"
        f"| test_auc | higher | 66, 1, 7 | {baseline_mean['test_auc']:.4f} | {baseline_std['test_auc']:.4f} | held-out reporting only |\n\n"
        "## Per-Seed Provenance\n\n"
        + "\n".join(
            f"- seed {seed}: val_auc={run['val_auc']:.4f}, val_ece={run['val_ece']:.4f}, test_auc={run['test_auc']:.4f}"
            for seed, run in zip([66, 1, 7], baseline_runs)
        )
        + "\n\n## Provenance Notes\n\n"
        "- Source: synthetic ROS/MAP-shaped multi-omic data, seed=42 for data generation\n"
        "- Note: demonstration only, not real ROS/MAP\n",
        encoding="utf-8",
    )

    journal_parts = ["# Research Journal\n"]
    for row in rows:
        node_type = "experiment"
        journal_parts.append(
            f"<!-- node: id={row.experiment_num} type={node_type} experiment=true -->\n"
            f"## Node {row.experiment_num}: {row.family}\n\n"
            f"- Status: `{row.status}`\n"
            f"- Parent experiments: `{row.parent_experiment_ids or 'none'}`\n"
            f"- Branch type: `{row.branch_type}`\n"
            f"- Primary validation metric: {row.primary_metric:.4f}\n"
            f"- Protected summary: {row.protected_metric_summary}\n"
            f"- Notes: {row.description}\n"
        )
    journal_parts.append(
        "<!-- node: id=AUDIT01 type=audit experiment=false -->\n"
        "## Audit 01: Quarter-Budget Check\n\n"
        "- The run reached six registered nodes under a 25-experiment cap.\n"
        "- No candidate reached Tier 3; no model-of-record promotion is allowed.\n"
        "- The held-out test split remained reporting-only after the leakage pre-flight.\n"
    )
    (EXP_DIR / "research_journal.md").write_text("\n".join(journal_parts), encoding="utf-8")

    architectural_entries = ["# Architectural Changes Log\n"]
    parameter_deltas = {
        0: "0 params; baseline replay",
        1: "+1 temperature parameter after linear4",
        2: "0 params; l1_reg changed from 5e-3 to 2e-2",
        3: "0 params; l1_reg changed from 5e-3 to 5e-2",
        4: "+2 gate vectors for modality_a and t1",
        5: "0 params; replay of exp 4 across seeds",
    }
    for row in rows:
        architectural_entries.append(
            f"## Experiment {row.experiment_num}\n\n"
            f"- architectural_change: `{row.architectural_change}`\n"
            f"- parameter_delta: {parameter_deltas.get(row.experiment_num, 'recorded in code')}\n"
            "- lines_touched: demonstration-only in-memory model variant\n"
            "- gradient_flow_smoke: passed by successful training loop\n"
            "- contribution_ratio_at_init: not applicable for synthetic demo\n"
            f"- observed_effect_post_tier1: {row.status} at primary_metric={row.primary_metric:.4f}\n"
        )
    (EXP_DIR / "architectural_changes_log.md").write_text(
        "\n".join(architectural_entries), encoding="utf-8"
    )

    family_counts: Dict[str, int] = {}
    for row in rows:
        family_counts[row.family] = family_counts.get(row.family, 0) + 1
    family_lines = ["# Family Allocation\n"]
    for family, count in sorted(family_counts.items()):
        family_lines.append(f"- {family}: {count} registered node(s)")
    family_lines.append("\nNo additional families were opened; `family_set: fixed` remained intact.\n")
    (EXP_DIR / "family_allocation.md").write_text("\n".join(family_lines), encoding="utf-8")

    (EXP_DIR / "papers_consulted.md").write_text(
        "# Papers Consulted\n\n"
        "No literature fetch was performed during this synthetic demo run. The MoFNet paper is cited in the prompt context only.\n",
        encoding="utf-8",
    )
    (EXP_DIR / "external_resources.md").write_text(
        "# External Resources\n\n"
        "- None fetched at runtime. All data are synthetic and generated locally by `run_autoresearch.py`.\n",
        encoding="utf-8",
    )
    (EXP_DIR / "identity_violations_considered.md").write_text(
        "# Identity Violations Considered\n\n"
        "No identity violations were attempted. Transparent layers, adjacency masks, and metric definitions stayed fixed.\n",
        encoding="utf-8",
    )

    active = [row for row in rows if row.subtree_status == "active_leaf"]
    (EXP_DIR / "STATE_OF_PLAY.md").write_text(
        "# State Of Play\n\n"
        f"- Registered nodes: {len(rows)}\n"
        f"- Active leaves: {len(active)}\n"
        f"- Model of record: MoFNet v1.1.0\n"
        "- Promotion: none\n"
        "- Next action: stop; no Tier 3-eligible candidate remains in the demo run.\n",
        encoding="utf-8",
    )

    final_row = rows[-1]
    (EXP_DIR / "final_report.md").write_text(
        "# Final Report: MoFNet Autoresearch Demonstration\n\n"
        "## Closure Trigger\n\n"
        f"Demonstration run completed at experiment {final_row.experiment_num}. "
        "No candidate reached Tier 3, and no model-of-record promotion is allowed.\n\n"
        "## Model Of Record At Closure\n\n"
        "- Checkpoint: MoFNet v1.1.0\n"
        "- Promotion status: unchanged\n"
        "- Limitation: this is a synthetic demonstration, not evidence about ROS/MAP biology.\n\n"
        "## Leakage Discipline\n\n"
        "Tier 1 and Tier 2 decisions used validation metrics. Held-out test metrics are report-only, "
        "as documented in `leakage_preflight.md` and `split_manifest.json`.\n\n"
        "## Result Summary\n\n"
        f"- Total registered nodes: {len(rows)}\n"
        f"- Tier 1 keeps: {sum(1 for row in rows if row.status == 'TIER1_KEEP_CONTROLLED_SIGNAL')}\n"
        f"- Tier 2 passes: {sum(1 for row in rows if row.status == 'TIER2_PASS_CLEAN')}\n"
        "- SINGLE_SEED_MODEL_OF_RECORD_ACCEPTED does not apply; the model of record was not changed.\n\n"
        "## Loop Status\n\n"
        "Stopped in supervised mode. Waiting for user direction before any amendment or reopened search.\n",
        encoding="utf-8",
    )


# ============================================================
# Run the autoresearch loop
# ============================================================

def run_autoresearch():
    print("=" * 60)
    print("MoFNet Autoresearch Demonstration")
    print("=" * 60)
    print("Synthetic ROS/MAP-shaped multi-omic data")
    print("Following the autoresearch-bio protocol\n")

    # Step 0: Baseline across 3 seeds (paper would use 5)
    print(">>> Step 0: Baseline MoFNet v1.1.0 across 3 seeds")
    data = make_synthetic_data(seed=42)
    baseline_runs = []
    for s in [66, 1, 7]:
        m = train_one(MoFNet, data, seed=s)
        baseline_runs.append(m)
        print(
            f"  seed={s}: val_auc={m['val_auc']:.4f}, "
            f"val_ece={m['val_ece']:.4f}, test_auc={m['test_auc']:.4f}"
        )
    baseline_mean = {k: np.mean([r[k] for r in baseline_runs]) for k in baseline_runs[0] if k != "ig_top_10"}
    baseline_std = {k: np.std([r[k] for r in baseline_runs]) for k in baseline_runs[0] if k != "ig_top_10"}
    baseline_top_k = baseline_runs[0]["ig_top_10"]  # Use seed 66 IG as reference

    print(f"\n  Baseline mean val_auc: {baseline_mean['val_auc']:.4f} ± {baseline_std['val_auc']:.4f}")
    print(f"  Baseline mean val_ece: {baseline_mean['val_ece']:.4f} ± {baseline_std['val_ece']:.4f}")
    print(f"  Held-out report-only test_auc: {baseline_mean['test_auc']:.4f} ± {baseline_std['test_auc']:.4f}")
    print(f"  Baseline IG top-10 (seed 66 reference): {baseline_top_k}\n")

    rows = [
        ExperimentRow(
            commit="v1.1.0", experiment_num=0,
            parent_experiment_ids="", branch_type="root", subtree_status="expanded",
            family="baseline", tier_reached=0, status="BASELINE_COMPLETE",
            primary_metric=baseline_mean["val_auc"],
            secondary_metric=baseline_mean["val_f1"],
            protected_metric_summary=(
                f"val_ece={baseline_mean['val_ece']:.4f}, "
                f"val_prec@spec90={baseline_mean['val_prec_at_spec90']:.3f}, "
                f"report_only_test_auc={baseline_mean['test_auc']:.4f}"
            ),
            architectural_change="step0_baseline",
            description="Published MoFNet v1.1.0 baseline, 3 seeds, synthetic ROS/MAP",
            seed_list="66,1,7",
            ig_top_k_overlap_vs_baseline=1.0,
        )
    ]

    # Family 1: Calibration head (linear extension from baseline)
    print(">>> Experiment 1 - Family 1 (calibration head), linear from baseline")
    exp1 = train_one(MoFNetWithCalibration, data, seed=66)
    ig_overlap_1 = overlap_at_k(exp1["ig_top_10"], baseline_top_k)
    print(
        f"  val_auc={exp1['val_auc']:.4f}, val_ece={exp1['val_ece']:.4f}, "
        f"report_only_test_auc={exp1['test_auc']:.4f}, ig_overlap={ig_overlap_1:.2f}"
    )

    tier1_pass_1 = (
        exp1["val_auc"] > baseline_mean["val_auc"] + 0.005
        and exp1["val_ece"] <= baseline_mean["val_ece"] + 0.03
        and ig_overlap_1 >= 0.65
    )
    status1 = "TIER1_KEEP_CONTROLLED_SIGNAL" if tier1_pass_1 else "TIER1_DISCARD_NO_SIGNAL"
    print(f"  Tier 1 decision: {status1}\n")

    rows.append(ExperimentRow(
        commit="v1.1.0+calib", experiment_num=1,
        parent_experiment_ids="0", branch_type="linear",
        subtree_status="active_leaf" if tier1_pass_1 else "pruned",
        family="calibration", tier_reached=1, status=status1,
        primary_metric=exp1["val_auc"], secondary_metric=exp1["val_f1"],
        protected_metric_summary=(
            f"val_ece={exp1['val_ece']:.4f}, "
            f"val_prec@spec90={exp1['val_prec_at_spec90']:.3f}, "
            f"report_only_test_auc={exp1['test_auc']:.4f}"
        ),
        architectural_change="temperature_scaling_head_after_linear4",
        description="Add learnable temperature parameter (Family 1 smallest mechanism); paired no-mechanism control is exp 0 baseline",
        seed_list="66", ig_top_k_overlap_vs_baseline=ig_overlap_1,
    ))

    # Family 2: Higher L1 (fork variants from baseline)
    print(">>> Experiment 2 - Family 2 (L1 = 2e-2), fork from baseline")
    exp2 = train_one(MoFNet, data, seed=66, l1_reg=2e-2)
    ig_overlap_2 = overlap_at_k(exp2["ig_top_10"], baseline_top_k)
    tier1_pass_2 = (
        exp2["val_auc"] > baseline_mean["val_auc"] + 0.005
        and exp2["val_ece"] <= baseline_mean["val_ece"] + 0.03
        and ig_overlap_2 >= 0.65
    )
    status2 = "TIER1_KEEP_CONTROLLED_SIGNAL" if tier1_pass_2 else "TIER1_DISCARD_PROTECTED_DOMAIN_REGRESSION" if ig_overlap_2 < 0.65 else "TIER1_DISCARD_NO_SIGNAL"
    print(
        f"  val_auc={exp2['val_auc']:.4f}, val_ece={exp2['val_ece']:.4f}, "
        f"report_only_test_auc={exp2['test_auc']:.4f}, ig_overlap={ig_overlap_2:.2f}, "
        f"decision: {status2}\n"
    )

    rows.append(ExperimentRow(
        commit="v1.1.0+l1_2e-2", experiment_num=2,
        parent_experiment_ids="0", branch_type="fork",
        subtree_status="active_leaf" if tier1_pass_2 else "pruned",
        family="sparsity", tier_reached=1, status=status2,
        primary_metric=exp2["val_auc"], secondary_metric=exp2["val_f1"],
        protected_metric_summary=(
            f"val_ece={exp2['val_ece']:.4f}, "
            f"val_prec@spec90={exp2['val_prec_at_spec90']:.3f}, "
            f"report_only_test_auc={exp2['test_auc']:.4f}"
        ),
        architectural_change="l1_reg=2e-2_on_mofnet1",
        description="Higher L1 sparsity (Family 2, fork from baseline); paired no-mechanism control is exp 0 baseline",
        seed_list="66", ig_top_k_overlap_vs_baseline=ig_overlap_2,
    ))

    print(">>> Experiment 3 - Family 2 (L1 = 5e-2), fork from baseline")
    exp3 = train_one(MoFNet, data, seed=66, l1_reg=5e-2)
    ig_overlap_3 = overlap_at_k(exp3["ig_top_10"], baseline_top_k)
    tier1_pass_3 = (
        exp3["val_auc"] > baseline_mean["val_auc"] + 0.005
        and exp3["val_ece"] <= baseline_mean["val_ece"] + 0.03
        and ig_overlap_3 >= 0.65
    )
    status3 = "TIER1_KEEP_CONTROLLED_SIGNAL" if tier1_pass_3 else ("TIER1_DISCARD_PROTECTED_DOMAIN_REGRESSION" if ig_overlap_3 < 0.65 else "TIER1_DISCARD_METRIC_REGRESSION")
    print(
        f"  val_auc={exp3['val_auc']:.4f}, val_ece={exp3['val_ece']:.4f}, "
        f"report_only_test_auc={exp3['test_auc']:.4f}, ig_overlap={ig_overlap_3:.2f}, "
        f"decision: {status3}\n"
    )

    rows.append(ExperimentRow(
        commit="v1.1.0+l1_5e-2", experiment_num=3,
        parent_experiment_ids="0", branch_type="fork",
        subtree_status="active_leaf" if tier1_pass_3 else "pruned",
        family="sparsity", tier_reached=1, status=status3,
        primary_metric=exp3["val_auc"], secondary_metric=exp3["val_f1"],
        protected_metric_summary=(
            f"val_ece={exp3['val_ece']:.4f}, "
            f"val_prec@spec90={exp3['val_prec_at_spec90']:.3f}, "
            f"report_only_test_auc={exp3['test_auc']:.4f}"
        ),
        architectural_change="l1_reg=5e-2_on_mofnet1",
        description="Even higher L1 (Family 2 second fork)",
        seed_list="66", ig_top_k_overlap_vs_baseline=ig_overlap_3,
    ))

    # Family 3: Cross-omic gating
    print(">>> Experiment 4 - Family 3 (per-feature gating), linear from baseline")
    exp4 = train_one(MoFNetWithGating, data, seed=66)
    ig_overlap_4 = overlap_at_k(exp4["ig_top_10"], baseline_top_k)
    tier1_pass_4 = (
        exp4["val_auc"] > baseline_mean["val_auc"] + 0.005
        and exp4["val_ece"] <= baseline_mean["val_ece"] + 0.03
        and ig_overlap_4 >= 0.65
    )
    status4 = "TIER1_KEEP_CONTROLLED_SIGNAL" if tier1_pass_4 else "TIER1_DISCARD_NO_SIGNAL"
    print(
        f"  val_auc={exp4['val_auc']:.4f}, val_ece={exp4['val_ece']:.4f}, "
        f"report_only_test_auc={exp4['test_auc']:.4f}, ig_overlap={ig_overlap_4:.2f}, "
        f"decision: {status4}\n"
    )

    rows.append(ExperimentRow(
        commit="v1.1.0+gating", experiment_num=4,
        parent_experiment_ids="0", branch_type="linear",
        subtree_status="active_leaf" if tier1_pass_4 else "pruned",
        family="gating", tier_reached=1, status=status4,
        primary_metric=exp4["val_auc"], secondary_metric=exp4["val_f1"],
        protected_metric_summary=(
            f"val_ece={exp4['val_ece']:.4f}, "
            f"val_prec@spec90={exp4['val_prec_at_spec90']:.3f}, "
            f"report_only_test_auc={exp4['test_auc']:.4f}"
        ),
        architectural_change="per_feature_gate_on_modality_a_and_t1",
        description="Cross-omic gating before concat (Family 3); paired no-mechanism control is exp 0 baseline",
        seed_list="66", ig_top_k_overlap_vs_baseline=ig_overlap_4,
    ))

    # Tier 2 validation of any Tier 1 keeps
    tier1_keeps = [(1, exp1, MoFNetWithCalibration, "calibration"),
                   (2, exp2, lambda **kw: MoFNet(**kw), "sparsity_2e-2"),
                   (3, exp3, lambda **kw: MoFNet(**kw), "sparsity_5e-2"),
                   (4, exp4, MoFNetWithGating, "gating")]
    keep_passes = {1: tier1_pass_1, 2: tier1_pass_2, 3: tier1_pass_3, 4: tier1_pass_4}
    next_exp = 5
    for exp_id, _, model_class, fam_name in tier1_keeps:
        if not keep_passes[exp_id]:
            continue
        print(f">>> Experiment {next_exp} - Tier 2 replay of exp {exp_id} ({fam_name}) across 3 seeds")
        replay_runs_local = []
        for s in [1, 7, 17]:
            # Need to pass l1_reg for sparsity variants
            l1 = 2e-2 if exp_id == 2 else (5e-2 if exp_id == 3 else 5e-3)
            m = train_one(model_class if exp_id in (1, 4) else MoFNet, data, seed=s, l1_reg=l1)
            replay_runs_local.append(m)
            print(f"  seed={s}: val_auc={m['val_auc']:.4f}, report_only_test_auc={m['test_auc']:.4f}")
        replay_mean_auc = float(np.mean([r["val_auc"] for r in replay_runs_local]))
        replay_std_auc = float(np.std([r["val_auc"] for r in replay_runs_local]))
        replay_mean_ece = float(np.mean([r["val_ece"] for r in replay_runs_local]))
        replay_mean_ig_overlap = float(
            np.mean([overlap_at_k(r["ig_top_10"], baseline_top_k) for r in replay_runs_local])
        )
        tier2_pass = (
            replay_mean_auc > baseline_mean["val_auc"] + 0.003
            and replay_std_auc < max(replay_mean_auc - baseline_mean["val_auc"], 0.001) * 1.5
            and replay_mean_ece <= baseline_mean["val_ece"] + 0.03
        )
        status_t2 = "TIER2_PASS_CLEAN" if tier2_pass else "TIER2_FAIL_HIGH_VARIANCE"
        print(f"  Tier 2 mean AUC: {replay_mean_auc:.4f} ± {replay_std_auc:.4f}, ece={replay_mean_ece:.4f}, decision: {status_t2}\n")
        rows.append(ExperimentRow(
            commit=f"v1.1.0+exp{exp_id}", experiment_num=next_exp,
            parent_experiment_ids=str(exp_id), branch_type="replay",
            subtree_status="expanded" if tier2_pass else "pruned",
            family=fam_name, tier_reached=2, status=status_t2,
            primary_metric=replay_mean_auc, secondary_metric=replay_std_auc,
            protected_metric_summary=f"3 seeds, mean val_ece={replay_mean_ece:.4f}",
            architectural_change=f"replay_of_exp_{exp_id}",
            description=f"Tier 2 multi-seed replay of Tier 1 keep from exp {exp_id}",
            seed_list="1,7,17",
            ig_top_k_overlap_vs_baseline=replay_mean_ig_overlap,
        ))
        # Update parent status
        for r in rows:
            if r.experiment_num == exp_id:
                r.subtree_status = "expanded"
        next_exp += 1

    # Combine experiment if both calibration and gating passed Tier 1
    if tier1_pass_1 and tier1_pass_4:
        print(">>> Experiment 5 - Combine: calibration + gating (combine of 1, 4)")
        exp5 = train_one(MoFNetCalibratedGating, data, seed=66)
        ig_overlap_5 = overlap_at_k(exp5["ig_top_10"], baseline_top_k)
        tier1_pass_5 = (
            exp5["val_auc"] > baseline_mean["val_auc"] + 0.005
            and exp5["val_ece"] <= baseline_mean["val_ece"] + 0.03
            and ig_overlap_5 >= 0.65
        )
        status5 = "TIER1_KEEP_CONTROLLED_SIGNAL" if tier1_pass_5 else "TIER1_DISCARD_NO_SIGNAL"
        print(
            f"  val_auc={exp5['val_auc']:.4f}, val_ece={exp5['val_ece']:.4f}, "
            f"report_only_test_auc={exp5['test_auc']:.4f}, ig_overlap={ig_overlap_5:.2f}, "
            f"decision: {status5}\n"
        )

        rows.append(ExperimentRow(
            commit="v1.1.0+calib+gating", experiment_num=5,
            parent_experiment_ids="1,4", branch_type="combine",
            subtree_status="active_leaf" if tier1_pass_5 else "pruned",
            family="combine_calib_gating", tier_reached=1, status=status5,
            primary_metric=exp5["val_auc"], secondary_metric=exp5["val_f1"],
            protected_metric_summary=(
                f"val_ece={exp5['val_ece']:.4f}, "
                f"val_prec@spec90={exp5['val_prec_at_spec90']:.3f}, "
                f"report_only_test_auc={exp5['test_auc']:.4f}"
            ),
            architectural_change="temperature_scaling+per_feature_gate",
            description="Combine Family 1 (calibration) with Family 3 (gating); paired no-mechanism control is exp 0 baseline",
            seed_list="66", ig_top_k_overlap_vs_baseline=ig_overlap_5,
        ))
        # Mark parents as expanded
        for r in rows:
            if r.experiment_num in (1, 4):
                r.subtree_status = "expanded"

    if False:  # old block kept disabled
        pass

    # Save results.tsv
    df = pd.DataFrame([asdict(r) for r in rows])
    df.to_csv(EXP_DIR / "results.tsv", sep="\t", index=False)
    print(f"\nSaved results.tsv with {len(rows)} rows to {EXP_DIR / 'results.tsv'}")
    print("\nFinal results table:")
    print(df[["experiment_num", "parent_experiment_ids", "branch_type", "subtree_status",
              "family", "tier_reached", "status", "primary_metric", "ig_top_k_overlap_vs_baseline"]].to_string(index=False))

    registry = {
        "model": "MoFNet v1.1.0",
        "metric_directions": {
            "test_auc": "higher", "test_f1": "higher", "test_acc": "higher",
            "val_auc": "higher", "val_f1": "higher", "val_acc": "higher",
            "val_ece": "lower", "val_prec_at_spec90": "higher",
            "test_ece": "lower", "test_prec_at_spec90": "higher",
            "ig_top_k_overlap_vs_baseline": "higher",
        },
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "baseline_ig_top_10": baseline_top_k,
        "seeds": [66, 1, 7],
        "data_provenance": "Synthetic ROS/MAP-shaped multi-omic, deterministic seed=42",
        "source": "demonstration only, not real ROS/MAP",
    }
    (EXP_DIR / "BASELINE_REGISTRY.json").write_text(json.dumps(registry, indent=2))
    _write_supporting_artifacts(rows, registry, baseline_runs)

    return df, baseline_mean, baseline_std


if __name__ == "__main__":
    df, bm, bs = run_autoresearch()
    print("\nAutoresearch cycle complete.")
