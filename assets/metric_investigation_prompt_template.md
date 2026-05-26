# Metric Investigation Prompt Template

```markdown
# Metric Investigation: <Project / Run>

## Purpose

Investigate whether the current evaluation metrics are reliable enough to reopen architecture search. This is not architecture search. Do not modify production model code, training scripts, locked files, or the model/system of record.

## Scope

Create isolated directory:

`outputs/<metric_investigation_name>/`

Required outputs:

- `INVENTORY.md`
- `METHODS.md`
- `BASELINES.md`
- `VARIANCE_DECOMPOSITION.md`
- `METRIC_STACK_RESULTS.md`
- `REPORT.md`

## Active Model/System Of Record

- Checkpoint: `<TO_FILL_BEFORE_LAUNCH>`
- Commit/config: `<TO_FILL_BEFORE_LAUNCH>`
- Baseline registry: `<path>`

## Task 0: Inventory First

List available artifacts before computing anything:

- prediction arrays;
- pseudobulk profiles;
- per-seed metrics;
- checkpoints;
- evaluation outputs;
- data split files;
- summary reports;
- preprocessing transforms.

State which metrics can be computed from existing artifacts and which require fresh evaluation.

## Baselines And Nulls

Report every model metric alongside:

- model-of-record baseline;
- technical duplicate ceiling;
- source-as-target null;
- global dataset mean null;
- matched-target-time mean null;
- matched-cell-type mean null;
- variance-shrunk prediction null;
- pseudobulk-only mean null;
- random-label/permuted-condition null if appropriate.

## Variance Decomposition

Separate:

- training stochasticity;
- evaluation/bootstrap noise;
- biological/domain/sampling variability;
- split sensitivity;
- condition/cell-type sensitivity.

## Metric Directionality

Create a table:

| Metric | Direction | What it rewards | Known loophole | Robustness status |
| --- | --- | --- | --- | --- |

Convert metrics to signed beneficial z-scores when possible.

## Reopening Rule

Reopen architecture search only if:

1. at least two near-miss candidates beat the model-of-record baseline by >1σ on at least two robust metrics;
2. the technical duplicate ceiling shows real headroom above the model-of-record baseline;
3. candidates are not merely matching a null or mode-collapse baseline;
4. protected biological or domain metrics remain within gate.

If these conditions fail, keep architecture search closed and recommend the next phase.

## Final Report

`REPORT.md` must conclude with one of:

- `METRIC_REOPEN_ARCHITECTURE_SEARCH`
- `METRIC_KEEP_SEARCH_CLOSED`
- `METRIC_MORE_ARTIFACTS_REQUIRED`
- `METRIC_STACK_INVALID_OLD_SEARCH_PAUSED`
```
