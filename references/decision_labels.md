# Decision Label Vocabulary

Pre-register exact labels. Avoid vague labels such as "promising," "looks good," "interesting," or "maybe keep."

Use these labels directly or adapt them with the same level of specificity.

---

## Baseline And Setup

```text
BASELINE_COMPLETE
BASELINE_AMBIGUOUS_PROVENANCE_BLOCKED
BASELINE_REGISTRY_UPDATED
METRIC_DIRECTIONALITY_CONFIRMED
EXPERIMENT_PREALIGN_ABORTED_IMPLEMENTATION_MISMATCH
```

---

## Tier 1 Labels

```text
TIER1_KEEP_CONTROLLED_SIGNAL
TIER1_DISCARD_NO_SIGNAL
TIER1_DISCARD_CAP_BOUND
TIER1_DISCARD_MARKER_OR_PROGRAM_REGRESSION
TIER1_DISCARD_PROTECTED_DOMAIN_REGRESSION
TIER1_DISCARD_METRIC_REGRESSION
TIER1_DISCARD_IMPLEMENTATION_MISMATCH
TIER1_DISCARD_MODE_COLLAPSE
TIER1_DISCARD_IDENTITY_VIOLATION
TIER1_DISCARD_MISSING_DIAGNOSTICS
TIER1_DISCARD_MISSING_LINEAGE
```

---

## Tier 2 Labels

```text
TIER2_PASS_CLEAN
TIER2_PASS_HIGH_RISK_DO_NOT_PROMOTE_YET
TIER2_FAIL_SIGNAL_NOT_RETAINED
TIER2_FAIL_CAP_BOUND
TIER2_FAIL_METRIC_REGRESSION
TIER2_FAIL_VALIDATOR_REGRESSION
TIER2_FAIL_HIGH_VARIANCE
TIER2_FAIL_MODE_COLLAPSE
TIER2_FAIL_PROTECTED_BIOLOGY_REGRESSION
TIER2_FAIL_PROTECTED_DOMAIN_REGRESSION
```

---

## Tier 3 Labels

```text
TIER3_PASS_NEW_BASELINE
TIER3_FAIL_USEFUL_FAILURE
TIER3_FAIL_NO_GENERALIZATION
TIER3_FAIL_PROTECTED_GATE
TIER3_FAIL_STATISTICALLY_UNSTABLE
TIER3_FAIL_PROVENANCE_AMBIGUITY
```

---

## Family And Search Labels

```text
FAMILY_ACTIVE
FAMILY_DEEPEN
FAMILY_COOLDOWN
FAMILY_RETIRED
FAMILY_REOPENED_BY_AMENDMENT
SEARCH_CONTINUE
SEARCH_AMEND
SEARCH_METRIC_AUDIT_REQUIRED
SEARCH_CLOSED_NO_NEW_BASELINE
SEARCH_CLOSED_NEW_BASELINE_PROMOTED
```

---

## Lineage And Subtree Labels

```text
LINEAGE_ROOT
LINEAGE_LINEAR
LINEAGE_FORK
LINEAGE_COMBINE
LINEAGE_REPLAY
SUBTREE_ACTIVE_LEAF
SUBTREE_EXPANDED
SUBTREE_PRUNED
SUBTREE_PROMOTED
SUBTREE_RETIRED
SUBTREE_PRUNE_REASON_CAP_BOUND
SUBTREE_PRUNE_REASON_MODE_COLLAPSE
SUBTREE_PRUNE_REASON_FAMILY_RETIRED
SUBTREE_PRUNE_REASON_METRIC_INVALIDATED
```

---

## Metric Investigation Labels

```text
METRIC_INVESTIGATION_OPENED
METRIC_STACK_VALIDATED
METRIC_STACK_INVALID_OLD_SEARCH_PAUSED
METRIC_REOPEN_ARCHITECTURE_SEARCH
METRIC_KEEP_SEARCH_CLOSED
METRIC_MORE_ARTIFACTS_REQUIRED
```

---

## Debate Council Labels

```text
COUNCIL_EXECUTE_AMENDMENT
COUNCIL_ITERATE_DEBATE
COUNCIL_ESCALATE_TO_USER
COUNCIL_RETIRE_FAMILY
COUNCIL_BLOCKED_BY_MONITOR
COUNCIL_BLOCKED_BY_IDENTITY
COUNCIL_BLOCKED_BY_LOCKED_FILE
COUNCIL_BLOCKED_BY_LOW_CONFIDENCE
COUNCIL_BLOCKED_BY_MONOCULTURE_LOCKIN
COUNCIL_BLOCKED_BY_BIOLOGY_INTERPRETATION
COUNCIL_BLOCKED_BY_AMENDMENT_REVIEW_FAIL
```

---

## Amendment Review Labels

```text
AMENDMENT_REVIEW_PASS
AMENDMENT_REVIEW_FAIL_MONOCULTURE
AMENDMENT_REVIEW_FAIL_IDENTITY_DRIFT
AMENDMENT_REVIEW_FAIL_METRIC_TUNNEL
AMENDMENT_REVIEW_FAIL_RECENCY_BIAS
AMENDMENT_REVIEW_FAIL_COMPLEXITY_CREEP
AMENDMENT_REVIEW_FAIL_COST_OF_BEING_WRONG
AMENDMENT_REVIEW_FAIL_SAFETY_BOUNDARY
```

---

## Artifact Retention Labels

```text
ARTIFACT_RETAIN_MODEL_OF_RECORD
ARTIFACT_RETAIN_TIER3_WINNER
ARTIFACT_RETAIN_AUDIT_RELEVANT_NEAR_MISS
ARTIFACT_DELETE_TIER1_DISCARD_CHECKPOINT
ARTIFACT_DELETE_TIER2_FAILURE_CHECKPOINT
ARTIFACT_RETAIN_METRICS_AND_LOGS
```

## Reserved Strings In Automated Status Labels

Status values emitted by code (any field in `results.tsv`, `summary.json`, or other run-time artifacts whose value comes from a `status = ...` assignment or enum) must not contain comparator-relative tokens. Status is an outcome, never a relative claim.

The following substrings are reserved and must not appear in any auto-emitted status label:

```text
# Claim-strength tokens (smuggle in a benchmark assertion)
BEAT          SOTA            WINS
OUTPERFORMS   SURPASSES       STATE_OF_THE_ART
BENCHMARK_WIN

# Comparator-relative tokens (encode a comparison to a reference number)
ABOVE_REFERENCE     BELOW_REFERENCE     EQUAL_REFERENCE
MATCHES_REFERENCE   WITHIN_X_OF         EXCEEDS_REFERENCE
MISSES_REFERENCE
```

Acceptable alternatives for "the candidate's metric is above a documented reference threshold":

```text
TIER1_KEEP_VALIDATION_ABOVE_REF       # outcome of the gate, not a claim
TIER2_MULTI_SEED_VALIDATION_ABOVE_REF
POSTLOCK_VALIDATION_KEEP              # plain outcome
```

Relative comparisons to literature, internal references, or prior model-of-record numbers live in the `protected_metric_summary` JSON column of `results.tsv` and in `final_report.md` prose, never in the status column.

The leakage pre-flight audit (`core_protocol.md §3.5`) must grep the codebase and run-summary artifacts for the reserved substrings and refuse to launch if any are found.

## Amendment Review Auto-Override Label

```text
AMENDMENT_REVIEW_FAIL_AUTO_OVERRIDE
```

Applied to any amendment block authored by the same autonomous process that hit the stop condition it purports to override (see `core_protocol.md §14`). The amendment is non-actionable; the loop must wait for a supervised human turn or a Debate Council convocation in a different agent process.

## Literature, Metric Identity, Resumability, And Reproduction-Provenance Labels

```text
LITERATURE_PASS_REQUIRED_BY_STALL
LITERATURE_GROUNDING_MISSING
LITERATURE_DISCIPLINE_VIOLATION
METRIC_IDENTITY_DIFF_REQUIRED
APPEND_ONLY_LOG_ORPHAN_UNRESOLVED
IDENTITY_BLOCK_INCOMPLETE
ARCHITECTURAL_LOG_TEMPLATE_ONLY
IDENTITY_VIOLATIONS_LOG_SKELETON
RESOURCE_PROVENANCE_VIOLATION
RESUMABILITY_STATE_OF_PLAY_STALE
RESUMABILITY_STATE_OF_PLAY_OVERSIZED
RESUMABILITY_INSIGHT_BRIEFS_MISSING
HANDOFF_DOCUMENT_OVERSIZED
REPRODUCTION_PROVENANCE_MISSING
EXTERNAL_BASELINE_REIMPLEMENTATION_MISLABELED
EXTERNAL_BASELINE_SPLIT_PARITY_UNDOCUMENTED
REFERENCE_NUMBER_HARDCODED_IN_REPORT
SEARCH_CLOSED_NO_NEW_BASELINE_MCC_FLOOR
```

Semantics, briefly:

- `LITERATURE_PASS_REQUIRED_BY_STALL` — three consecutive Tier 1 discards in a family, a Tier 2 failure with protected-metric regression, a metric investigation that rules out a mechanism class, or +20 experiments since the last pass without clearing the MCC floor. Blocks the next mechanism for the family until a literature pass completes (see `core_protocol.md §13`).
- `LITERATURE_GROUNDING_MISSING` — a family produced a Tier 1 keep while papers tagged to its mechanism class sit in `papers_consulted.md` with empty `Experiment where tried / Outcome` fields. Blocks Tier 2 promotion until the entries are filled.
- `LITERATURE_DISCIPLINE_VIOLATION` — `papers_consulted.md` is byte-identical to `assets/papers_consulted_starter.md` after the first 10 experiments (see `evals/process_checklist.md`).
- `METRIC_IDENTITY_DIFF_REQUIRED` — a phase boundary touched a gate-bearing column without an accompanying `METRIC_IDENTITY_DIFF.md` (see `core_protocol.md §7`).
- `APPEND_ONLY_LOG_ORPHAN_UNRESOLVED` — orphan rows (TMP / TODO / template-only) survive closure. Blocks Tier 3 promotion for any candidate whose lineage passes through the affected log section.
- `IDENTITY_BLOCK_INCOMPLETE` — a per-experiment `summary.json` lacks the required identity block (see `artifact_retention.md`). The row is excluded from promotion evidence.
- `ARCHITECTURAL_LOG_TEMPLATE_ONLY`, `IDENTITY_VIOLATIONS_LOG_SKELETON`, `RESOURCE_PROVENANCE_VIOLATION` — stub-compliance failures detected by the validation script (see `evals/process_checklist.md`).
- `RESUMABILITY_STATE_OF_PLAY_STALE` — `STATE_OF_PLAY.md` is missing or older than the most recent `results.tsv` row.
- `RESUMABILITY_STATE_OF_PLAY_OVERSIZED` — `STATE_OF_PLAY.md` exceeds the ~2 KB cap (it is state, not history).
- `RESUMABILITY_INSIGHT_BRIEFS_MISSING` — ≥100 experiments with an empty `insights/` directory (see `artifact_retention.md`).
- `HANDOFF_DOCUMENT_OVERSIZED` — `CODEX_HANDOFF.md` or equivalent exceeds the ~8 KB state cap. Blocks closure until trimmed.
- `REFERENCE_NUMBER_HARDCODED_IN_REPORT` — a plot/PDF/blog generator embeds a numeric comparator as a module constant instead of reading from `BASELINE_REGISTRY.md` or `external_public_baselines.tsv`. Caught by code review rather than the validator (see `artifact_retention.md`).
- `REPRODUCTION_PROVENANCE_MISSING` — a row in `external_public_baselines.tsv` lacks `reproduction_mode`, `claim_strength`, `upstream_commit_or_release`, or `metric_selection_policy` (see `biology_addendum.md` / `domain_adaptation.md`).
- `EXTERNAL_BASELINE_REIMPLEMENTATION_MISLABELED` — a `full_reimplementation` row claims `upstream_unchanged` semantics, or a plot/PDF/blog renders the row without the required reimplementation label.
- `EXTERNAL_BASELINE_SPLIT_PARITY_UNDOCUMENTED` — a row in `external_public_baselines.tsv` is missing `eval_split`, `split_parity`, or `split_manifest_sha256`, or `split_parity` has an invalid value. The comparison cannot be cited until parity is declared. `different_train_different_eval` is allowed but flags the row as ballpark-only and forbids its use as evidence in "the model beats X" claims (see `biology_addendum.md "External Baseline Split Parity"`).
- `SEARCH_CLOSED_NO_NEW_BASELINE_MCC_FLOOR` — experiment cap reached with no candidate clearing the family-wise multiple-comparison floor (see `statistical_promotion.md`).
