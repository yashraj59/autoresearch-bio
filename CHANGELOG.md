# Changelog

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
