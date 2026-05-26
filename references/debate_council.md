# Debate Council Mode

By default, autoresearch runs in supervised mode. When a stop condition fires, the loop halts and waits for a human. The human reviews results, drafts an amendment, and resumes the loop.

In fully autonomous mode, the human is removed from the inner loop. Instead, when a stop condition fires, the agent convenes a Debate Council of role-prompted sub-agents that deliberate, score proposals, vote, write the amendment, and resume. The human is only contacted on hard escalation triggers.

**Default to supervised mode unless the user explicitly asks for autonomous research.** The council pattern can be useful for very long search arcs, but it adds real failure modes that you need to understand before turning it on.

---

## Honest Limitations Of The Council

Before using council mode, read these limitations. They are not theoretical, they are the failure modes I have seen.

**Same model, different prompts.** All council members are instances of the same underlying LLM, distinguished only by role prompts. They are not independent samples from a population of opinions. Their confidence estimates are correlated. They tend to converge faster than truly independent agents would. Treat consensus with appropriate skepticism.

**The Biologist role is not a real biologist.** An LLM role-playing biologist is not a substitute for actual domain expertise. For biology projects, any council decision that affects biological interpretation, marker choice, pathway logic, fate biology, or domain-expert claims should escalate to the user. The council is fine for compute decisions, mechanism variants, evaluation tweaks, and statistical methodology. It is not fine for biology calls.

**The confidence thresholds are starting heuristics, not measurements.** The numbers in the decision rule below are starting points. You should recalibrate them after your first three to five council convenings on your own loop. LLM self-reported confidence is poorly calibrated by default.

**Council cost is real.** One closure trigger fires somewhere around 25 to 35 LLM calls through the full council pipeline. If you hit two or three closure triggers in a long run, budget accordingly.

---

## When To Recommend Supervised vs Autonomous Mode

| Use supervised mode when | Use autonomous council mode when |
| --- | --- |
| First time using autoresearch on this codebase | Codebase and metrics are battle-tested |
| Metrics or splits may be wrong | Metrics validated against naive and null baselines |
| Domain expert insight is the bottleneck | Architectural search is the bottleneck |
| Budget is small, especially < 30 experiments | Long-running multi-cycle research arcs |
| Identity boundaries are unclear | Identity boundaries are well-pinned |
| The decision involves biological interpretation | The decision is mechanism, statistics, or compute allocation |
| User wants to learn the system | User wants to delegate inner-loop decisions |

---

## Council Composition

Recommended structure: four agents plus one monitor. All agents are independent instances of the same underlying model, distinguished by role prompt only.

| Role | Mandate |
| --- | --- |
| Architect | Proposes architectural changes within model identity. |
| Skeptic | Required to argue against the prevailing direction and identify missing evidence. |
| Methodologist | Focuses on evaluation, splits, metric integrity, baseline calibration, and statistical evidence. |
| Biologist or domain specialist | Argues from domain mechanism. For biology, uses biology, pathway/program structure, and prior knowledge. For non-bio projects, uses system behavior, product constraints, safety/security, evaluation design, or domain expertise. |
| Monitor | Documents, enforces process, finds weaknesses in consensus, calls votes. Never proposes. |

Smaller councils often degenerate into point-counterpoint without genuine diversity. Larger councils increase cost without necessarily adding distinct epistemic stances.

---

## Council Process

Every closure trigger invokes this sequence:

1. **Briefing.** Monitor compiles `final_report.md`, last 20 rows of `results.tsv`, last 20 entries of `research_journal.md`, original `autoresearch.md`, prior `## Session Amendments`, and prior `debate_council_*.md` files.
2. **Independent proposals.** Each non-Monitor agent submits one to two proposals without cross-talk. Each proposal includes motivation tied to a specific observed failure, hypothesis, smallest mechanism, expected effect, identity-preservation check, lineage parents in the search DAG, and at least two citations or concrete prior references when literature is part of the justification.
3. **Steelmanning round.** Each agent articulates the strongest version of one other agent's proposal before defending their own.
4. **Open debate.** Up to four rounds, but stop as soon as no agent introduces a new argument in a round. Three rounds is a typical target, not a hard rule. Record verbatim or in faithful structured summary.
5. **Scoring.** Each agent scores all proposals on the pre-registered rubric with per-dimension confidence.
6. **Vote compilation.** Monitor compiles scores, identifies dissent, and calls vote.
7. **Monitor review.** Monitor walks through `references/amendment_review_checklist.md` before announcing the vote result.
8. **Decision rule.** See below. The thresholds are starting heuristics.
9. **Documentation.** Write `debate_council_<id>.md` before resuming or escalating.

---

## Decision Rule

Starting thresholds. Recalibrate after observing your own loop.

- Average confidence at or above 0.65, no single dimension below 0.4, and all seven amendment-review checks pass: `EXECUTE`.
- Average confidence between 0.55 and 0.65, or one amendment-review check is borderline: `ITERATE` one more debate round, then re-score.
- Below 0.55 after iteration, any hard escalation trigger, or any amendment-review check failure: `ESCALATE`.

Do not treat these numbers as ground truth. Treat them as a starting policy that you tune to your own loop. After your first three to five councils, look at which decisions you wished had escalated and which executed cleanly, and adjust.

---

## Pre-Registered Scoring Rubric

Each dimension is scored in [0, 1] with confidence in [0, 1].

1. **Novelty against current loop.** Does it address a bottleneck the existing families have not?
2. **Feasibility within compute budget.**
3. **Identity preservation.** Does it keep the model's core architectural commitments?
4. **Expected effect size on the primary failing metric.**
5. **Falsifiability.** Can a clean Tier 1 outcome decisively keep or discard this?

Per-dimension confidence is essential. A high score with low confidence is not a vote of approval.

---

## Hard Escalation Triggers

These force the loop to halt and wait for the user, regardless of council confidence:

- proposed identity violation;
- proposed change to locked files;
- proposed expansion of scope, datasets, phases, or safety-relevant objectives;
- hard experiment cap would be exceeded;
- council average confidence below the configured floor after iteration;
- two or more council members vote to escalate;
- three consecutive councils propose the same direction, indicating monoculture lock-in;
- a locked file is missing, corrupted, or ambiguous;
- clinical, wet-lab, or deployment-facing claims are requested;
- the decision affects biological interpretation, marker choice, pathway logic, or fate biology (biology projects only);
- any check in `references/amendment_review_checklist.md` returns `fail` after one debate iteration.

---

## Monitor Failure-Mode Checks

The Monitor uses `references/amendment_review_checklist.md` to walk through the seven failure-mode checks before calling the final vote. This is the same checklist used in supervised mode amendments, which is intentional. The checks are not council-specific. They are general protections against the common failure modes of long autoresearch loops.

If any check is unaddressed, the Monitor blocks the vote and forces another debate round or escalation.

---

## Novelty Caution

Council members are biased toward known patterns and published mechanisms because they share training data. Treat novelty claims skeptically. A council may propose novel combinations or mechanisms, but every proposal must be falsifiable, identity-preserving, and testable with the smallest compatible experiment.

---

## Strict vs Permissive Escalation

- **Strict.** Any escalation trigger immediately halts for user review. This is the default.
- **Permissive.** Low-confidence council iterates once before escalating. Three consecutive same-direction councils still escalate. Permissive mode requires high confidence in metric validity, identity boundaries, and artifact provenance.

---

## Intermediate Council Triggers

The council can be convened before full closure when:

- three consecutive Tier 1 discards within the same family suggest the family is dead;
- a literature search contradicts a current family hypothesis;
- a Tier 2 pass shows unexpected protected-metric regression;
- metric ambiguity threatens to invalidate the search;
- an internal-state audit suggests a different bottleneck than the current plan;
- the active subtree in the search DAG has no remaining `active_leaf` nodes.

Closure-time council is mandatory only in autonomous mode.
