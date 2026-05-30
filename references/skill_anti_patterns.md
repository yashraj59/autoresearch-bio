# Skill Anti-Patterns

A digest of the failure modes this skill exists to catch. Each one was surfaced by a real run, not invented. For each: what it looks like, why it is tempting, what the skill enforces against it, and the decision label that catches it.

Read this before launching a long autonomous loop. Most autonomy failures are one of these.

## 1. Locked-test as selection oracle

**Looks like:** evaluating candidates on the same held-out split repeatedly and using those scores to decide which candidate to keep, warm-start, or promote.
**Tempting because:** the held-out split is the metric you care about, so checking it often feels like diligence.
**Skill enforces:** the four-role split (`core_protocol.md §3.5`); `validation` is the repeatable selection surface and every read counts toward the multiple-comparison floor; `locked_test` is read once at closure and then spent.
**Label:** `FAIL_TEST_IN_SELECTION`, `locked_split_spent_without_new_holdout_registered`.

## 2. Spiral support nodes

**Looks like:** building harnesses, wrappers, metric scripts, and preflight guards in sequence without launching the next experiment.
**Tempting because:** each piece of scaffolding is individually useful and feels productive.
**Skill enforces:** the non-experiment node cap (`core_protocol.md §15`).
**Label:** `SPIRAL_NON_EXPERIMENT_NODE_CAP_EXCEEDED`.

## 3. Unauthorized self-reopen

**Looks like:** after `SEARCH_CLOSED_NO_NEW_BASELINE`, the loop writes a new amendment and resumes because the goal "was not reached yet."
**Tempting because:** the stop threshold was not hit, so continuing feels like finishing the job.
**Skill enforces:** closure terminality (`core_protocol.md §22`); reopen requires an explicit verb in the preceding user message plus a `REOPEN_AUTHORIZATION_RECORD.md`.
**Label:** `REOPEN_REQUIRES_EXPLICIT_USER_INSTRUCTION`.

## 4. Screen-as-ranker without calibration

**Looks like:** using a cheap proxy metric to rank candidates for expensive confirmation reads, assuming it tracks the promotion metric because both measure "the same thing."
**Tempting because:** the proxy is cheap and computed every epoch.
**Skill enforces:** the screen calibration audit (`core_protocol.md §17`, `metric_calibration_audit.md`).
**Label:** `METRIC_SCREEN_DEMOTED_BY_CALIBRATION_AUDIT`.

## 5. Unattributed family deepening

**Looks like:** a new mechanism clears the static floor, so the loop deepens it to multi-seed and promotion, without ever checking whether the same recipe without the mechanism would score as well.
**Tempting because:** an above-floor score looks like the mechanism worked.
**Skill enforces:** the attribution-control default for a new family's first experiment (`core_protocol.md §18`).
**Label:** `TIER1_DISCARD_UNATTRIBUTABLE` (and the positive `TIER1_KEEP_CONTROLLED_SIGNAL`).

## 6. Single-seed model of record without disclosure

**Looks like:** the promoted model rests on one seed's confirmation read, reported as if seed-confirmed.
**Tempting because:** seeds are expensive and the single result looked strong.
**Skill enforces:** single-seed disclosure (`core_protocol.md §20`).
**Label:** `SINGLE_SEED_MODEL_OF_RECORD_ACCEPTED`.

## 7. Hardcoded reference numbers in plot generators

**Looks like:** a plot, PDF, or blog generator embeds a comparator number as a module constant instead of reading it from the registry.
**Tempting because:** it is one line and the number "is not going to change."
**Skill enforces:** single-source-of-truth for reference numbers (`artifact_retention.md`).
**Label:** `REFERENCE_NUMBER_HARDCODED_IN_REPORT`.

## 8. Starter file untouched

**Looks like:** `papers_consulted.md` is byte-identical to its starter after many experiments; the loop reinvents mechanisms already in the cited literature.
**Tempting because:** literature search is slow and the loop has momentum.
**Skill enforces:** literature discipline and the pre-launch fetch-evidence check (`core_protocol.md §13`, §24).
**Label:** `LITERATURE_DISCIPLINE_VIOLATION`, `LITERATURE_PASS_FETCH_EVIDENCE_MISSING`, `LITERATURE_GROUNDING_MISSING`.

## 9. Council round-robin

**Looks like:** a debate trace exists but the skeptic does not engage the builder's actual claim and the methodologist does not address the skeptic's strongest point.
**Tempting because:** producing a trace satisfies the file-exists check; substance is harder.
**Skill enforces:** cross-rebuttal structural requirement (`debate_council.md`). Note the validator check is a heuristic, not a proof of substance.
**Label:** `COUNCIL_ROUND_ROBIN_PATTERN_DETECTED`.

## 10. Pause-grade gate on a non-promotion metric

**Looks like:** the loop halts or blocks next-experiment selection based on a secondary or proxy metric while the actual promotion metric keeps drifting.
**Tempting because:** the proxy is what is cheap to compute at gate time.
**Skill enforces:** gate-metric alignment (`core_protocol.md §21`).
**Label:** caught at review; no single automated label.

## 11. Literature pass without fetch evidence

**Looks like:** paper titles appear in `papers_consulted.md` with no URL, timestamp, surface, or extract; nothing was actually retrieved.
**Tempting because:** writing a title is faster than fetching and reading.
**Skill enforces:** fetch-evidence fields (`core_protocol.md §24`).
**Label:** `LITERATURE_PASS_FETCH_EVIDENCE_MISSING`.

## 12. INSIGHT_BRIEF as forward enumeration only

**Looks like:** briefs list the next five experiments but never check whether the previous brief's predictions came true.
**Tempting because:** planning forward is easier than auditing your own past predictions.
**Skill enforces:** the reflective-audit requirement (`core_protocol.md §25`).
**Label:** `INSIGHT_BRIEF_REFLECTION_MISSING`.
