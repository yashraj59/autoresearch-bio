# Documentation, Artifact Retention, And File-System Discipline

This reference defines the required documentation files and retention policy for autoresearch loops.

---

## Required Documentation Files

Initialize and maintain these files in the autoresearch directory:

| File | Purpose |
| --- | --- |
| `results.tsv` | One structured row per experiment, with lineage columns. |
| `research_journal.md` | Narrative log: hypothesis, implementation, result, decision, learning, lineage note. |
| `architectural_changes_log.md` | Code-level architecture record: modules changed, init, params, cost, expected vs observed effect. |
| `family_allocation.md` | Experiments used per family, Tier 1 keeps, Tier 2 passes, Tier 3 wins, status, sweep axes, and pruned subtree records. |
| `BASELINE_REGISTRY.md` | Source of truth for baseline metrics and provenance. |
| `papers_consulted.md` | Literature search record: citation, technique extracted, mapping to experiment, outcome. |
| `external_resources.md` | Downloaded datasets/resources, URLs, versions, license/provenance. |
| `identity_violations_considered.md` | Ideas considered but rejected or deferred because they violate identity/scope. |
| `insights/INSIGHT_BRIEF_NNN.md` | Every 10 experiments or major pivot: synthesis and next decisions. |
| `STATE_OF_PLAY.md` | Next-action-only state snapshot regenerated after every experiment. Replaces, never appends to, the previous snapshot. |
| `leakage_preflight.md` | Launch-precondition audit (see `core_protocol.md §3.5`). |
| `split_manifest.json` | Four-role split declaration (see `core_protocol.md §3.5`). |
| `METRIC_IDENTITY_DIFF.md` | Required at every phase boundary (amendment, leakage correction, prompt rewrite, evaluator refactor) per `core_protocol.md §7`. |
| `final_report.md` | Closure report when stop condition fires. |

---

## `results.tsv` Minimum Columns

```text
commit	experiment_num	parent_experiment_ids	branch_type	subtree_status	family	tier_reached	status	primary_metric	secondary_metric	protected_metric_summary	architectural_change	description
```

Recommended additional columns for biological projects:

```text
seed_list	dataset_split	model_of_record	candidate_checkpoint	marker_program_status	directionality_status	population_status	cap_hit_fraction	aux_to_main_ratio	artifact_retention
```

For non-bio projects, replace or supplement these with protected domain columns such as:

```text
protected_domain_status	latency_status	memory_status	safety_status	correctness_status	heldout_benchmark_status
```

The lineage columns (`parent_experiment_ids`, `branch_type`, `subtree_status`) are required for every row, including Step 0 baselines. Step 0 baselines have empty `parent_experiment_ids` and `branch_type = root`.

---

## `research_journal.md` Entry Template

```markdown
## Experiment <N>: <Title>

**Parents**: <comma-separated parent experiment_num list, or "none" for root>

**Branch type**: <root | linear | fork | combine | replay>

**Lineage note**: <one line: why these parents and why this branch type>

**Hypothesis**: <failure mode + why mechanism might help>

**Family**: <family name and allocation count>

**Implementation**: <specific code change, commit, config, parameter count>

**Initialization / identity preservation**: <how baseline behavior is preserved at init; smoke-test result>

**Tier result**: <Tier 1/2/3 result with metrics>

**Diagnostics**: <contribution ratios, cap-hit fraction, variance, marker/program effects, benchmark slices, latency, memory, regression tests, etc.>

**Decision**: <exact decision label>

**Subtree status update**: <how this experiment changes the lineage DAG; e.g., parent N changed from active_leaf to expanded>

**Learning**: <what this teaches; what to retire/cool down/reopen>

**Artifact retention**: <checkpoint deleted/retained/audit-relevant>
```

---

## Per-Experiment `summary.json` Reproducibility Identity Block

Every per-experiment `summary.json` (or equivalent run-record file under `outputs/<experiment_id>/`) must contain a top-level `identity` object with the following fields. Without this block, the file is not valid Tier evidence and cannot support a Tier 2 or Tier 3 promotion claim.

```json
{
  "identity": {
    "code_commit": "<git sha of the search driver and model code at run time>",
    "data_checksum": "<sha256 of the resolved dataset or the upstream commit/version>",
    "split_manifest_sha256": "<sha256 of split_manifest.json used by this run>",
    "driver_script_path": "<repo-relative path to the script that produced this row>",
    "python_version": "<e.g. 3.11.4>",
    "framework_versions": {"<name>": "<version>"},
    "random_seeds": [66, 1, 7, 17, 23],
    "split_construction_seed": 42,
    "created_utc": "<ISO 8601 UTC timestamp>",
    "parent_experiment_ids": ["<EXPNNN>"],
    "branch_type": "<root|linear|fork|combine|replay>",
    "leakage_guard": "<PASS_NO_TEST_SELECTION | WARN_TEST_READ_FOR_DIAGNOSTICS_ONLY | FAIL_TEST_IN_SELECTION>"
  },
  "config": { /* hyperparameters and run flags as before */ },
  "metrics": { /* per-seed and aggregated metrics */ }
}
```

The closure check in `final_report.md` must list any experiment whose `summary.json` lacks a complete `identity` block. Such experiments are tagged `IDENTITY_BLOCK_INCOMPLETE` and excluded from promotion evidence.

---

## Resumability Discipline

A new agent session reading the run state must be able to act in under 5 minutes of reading. Agents naturally convert handoff documents into append-only chat logs; the skill counters that with three caps:

1. **Handoff documents (`CODEX_HANDOFF.md`, `HANDOFF.md`, or equivalent) are state, not history.** Hard cap ~8 KB. Replace stale sections, do not append. Per-experiment chronology lives in `research_journal.md`; cite the latest journal anchor.
2. **`STATE_OF_PLAY.md` is mandatory.** A next-action-only file (≤2 KB) regenerated after every experiment. Required contents: current model of record, last completed experiment ID and outcome, next single proposed action, blockers, open `LITERATURE_PASS_REQUIRED_BY_STALL` flags.
3. **`insights/INSIGHT_BRIEF_NNN.md` every 10 experiments.** ≤1 KB each. A loop with ≥100 experiments and an empty `insights/` directory fails the resumability check and must pause until at least the most recent two briefs are written.

"Files To Read First" lists in any handoff document must contain at most five entries, with `STATE_OF_PLAY.md` as the fifth.

---

## `insights/INSIGHT_BRIEF_NNN.md` Schema

Each brief is the cognitive checkpoint that prevents an autoresearch loop from drifting into directionless mechanism-tinkering. Required contents (≤1 KB total):

- **Experiment-num range:** the inclusive span this brief covers (e.g. `EXP030`–`EXP039`).
- **Active family-allocation snapshot:** one-line per family with `Tier 1 keeps / Tier 2 passes / status`.
- **What we learned since the prior brief:** one paragraph. New mechanisms that worked, new failure modes observed, new metric understanding.
- **What mechanism class we are not pursuing further:** one paragraph. Families retired, ideas escalated to `identity_violations_considered.md`, dead-end mechanisms.
- **Next 5 planned experiment IDs with rationale:** one line each. If the rationale references a paper, link to the entry in `papers_consulted.md`.

Closure (`final_report.md`) must list every missing INSIGHT_BRIEF gap (e.g. "EXP030–EXP049 had no brief written"). Loops that close with brief gaps cannot promote a Tier 3 winner without an amendment explaining the cognitive-checkpoint lapse.

---

## Append-Only Log Hygiene

Append-only logs (`results.tsv`, `architectural_changes_log.md`, `family_allocation.md`, `papers_consulted.md`, `research_journal.md`) accumulate orphan entries when partial runs abort or templates get pasted but never filled. The skill forbids the following patterns:

- entry titles `TMP`, `TODO`, `<...>`, `XXX`, `FIXME`, or any all-uppercase placeholder;
- a heading line followed by a body section that contains only the template placeholder text (e.g. `Change: <one-line hyperparameter string>`);
- two consecutive entries whose only difference is the title (identical body prose despite different hyperparameters in `results.tsv`).

The closure step in `final_report.md` must enumerate every orphan row found and either:

- **backfill** with real data (preferred) — the orphan becomes a real entry; or
- **delete** with a one-line reason recorded in the journal entry that ran at the time.

Orphan rows that survive closure trigger label `APPEND_ONLY_LOG_ORPHAN_UNRESOLVED` and prevent Tier 3 promotion of any candidate whose lineage passes through the affected log section.

---

## Single Source Of Truth For Reference Numbers

Any plot, PDF, blog post, or report generator that compares the model of record or a candidate against an internal baseline or external literature number must load the comparator from a canonical artifact and cite the row, not from a hardcoded module-level constant.

Sources of truth:

- internal baselines → `BASELINE_REGISTRY.md`;
- external literature comparators → `external_public_baselines.tsv` (or the equivalent project-level TSV referenced from the registry);
- promotion thresholds → the protected-metric block of the active `autoresearch.md` prompt or its amendment.

Anti-patterns flagged in code review:

- `PUBLIC_REFERENCE = 0.901` as a module constant in a plot/PDF/blog generator;
- a hardcoded absolute filesystem path to a specific run's plot directory;
- inline numeric thresholds in matplotlib annotations that don't trace back to a CSV/MD cell.

Recommended fingerprint: every report generator includes a `# source: <file>#<row-or-cell>` comment next to every numeric comparator it renders.

---

## Artifact And Checkpoint Retention

Delete large checkpoints for:

- Tier 1 discards;
- Tier 2 failures not marked audit-relevant;
- Tier 3 failures unless required for comparison;
- nodes marked `pruned` or `retired_subtree` unless audit-relevant.

Retain forever:

- Markdown reports;
- JSON/CSV/TSV metrics including the full `results.tsv` with lineage columns;
- logs;
- provenance;
- prediction arrays when needed for metric reanalysis;
- evaluation outputs;
- external resource metadata;
- architectural change logs;
- Tier 3 winning checkpoints (marked `promoted` in `subtree_status`);
- active model-of-record checkpoint;
- audit-relevant near-miss checkpoints.

Before deleting a near-miss checkpoint, ask whether it may be needed for an internal-state audit or metric reanalysis. If yes, mark it audit-relevant.

---

## File-System Scope Discipline

Investigation and sandbox directories must not modify production code.

Rules:

- new investigation code lives inside the investigation directory;
- do not touch model modules or training scripts in metric-only investigations;
- do not import production code in clean-room metric checks unless the investigation explicitly allows it;
- do not overwrite baseline summaries with candidate summaries;
- write provenance before downloading external resources;
- if a script writes to a shared file, verify it cannot corrupt Step 0 artifacts;
- do not modify locked files without an explicit amendment.

The model/system of record is protected at the file-system level, not just in narrative.

---

## Final Report Requirements

When stop conditions fire, write `final_report.md` with:

1. closure trigger;
2. model/system of record at closure;
3. total experiments and status counts;
4. family-by-family findings;
5. strongest wins and strongest useful failures;
6. search-tree summary (lineage DAG): which subtrees were explored deeply, which were pruned, where the Tier 3 winner came from;
7. protected no-regression status;
8. biological safety/provenance caveats or non-bio safety/security/privacy/compliance caveats;
9. metric/evaluation caveats;
10. artifact retention summary;
11. recommended next phase;
12. explicit instruction that the autonomous loop stopped.
