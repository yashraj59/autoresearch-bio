# Final Report: MoFNet Autoresearch Demonstration

## Closure Trigger

Demonstration run completed at experiment 5. Tier 2 multi-seed validation of the only Tier 1 keep returned `TIER2_FAIL_HIGH_VARIANCE`, leaving no active Tier 1 keeps in the search tree and no candidate eligible for Tier 3 promotion. Loop halted per protocol.

## Model Of Record At Closure

- Checkpoint: MoFNet v1.1.0
- Commit: `v1.1.0` (matches Journal of Alzheimer's Disease 2025 publication)
- Config: `hidden2=96, hidden3=16, dropout=0.5, lr=1e-3, weight_decay=8e-4, l1_reg=5e-3`
- Baseline registry: `outputs/experiments/BASELINE_REGISTRY.json`
- Promotion status: unchanged. No candidate was promoted.

## Experiment Summary

| Count | Value |
| --- | --- |
| Total experiments | 6 (including baseline) |
| Tier 1 keeps | 1 (gating) |
| Tier 2 passes | 0 |
| Tier 3 passes | 0 |
| Useful failures | 1 (gating, caught by Tier 2 noise check) |
| Families retired | 2 (calibration, sparsity) |
| Subtrees pruned | 4 |

## Family-By-Family Findings

| Family | Experiments | Best result | Status | Lesson |
| --- | --- | --- | --- | --- |
| Calibration (Family 1) | exp 1 | AUC 0.9004 single seed, ECE 0.145 | retired | Temperature head improved AUC slightly but worsened ECE, opposite of the intended calibration benefit |
| Sparsity (Family 2) | exp 2, 3 | AUC 0.8850 / 0.8844 | retired | Higher L1 hurt AUC on this synthetic distribution; useful failure |
| Gating (Family 3) | exp 4, 5 | Tier 1 0.8965, Tier 2 0.8937 ± 0.0024 | pruned at Tier 2 | Tier 1 looked like a clean keep but Tier 2 mean matched baseline exactly, classic single-seed false positive |

## Search Tree Summary

The DAG has 6 nodes. Exp 0 is the root (Step 0 baseline). Three families branched from it: exp 1 (linear, calibration), exps 2 and 3 (fork pair, sparsity at two L1 values), and exp 4 (linear, gating). Exp 5 is a `replay` child of exp 4 representing the Tier 2 multi-seed validation. No `combine` experiments fired because only one Tier 1 keep was available, and that keep failed Tier 2 before any combinations could be proposed.

Visualization: `outputs/plots/mofnet_autoresearch_tree.png`

## Strongest Useful Failure

Experiment 4 (gating, Family 3) at Tier 1 with seed 66 showed test AUC = 0.8965, which is within the baseline 1σ band (0.8937 ± 0.0031) but above the baseline mean. The Tier 1 gate accepted it because val AUC met the threshold. Tier 2 multi-seed replay across seeds [1, 7, 17] produced mean AUC = 0.8937 ± 0.0024, exactly matching the baseline. The "improvement" was lucky seed variance.

This is the central case the autoresearch-bio protocol is designed to catch. A naive loop without Tier 2 multi-seed validation would have promoted exp 4 as a "win" and the user would have spent compute on a non-improvement.

## Protected No-Regression Status

All experiments produced IG top-10 overlap of 1.0 against the baseline reference. This is partly because the synthetic dataset has strong signal features that dominate attributions; on real ROS/MAP the IG stability gate would do real work. The ECE gate held throughout. Precision @ specificity ≥ 0.90 held at 1.0 across all experiments (small test set, easy positive class).

## Statistical Evidence

- Baseline: mean test AUC 0.8937, std 0.0031 across seeds [66, 1, 7]
- Tier 2 gating replay: mean 0.8937, std 0.0024 across seeds [1, 7, 17]
- Paired delta: ≈ 0
- Practical effect size: 0
- Multiple-comparison risk: low (4 candidates, no fishing)

The minimum meaningful improvement pre-registered in `autoresearch.md` was +0.015 absolute AUC. No candidate came close.

## Biological Evidence And Caveats

This demonstration ran on synthetic ROS/MAP-shaped data. The signal features were chosen deterministically and IG stability is therefore artificially high. On real ROS/MAP:

- IG top-K stability would have variance and would be a real protected gate.
- Subnetwork concordance with the published findings (innate immunity, protein clearance, neurotransmitter release) would need to be checked against the actual marker lists from the 2025 paper.
- Cross-cohort generalization would require an external AD cohort, which was marked `TO_FILL_BEFORE_LAUNCH`.

No deployment-facing biological claims should be drawn from this demonstration. Numbers are illustrative of protocol behavior, not biology.

## Metric / Evaluation Caveats

The Tier 1 gate used `val_auc > baseline_val_mean + 0.005` and `ig_overlap >= 0.65`. The val AUC gate is the single largest filter and is dominated by single-seed noise. The protocol's strength is exactly that Tier 2 catches what Tier 1 lets through.

## Artifact Retention Summary

- Retained: baseline checkpoint (model of record), all results.tsv rows including pruned ones, baseline registry, plots, this report.
- Deleted: candidate checkpoints for all pruned experiments.
- Audit-relevant: exp 4 (gating Tier 1 keep that failed Tier 2). Keep its weights for future internal-state diagnostics if anyone wants to understand the seed-luck signature.

## Recommended Next Phase

The current architecture search exhausted three families without a Tier 3 candidate. Per the skill protocol, the next phase should be one of:

1. Metric / evaluation reform. Specifically: re-examine whether AUC at the published level is approaching the empirical ceiling. Run a technical-duplicate or null-baseline analysis to estimate headroom. This is `references/metric_investigation.md` territory.
2. Dataset expansion. ROS/MAP alone may be undersized for further improvement. Adding ADNI multi-omic or AMP-AD bulk RNA-seq could open new headroom.
3. Calibration as a separate goal. Family 1 hurt ECE rather than helping. A dedicated calibration investigation (post-hoc isotonic regression, Platt scaling on the val set without retraining) might improve clinical relevance without touching the model.
4. Reopen Family 3 (gating) with a different parameterization. The per-feature gate hit baseline noise. A modality-level gate (one weight for modality A, one for the transparent branch) might give cleaner signal.

Do not keep running small variants of the three retired families without a new diagnostic reason. The autoresearch-bio protocol explicitly warns against that.

## Loop Status

The autonomous loop is stopped. Waiting for user direction on next phase. Supervised mode (no Debate Council convened, since the run was supervised by default per the skill protocol).
