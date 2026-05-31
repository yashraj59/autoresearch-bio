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

### Who designs the families: user, planner, or hybrid

The skill governs the method, not the science. The families, the thesis, and the metric being optimized are the user's call; the discipline around them is the skill's. There are three ways the family set gets written, all first-class:

- **User-supplied.** The user hands over the families (and possibly the tiers and metrics) they want tested. The planner formalizes them into the disciplined structure (a Step 0 comparison, a gate, a stop/pivot rule each) and does not invent its own.
- **Planner-proposed.** The user hands over only the problem and context and proposes nothing. The planner designs the full family set. This is fully supported; "I did no proposal" is not deferral as long as the planner produces a complete design (see §15 and the prompt-completeness check). The quality of proposed families scales with the context the planner is given; a bare problem statement yields generic families.
- **Hybrid.** The user fixes some families and lets the planner propose the rest.

Each family carries an `origin` tag, `user_fixed` or `planner_proposed`. A `user_fixed` family may be retired or replaced only by the user, never by the loop.

### Family-set mode and who may add a family

Adding a family that is not in the current set is an amendment (the rule above). Who is allowed to author that amendment depends on two independent switches declared in the `autoresearch.md`:

- `family_set: fixed` — the set is closed. The loop runs exactly these families and may not add another without an explicit user re-grant. In supervised mode the loop may still *recommend* a new family in the closure next-phase decision (§27), but it may not *launch* experiments in an unauthorized family.
- `family_set: open` — the planner or, in autonomous mode, the council may propose adding a family through the normal amendment path, subject to `references/amendment_review_checklist.md`.

Combined with the autonomy switch:

| autonomous | family_set | who may add a family |
| --- | --- | --- |
| off | fixed | only the user, by editing the plan; loop runs the set and recommends-only at closure |
| off | open | a human amendment; the loop never self-adds |
| on | fixed | nobody; the council runs hands-off but may not author a new-family amendment |
| on | open | the council, via an amendment that passes the amendment review checklist |

The `on + fixed` row is the "autonomous execution of exactly my thesis" mode: the loop runs overnight without intervention but never wanders off the family set the user fixed. How many families a run allows, and any stricter bar for an autonomously-added family, are policy the planner writes into the specific `autoresearch.md`; the skill supplies the mechanism (amendment plus review checklist), not the numbers.

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

### Metric Identity Across Phase Boundaries

Every protected-metric column has a definitional fingerprint:

- formula or computation steps;
- inputs (which split, which model checkpoint, which seed convention);
- directionality;
- whether the metric compares against a fixed baseline artifact or against the candidate itself.

When the loop crosses a phase boundary — amendment, leakage correction, new prompt, dataset change, evaluator refactor — the agent must emit `METRIC_IDENTITY_DIFF.md` listing, for every gate-bearing column: `previous definition`, `new definition`, `threshold revalidation status` (`unchanged`, `re-derived from new baselines`, `disabled`). A silently redefined column with an unchanged threshold is a metric-laundering pattern and must fail the pre-flight check (§3.5).

Recorded violation in the MoFNet POC: `ig_top_k_overlap` meant *candidate-vs-Step-0-baseline IG top-20 overlap* during `EXP000`–`EXP122`; the leakage-corrected continuation silently redefined it as *cross-seed IG top-20 overlap of the candidate*. Same column name, same 0.70 threshold, fundamentally easier metric. Status label: `METRIC_IDENTITY_DIFF_REQUIRED` (see `decision_labels.md`).

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

The MoFNet POC showed that "search the literature" written as prose is not enough. The agent had a starter file listing three directly-relevant 2025 SOTA papers (HyperCLSA, CMGL, MOGOLA) whose published mechanism (cross-omic attention) the agent then re-invented from scratch across 123 experiments, leaving `papers_consulted.md` byte-identical to its starter. This section makes literature search a structural part of the loop instead of a prose intention.

This section is enforced at two points: at stall (the `LITERATURE_PASS_REQUIRED_BY_STALL` triggers below) and before every launch (the pre-launch cadence check and per-paper fetch-evidence requirement in §24). Every paper added in any pass must carry the four fetch-evidence fields defined in §24, or it does not count as a literature pass.

### Canonical Search Surfaces

The agent must search **at least three** of the following surfaces per literature pass, picked from the relevant domain. Naming them explicitly prevents drift to whatever the agent happens to remember from its training data.

**Biology / scientific ML:**

- arXiv (`q-bio.*`, `stat.ML`, `cs.LG` subject classes)
- bioRxiv
- medRxiv
- PubMed / NCBI
- OpenAlex
- Semantic Scholar
- Connected Papers (for citation-graph expansion of a known seed paper)
- OpenReview (NeurIPS / ICLR / ICML bio tracks)
- Domain databases as search surfaces, not just priors: Reactome, MSigDB, GO, ClinVar, GTEx, ENCODE, Human Cell Atlas (HCA), STRING, KEGG, DepMap. (See `biology_addendum.md` for their use as priors.)
- When running under Codex or another agent harness that ships a dedicated life-science skill (e.g. `$life-science-research`), invoke it as the primary surface for bio queries and treat the surfaces above as fallbacks. Record the invocation in the literature pass note.

**General ML / software / agents / benchmarking:**

- arXiv (`cs.LG`, `cs.AI`, `cs.CL`, `cs.CV`, `cs.SE`, `stat.ML`)
- Semantic Scholar
- OpenReview (NeurIPS / ICLR / ICML / ACL / EMNLP / ICSE / FSE proceedings)
- Papers with Code
- NeurIPS / ICLR / ICML proceedings sites
- ACL Anthology for NLP tasks
- Google Scholar as a last-resort breadth surface; never as the only surface.

### Agent Fetch Fingerprint

The agent's literature pass must declare its fetch fingerprint in `leakage_preflight.md` (and re-declare on every amendment). The skill remains agent-agnostic — any of the following is acceptable, but the choice must be explicit and consistently applied:

1. **Agent-harness web tools.** `WebSearch` + `WebFetch` available in Claude Code, Codex, Cursor, Aider, or analogous harnesses. The agent must include the tool names it used in the literature pass note. Permissions must allow outbound fetch.
2. **Semantic Scholar API.** Direct HTTP calls (`https://api.semanticscholar.org/graph/v1/...`) authenticated via `SEMANTIC_SCHOLAR_API_KEY`. The driver records the API version and the search query. Rate-limit aware.
3. **MCP paper-search server.** Examples: `mcp-paper-search`, `pubmed-mcp`, `arxiv-mcp`, `semantic-scholar-mcp`, `biorxiv-mcp`. The agent declares the server name and version in `leakage_preflight.md` and records the MCP tool calls in the literature pass note.

A loop that declares no fetch fingerprint and produces an unchanged `papers_consulted.md` after the cadence trigger fires is in `LITERATURE_DISCIPLINE_VIOLATION` (see `decision_labels.md`).

### Cadence Triggers

Two independent triggers fire a literature pass. Either is enough.

1. **Fixed cadence.** Every 5–10 experiments. Reading the research journal is part of this pass.
2. **When-stuck trigger.** A literature pass is required *before the next mechanism is proposed* if any of the following holds:
   - a family produces **three consecutive Tier 1 discards**;
   - a Tier 2 failure ships with a **protected-metric regression**;
   - a metric investigation closes a mechanism class as ruled out;
   - the multiple-comparison floor (`statistical_promotion.md`) has not been cleared and the experiment count has grown by ≥ 20 since the last literature pass.

   The trigger is recorded with status label `LITERATURE_PASS_REQUIRED_BY_STALL` in `results.tsv` and `family_allocation.md`. Until the literature pass is complete and `papers_consulted.md` has at least one new entry tagged to the stalled family, no new mechanism may launch for that family.

### Starter-File Cross-Check Before First Tier 1 Keep

Before any pre-specified family produces its **first Tier 1 keep**, the agent must cross-check the family against the starter file:

1. read `papers_consulted_starter.md` (and the run-local `papers_consulted.md`);
2. identify any papers tagged to the family's mechanism class;
3. for each such paper, ensure the run-local file's `Experiment where it was tried / Outcome` fields are populated for at least one experiment in the family;
4. if a tagged paper exists in the starter but the family's `Experiment where it was tried` field is empty, halt for a literature pass with status label `LITERATURE_GROUNDING_MISSING` (see `evals/process_checklist.md`).

This is the rule that would have prevented the MoFNet POC from re-inventing cross-omic attention while three referenced papers describing it sat in the starter file with empty outcome fields for 123 experiments.

### Per-Paper Record

For each paper used, record in `papers_consulted.md`:

```text
Title
Authors
Venue / year
Link / DOI
Search surface that returned it          # e.g. "Semantic Scholar query 'cross-omic attention BRCA'"
Fetch fingerprint                          # e.g. "WebFetch in Codex" / "mcp-paper-search v0.3"
Concrete technique extracted              # one mechanism, not the whole paper
Which family it supports
How it maps to existing code               # module / function / config flag
Whether it preserves model identity
Experiment where it was tried              # EXPNNN
Outcome                                    # Tier 1 keep / discard / Tier 2 fail / etc.
Notes / caveats / follow-ups
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

## 15. Non-Experiment Node Cap

Profile: lean and full.

The loop may not record more than three consecutive non-experiment nodes (any node that does not register a row in `results.tsv`) without either launching an experiment or emitting `COUNCIL_ESCALATE_TO_USER` with a one-line explanation of which experiment is being deferred. Metric investigations, audits, amendments, literature passes, support-only nodes, and council-deliberation-only nodes all count. After a supervised resume instruction, the next real action must be an experiment, not another support node.

### Mandatory node headers

So this cap can be enforced rather than hoped for, every node entry in `research_journal.md` must begin with a machine-readable header comment:

```
<!-- node: id=<NNN> type=<experiment|audit|amendment|literature|support|council> experiment=<true|false> -->
```

`type=experiment` (or `experiment=true`) marks a node that registers a `results.tsv` row. Every other type is a non-experiment node and counts toward the three-consecutive cap. The same headers let the quarter-budget audit (§23) find `type=audit` nodes. A run that has registered experiments but whose journal carries no node headers is itself a `SPIRAL_NON_EXPERIMENT_NODE_CAP_EXCEEDED` failure, because the cap cannot be checked without them. `validate_non_experiment_node_cap()` enforces both the header presence and the consecutive-count rule.

Examples of the same failure across domains:

- Image classification: building data-augmentation pipelines, evaluation harnesses, and checkpoint-comparison scripts in sequence without launching the next training run.
- Retrieval and search: scaffolding query-set generators, NDCG calculators, and slice-level reporting before running the next reranker variant.
- Single-cell perturbation: writing preflight guards, runner wrappers, and closure-procedure runners without launching the next Tier 1 candidate.

The support work is individually valid. The failure is accumulation without intervening experiments. Detected by `validate_non_experiment_node_cap()`; the label is `SPIRAL_NON_EXPERIMENT_NODE_CAP_EXCEEDED`.

---

## 16. Closure-Time Fallback Actions Must Execute

Profile: lean and full (conditional on an amendment specifying a closure action).

If any amendment active at closure specifies a closure-time action (a locked read, a final inference, a confirmation experiment, a registration step), that action becomes the first step of the closure procedure (§26) and must execute before `final_report.md` is written. The closure procedure must enumerate pending closure-bound actions from the active-amendments table before proceeding to closure plots. A closure that writes `final_report.md` with an unresolved `CLOSURE_FALLBACK_READ_PENDING` row is a defect; `validate_closure_fallback_actions()` catches this. The paired label `CLOSURE_FALLBACK_READ_EXECUTED` records that the action ran.

---

## 17. Screen Calibration Audit Cadence

Profile: lean and full.

When a run has accumulated at least ten registered candidates with paired screen scores and model-of-record-metric scores, and at every quarter-budget audit thereafter (§23), the loop computes Pearson and Spearman correlations between them using the procedure in `references/metric_calibration_audit.md`. The audit reuses existing `validation`-role reads where available. Additional historical-checkpoint reads require explicit user authorization, with prediction artifacts deleted after metric extraction.

Read-surface reminder (consistent with §3.5): confirmation reads taken during search are `validation`-role reads. They are a repeatable selection surface, and every such read counts toward the multiple-comparison floor N in `statistical_promotion.md`, so trust in the screen-vs-promotion comparison decays as reads accumulate. The `locked_test` role is read once at closure and is never the surface a mid-search calibration audit reuses.

If Pearson r >= 0.75 or Spearman rho >= 0.75 on n >= 10, the screen is `CALIBRATED_KEEP`. If both fall in [0.6, 0.75), the screen is `CALIBRATED_DEGRADED_MONITOR`. If either falls below 0.6, the screen is `METRIC_SCREEN_DEMOTED_BY_CALIBRATION_AUDIT`: the controlled-margin gate is suspended pending a supervised amendment registering a calibration-aware replacement screen.

The failure mode this prevents is using an internally valid screen (non-leaking, well-defined) to rank candidates for expensive confirmation reads when the screen's rank-ordering correlation with the promotion metric is weak. Examples:

- Image classification: dev-split accuracy as a screen for a rare-class-weighted test metric, when dev accuracy is dominated by easy classes and ranks candidates differently.
- Retrieval: NDCG@10 on head-skewed dev queries as a screen for tail-dependent live click-through.
- Single-cell perturbation: a target-heldout local distributional metric as a screen for the deliverable's official scoring.

---

## 18. Attribution-Control Default For A New Family's First Experiment

Profile: full requires it for every new family's first experiment; lean requires it before a family's first keep is promoted.

The first experiment of any newly opened family is paired with a no-mechanism control run using the same seed, manifest, and recipe with the new mechanism disabled. The two runs share a parent node label and register as an attribution pair. A `TIER1_KEEP_CONTROLLED_SIGNAL` decision for the new mechanism requires that the mechanism arm beats the control arm by the controlled-margin threshold on the gating metric. Clearing the static floor alone yields `TIER1_DISCARD_UNATTRIBUTABLE`, regardless of absolute score.

This attribution control is the primary anti-noise check and, in low-compute mode, replaces multi-seed Tier 2 replay as the default. Multi-seed replay answers "is the lift stable across random inits"; the no-mechanism control answers "is the lift from the mechanism or would the recipe without it do as well." The control is the cheaper of the two: one extra run per family rather than k extra runs per keep. Full-profile runs may use both; lean-profile runs use the control and treat multi-seed replay as opt-in. The paired control costs one extra experiment per family. Across six to ten families the overhead is 3 to 5 percent of a 200-experiment budget, and it catches the most expensive autonomy failure: deepening a no-op mechanism to multi-seed.

---

## 19. Borderline Retention And Closure Fallback

Profile: lean and full.

A candidate that clears the static floor but misses the controlled-margin gate over its parent screen is labeled `TIER1_BORDERLINE`. Its checkpoint and screen diagnostics are retained, not deleted. It remains ineligible for a `validation`-role confirmation read during search. At closure, if no candidate beat the model of record during the run, the strongest borderline by screen score is eligible for one `validation` confirmation read as a closure fallback under §16; if it then beats the model of record it may become the model of record before the single `locked_test` read. Tie-break: protected-metric stability (no regression preferred), then lineage recency.

When three or more borderlines accumulate within one family without any clearing the controlled margin, the family enters `FAMILY_BORDERLINE_COOLDOWN`. This is distinct from `FAMILY_COOLDOWN`: the signal is a metric ceiling or architecture limit, not an absent mechanism. Reopening the family requires a literature pass.

---

## 20. Single-Seed Model-Of-Record Disclosure

Profile: lean and full.

When `final_report.md` is written and the model of record was promoted from a single-seed confirmation read, the Score Summary section must flag this as a known limitation. The closing procedure may optionally run one additional non-original-seed replay of the model-of-record recipe as a stability check, or record an explicit `SINGLE_SEED_MODEL_OF_RECORD_ACCEPTED` decision attributable to a supervised instruction. Default is to flag, not run. This is a seed-confirmation disclosure; it is separate from the selection-tuning disclosure that applies whenever the `validation` surface was read many times (see §17 and `statistical_promotion.md`).

---

## 21. Gate-Metric Alignment

Profile: lean and full.

Any gate that pauses search, halts experiments, or blocks next-experiment selection must be defined on the same metric used for model-of-record promotion. Gates on secondary or proxy metrics may downgrade trust in those metrics (for example demoting a screen to floor-only per §17) but may not pause the search itself.

The failure mode is a pause-grade gate on a metric different from the promotion metric, which creates the situation where the primary metric appears in the protocol header while a secondary metric controls execution flow. The loop halts for the wrong reason while the real metric continues to drift.

---

## 22. Closure Terminality (Extension Of §14)

Profile: lean and full.

`SEARCH_CLOSED_NO_NEW_BASELINE` is terminal absent an explicit reopen verb ("reopen", "resume", "restart", "keep running", "continue the search", or an unambiguous equivalent) in the immediately preceding user message. Restated goal context, council debates about further mechanisms, deep-research artifacts produced after closure, observations that an official stop threshold was not reached, or "active goal context reasserted" are not reopen instructions. A `SEARCH_AMEND` node parented to `SEARCH_CLOSED_NO_NEW_BASELINE` without a `REOPEN_AUTHORIZATION_RECORD.md` artifact that quotes the user's instruction is labeled `REOPEN_REQUIRES_EXPLICIT_USER_INSTRUCTION` and refused.

---

## 23. Quarter-Budget Reassessment Gate

Profile: lean and full.

At every 25 percent of the experiment budget (50, 100, 150 experiments for a 200-cap run), the loop pauses experiment selection and runs the reassessment procedure:

1. Read the full `research_journal.md` and `results.tsv`.
2. Regenerate summaries.
3. Run the §17 calibration audit.
4. Ask: is the current gate actually predictive of the protected objective?
5. If the audit identifies that the gating screen has weakened, recent experiments cluster around a local optimum, or evidence for the current direction is thin or contradictory, run a bounded diagnostic study (a metric-correlation sweep, a no-mechanism replay of a recent candidate, a multi-seed stability check on the model of record, or an isolated metric investigation) before selecting the next experiment. Bound the diagnostic to no more than 3 percent of the remaining budget.
6. Write an `AUDITNN` node with the calibration verdict, the diagnostic findings if any, and a concrete next-phase decision. The node carries the §15 header with `type=audit` so the validator can find it.
7. Only then select the next experiment.

If the audit fires and the loop selects a next experiment without writing the `type=audit` node or running the bounded diagnostic when triggered, `validate_quarter_budget_audit()` flags the run (pass the experiment budget via `--budget N`; without it the check is advisory because the validator cannot know the cap).

---

## 24. Literature Cadence Pre-Launch Check And Fetch Evidence

Profile: lean and full. Extends §13.

Before launching any new experiment, the loop checks the timestamp on `papers_consulted.md`. If between five and ten experiments have elapsed since the last literature pass, or if the previous five experiments cluster in one family, the loop must run a literature pass before selecting the next mechanism. The pass touches at least two distinct surfaces per §13.

Every paper added in a pass must record machine-checkable fetch evidence:

- `fetch_url` — the URL the paper was retrieved from.
- `fetch_timestamp` — UTC timestamp of retrieval.
- `fetch_surface` — which surface from §13 the URL came from (arXiv, bioRxiv, PubMed, Semantic Scholar, etc.).
- `extraction_snippet` — a 50 to 200 word direct extract from the paper showing the mechanism, finding, or claim being cited. Not a summary written by the agent; an extract from the source.

Papers added without all four fields are flagged `LITERATURE_PASS_FETCH_EVIDENCE_MISSING` and do not count as a literature pass for cadence purposes. This prevents the failure mode where the agent writes paper titles into `papers_consulted.md` without actually retrieving anything.

---

## 25. INSIGHT_BRIEF Reflective Audit

Profile: lean and full.

Every tenth experiment, the loop writes `outputs/insights/INSIGHT_BRIEF_NNN.md` per the cadence in `references/artifact_retention.md`. The brief contains the previously specified fields (experiment-num range, family-allocation snapshot, what was learned, what is not being pursued, next 5 planned experiments) plus a reflective audit of the previous brief:

- Each of the previous brief's "next 5 planned experiments" entries is rated `executed_as_planned`, `executed_with_deviation`, or `not_executed`.
- For each executed entry: was the predicted outcome correct?
- For each prediction that was wrong: what about the prior model of the search space was incorrect, and how does that change the next 5 planned experiments?

Briefs without the reflective-audit section are flagged `INSIGHT_BRIEF_REFLECTION_MISSING`. The first brief (`INSIGHT_BRIEF_001.md`) has no prior brief to audit and is exempt. The failure mode this prevents is briefs becoming a planning document rather than a learning document.

---

## 26. Closure And Final Report

When stop conditions fire, first execute any pending closure-time actions enumerated under §16, then write `final_report.md` with:

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

## 27. Common Next-Phase Decisions

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
