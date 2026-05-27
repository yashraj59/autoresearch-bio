# Statistical Promotion Discipline

Use this reference whenever a candidate is compared against the model/system of record, especially for Tier 2 and Tier 3 decisions.

---

## Promotion Standard

A candidate can be promoted only when the evidence is both statistically credible and practically meaningful.

For every Tier 2 or Tier 3 comparison:

- report per-seed values;
- report mean and standard deviation;
- report confidence intervals when feasible;
- prefer paired comparisons when candidate and baseline share seeds/splits;
- report practical effect size, not only significance;
- define the minimum meaningful improvement before the run begins;
- flag multiple-comparison risk when many candidates were tried;
- never promote a candidate whose improvement is smaller than baseline/evaluation noise;
- never promote a candidate that fails a protected or catastrophic gate.

---

## Minimum Meaningful Improvement

Before launch, define a minimum meaningful improvement for the primary metric and any promotion-critical secondary metric.

Example:

```text
Primary delta cosine baseline = 0.413 ± 0.018
Minimum meaningful improvement = +0.025 absolute
Tier 2 pass requires candidate mean >= 0.438 and no protected-regression gate failure.
```

Small nominal gains are not wins when they are below the noise floor or were selected from many attempts.

---

## Paired Evaluation Preference

When possible, evaluate baseline and candidate on the same:

- seeds;
- data splits;
- perturbations/conditions or task/scenario classes;
- cell types or protected benchmark slices;
- evaluation bootstrap samples;
- held-out benchmarks, regression suites, or simulator scenarios.

Paired comparisons reduce variance and make regressions easier to detect.

---

## Multiple-Comparison Risk

Autonomous search can produce many candidates. A single apparent win among many failed variants may be selection noise.

For long loops, require at least one of:

- repeated improvement across seeds;
- held-out dataset improvement;
- bootstrap confidence interval excluding the baseline noise band;
- improvement on two independent robust metrics;
- mechanism-specific diagnostics consistent with the hypothesis.

Do not rationalize a candidate after the fact by choosing only the metric where it happened to look good.

### Family-Wise Multiple-Comparison Floor

For a search with `N` total Tier 1 single-seed candidates evaluated against the same primary metric, no candidate may be:

- named "current best";
- promoted to Tier 2;
- cited as evidence in `final_report.md`;
- featured in any plot, PDF, or blog generator's "winner" position;

unless its signed beneficial z-score against the Step 0 baseline (see "Signed Beneficial Score" below) exceeds the family-wise floor

```text
z_floor(N) = 2 + sqrt(log(N) / 2)     # informal Bonferroni-style floor
```

Reference values: N=10 → 1.07 over the +1σ rule of thumb → z_floor ≈ 3.07; N=100 → z_floor ≈ 3.52; N=500 → z_floor ≈ 3.91. Use the `baseline_std` from `BASELINE_REGISTRY.md` to compute z. If the project prefers a formal Bonferroni at α=0.05 (`z_floor = Φ⁻¹(1 − α/N)`), it may substitute and must record the choice in the `autoresearch.md` prompt.

Log `N` (cumulative Tier 1 candidate count) and `z_floor(N)` in `results.tsv` every 10 experiments. Surface both in `family_allocation.md` at every Stage transition.

If the experiment cap is reached with no candidate clearing the floor, close the loop with status `SEARCH_CLOSED_NO_NEW_BASELINE_MCC_FLOOR` (see `core_protocol.md §14`) and report the strongest sub-floor candidate honestly as "exploratory; below multiple-comparison floor for N=…".

The floor is per primary metric. If the search optimizes against several metrics, apply the floor independently per metric and require the candidate to clear at least one.

---

## Signed Beneficial Score

When many metrics have different directions, convert each to a signed beneficial z-score where positive means better than baseline.

```text
higher-is-better: z = (candidate_mean - baseline_mean) / baseline_std
lower-is-better:  z = (baseline_mean - candidate_mean) / baseline_std
```

If baseline standard deviation is zero or unavailable, use bootstrap evaluation noise, technical-duplicate variation, or mark the comparison as unresolved.

---

## Promotion Decision Template

```markdown
## Statistical Promotion Review: <candidate>

**Model/system of record**: <checkpoint/commit/config/release>
**Candidate**: <checkpoint/commit/config>
**Comparison type**: <paired | unpaired | partial>
**Seeds**: <list>
**Splits/datasets/benchmarks/suites**: <list>

| Metric | Direction | Baseline mean ± std | Candidate mean ± std | Delta | Beneficial z | Gate | Pass? |
| --- | --- | --- | --- | --- | --- | --- | --- |

**Minimum meaningful improvement**: <value and justification>
**Multiple-comparison context**: <number of candidates tried and families searched>
**Protected metrics**: <pass/fail summary>
**Diagnostic consistency**: <does mechanism behavior match hypothesis?>
**Decision**: <TIER2_PASS_CLEAN | TIER2_PASS_HIGH_RISK_DO_NOT_PROMOTE_YET | TIER3_PASS_NEW_BASELINE | TIER3_FAIL_USEFUL_FAILURE>
**Rationale**: <concise evidence>
```
