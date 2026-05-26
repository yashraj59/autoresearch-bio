# Core Autoresearch Protocol

This reference contains the reusable execution discipline for autonomous ML/dev research loops. It is written from a biological ML perspective, but the control logic applies to any model-development or benchmark-driven software loop that uses a coding agent: retrieval systems, language models, recommender systems, forecasting, computer vision, robotics, performance optimization, and feature-development experiments.

---

## 1. What Autoresearch Is

Autoresearch is a bounded, hypothesis-driven loop in which an autonomous coding agent:

1. writes a hypothesis;
2. implements the smallest mechanism that tests it;
3. trains and evaluates under pre-registered gates;
4. logs all metrics and diagnostics;
5. assigns an exact decision label;
6. updates the research plan;
7. stops cleanly when stop conditions fire.

Autoresearch is not random exploration, unbounded compute spending, metric chasing, or “let the agent figure it out.” Without strict gates and a protected baseline, autonomous agents tend to drift toward mechanisms that improve broad metrics while breaking protected behavior, saturating contribution caps, collapsing diversity, or overfitting to one dataset.

The load-bearing elements are:

- protected model/system of record;
- Step 0 baseline registry;
- pre-specified architectural families;
- tiered evaluation gates;
- statistical promotion discipline;
- exact decision labels;
- stop conditions.

---

## 2. Protected Model Of Record

Every autoresearch prompt must name a model, implementation, checkpoint, release, or commit of record:

```text
Model or implementation of record: <experiment/checkpoint/commit/tag/config/release>
```

Rules:

- Tier 1 keeps do not rebase.
- Tier 2 passes do not rebase.
- Only an explicit Tier 3 pass that satisfies every pre-registered gate can become the new model/system of record.
- If no candidate passes Tier 3, the original model/system of record remains active.
- A candidate that improves one metric while failing a protected gate is a useful failure, not a baseline. For non-bio projects, protected gates may include regression tests, latency, memory, security, API compatibility, fairness, robustness, calibration, or segment-level quality.
- The prompt must include exact baseline values for all metrics used in gates.

Avoid vague language such as “approximately preserve baseline.” Use explicit thresholds derived from Step 0 baselines.

---

## 3. Step 0 Baselines Before Architecture Search

Before any architectural experiment, run or verify the current baseline architecture on every dataset used for evaluation. Use the same seed count planned for Tier 2 whenever feasible.

Step 0 deliverables:

```text
outputs/<run>/step0_baselines/<dataset>_baseline.md
outputs/<run>/step0_baselines/SUMMARY.md
outputs/<run>/BASELINE_REGISTRY.md
```

`BASELINE_REGISTRY.md` must record:

- dataset name;
- split name/version;
- model commit/checkpoint/config;
- seed list;
- metric mean/std and per-seed values;
- metric directionality: higher-is-better or lower-is-better;
- source file for every baseline number;
- known ambiguity or provenance caveats.

If two artifacts disagree about a baseline, resolve by reading raw per-seed metric files, not summary Markdown. If ambiguity remains, state it explicitly and do not silently pick the more convenient number.

---

## 4. Model Identity And Allowed Changes

Every project needs an identity section with three parts. In biology this protects scientific interpretation; in general development it protects the current product contract, benchmark protocol, API surface, regression suite, and user-facing behavior.

### Keep

Core commitments that cannot be replaced without user approval. Examples:

- residual update form;
- iterative refinement loop;
- frozen foundation embeddings;
- decoder family;
- data split;
- evaluation scripts;
- benchmark protocol.

### Can Modify

Areas available for experiments. Examples:

- small residual heads;
- routing or gating mechanisms;
- auxiliary losses;
- calibration heads;
- memory attention temperature;
- graph priors;
- training schedules;
- inference sampling settings.

### Cannot Modify

Locked items. Examples:

- data splits;
- evaluator logic;
- protected metrics;
- gene/label/domain target sets;
- test labels;
- benchmark leakage controls;
- production deployment path;
- public API contracts;
- regression-test definitions.

### Escalation Rule

If a proposed experiment violates identity, the agent must document it in `identity_violations_considered.md` and wait for explicit user approval unless the active prompt explicitly enables autonomous Debate Council handling for that class of change. Locked-file changes still require escalation.

---

## 5. Pre-Specified Architectural Families

Define three to five architectural families before launch. Each family must include:

- **Motivation:** the specific baseline failure mode it addresses;
- **Hypothesis:** why this mechanism should fix that failure;
- **Suggested experiments:** concrete variants in rough priority order;
- **Constraints:** initialization, contribution caps, logging, parameter budget, and allowed files;
- **Stop/pivot rule:** when to pause, retire, or escalate the family.

Avoid “try anything” families. If a mechanism class is not pre-specified, the agent must ask for an amendment or document why it is out of scope.

Useful family examples:

- source/stage-aware memory calibration;
- output-to-conditioning feedback;
- hierarchical pathway or module updates;
- cross-stream attention/coupling;
- graph topology priors;
- uncertainty-calibrated emission heads;
- rollout consistency or long-horizon trajectory regularization;
- modular mixture-of-experts routing;
- physics-, biology-, policy-, or domain-constrained residual updates.

---

## 6. Tiered Evaluation Gates

Use three tiers with escalating compute commitment.

### Tier 1: Single-Seed Fast Evaluation

Purpose: cheap signal filter.

Pass requires:

- at least one registered target improves by a meaningful margin;
- no catastrophic regression on protected metrics;
- no obvious cap saturation, mode collapse, or mechanism pathology;
- required diagnostics are present;
- implementation matches the pre-registered mechanism.

Tier 1 is not proof. It is permission to spend more compute.

### Tier 2: Multi-Seed Validation

Purpose: catch single-seed false positives.

Usually use at least three seeds unless compute constraints force fewer. Report per-seed values, mean, standard deviation, and confidence interval when possible.

Pass requires:

- Tier 1 signal holds across seeds;
- improvement is larger than baseline/evaluation noise;
- practical effect size exceeds the pre-registered minimum meaningful improvement;
- protected metrics remain within gates;
- no seed-specific collapse;
- no multiple-comparison rationalization after many failed candidates.

### Tier 3: No-Regression / Generalization Validation

Purpose: decide whether to promote.

A Tier 3 pass requires all of:

- improvement on the primary search target;
- preservation of no-regression validators;
- generalization to at least one held-out dataset, protocol, split, species, condition, or benchmark;
- no hard-fail diagnostic trigger;
- full documentation;
- artifact retention plan;
- explicit promotion statement.

Only Tier 3 can rebase the model/system of record.

---

## 7. No-Regression Gates With Tight Numerical Thresholds

Use explicit gates derived from Step 0 baselines:

```text
Metric A baseline = 0.80, candidate must be >= 0.76  # 5% slack
Metric B baseline = 0.00, candidate must be <= 1.00  # any substantive return is failure
Metric C baseline = 0.45, catastrophic fail if < 0.30
```

Define hard-fail conditions that disqualify regardless of headline improvement:

- protected metric regression beyond threshold;
- mode collapse or diversity collapse;
- cap-bound contribution ratios;
- marker/program collapse in biology tasks;
- validator dataset collapse;
- exact implementation mismatch with the pre-registered mechanism;
- missing required diagnostics;
- scope or identity violation.

---

## 8. Experiment Lifecycle

Each experiment follows the same lifecycle:

1. Write hypothesis before changing code.
2. Implement the smallest mechanism that tests the hypothesis.
3. Add config flags so the model can run with the feature disabled.
4. Preserve baseline behavior at initialization.
5. Run implementation smoke tests.
6. Run Tier 1.
7. Apply exact decision label.
8. Revert, retain, or advance.
9. Update every documentation file.
10. Check stop conditions.

### Required Smoke Tests Before Training

For every new component, verify:

- output difference from baseline at initialization is zero or explicitly bounded;
- gradients flow through the intended path;
- no dead path from double-zero initialization;
- contribution ratio starts in the expected range;
- cap-hit fraction starts near zero;
- required diagnostics appear in logs;
- parameter count and memory cost are recorded;
- shape compatibility and vocabulary compatibility are checked.

If a run starts with an implementation mismatch, stop it and mark:

```text
EXPERIMENT_PREALIGN_ABORTED_IMPLEMENTATION_MISMATCH
```

Delete partial checkpoints that could confuse selection, but retain a minimal audit note. Do not count it as a scientific failure.

---

## 9. Contribution Ratio And Cap-Bound Rules

Any new residual, auxiliary pathway, attention branch, graph prior, feedback signal, or loss term must log contribution ratios.

Required logs:

```text
raw_contribution_ratio
post_gate_contribution_ratio
final_contribution_ratio
cap_hit_fraction
contribution_to_base_ratio
contribution_to_memory_ratio  # if memory exists
ratio_by_epoch
ratio_by_dataset
ratio_by_horizon_or_condition
```

Rules:

- A mechanism that is cap-bound across batches/seeds is not interpretable.
- A model with cap-bound contribution and metric regression cannot be promoted.
- Do not rescue cap-bound failures by increasing the cap unless the hypothesis is explicitly about capacity limits.
- If raw output is huge but final output looks small only because of normalization or clipping, classify as magnitude domination unless all diagnostics show controlled coordination.

A useful pattern is:

```text
raw ratio: bounded and not exploding
post-gate ratio: selective, not constant
final ratio: small but nonzero
cap-hit fraction: low
```

---

## 10. Auxiliary Loss Discipline

Auxiliary losses often look small by scalar weight but dominate the main objective.

For every auxiliary loss, log:

```text
unweighted_aux_loss
weighted_aux_loss
main_loss
weighted_aux_to_main_ratio
cap_or_ratio_clip_fraction
```

Rules:

- Start with ratio caps, not only scalar weights.
- If the cap binds frequently, report that as a result rather than increasing the scalar.
- Do not let an auxiliary biology/state/calibration loss dominate the main loss.
- If a loss improves one marker while damaging distributional or validator metrics, it is a useful failure, not a win.

---

## 11. Compute-Aware Family Allocation

Do not blindly enforce fixed experiment counts if compute is limited or early failures are conclusive.

### Stage A: Setup and Baselines

- Run Step 0 baselines.
- Verify metric scripts and diagnostics.
- Build `BASELINE_REGISTRY.md`.

### Stage B: Smoke-Test Families

- Run one to two experiments per family.
- Prefer smallest mechanisms that directly test the family hypothesis.
- Keep family allocation visible in `family_allocation.md`.

### Stage C: Deepen Only Productive Families

A family earns more experiments only if it shows controlled, non-destructive signal.

### Stage D: Close Or Audit

If all families fail or the same failure pattern recurs across families, do not keep trying variants. Either:

- close the architecture search;
- open a metric/evaluation investigation;
- open a diagnostic-only internal-state audit;
- defer to data-scale/self-supervised pretraining;
- request explicit reopening criteria.

---

## 12. Mid-Session Amendments

Amendments are normal. Long research loops learn things that should reshape the plan.

A good amendment includes:

1. direct instruction: what to do next;
2. active model/system of record reaffirmed;
3. fixed reference metrics;
4. updated thesis;
5. family cooldown/retirement updates;
6. immediate next experiment or audit;
7. decision tree for outcomes;
8. tightened gates;
9. contribution-ratio / cap-bound rules;
10. do-not-run list;
11. required reports;
12. stop/user-review trigger;
13. exact text the user can paste into the agent.

Amendments override outdated allocation rules. For example, if a family has repeated Tier 2 failures with the same mechanism, do not keep running it only because the original plan allocated more experiments.

---

## 13. Literature Search Discipline

Every 5-10 experiments, search the literature and read the research journal.

Search for:

- recent SOTA in the model class;
- known failure modes of the task;
- standard evaluation metric stacks;
- adjacent mechanisms from other fields;
- domain-specific priors.

For each paper used, record:

```text
Title
Authors
Venue/year
Link/DOI
Concrete technique extracted
Which family it supports
How it maps to existing code
Whether it preserves model identity
Experiment where it was tried
Outcome
```

Do not implement an entire paper. Extract one concrete mechanism and test it with the smallest compatible change.

---

## 14. Stop Conditions

Pre-register stop conditions before launch.

Typical stop conditions:

- hard experiment cap reached;
- target number of Tier 3 wins achieved;
- consecutive Tier 1 discard cap reached;
- all families tested without a Tier 3 win;
- repeated cap-bound or mode-collapse failures across families;
- compute budget exhausted;
- user-directed closure;
- required artifact/provenance ambiguity cannot be resolved;
- metric investigation shows old metrics are invalid and architecture search must pause.

When a stop trigger fires:

1. finish the current experiment if it is already running;
2. write the journal entry;
3. update `results.tsv` and `family_allocation.md`;
4. write `final_report.md`;
5. generate any required closure plots;
6. in supervised mode, stop the autonomous loop and wait for explicit user direction;
7. in autonomous Debate Council mode, convene the council, which either writes an amendment and resumes, iterates the debate, or escalates to the user.

“Stop” means stop. Do not launch the next experiment and do not ask a question while continuing autonomously. In autonomous mode, the council is the only mechanism for transitioning across a stop trigger.

---

## 15. Closure And Final Report

When stop conditions fire, write `final_report.md` with:

1. closure trigger;
2. model/system of record at closure;
3. total experiments and status counts;
4. family-by-family findings;
5. strongest wins and strongest useful failures;
6. protected no-regression status;
7. metric/evaluation caveats;
8. artifact retention summary;
9. recommended next phase;
10. explicit instruction that the autonomous loop stopped.

Closure is not failure. It is evidence that the current search space is exhausted or that the next bottleneck is evaluation, data, representation, or identity rather than architecture.

---

## 16. Common Next-Phase Decisions

When architecture search closes without a new baseline, the next phase is usually one of:

- self-supervised or broader-data pretraining;
- metric/evaluation reform;
- dataset expansion or better labels;
- internal-state diagnostic audit;
- representation analysis;
- finalization/reporting;
- human expert review;
- a new model class, if identity constraints block progress.

Do not keep trying small variants of a repeatedly failed mechanism class without a new diagnostic reason.
