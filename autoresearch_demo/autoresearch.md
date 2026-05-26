# MoFNet Autoresearch-Bio: Improve Alzheimer's Classification Without Breaking Interpretability

## Model Or System Of Record

- Model: MoFNet v1.1.0 (single-file `mofnet.py`)
- Commit/tag: `v1.1.0` (matches Journal of Alzheimer's Disease 2025 publication; PubMed 38728189)
- Config: `hidden2=96, hidden3=16, dropout=0.5, lr=1e-3, weight_decay=8e-4, l1_reg=5e-3, epochs=100, batch_size=32`
- Why active: published, peer-reviewed baseline. Test metrics on ROS/MAP are the reference.
- Domain: biology, scientific ML, single-cohort multi-omic disease classification
- Rebasing rule: only a Tier 3 pass that satisfies every pre-registered gate, including interpretability stability, can supersede this model of record.

## Role

You are an autonomous research agent improving MoFNet for Alzheimer's classification on the ROS/MAP cohort. You must document every experiment, preserve the published baseline, protect interpretability and clinical-relevance metrics, track experiment lineage, and stop when stop conditions fire.

This run is not unbounded exploration, metric hacking, or permission to change the transparent layer structure, the adjacency masks, the data splits, or the evaluation script.

## Setup

1. Create branch `autoresearch-2026-05` from commit `v1.1.0`.
2. Read these files completely:
   - `mofnet.py`
   - `tests/test_mofnet.py`
   - `README.md`
   - `pyproject.toml`
   - The published paper for context on biological interpretation
3. Initialize required logs:
   - `results.tsv` with lineage columns (`parent_experiment_ids`, `branch_type`, `subtree_status`)
   - `research_journal.md`
   - `architectural_changes_log.md`
   - `family_allocation.md`
   - `BASELINE_REGISTRY.md`
   - `papers_consulted.md`
   - `external_resources.md`
   - `identity_violations_considered.md`
   - `insights/`
4. Verify the existing CLI runs end-to-end on a small synthetic dataset before touching architecture.
5. Run Step 0 baselines before any architecture search.

## Model Identity

### Keep

- The two transparent layers `mofnet1` and `mofnet2` with `MoFNetLayer` masked-linear semantics.
- The trans-omic information flow: modality_b → mofnet1 → concat with modality_a → mofnet2 → dense head.
- The adjacency masks `adj1` and `adj2` as the prior biological structure.
- The L1 penalty on `mofnet1.weight` as the sparsity prior.
- Integrated Gradients as the explainability method.

### Can Modify

- The dense head after `mofnet2` (`linear2`, `linear3`, `linear4`).
- Dropout placement and rate.
- Auxiliary calibration heads attached after `linear4`.
- Optional cross-omic gating between `modality_a` features and `t1` output before the concat.
- The optimizer schedule, weight decay, and L1 weight (but not removal of L1).
- Training-time auxiliary losses that do not modify the masked layers.

### Cannot Modify

- `adj1.csv` and `adj2.csv` (the biological priors).
- The `MoFNetLayer` masked structure.
- The two-layer transparent design.
- The data splits used in the published paper.
- The integrated-gradients evaluation script.
- The metric definitions (accuracy, precision, recall, F1, AUC, specificity).

### Escalation Rule

If a proposed experiment violates identity or locked files, document it in `identity_violations_considered.md` and stop for amendment. Do not silently expand scope to remove the transparent layers.

## Step 0 Baselines

Run MoFNet v1.1.0 on the published ROS/MAP train/val/test split using 5 seeds.

- Datasets and roles:
  - Search dataset: ROS/MAP train + val
  - No-regression validator: ROS/MAP test (held out from search, evaluated only at Tier 3)
  - Held-out generalization: external AD cohort if available (e.g., ADNI multi-omic subset), otherwise mark as `TO_FILL_BEFORE_LAUNCH`
- Seeds: `[66, 1, 7, 17, 23]`
- Baseline registry required: yes.
- Ambiguity rule: if summary metrics disagree with per-seed JSON outputs, inspect raw per-seed files. If ambiguity remains, mark `BASELINE_AMBIGUOUS_PROVENANCE_BLOCKED`.

`BASELINE_REGISTRY.md` must record the dataset, split, checkpoint, commit, config, seed list, per-seed metrics, mean/std, metric directionality, source files, and caveats.

Step 0 baselines are logged as `root` nodes in the lineage DAG with empty `parent_experiment_ids`.

## Search Targets

### Primary Metrics

| Metric | Direction | Baseline mean ± std | Minimum meaningful improvement | Tier 3 gate |
| --- | --- | --- | --- | --- |
| Test AUC | higher | `TO_FILL_BEFORE_LAUNCH` | +0.015 absolute | mean ≥ baseline + 0.015 and CI excludes baseline |

### Secondary Metrics

| Metric | Direction | Baseline mean ± std | Gate |
| --- | --- | --- | --- |
| Test F1 | higher | `TO_FILL_BEFORE_LAUNCH` | not worse than baseline by > 0.02 |
| Test accuracy | higher | `TO_FILL_BEFORE_LAUNCH` | not worse than baseline by > 0.02 |

### Protected Biological And Clinical Metrics

| Metric | Protected behavior | Baseline mean ± std | Regression gate | Catastrophic fail |
| --- | --- | --- | --- | --- |
| Integrated Gradients top-K stability | top-20 feature overlap across seeds must remain ≥ 0.70 | `TO_FILL_BEFORE_LAUNCH` | drop ≤ 0.05 | drop > 0.10 |
| Precision @ specificity ≥ 0.90 | clinical relevance | `TO_FILL_BEFORE_LAUNCH` | drop ≤ 0.03 | drop > 0.08 |
| Expected Calibration Error (ECE) | clinical calibration | `TO_FILL_BEFORE_LAUNCH` | does not increase by > 0.02 | increases > 0.05 |
| Subnetwork concordance with published findings | innate immunity, protein clearance, neurotransmitter release modules | `TO_FILL_BEFORE_LAUNCH` | overlap ≥ 0.60 | overlap < 0.40 |

A candidate that improves AUC while damaging integrated-gradients stability or pathway concordance is a useful failure, not a new baseline. The whole point of MoFNet is interpretability. AUC alone is not enough.

## Architectural Families

### Family 1: Auxiliary calibration on the emission head

- Motivation: clinical use needs well-calibrated probabilities, not just discrimination. ECE on the published baseline is the gap most likely to matter for downstream clinical workflows.
- Hypothesis: a temperature-scaling head or beta-calibration head trained jointly will improve ECE without affecting integrated-gradients attribution on transparent layers, because the head sits after `linear4`.
- Suggested experiments:
  1. Add a learnable temperature parameter after `linear4`. Train end-to-end. Smallest mechanism.
  2. Replace temperature with a 2-parameter Platt-style head (`a * logit + b`).
  3. Beta calibration head (two-parameter Beta distribution).
- Constraints: head must sit after `linear4`. Must not modify transparent layers. Parameter budget: ≤ 5 added params.
- Required diagnostics: ECE, reliability diagram, AUC stability, IG top-K stability.
- Stop/pivot rule: retire if no calibration improvement after 3 variants, or if any variant damages IG stability.

### Family 2: Stronger sparsity on transparent layers

- Motivation: ROS/MAP is small (~1000 samples). Overfitting risk on the transparent layers is high.
- Hypothesis: increasing L1 on `mofnet1.weight`, or adding group-sparsity on `mofnet2`, will improve generalization and tighten interpretability (fewer, more confident attributions).
- Suggested experiments:
  1. L1 weight grid: `[1e-2, 2e-2, 5e-2]` (linear extensions of baseline).
  2. Group-L1 on `mofnet2` rows (gene-level sparsity).
  3. Combined L1 on `mofnet1` plus group-L1 on `mofnet2`.
- Constraints: cannot remove L1 entirely; cannot change adjacency masks.
- Required diagnostics: effective sparsity (% near-zero weights), top-K IG stability, AUC, contribution ratio.
- Stop/pivot rule: retire if effective sparsity exceeds 90% with AUC drop > 0.03, indicating the model is collapsing into a few features.

### Family 3: Cross-omic gating before concat

- Motivation: in baseline, modality A and the transparent output `t1` are concatenated without weighting. This treats all features equally even when one modality is dominant.
- Hypothesis: a gating layer that learns per-feature weights for `modality_a` and `t1` before concat will improve AUC by focusing capacity on the more informative modality without breaking the transparent structure.
- Suggested experiments:
  1. Scalar gate: one learnable weight per modality (2 params).
  2. Per-feature gate on `t1` (transparent_dims params).
  3. Per-feature gate on both `modality_a` and `t1`.
- Constraints: gate must be a positive multiplicative weight; cannot replace the concat with attention.
- Required diagnostics: gate values per modality, contribution ratio of `modality_a` vs `t1` before concat.
- Stop/pivot rule: retire if gate collapses to one modality and IG stability drops > 0.05.

### Family 4: Uncertainty-aware predictions via MC dropout

- Motivation: clinical predictions need uncertainty estimates. The current single-pass prediction does not provide one.
- Hypothesis: enabling MC dropout at inference and averaging multiple stochastic forward passes will give calibrated uncertainty without changing the trained model.
- Suggested experiments:
  1. MC dropout with K=20 samples at inference only.
  2. MC dropout combined with calibration head from Family 1 (this would be a `combine` node).
- Constraints: training-time loss unchanged; inference cost ≤ 20x baseline.
- Required diagnostics: predictive entropy distribution, calibration with and without MC, AUC.
- Stop/pivot rule: retire if MC averaging hurts AUC by > 0.01.

## Lineage Rules

Every experiment must be logged as a node in the search DAG. The agent records `parent_experiment_ids`, `branch_type` (one of `root`, `linear`, `fork`, `combine`, `replay`), and `subtree_status` (one of `active_leaf`, `expanded`, `pruned`, `promoted`, `retired_subtree`).

Step 0 baseline is `root`. Variants within a family from the same parent are `fork`. Tier 2 multi-seed runs of a Tier 1 keep are `replay`. Combination experiments (e.g., Family 1 + Family 3) are `combine` with both parents listed.

Read `references/lineage.md` for the full rules.

## Tiered Evaluation

### Tier 1: Fast Single-Seed Filter

- Procedure: train with seed=66, 50 epochs (half the full schedule), evaluate on ROS/MAP val and a small probe on test.
- Keep criteria:
  - AUC on val ≥ baseline val AUC + 0.01
  - ECE does not increase by > 0.03
  - IG top-20 overlap with baseline ≥ 0.65
  - lineage columns recorded
- Fail-fast labels:
  - `TIER1_DISCARD_NO_SIGNAL`
  - `TIER1_DISCARD_PROTECTED_DOMAIN_REGRESSION`
  - `TIER1_DISCARD_MARKER_OR_PROGRAM_REGRESSION`

### Tier 2: Multi-Seed Validation

- Procedure: 5 seeds `[66, 1, 7, 17, 23]`, full 100-epoch training.
- Pass criteria:
  - AUC improvement holds across seeds with std smaller than the claimed effect
  - ECE non-regression holds
  - IG stability gate holds
  - precision @ specificity ≥ 0.90 non-regression holds
- Tier 2 results are logged as `replay` of the corresponding Tier 1 keep.

### Tier 3: No-Regression / Generalization Validation

- Procedure: evaluate on held-out ROS/MAP test (no-regression) and external AD cohort if available (generalization).
- Promotion criteria:
  - AUC improves by ≥ 0.015 with CI excluding baseline
  - all protected biological and clinical metrics pass
  - subnetwork concordance with published findings ≥ 0.60
  - integrated-gradients top-K stability gate holds
  - generalization check passes

Only Tier 3 passes can promote a new model of record.

## Required Diagnostics

### Universal

```text
raw_contribution_ratio
post_gate_contribution_ratio
final_contribution_ratio
cap_hit_fraction
contribution_to_base_ratio
ratio_by_epoch
ratio_by_dataset
unweighted_aux_loss
weighted_aux_loss
main_loss
weighted_aux_to_main_ratio
mode_collapse_null_comparison
```

### Biology (keep for MoFNet)

```text
ig_top_k_stability
ig_subnetwork_concordance
pathway_capture_innate_immunity
pathway_capture_protein_clearance
pathway_capture_neurotransmitter
cross_omic_modality_weight_ratio
```

## Family Allocation

- Stage A: Step 0 baselines for v1.1.0 across 5 seeds; build `BASELINE_REGISTRY.md`.
- Stage B: 1 smoke test per family (4 experiments total).
- Stage C: deepen only families with controlled, non-destructive signal.
- Stage D: close or open a metric/IG-stability investigation if repeated IG regressions occur.

- Initial experiment cap: 25
- Consecutive Tier 1 discard cap: 5
- Tier 2 seed count: 5
- Tier 3 promotion target count: 1

## Statistical Promotion Discipline

For every Tier 2 and Tier 3 comparison: report per-seed values, mean and std, paired comparison against baseline on the same 5 seeds, practical effect size, multiple-comparison flag. Never promote a candidate whose AUC improvement is smaller than the per-seed baseline standard deviation.

## Stop Conditions

Stop when any of these fire:

- experiment cap of 25 reached
- consecutive Tier 1 discards reach 5
- all four families tested without a Tier 3 win
- repeated IG-stability regressions across two or more families
- ROS/MAP test set artifact ambiguity cannot be resolved
- a metric investigation invalidates the AUC delta interpretation
- the active subtree in the search DAG has no remaining `active_leaf` nodes and no new family is authorized
- user-directed closure

When stop fires: finish current experiment, write journal entry, update `results.tsv` and `family_allocation.md`, write `final_report.md` including a search-tree summary, and halt unless Debate Council mode is explicitly enabled.

## Autonomy Mode

Mode: `supervised`

Default. The Debate Council is not enabled for this run because the integrated-gradients interpretability call is the central scientific claim of MoFNet, and biology-interpretation decisions should not be delegated to a council of role-prompted LLMs. Stop conditions halt the loop and wait for the user to write the amendment.

## Safety Boundary

This is computational model research planning only. Do not produce clinical recommendations, diagnostic claims, or deployment-facing biological claims from Tier 1 or Tier 2 results. The ROS/MAP dataset and external AD cohorts require proper data-use agreements and de-identification confirmation before any external claim is made.

Begin only after Step 0 baselines are complete.
