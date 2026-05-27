# Changelog

## Unreleased — Leakage pre-flight, process-loophole guardrails, reproducibility identity, agent-agnostic framing

### Added

- `references/core_protocol.md §3.5 "Leakage Pre-Flight Check (Step 0 Companion)"`. Mandatory four-role split (`train` / `validation` / `locked_test` / `legacy_test`), required `leakage_preflight.md` audit before the loop launches, ban on test-derived attributions feeding back into training, ban on frozen on-disk test-derived artifacts surviving across protocol amendments, post-spent-locked-split discipline (close or re-charter), external-baseline metric-selection policy that must precede the upstream baseline run, and an automatic Tier 3 disqualification rule for `FAIL_TEST_IN_SELECTION` rows.
- `references/core_protocol.md §14 "Stop-Trigger Amendments Must Originate Outside The Loop"`. An amendment overturning a fired stop condition must come from a supervised human turn or a Debate Council convocation in a different agent process. Same-process auto-overrides are labelled `AMENDMENT_REVIEW_FAIL_AUTO_OVERRIDE` and refused.
- `references/decision_labels.md "Reserved Strings In Automated Status Labels"`. Auto-emitted status labels may not contain claim-strength tokens (`BEAT`, `SOTA`, `WINS`, `OUTPERFORMS`, `SURPASSES`, `STATE_OF_THE_ART`, `BENCHMARK_WIN`) or comparator-relative tokens (`ABOVE_REFERENCE`, `BELOW_REFERENCE`, `MATCHES_REFERENCE`, `WITHIN_X_OF`, `EXCEEDS_REFERENCE`, `MISSES_REFERENCE`). Relative comparisons live in `protected_metric_summary` JSON or `final_report.md` prose only.
- `references/decision_labels.md "Amendment Review Auto-Override Label"`. The `AMENDMENT_REVIEW_FAIL_AUTO_OVERRIDE` label and its semantics.
- `references/statistical_promotion.md "Family-Wise Multiple-Comparison Floor"`. `z_floor(N) = 2 + sqrt(log(N) / 2)` (or formal Bonferroni at user choice). No candidate can be named "current best", promoted to Tier 2, or featured in reports unless its signed beneficial z clears the floor. Closure label `SEARCH_CLOSED_NO_NEW_BASELINE_MCC_FLOOR`.
- `references/artifact_retention.md "Per-Experiment summary.json Reproducibility Identity Block"`. Mandatory top-level `identity` object covering `code_commit`, `data_checksum`, `split_manifest_sha256`, `driver_script_path`, `python_version`, `framework_versions`, `random_seeds[]`, `split_construction_seed`, `created_utc`, `parent_experiment_ids`, `branch_type`, `leakage_guard`. Missing block flagged `IDENTITY_BLOCK_INCOMPLETE` and excluded from promotion evidence.
- `assets/split_manifest.schema.json` — JSON Schema for the four-role split manifest with the disjointness-check record and enumerated `permitted_uses`.
- `assets/papers_consulted_starter.md` — canonical literature-log starter. The run copies this into its working directory; the validation script diffs against it to detect untouched starters.
- `references/lineage.md "Required leakage_guard Column"` subsection. Every `results.tsv` row carries `leakage_guard` ∈ {`PASS_NO_TEST_SELECTION`, `WARN_TEST_READ_FOR_DIAGNOSTICS_ONLY`, `FAIL_TEST_IN_SELECTION`}. Missing column defaults to `FAIL`.
- `references/metric_investigation.md` restatement of the "test-derived signals are not training inputs" rule and a new trigger condition tied to `leakage_preflight.md` re-examination.
- `evals/process_checklist.md "Machine-Checkable Stub-Compliance Rules"`. Quality checks for `architectural_changes_log.md` (must record real per-entry metadata, not template prose), `identity_violations_considered.md` (≥1 entry per 20 experiments after a 50-experiment ramp), `external_resources.md` (must cover every dataset/resource verifiable on disk), and `papers_consulted.md` (non-empty diff against starter after 10 experiments). Failure labels: `ARCHITECTURAL_LOG_TEMPLATE_ONLY`, `IDENTITY_VIOLATIONS_LOG_SKELETON`, `RESOURCE_PROVENANCE_VIOLATION`, `LITERATURE_DISCIPLINE_VIOLATION`.
- `scripts/validate_autoresearch_artifacts.py`: new checks for the `leakage_preflight.md` / `split_manifest.json` required files, the `leakage_guard` column with enum validation, reserved-substring scan over every `status` value, template-only architectural log detection, identity-violations skeleton detection, and papers-consulted starter diff. Resolves the skill's `assets/` from the script's own location or `AUTORESEARCH_BIO_ASSETS` env var.
- `SKILL.md` launch precondition: the skill refuses Tier 1 runs until `leakage_preflight.md` and `split_manifest.json` exist.
- `SKILL.md` "Agent Compatibility" subsection making the agent-agnostic stance explicit (Claude Code, ChatGPT / Codex agents, Cursor, Aider, custom SDK harnesses, or no agent at all).

### Changed

- `SKILL.md` frontmatter `description` now mentions leakage pre-flight and agent-agnostic prompting.
- `SKILL.md` intro reframed as **bio-first, domain-general, agent-agnostic**. Skill output remains plain-Markdown prompts with no vendor-specific tool calls.
- `references/core_protocol.md §3` Step 0 deliverables list extended with `split_manifest.json` and `leakage_preflight.md`.
- `references/core_protocol.md §14` stop-conditions list extended with `locked_split_spent_without_new_holdout_registered` and the multiple-comparison-floor closure trigger.
- `references/biology_addendum.md` safety boundary extended with an explicit rule that "improvement over baseline on the selection split" is exploratory and never a benchmark claim. Required confirmations: fresh held-out split, nested CV, or external cohort.
- `evals/process_checklist.md` failure conditions extended with the launch-precondition check (no `leakage_preflight.md` / `split_manifest.json` → fail) and the reserved-substring scan over every emitted status.

### Motivating evidence

- All of the above are driven by the [MoFNet POC](https://github.com/yashraj59/MoFNet), in which the prior version of this protocol:
  - allowed the locked test split to be used as a selection oracle across 123 trials;
  - permitted a continuation script to auto-write an amendment overturning its own stop trigger;
  - emitted status strings containing `PUBLIC_REFERENCE_BEAT` and `BELOW_PUBLIC_REFERENCE` directly into `results.tsv`;
  - left frozen on-disk integrated-gradients files derived from the test set readable by every downstream experiment, even after the leakage-corrected amendment;
  - produced 100+ Tier 1 single-seed runs against the same primary metric with no multiple-comparison correction;
  - logged 130+ architectural changes whose entries were template prose with no per-entry metadata.
  The patches in this release convert each of those failures from a prose rule into a structural pre-flight, schema, or grep-style check the validation script can enforce.

## 2026-05-26 — Lineage and council cleanup

### Added

- `references/lineage.md` defining the lightweight DAG layer. Every experiment now records `parent_experiment_ids`, `branch_type` (root/linear/fork/combine/replay), and `subtree_status` (active_leaf/expanded/pruned/promoted/retired_subtree).
- `references/amendment_review_checklist.md` salvaged from the Monitor failure-mode checks in the Debate Council. The seven checks now apply to both supervised amendments and council amendments.
- Lineage columns in `assets/results_tsv_schema.tsv`.
- Lineage fields in `assets/research_journal_entry_template.md`.
- Lineage section in `assets/autoresearch_template.md`.
- Lineage and amendment-review decision labels in `references/decision_labels.md`.
- Lineage trigger prompts in `evals/trigger_prompts.csv`.
- Lineage and launch-message checks in `evals/process_checklist.md`.
- Lineage column validation in `scripts/validate_autoresearch_artifacts.py`.
- Launch-message-block check in `scripts/validate_skill_repo.py`.

### Changed

- README rewritten to restore first-person research-log voice from the original single-file skill. Stripped the corporate "Who Can Use It" tables, installation matrix, and validation instructions. Moved file-guide content to short bullets.
- `assets/autoresearch_template.md` no longer includes a launch instruction block. The launch message is now emitted as a separate chat block when the agent produces an autoresearch.md.
- `SKILL.md` explicitly instructs the agent to emit the launch message separately as chat text, not inside the autoresearch.md file.
- `assets/autoresearch_template.md` Required Diagnostics block split into three sub-blocks: universal, biology-only, non-bio-only. Users keep what applies and delete the other sub-block.
- `references/debate_council.md` revised with four tweaks:
  - Honest limitations section added at the top.
  - Confidence thresholds (0.65 / 0.55) relabeled as starting heuristics that should be recalibrated after the first 3-5 council convenings.
  - "Exactly three rounds" replaced with "up to four rounds, stop when no new arguments appear."
  - Biology-interpretation decisions added as a hard escalation trigger, with explicit note that the Biologist role is not a real biologist.
  - Monitor failure-mode checks moved into `references/amendment_review_checklist.md`.
- `references/artifact_retention.md` updated with lineage columns in the results.tsv schema and a search-tree summary requirement in the final report.

### Preserved

- Protected model of record.
- Step 0 baseline registry.
- Tiered gates.
- No Tier 1/Tier 2 rebasing.
- Stop/amend/close discipline.
- Metric investigation protocol.
- Debate Council pattern (now opt-in, supervised default).
- Biology-specific evaluation discipline.
- Domain adaptation reference for non-bio use.

## 2026-05-26 — Bio-first, domain-flexible update

### Changed

- Clarified that `autoresearch-bio` is bio-first, not bio-only.
- Updated `README.md` with non-bio usage examples and a domain mapping table.
- Updated `SKILL.md` frontmatter and trigger rules to support bounded autonomous model-development and software research loops outside biology.
- Added domain-adaptation guidance for translating biological no-regression checks into project-specific protected behavior.
- Added `references/domain_adaptation.md` for language/code systems, vision, recommenders, search/retrieval, forecasting, robotics, infrastructure, and general software/model development.
- Added non-biological trigger evals for recommender, vision, time-series, and general dev loops.

## 2026-05-26 — Initial repo-style revision

Initial repo-style revision of the original single-file `autoresearch-bio` skill.

### Added

- Modular `references/` files for core protocol, biology, metrics, statistics, Debate Council, decision labels, artifact retention, and domain adaptation.
- Paste-ready `assets/` templates.
- Trigger and process evals.
- Validation scripts.
- README, manifest, changelog, `.gitignore`, and MIT license.

### Changed

- Kept `name: autoresearch-bio`.
- Rewrote the skill description for better triggerability and clearer boundaries.
- Shortened the top-level `SKILL.md` into an operational playbook.
- Added explicit Do-Not-Use guidance.
- Added missing-information policy.
- Added low-compute mode.
- Added stronger statistical promotion criteria.
- Added clearer biology safety/compliance boundaries.
- Revised Debate Council novelty language so the council can propose novel combinations while remaining skeptical and falsifiable.
