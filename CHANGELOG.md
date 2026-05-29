# Changelog

## Unreleased — Autonomy gaps, council trace preservation, calibration audit cadence, literature fetch evidence, insight-brief reflection

### Added

- **`references/core_protocol.md` §15-§25** (the existing Closure and Next-Phase sections moved to §26-§27; §1-§14 unchanged):
  - §15 non-experiment node cap (`SPIRAL_NON_EXPERIMENT_NODE_CAP_EXCEEDED`).
  - §16 closure-time fallback actions must execute (`CLOSURE_FALLBACK_READ_PENDING` / `_EXECUTED`).
  - §17 screen calibration audit cadence (`METRIC_SCREEN_DEMOTED_BY_CALIBRATION_AUDIT`). Reads taken during search are `validation`-role reads counting toward the multiple-comparison floor; `locked_test` is read once at closure. This reconciles the audit with the existing §3.5 four-role split rather than inventing a parallel "locked read" concept.
  - §18 attribution-control default for a new family's first experiment (`TIER1_DISCARD_UNATTRIBUTABLE` / `TIER1_KEEP_CONTROLLED_SIGNAL`). Declared the primary anti-noise check; in low-compute mode it replaces multi-seed Tier 2 replay, which becomes opt-in.
  - §19 borderline retention and closure fallback (`TIER1_BORDERLINE`, `FAMILY_BORDERLINE_COOLDOWN`).
  - §20 single-seed model-of-record disclosure (`SINGLE_SEED_MODEL_OF_RECORD_ACCEPTED`).
  - §21 gate-metric alignment.
  - §22 closure terminality / reopen authorization (`REOPEN_REQUIRES_EXPLICIT_USER_INSTRUCTION`).
  - §23 quarter-budget reassessment gate.
  - §24 literature cadence pre-launch check and fetch evidence (`LITERATURE_PASS_FETCH_EVIDENCE_MISSING`).
  - §25 INSIGHT_BRIEF reflective audit (`INSIGHT_BRIEF_REFLECTION_MISSING`).
  - Each section carries a Profile tag (lean and full, or full only) so the additions tier cleanly with the existing Low-Compute Mode instead of crushing small runs.
- **`references/debate_council.md`**: Trace Preservation Requirement, Cross-Rebuttal Structural Requirement (`COUNCIL_TRACE_MISSING`, `COUNCIL_TRACE_SUMMARY_ONLY`, `COUNCIL_ROUND_ROBIN_PATTERN_DETECTED`), Council Decision Budget (`decision_budget_consumed`), and single-vendor disclosure on amendment-grade decisions (`COUNCIL_DIVERSITY_SINGLE_VENDOR`).
- **`references/metric_calibration_audit.md`** and **`references/skill_anti_patterns.md`** (two new reference files).
- **`assets/calibration_audit_template.md`**, **`assets/insight_brief_template.md`**, **`assets/reopen_authorization_template.md`** (three new templates). Expanded `assets/debate_council_template.md` to the trace structure.
- **`references/decision_labels.md`**: 16 new labels with one-line semantics.
- **`scripts/validate_autoresearch_artifacts.py`**: ten new checks. Advisory output is now partitioned from hard errors so "could not check" notes (missing journal node headers, no `--budget`, no council-trace dir) do not fail the run. The semantic council-trace checks are explicitly heuristic (surface markers, not proof of debate substance) per their docstrings. Journal-ordering checks read an optional machine-readable node header and degrade to advisory when absent.

### Changed

- `references/artifact_retention.md`: added `decision_budget_consumed` to the `summary.json` identity block; added `single_seed_model_of_record_acknowledged`; lowered the INSIGHT_BRIEF cadence threshold from N>=100 to N>=20; extended the INSIGHT_BRIEF schema with the reflective-audit fields.
- `references/amendment_review_checklist.md`: added check 8 (closure-action enforceability); renamed to the Eight Checks.
- `references/core_protocol.md §13`: literature discipline now enforced both at stall and pre-launch, with the four fetch-evidence fields required on every added paper.
- `SKILL.md` Reference Loading Map: added rows for `metric_calibration_audit.md` and `skill_anti_patterns.md`.

### Motivating evidence

Surfaced by the RAM PoC autonomous run on the Arc Institute Virtual Cell Challenge: the loop spent too many consecutive support nodes before returning to experiments, anchored on a cheap screen metric whose correlation with the promotion metric was never audited, skipped the insight-brief and literature cadences that the skill already mandated, and under-documented council decisions. The fixes generalize the lessons (the cell-eval and VCC specifics stay out of the skill): a non-experiment node cap, a screen-vs-promotion calibration audit, a quarter-budget reassessment, literature fetch evidence, reflective briefs, and council trace preservation. The §18 attribution control is the cheap rigor check that replaces multi-seed replay when compute is tight, and §17/§3.5 keep the repeated-confirmation-read pattern honest by counting every `validation` read toward the multiple-comparison floor and reserving `locked_test` for a single closure read.

### Deferred to a later PR

Parts 8-9 of the upgrade spec (a `quickstart/`, a second non-bio worked demo, project-type overlays, and an `engineering_runbook.md`) are additive onboarding material and are not included here. The existing `autoresearch_demo/` predates the PR #1-5 file requirements and already fails the validator; regenerating it to be validator-clean is part of that deferred onboarding work.

## Unreleased — Council self-critique step

### Added

- **New Council Process step 3, "Self-critique."** Between independent proposals (step 2) and steelmanning (step 4, renumbered from 3), each agent must articulate the single strongest argument against its own proposal and either revise the proposal to address it, or attach the unaddressed weakness as a `self_identified_weakness` field on the submission. The Monitor enforces the field. Proposals missing it, or containing boilerplate that could be copy-pasted onto any proposal, are rejected before they reach scoring. Inspired by the STaR / SCoRe family of self-training methods that exploit the recognition-better-than-generation asymmetry in LLMs, adapted to a decision-making context rather than a training context.
- **New section `references/debate_council.md "Self-Critique Honest Limitations"`** documenting what self-critique catches and what it does not. Specifically: single-agent correlation (a model agreeing with itself), novel-mechanism blind spots (no recognition signal for unfamiliar ideas), boilerplate hazard (generic weaknesses that fail the Monitor's enforcement), and the per-closure cost (roughly 4 to 8 extra LLM calls on top of the existing 25 to 35). Self-critique complements but does not replace the Skeptic role or multi-vendor diversity.
- **New label `COUNCIL_PROPOSAL_SELF_CRITIQUE_MISSING`** in `references/decision_labels.md`.

### Changed

- `references/debate_council.md` Council Process renumbered from 9 to 10 steps. The Documentation step now requires `debate_council_<id>.md` to include each proposal's `self_identified_weakness` field verbatim.

### Motivating evidence

The Skeptic role and multi-vendor diversity are good at catching weaknesses in other agents' proposals. They do less for the asymmetry between what a model generates and what the same model can recognize as flawed. Self-critique is the cheap intra-agent quality filter that catches obvious-bad-proposals before they cost the council four rounds of debate. It is explicitly not a substitute for the Skeptic or for multi-vendor councils; the three layers stack.

## Unreleased — Council multi-vendor option + README rewrites

### Added

- **`references/debate_council.md "Council Model Diversity"` (new section).** The Debate Council now supports an opt-in multi-vendor configuration where each role (Architect, Skeptic, Methodologist, Biologist or domain specialist, Monitor) can run on a different model vendor. Config shape:

  ```yaml
  council_models:
    architect:     anthropic/claude-opus-4.7
    skeptic:       openai/gpt-5.5-pro
    methodologist: google/gemini-pro
    biologist:     anthropic/claude-opus-4.7
    monitor:       openai/gpt-5.5-pro
  ```

  Or the default easy onramp:

  ```yaml
  council_models: same_model_all_roles
  ```

  Recommendation is at least two distinct vendors across the five roles for closure-critical decisions; all-same-vendor remains valid but is logged as `council_diversity: single_vendor`. New failure modes (cost variance, latency variance, role-vendor confounding, output format drift, vendor monoculture across runs) are documented in the same section. The skill specifies the protocol; the actual API orchestration is the user's harness responsibility.

- **`references/decision_labels.md` new label `COUNCIL_MULTI_VENDOR_FALLBACK_USED`.** Fires when a configured role falls back to the primary vendor because of a missing API key, timeout, or error mid-council.

### Changed

- **`references/debate_council.md "Same model, different prompts"` warning.** Reworded to note that this applies to the default single-vendor configuration and points the reader at the new Council Model Diversity section as the mitigation.

- **`README.md` Lineage tracking section.** Rewritten from changelog framing ("This revision adds a lightweight DAG layer...") to user-facing feature description ("Every experiment records its parent IDs and a branch type...").

- **`README.md` Debate Council section.** Rewritten from changelog framing ("This revision keeps the Debate Council as an opt-in option...") to user-facing description that names the five roles (Architect, Skeptic, Methodologist, Biologist or domain specialist, Monitor), describes what the council actually does (propose, steelman, debate, score, vote, write amendment), and surfaces the new multi-vendor option as the recommended configuration for closure-critical decisions.

### Motivating evidence

The current "Same model, different prompts" limitation in `debate_council.md` line 15 is the council's most-acknowledged weakness. Role prompts give you four prompt variations of one underlying model, not four independent models. Multi-vendor configuration directly mitigates this by introducing genuine distribution diversity across council members, while keeping the default single-vendor configuration as a valid easy onramp for users with only one API key.

## Unreleased — External baseline split parity

### Added

- **`references/biology_addendum.md "External Baseline Split Parity"`.** A separate subsection under External Baseline Reproduction Provenance. Every row of `external_public_baselines.tsv` must declare `eval_split` (which `split_manifest.json` role the score was computed on), `split_parity` (`same_train_same_eval` / `same_train_different_eval` / `different_train_different_eval`), and `split_manifest_sha256`. A `different_train_different_eval` row is documented as ballpark reference only and may not be cited as evidence in "the model beats X" claims. The recommended workflow: write a script that loads `split_manifest.json`, trains each external on the project's `train` indices using the external's documented default hyperparameters, evaluates separately on each held-out role, and writes one row per `(external, eval_split)` pair with `split_parity = same_train_same_eval`. The worked example lives at [`mofnet_poc/scripts/run_externals_same_mlomics_split.py`](https://github.com/yashraj59/mofnet_poc/blob/main/scripts/run_externals_same_mlomics_split.py).
- **`references/domain_adaptation.md`** mirrors the same rule for non-bio projects.
- **`references/decision_labels.md`** new label `EXTERNAL_BASELINE_SPLIT_PARITY_UNDOCUMENTED`.
- **`scripts/validate_autoresearch_artifacts.py`** now checks `eval_split` and `split_parity` columns in `external_public_baselines.tsv`, enforces the enum on `split_parity`, and surfaces the new label when columns are missing.

### Motivating evidence

The MoFNet POC originally ran MOGONET and moBRCA-net on the MOGONET BRCA preprocessed split (875 samples, 1000 features per omic) while MoFNet ran on MLOmics GS-BRCA Top (671 samples, 5000/5000/366 features). The comparison was reported as a head-to-head when in fact the externals were on a different dataset slice with different feature selection and a different train/test partition. The autoresearch-bio external-baseline rule in PR #2 caught reproduction-mode lies and metric-selection-policy lies but did not catch the split-parity lie. This patch closes that gap.

## Unreleased — Literature search hardening, resumability, and provenance discipline

### Added

- **`references/core_protocol.md §13 "Literature Search Discipline"` — replaced wholesale.** Names canonical search surfaces by domain (biology: arXiv q-bio / bioRxiv / medRxiv / PubMed / OpenAlex / Semantic Scholar / Connected Papers / OpenReview / Reactome / MSigDB / GO / ClinVar / GTEx / ENCODE / HCA / STRING / KEGG / DepMap; general ML: arXiv / Semantic Scholar / OpenReview / Papers with Code / proceedings sites / ACL Anthology). At least three per pass. References the Codex `$life-science-research` skill as a primary bio surface when available. Specifies a three-mode fetch fingerprint (`agent_harness_web_tools` / `semantic_scholar_api` / `mcp_paper_search`) declared in `leakage_preflight.md` and `papers_consulted.md`. Adds a "when-stuck" trigger independent of fixed cadence: three consecutive Tier 1 discards in a family, a Tier 2 failure with protected-metric regression, a metric investigation that rules out a mechanism class, or +20 experiments without clearing the multiple-comparison floor. Trigger label: `LITERATURE_PASS_REQUIRED_BY_STALL`. Adds the starter-file cross-check before any family's first Tier 1 keep: tagged papers must have populated `Experiment where it was tried / Outcome` fields. Failure label: `LITERATURE_GROUNDING_MISSING`. The per-paper record now includes search-surface and fetch-fingerprint fields.
- **`references/core_protocol.md §7 "Metric Identity Across Phase Boundaries"`.** Every gate-bearing column has a definitional fingerprint. Phase boundaries (amendment, leakage correction, prompt rewrite, evaluator refactor) require `METRIC_IDENTITY_DIFF.md`. Failure label: `METRIC_IDENTITY_DIFF_REQUIRED`.
- **`references/lineage.md` — new `grid_sweep` branch type.** Three or more children of one parent that share a mechanism class and differ only in continuous/categorical hyperparameters. Only the best child per sweep may advance to Tier 2; sweep axes are documented in `family_allocation.md` so the multiple-comparison floor correctly attributes the candidate count.
- **`references/artifact_retention.md` — four new sections.**
  - "Resumability Discipline" — `*HANDOFF*.md` cap ~8 KB, mandatory `STATE_OF_PLAY.md` (≤2 KB, replaced not appended), `insights/INSIGHT_BRIEF_NNN.md` cadence every 10 experiments. Failure labels: `RESUMABILITY_STATE_OF_PLAY_STALE`, `RESUMABILITY_INSIGHT_BRIEFS_MISSING`, `HANDOFF_DOCUMENT_OVERSIZED`.
  - "`insights/INSIGHT_BRIEF_NNN.md` Schema" — required fields (experiment-num range, family-allocation snapshot, what was learned, what is not being pursued, next 5 planned experiments).
  - "Append-Only Log Hygiene" — forbidden placeholder titles (`TMP`, `TODO`, `XXX`, `FIXME`); closure must backfill or delete orphans. Failure label: `APPEND_ONLY_LOG_ORPHAN_UNRESOLVED`.
  - "Single Source Of Truth For Reference Numbers" — plot/PDF/blog generators must read comparator numbers from `BASELINE_REGISTRY.md` or `external_public_baselines.tsv`, never from hardcoded module constants. Failure label: `REFERENCE_NUMBER_HARDCODED_IN_REPORT`.
- **`references/biology_addendum.md` + `references/domain_adaptation.md` — "External Baseline Reproduction Provenance"** identical rule in both. Every comparator-TSV row must declare `reproduction_mode` (`upstream_unchanged` / `upstream_patched` / `full_reimplementation`), `claim_strength`, `upstream_commit_or_release`, `metric_selection_policy`. A `full_reimplementation` may not be reported as a published-baseline reproduction. Failure labels: `REPRODUCTION_PROVENANCE_MISSING`, `EXTERNAL_BASELINE_REIMPLEMENTATION_MISLABELED`.
- **`references/decision_labels.md` — new label block** covering all of the above with one-line semantics.
- **`evals/process_checklist.md` — five new check blocks.** Tightened literature discipline (untouched-starter + stall-triggered pass + starter cross-check before first Tier 1 keep), resumability & cognitive checkpoint (STATE_OF_PLAY presence/staleness, INSIGHT_BRIEF cadence, handoff size), metric identity at phase boundaries, append-only log hygiene, external-baseline reproduction provenance, reference-number single source of truth.
- **`scripts/validate_autoresearch_artifacts.py` — new validators.**
  - `grid_sweep` added to `VALID_BRANCH_TYPES` and the single-parent constraint.
  - `validate_resumability()` — STATE_OF_PLAY presence/size, INSIGHT_BRIEF cadence at N≥100, handoff size cap.
  - `validate_append_only_logs()` — scans for orphan markers (`TMP` / `TODO` / `XXX` / `FIXME` / `<...>` / `<TBD>`).
  - `validate_external_baselines_tsv()` — checks required reproduction-provenance columns and the "reimplementation claiming reproduction" anti-pattern.
- **`assets/papers_consulted_starter.md` — rewritten** with the canonical search surfaces, the fetch-fingerprint declaration template, and the extended per-paper record fields.

### Changed

- `references/artifact_retention.md` "Required Documentation Files" table now lists `STATE_OF_PLAY.md`, `leakage_preflight.md`, `split_manifest.json`, and `METRIC_IDENTITY_DIFF.md` alongside the existing required artifacts.
- `family_allocation.md`'s prescribed contents now include sweep-axis documentation.

### Motivating evidence

- The MoFNet POC had 123 experiments and `papers_consulted.md` byte-identical to its starter. The starter listed three 2025 SOTA papers using cross-omic attention (HyperCLSA, CMGL, MOGOLA). The agent invented Family 1 (cross-omic attention) from scratch while those references sat in the file with empty outcome fields. Zero arXiv / DOI / "et al." references appeared in 113 KB of research-journal text. Zero HTTP requests to bioRxiv / arXiv / PubMed / Semantic Scholar in any Python driver. The "search the literature" rule existed only as prose; this release converts it to (a) named surfaces, (b) declared fetch fingerprint, (c) when-stuck trigger, (d) starter-file cross-check enforced by the validator and by a `LITERATURE_GROUNDING_MISSING` status label.
- `insights/` was empty across 139 experiments; `CODEX_HANDOFF.md` reached 24 KB of append-only chat-style chronology. The resumability section converts the implicit cadence rule into a machine-checkable cap.
- `architectural_changes_log.md` had 4 `## TMP` orphan blocks from an aborted sweep; the new orphan-marker scan catches this class.
- `external_public_baselines.tsv` lacked any `reproduction_mode` column. `mobrca_net_py37_compat.py` is a 237-line from-scratch reimplementation logged with the canonical upstream URL as `source_repo`. The new provenance columns force a `full_reimplementation` row to label itself as such.

## Previously Unreleased — Leakage pre-flight, process-loophole guardrails, reproducibility identity, agent-agnostic framing

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
