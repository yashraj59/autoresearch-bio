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
outputs/<run>/split_manifest.json
outputs/<run>/leakage_preflight.md
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

`split_manifest.json` must declare four split roles (see §3.5) with disjoint sample IDs. `leakage_preflight.md` is the required pre-launch audit (see §3.5) and must be regenerated whenever data flow in the search code changes.

---

## 3.5 Leakage Pre-Flight Check (Step 0 Companion)

This section exists because a prior real-world run of this protocol (the MoFNet POC, 2026-05) leaked the locked test split through model selection across 123 trials despite all other invariants being honored. Prose-level "do not leak the test set" was not enough. This section makes the rule a structural pre-launch contract.

### Mandatory Four-Role Split

Every search loop must declare a `split_manifest.json` with the following roles. Pairwise sample-ID intersections must be empty.

- **`train`** — fits model parameters, fits preprocessing (imputers / scalers / normalizers), selects features and interaction pairs, builds masks, computes anchors and attributions used in subsequent training.
- **`validation`** — chooses architectures, hyperparameters, warm starts, pruning decisions, keep/fail status, candidate ranking. The search loop is permitted to read this split repeatedly.
- **`locked_test`** — one-time final confirmation after candidate freeze. The search loop must NEVER read this split during exploration. After it is read once for confirmation, it is considered spent and a new locked split is required for any further claims.
- **`legacy_test`** — historical reference splits from earlier exploratory work. Cited only for context; never used for current selection, status, or claims.

A schema is provided at `assets/split_manifest.schema.json`.

### Mandatory Pre-Flight Audit

Before any Step 0 result is accepted into the baseline registry, the agent must produce `leakage_preflight.md` answering each question below with a code-path citation (file and line range). The answer "I did not check" is not acceptable.

For each protected split (typically `locked_test` and any held-out cohort), enumerate:

1. **Reads.** Every code path that loads the split's features or labels.
2. **Uses.** For each read, classify the use as one of:
   - `final_evaluation_only` — read once after candidate freeze, never fed back into the search loop.
   - `diagnostics_only` — logged for human inspection but never read by selection / promotion / anchor / warm-start logic. Must include the agent's explicit statement of why this is structurally enforced.
   - `selection_signal` — DISQUALIFYING. Used by status assignment, Tier gate, family allocation, anchor selection, warm-start, attribution that feeds later training, hyperparameter ranking, or any other code path whose output influences which experiments run next.
3. **Indirect feedback.** Identify any artifact computed from the protected split (attributions, calibration curves, error analyses, saliency maps) that is later read during training, anchoring, or hyperparameter selection. Treat all such paths as `selection_signal`.
4. **Split disjointness.** Confirm pairwise empty intersection of sample IDs across all split roles, with a short code snippet showing the check.
5. **Benchmark-curation provenance.** If the benchmark's "Top-K" / feature-selected variant was constructed using full-dataset supervised feature selection, flag this as benchmark-level leakage and downgrade any external claim to "exploratory on curated benchmark" until a non-curated variant is also run.

If any path is classified `selection_signal`, the loop must not launch. Fix the path first.

### Test-Derived Signals Are Not Training Inputs

Attributions, saliency maps, calibration curves, error analyses, and any other quantity computed on a `locked_test` or held-out split are not eligible inputs to subsequent training, anchoring, warm-starting, or hyperparameter selection. Such quantities may appear in audits and final reports only.

When the search needs an anchor (e.g., integrated-gradients top-K features used as a regularization target), the anchor must be derived from `train` data only. If validation-derived anchors are used, they must be re-derived per validation fold to avoid implicit selection on the same fold used for candidate ranking.

### Frozen On-Disk Test-Derived Artifacts

Test-derived signals survive on disk across protocol amendments. The ban above applies to artifacts as much as to live computations.

If files such as `ig_top20.txt`, `baseline_attributions.npy`, `anchors.json`, `*_saliency.pt`, or any analogous attribution/explanation artifact were ever produced from a protected split in any prior run, they are themselves test-derived signals. They may not be read by any subsequent experiment's selection, status, gate, warm-start, or attribution code path — even after a leakage-corrected amendment that fixed the live driver.

The `leakage_preflight.md` audit must:

- enumerate by filename every on-disk artifact derived from a protected split in any prior phase of the project;
- search the current search code for any read of those filenames;
- certify (with code-path citation) that no later experiment reads them, or invalidate the artifacts before launch by either moving them out of the working tree or recomputing them from `train` data.

If such artifacts exist and are not enumerated, the loop must not launch.

### Post-Spent-Locked-Split Discipline

Once a `locked_test` split has been read for confirmation, the search loop must do exactly one of the following:

1. **Close.** Invoke §14 and write `final_report.md`. The locked-split read is the final evaluation; selection ends.
2. **Re-charter.** Pre-register a new holdout in `split_manifest.json` before any further candidate selection. The new role's `sample_ids`, `permitted_uses`, and "single-read-only" commitment must be recorded with a creation commit hash. The previous locked split is renamed to `legacy_test` and is cited for context only.

"Validation-only continuation" is not a stable state. The validation split is, by construction, a selection oracle for the loop; accumulating "above public reference on validation" rows after the locked split is spent re-runs the multiple-comparison failure the locked split was meant to control. The stop trigger `locked_split_spent_without_new_holdout_registered` (see §14) fires automatically in this state.

### External Baseline Metric-Selection Policy

Many upstream baseline scripts emit per-epoch test metrics by default and return the max-over-epoch value, which is itself a test-set selection. Running such a script unmodified imports that leakage into your project.

Before running any upstream baseline, the agent must:

1. inspect the upstream's metric loop and identify whether the reported number is `final_epoch`, `last_validation_epoch`, `best_observed_test`, `best_observed_validation`, or `single_evaluation`;
2. commit in writing, in `BASELINE_REGISTRY.md` or an explicit pre-run note, to which of those values will be used as the comparator for your loop;
3. if the chosen value differs from the upstream paper's reported number by more than the minimum meaningful improvement, report both numbers and label the difference openly.

The discipline must precede the run. Selecting the metric after seeing the per-epoch curve is itself test-set selection.

### Promotion Disqualification Rule

A row in `results.tsv` with `leakage_guard = FAIL_TEST_IN_SELECTION` (see `lineage.md`) cannot satisfy Tier 3 even if all metric gates pass. The amendment protocol (§12) must be invoked to refactor the search loop before further runs proceed.

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
- metric investigation shows old metrics are invalid and architecture search must pause;
- `locked_split_spent_without_new_holdout_registered` (see §3.5): a locked split was read for confirmation and no replacement holdout has been pre-registered, so the loop has no permissible final-evaluation surface and must close;
- no candidate clears the family-wise multiple-comparison floor at the experiment cap (see `statistical_promotion.md`).

When a stop trigger fires:

1. finish the current experiment if it is already running;
2. write the journal entry;
3. update `results.tsv` and `family_allocation.md`;
4. write `final_report.md`;
5. generate any required closure plots;
6. in supervised mode, stop the autonomous loop and wait for explicit user direction;
7. in autonomous Debate Council mode, convene the council, which either writes an amendment and resumes, iterates the debate, or escalates to the user.

“Stop” means stop. Do not launch the next experiment and do not ask a question while continuing autonomously. In autonomous mode, the council is the only mechanism for transitioning across a stop trigger.

### Stop-Trigger Amendments Must Originate Outside The Loop

A stop condition that has fired may not be overridden by an amendment authored in the same autonomous process that hit it. That is structurally indistinguishable from a `while not target_beaten: keep_searching` rewrite, and it re-introduces the multiple-comparison failure the stop condition exists to prevent.

Stop-trigger amendments require **one** of:

1. a supervised human turn that emits the new prompt block as chat text, applied by a separate agent invocation;
2. a Debate Council convocation (`references/debate_council.md`) in a different agent process that produces a documented quorum decision and identifies the new evidence justifying the override.

Auto-generated `## User Amendment:` blocks pasted into `research_journal.md` by the same process that hit the stop are disqualifying. Mark them `AMENDMENT_REVIEW_FAIL_AUTO_OVERRIDE` (see `decision_labels.md`) and refuse to launch Tier 1 runs under their direction. The recorded user instruction that motivated the override remains in `CONVERSATION_AND_INSTRUCTIONS_LOG.md` for traceability, but the amendment text itself must be authored outside the autonomous process.

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
