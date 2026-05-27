# Metric And Evaluation Investigation Protocol

Sometimes the next step is not another architecture. It is checking whether the metrics are misleading.

Open a focused metric investigation when any of these hold:

- single-seed wins repeatedly fail multi-seed validation;
- standard metrics improve while biological/domain structure regresses;
- baseline standard deviation is large relative to mean;
- candidates appear to exploit metric loopholes;
- predictions look compressed, mean-like, or mode-collapsed;
- different summaries disagree about the baseline;
- literature warns that common metrics reward mode collapse;
- null baselines are missing or suspiciously strong;
- technical duplicate or empirical ceiling is unknown;
- the `leakage_preflight.md` audit reveals a `selection_signal` path that was previously unaccounted for, or a `WARN_TEST_READ_FOR_DIAGNOSTICS_ONLY` classification needs re-examination.

### Test-Derived Signals Are Not Training Inputs

Attributions, saliency maps, calibration curves, error analyses, and any other quantity computed on a `locked_test` or held-out split are not eligible inputs to subsequent training, anchoring, warm-starting, or hyperparameter selection. Such quantities may appear in audits and final reports only.

When the search needs an anchor (for example, integrated-gradients top-K features used as a regularization target during training), the anchor must be derived from `train` data only. If validation-derived anchors are used, they must be re-derived per validation fold to avoid implicit selection on the same fold used for candidate ranking. The full rule and its rationale live in `core_protocol.md §3.5`; this file restates it because metric investigations are the most common place where the rule gets quietly violated.

---

## Investigation Rules

A metric investigation is not architecture search.

Rules:

- do not modify production model code;
- do not launch new architectural experiments;
- do not rebase the model/system of record;
- do not overwrite baseline summaries;
- use an isolated investigation directory;
- make all metric directionality explicit;
- document artifact limitations before drawing conclusions.

Create:

```text
outputs/<metric_investigation_name>/
```

Required outputs:

```text
INVENTORY.md
METHODS.md
BASELINES.md
VARIANCE_DECOMPOSITION.md
METRIC_STACK_RESULTS.md
REPORT.md
```

---

## Task 0: Inventory First

Before computing anything, list available artifacts:

- prediction arrays;
- pseudobulk profiles;
- per-seed metrics;
- checkpoints;
- evaluation outputs;
- data split files;
- summary reports;
- model configs;
- preprocessing transforms;
- raw vs normalized output formats.

State whether new metrics can be computed from existing artifacts or require fresh evaluation. If artifacts are missing, proceed with what exists and flag limitations.

---

## Baselines And Nulls

For distributional prediction tasks, create a realistic empirical ceiling by splitting target observations in half and comparing half A to half B.

Report every model metric alongside:

- model-of-record baseline;
- technical duplicate ceiling;
- source-as-target null;
- global dataset mean null;
- matched-target-time mean null;
- matched-cell-type mean null;
- variance-shrunk prediction null;
- pseudobulk-only mean null;
- random-label or permuted-condition null when appropriate.

A candidate that only matches a null baseline is not a model improvement.

---

## Variance Decomposition

Separate:

- training stochasticity: seed-to-seed variation;
- evaluation metric noise: bootstrap/test-resampling variation;
- biological/sampling variability: technical duplicate variation;
- split sensitivity: train/validation/test split changes;
- condition sensitivity: perturbation, donor, time, dose, protocol, or cell-type effects.

Report whether claimed improvements exceed each relevant noise source.

---

## Metric Directionality

Before applying thresholds, define every metric as higher-is-better or lower-is-better.

For comparison against a baseline distribution:

```text
higher-is-better: candidate > baseline_mean + 1σ
lower-is-better:  candidate < baseline_mean - 1σ
```

Prefer converting every metric to a signed beneficial z-score where positive means better than baseline.

---

## Metric Stack Design

A robust metric stack should include:

- one broad distributional metric;
- one directionality metric;
- one marker/program or pathway metric;
- one diversity/mode-collapse metric;
- one held-out/generalization metric;
- one null-baseline comparison;
- one empirical ceiling or technical-duplicate comparison when available.

No single metric can promote a model by itself.

---

## Reopening Criterion

Pre-register a reopening rule. Example:

```text
Reopen architecture search only if:
1. at least two near-miss candidates beat the model-of-record baseline by >1σ on at least two robust metrics, and
2. the technical duplicate baseline shows real headroom above the model-of-record baseline, and
3. the candidate is not merely matching a mode-collapse/null baseline, and
4. protected biological or domain metrics remain within gate.
```

If these conditions fail, keep architecture search closed and move to the next phase.

---

## Investigation Report Structure

```markdown
# Metric Investigation Report

## Question
<why this investigation was opened>

## Inventory Summary
<available artifacts and missing artifacts>

## Methods
<metrics, nulls, technical duplicate approach, bootstrap/variance plan>

## Metric Directionality
| Metric | Direction | Interpretation | Failure mode it detects |
| --- | --- | --- | --- |

## Baselines And Nulls
| Baseline/null | Description | Source artifacts | Notes |
| --- | --- | --- | --- |

## Variance Decomposition
<training/evaluation/biological/domain/split/condition variance>

## Results
<metric tables and plots>

## Reopening Decision
- [ ] Reopen architecture search
- [ ] Keep architecture search closed
- [ ] Require more artifacts before deciding

## Rationale
<evidence tied to reopening rule>

## Next Action
<exact next artifact or amendment>
```
