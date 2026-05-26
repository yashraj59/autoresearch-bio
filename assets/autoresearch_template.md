# <Project> Autoresearch-Bio: <Search Goal>

## Model Or System Of Record

- Model/system/checkpoint/service/config: `<TO_FILL_BEFORE_LAUNCH>`
- Commit/tag: `<TO_FILL_BEFORE_LAUNCH>`
- Config: `<TO_FILL_BEFORE_LAUNCH>`
- Why active: `<TO_FILL_BEFORE_LAUNCH>`
- Domain: `<biology | scientific ML | general ML | software/dev tooling | infrastructure | agent/benchmark | other>`
- Rebasing rule: only a Tier 3 pass that satisfies every pre-registered gate can supersede this model/system of record.

## Role

You are an autonomous research agent running a bounded, hypothesis-driven biological ML or domain-specific development loop. You must document every experiment, preserve the model/system of record, protect biological or domain-specific no-regression behavior, track experiment lineage, and stop when stop conditions fire.

This run is not unbounded exploration, metric hacking, hyperparameter-only tuning, or permission to change locked files.

## Setup

1. Create branch `<branch>` from `<commit>`.
2. Read these files completely:
   - `<model files>`
   - `<training scripts>`
   - `<evaluation scripts>`
   - `<data/split configs>`
   - `<existing logs/reports>`
3. Initialize required logs:
   - `results.tsv` (with lineage columns: `parent_experiment_ids`, `branch_type`, `subtree_status`)
   - `research_journal.md`
   - `architectural_changes_log.md`
   - `family_allocation.md`
   - `BASELINE_REGISTRY.md`
   - `papers_consulted.md`
   - `external_resources.md`
   - `identity_violations_considered.md`
   - `insights/`
4. Verify training/evaluation scripts.
5. Run or verify Step 0 baselines before any architecture, mechanism, implementation, or benchmark search.

## Model Identity

### Keep

- `<core architectural commitment>`
- `<frozen embedding / decoder / prior / protocol>`

### Can Modify

- `<small heads / gates / calibration / losses / schedules>`

### Cannot Modify

- `<data splits>`
- `<evaluator logic>`
- `<protected metrics>`
- `<gene/label sets / task labels / protected slices>`
- `<benchmark leakage controls>`
- `<production path>`

If a proposed experiment violates identity or locked files, document it in `identity_violations_considered.md` and stop for amendment unless the active prompt explicitly permits Debate Council escalation for that class of change.

## Step 0 Baselines

Run or verify the model or system of record on every dataset, benchmark, validation suite, or regression suite used for gates.

- Datasets and roles:
  - Search dataset/benchmark/suite: `<TO_FILL_BEFORE_LAUNCH>`
  - Secondary validation dataset/benchmark/suite: `<TO_FILL_BEFORE_LAUNCH>`
  - No-regression validator: `<TO_FILL_BEFORE_LAUNCH>`
  - Held-out/generalization dataset/benchmark/suite: `<TO_FILL_BEFORE_LAUNCH>`
- Seeds: `<TO_FILL_BEFORE_LAUNCH>`
- Baseline registry required: yes.
- Ambiguity rule: if summaries disagree, inspect raw per-seed metric files. If ambiguity remains, mark `BASELINE_AMBIGUOUS_PROVENANCE_BLOCKED` and do not launch architecture search.

`BASELINE_REGISTRY.md` must record dataset, split, checkpoint, commit, config, seed list, per-seed metrics, mean/std, metric directionality, source files, and caveats.

Step 0 baselines are logged as `root` nodes in the lineage DAG, with empty `parent_experiment_ids`.

## Search Targets

For biology, use biological metrics such as directionality, marker/program coherence, population structure, and held-out biological validators. For non-bio projects, replace these with protected domain metrics such as correctness, latency, memory, robustness, safety, security, fairness, policy compliance, regression tests, held-out benchmark slices, or simulator constraints.

### Primary Metrics

| Metric | Direction | Baseline mean ± std | Minimum meaningful improvement | Tier 3 gate |
| --- | --- | --- | --- | --- |
| `<metric>` | `<higher/lower>` | `<TO_FILL>` | `<TO_FILL>` | `<TO_FILL>` |

### Secondary Metrics

| Metric | Direction | Baseline mean ± std | Gate |
| --- | --- | --- | --- |
| `<metric>` | `<higher/lower>` | `<TO_FILL>` | `<TO_FILL>` |

### Protected Biological Or Domain-Specific Metrics

| Metric | Protected behavior | Baseline mean ± std | Regression gate | Catastrophic fail |
| --- | --- | --- | --- | --- |
| Directionality or task behavior | `<e.g., signed DE agreement, factuality, rare-class recall>` | `<TO_FILL>` | `<TO_FILL>` | `<TO_FILL>` |
| Coherence or consistency | `<e.g., pathway/module capture, format adherence, calibration>` | `<TO_FILL>` | `<TO_FILL>` | `<TO_FILL>` |
| Population/slice structure | `<e.g., cluster coverage, user segment, class slice, latency slice>` | `<TO_FILL>` | `<TO_FILL>` | `<TO_FILL>` |
| Held-out validator | `<dataset/split/regression suite/canary>` | `<TO_FILL>` | `<TO_FILL>` | `<TO_FILL>` |

A candidate that improves a headline metric while failing a protected biological or domain-specific gate is a useful failure, not a new baseline.

## Architectural Families

Define one to five families. Use one to two families in low-compute mode.

### Family 1: `<name>`

- Motivation: `<specific baseline failure mode>`
- Hypothesis: `<why this mechanism should help>`
- Suggested experiments:
  1. `<smallest compatible mechanism>`
  2. `<variant if signal appears>`
- Constraints: `<initialization, caps, parameter budget, allowed files>`
- Required diagnostics: `<ratios, marker checks, benchmark slices, latency/memory, regression tests, etc.>`
- Stop/pivot rule: `<exact rule>`

### Family 2: `<name>`

- Motivation:
- Hypothesis:
- Suggested experiments:
- Constraints:
- Required diagnostics:
- Stop/pivot rule:

## Lineage Rules

Every experiment must be logged as a node in the search DAG. The agent records:

- `parent_experiment_ids` (comma-separated list of parent experiment numbers, or empty for `root`);
- `branch_type` (one of `root`, `linear`, `fork`, `combine`, `replay`);
- `subtree_status` (one of `active_leaf`, `expanded`, `pruned`, `promoted`, `retired_subtree`).

Branch type definitions:

- `root`: first experiment in a family, or a Step 0 baseline. No parents.
- `linear`: direct extension of one parent with one new mechanism.
- `fork`: sibling variant from the same single parent, intentionally created at the same time.
- `combine`: combines mechanisms from two or more parents.
- `replay`: re-runs a previous experiment with a different seed, split, or evaluation. Same architecture as parent. Tier 2 validation of a Tier 1 keep is a `replay`.

Before changing code, the agent states the parent experiment numbers and the branch type. After the experiment, the agent updates the parent's `subtree_status` from `active_leaf` to `expanded` if this was the first child.

When the agent picks the next experiment, it picks the `active_leaf` with the strongest Tier 1 signal across non-pruned subtrees, or follows the family allocation plan if it explicitly requires a specific family next.

Pruning rules:

- When a family is retired, mark every descendant `retired_subtree`.
- When a parent shows persistent cap-bound or mode-collapse pathology across two or more children, mark the parent and its descendants `pruned`.
- Do not extend `pruned` or `retired_subtree` nodes without an explicit amendment.
- A Tier 3 winner is `promoted`, not pruned.

Read `references/lineage.md` for the full rules.

## Tiered Evaluation

### Tier 1: Fast Single-Seed Filter

- Procedure: `<TO_FILL>`
- Keep criteria:
  - primary or secondary signal exceeds Tier 1 threshold;
  - protected metrics do not catastrophically regress;
  - diagnostics are present;
  - no cap-bound or mode-collapse pathology;
  - implementation matches the pre-registered mechanism;
  - parent_experiment_ids and branch_type are recorded.
- Fail-fast labels:
  - `TIER1_DISCARD_NO_SIGNAL`
  - `TIER1_DISCARD_CAP_BOUND`
  - `TIER1_DISCARD_MARKER_OR_PROGRAM_REGRESSION`
  - `TIER1_DISCARD_PROTECTED_DOMAIN_REGRESSION`
  - `TIER1_DISCARD_METRIC_REGRESSION`
  - `TIER1_DISCARD_IMPLEMENTATION_MISMATCH`

Tier 1 keeps do not rebase the model/system of record.

### Tier 2: Multi-Seed Validation

- Procedure: `<TO_FILL>`
- Seeds: `<TO_FILL>`
- Pass criteria:
  - Tier 1 signal holds across seeds;
  - improvement exceeds noise and minimum meaningful improvement;
  - protected gates pass;
  - no seed-specific collapse;
  - no diagnostic hard fail.

Tier 2 passes do not rebase the model/system of record. Tier 2 results are logged as `replay` children of the corresponding Tier 1 keep.

### Tier 3: No-Regression / Generalization Validation

- Procedure: `<TO_FILL>`
- Generalization dataset/split/condition: `<TO_FILL>`
- Promotion criteria:
  - primary metric improves by pre-registered minimum meaningful improvement;
  - protected biological or domain-specific metrics pass;
  - no-regression validators pass;
  - held-out/generalization check passes;
  - diagnostics are controlled;
  - documentation complete;
  - artifact retention plan complete.

Only Tier 3 can promote a new model/system of record. The promoted node is marked `promoted` in `subtree_status`.

## Required Diagnostics

Log all universal diagnostics below. Then keep the bio sub-block or the non-bio sub-block based on the project domain and delete the other. If the project is mixed (for example, a biology system with strict latency or memory gates), keep both.

### Universal (all domains)

```text
raw_contribution_ratio
post_gate_contribution_ratio
final_contribution_ratio
cap_hit_fraction
contribution_to_base_ratio
contribution_to_memory_ratio        # if a memory module exists
ratio_by_epoch
ratio_by_dataset
ratio_by_condition
unweighted_aux_loss
weighted_aux_loss
main_loss
weighted_aux_to_main_ratio
mode_collapse_null_comparison
```

### Biology projects (delete if non-bio)

```text
marker_resolution_coverage
pathway_or_program_capture
population_diversity
direction_of_effect_agreement
held_out_perturbation_or_condition_status
cross_species_or_protocol_ortholog_coverage
```

### Non-bio projects (delete if pure biology)

```text
benchmark_slice_regression
latency_or_memory_regression
regression_test_failure_count
correctness_test_status
safety_or_policy_violation_count
robustness_slice_regression
```

## Family Allocation

- Stage A: Step 0 baselines and diagnostics verification.
- Stage B: one to two smoke tests per family. Smoke tests are `root` nodes in their family.
- Stage C: deepen only families with controlled, non-destructive signal. Deepening produces `linear`, `fork`, or `combine` children of earlier nodes.
- Stage D: close, audit metrics, or open an internal-state diagnostic if repeated failures recur.

Initial experiment cap: `<TO_FILL_BEFORE_LAUNCH>`
Consecutive Tier 1 discard cap: `<TO_FILL_BEFORE_LAUNCH>`
Tier 2 seed count: `<TO_FILL_BEFORE_LAUNCH>`
Tier 3 promotion target count: `<TO_FILL_BEFORE_LAUNCH>`

## Statistical Promotion Discipline

For every Tier 2 and Tier 3 comparison:

- report per-seed values, mean, and standard deviation;
- prefer paired comparisons when seeds/splits match;
- report practical effect size;
- compare against minimum meaningful improvement;
- flag multiple-comparison risk;
- never promote a candidate whose improvement is smaller than baseline/evaluation noise.

## Documentation Requirements

For every experiment, update:

- `results.tsv` including lineage columns;
- `research_journal.md` including a lineage note (parents, branch type, reason);
- `architectural_changes_log.md`;
- `family_allocation.md`;
- any relevant metric tables/plots;
- `papers_consulted.md` if literature was used;
- `external_resources.md` if resources were downloaded;
- `identity_violations_considered.md` if applicable.

Every 10 experiments or major pivot, write `insights/INSIGHT_BRIEF_NNN.md`.

## Artifact Retention

Delete large checkpoints for Tier 1 discards and non-audit Tier 2 failures. Retain metrics, logs, provenance, prediction arrays needed for metric reanalysis, active model-of-record checkpoint, Tier 3 winners, and audit-relevant near-misses.

Before deleting a near-miss checkpoint, decide whether it may be needed for internal-state audit or metric reanalysis.

## Stop Conditions

Stop when any condition fires:

- hard experiment cap reached;
- target number of Tier 3 wins achieved;
- consecutive Tier 1 discard cap reached;
- all families tested without a Tier 3 win;
- repeated cap-bound or mode-collapse failures across families;
- compute budget exhausted;
- required artifact/provenance ambiguity cannot be resolved;
- metric investigation shows old metrics are invalid;
- identity or locked-file violation is required to continue;
- the active subtree in the search DAG has no remaining `active_leaf` nodes and no new family is authorized;
- user-directed closure.

When stop fires:

1. finish the current experiment if already running;
2. write the journal entry;
3. update `results.tsv`, `family_allocation.md`, and lineage status of affected nodes;
4. write `final_report.md` including a search-tree summary;
5. generate required closure plots;
6. stop the autonomous loop unless Debate Council mode is explicitly enabled.

## Autonomy Mode

Mode: `<supervised | autonomous-strict | autonomous-permissive>`

Default: supervised.

If autonomous mode is enabled, use Debate Council process when a stop condition fires. The council applies the amendment review checklist (`references/amendment_review_checklist.md`) before voting. Hard escalation triggers include identity violations, locked-file changes, scope expansions, hard cap overruns, low council confidence after iteration, three consecutive same-direction councils, missing/corrupted locked files, safety-boundary concerns, and biology-interpretation decisions.

## Safety Boundary

This is computational model or software research planning only. For biological projects, do not produce wet-lab protocols, clinical recommendations, treatment advice, or deployment-facing biological claims. Tier 1 and Tier 2 results are not biological validation. For non-bio projects, enforce the relevant privacy, security, compliance, reliability, deployment, or user-safety guardrails.

Begin only after Step 0 baselines are complete.
