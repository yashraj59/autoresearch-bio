# Metric Calibration Audit

The procedure behind `core_protocol.md §17`. It answers one question: does the cheap screen the loop uses to rank candidates actually rank-order them the same way the expensive model-of-record metric does? If not, the loop has been spending confirmation reads on candidates the screen liked for the wrong reasons.

## When to run

- The first time the run has at least ten registered candidates with both a screen score and a model-of-record-metric score.
- At every quarter-budget reassessment thereafter (`core_protocol.md §23`).
- On demand after any amendment that changes the screen or the promotion metric.

## Procedure

1. **Identify paired-score candidates.** Collect every experiment in `results.tsv` that has both a screen score (the cheap in-loop metric) and a model-of-record-metric score (the promotion metric, computed on the `validation` role). You need n >= 10.
2. **Reuse existing reads.** Use the promotion-metric scores already recorded. Do not run new confirmation reads for the audit. If you believe additional historical-checkpoint reads are needed, that requires explicit user authorization, and the prediction artifacts must be deleted after the metric is extracted.
3. **Compute correlations.** Pearson r and Spearman rho between the screen score and the promotion-metric score across the n candidates. Report both with a bootstrap confidence interval.
4. **Compute rank-preservation rate.** Of all candidate pairs, the fraction where the screen and the promotion metric agree on which candidate is better. This is the directly decision-relevant quantity: it is how often the screen would have picked the right candidate for a confirmation read.
5. **Produce artifacts.** Write `outputs/metric_calibration_audit/report.md` (use `assets/calibration_audit_template.md`), `outputs/metric_calibration_audit/correlations.tsv`, and a scatter plot of screen vs promotion metric with the identity line.

## Thresholds

- Pearson r >= 0.75 or Spearman rho >= 0.75 on n >= 10: `CALIBRATED_KEEP`. The screen is trustworthy as a ranker.
- Both in [0.6, 0.75): `CALIBRATED_DEGRADED_MONITOR`. The screen still gates but the next reassessment re-checks it, and borderline calls should lean on the promotion metric.
- Either below 0.6: `METRIC_SCREEN_DEMOTED_BY_CALIBRATION_AUDIT`. The controlled-margin gate is suspended. The screen drops to a floor-only role (it can reject obviously-bad candidates but may not rank candidates for confirmation reads) until a supervised amendment registers a calibration-aware replacement screen.

## Reopening a demoted screen

A demoted screen returns to service only through a supervised amendment that registers a replacement or a fix, plus a fresh audit showing the new screen clears the threshold on n >= 10. Re-running the same demoted screen and hoping the next ten candidates correlate better is not sufficient.

## Why this exists

The MoFNet POC and the first VCC run both used a cheap local metric to decide which candidates earned an expensive confirmation read. A non-leaking, well-defined screen can still rank candidates differently from the metric that actually decides promotion, and when it does, every confirmation read it triggers is a partly-wasted read. This audit makes the screen earn its role rather than assuming a proxy tracks the gold metric because both have the same name.
