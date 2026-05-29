# Metric Calibration Audit — <run id>

Paste-ready template for `outputs/metric_calibration_audit/report.md`. See `references/metric_calibration_audit.md` for the procedure and thresholds.

## Audit context

- Date (UTC): <timestamp>
- Trigger: <first-10-candidates | quarter-budget reassessment N=... | post-amendment>
- Screen metric: <name of the cheap in-loop metric>
- Promotion metric: <name of the model-of-record metric, computed on the `validation` role>
- Candidates included (n): <integer, must be >= 10>

## Candidates

| experiment_num | screen_score | promotion_metric_score |
| --- | ---: | ---: |
| <EXPNNN> | <float> | <float> |

(One row per candidate that has both scores. n rows total.)

## Correlations

- Pearson r: <value> (95% CI <lo, hi>)
- Spearman rho: <value> (95% CI <lo, hi>)
- Rank-preservation rate (fraction of candidate pairs the screen and promotion metric agree on): <value>

## Scatter plot

- Path: `outputs/metric_calibration_audit/scatter.png`
- Screen on x, promotion metric on y, identity line drawn.

## Decision

- Verdict: <CALIBRATED_KEEP | CALIBRATED_DEGRADED_MONITOR | METRIC_SCREEN_DEMOTED_BY_CALIBRATION_AUDIT>
- Rationale: <one or two sentences tied to the thresholds in metric_calibration_audit.md>

## Required follow-up if demoted

- The controlled-margin gate is suspended.
- The screen drops to floor-only (may reject obviously-bad candidates, may not rank candidates for confirmation reads).
- A supervised amendment must register a calibration-aware replacement screen before the gate is restored.
- Re-running the same demoted screen is not sufficient; a fresh audit on n >= 10 with the replacement screen is required.
