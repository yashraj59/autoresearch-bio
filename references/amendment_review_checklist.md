# Amendment Review Checklist

Use this checklist before writing any session amendment, regardless of whether the amendment comes from a supervised human review or from a Debate Council decision in autonomous mode. The checks are the same. The goal is to catch the common failure modes of long autoresearch loops before they get encoded into the next plan.

These checks were originally Monitor-only inside the Debate Council. They are useful in supervised mode too, which is why they live in their own reference.

---

## When To Use This

Use this checklist:

- before writing a `Session Amendment` block in supervised mode;
- before the Monitor calls a vote in Debate Council mode;
- before reopening a retired family;
- before promoting a candidate that has been involved in many tries;
- before launching a new family that looks similar to a retired one.

---

## The Eight Checks

### 1. Monoculture lock-in

Is the proposed next mechanism a near-variant of one that already failed in this run? If yes, what specifically is different that should make the result different this time? If the answer is "we will tune it harder," that is not a real difference. Reject or escalate.

### 2. Identity drift

Does the proposal relax any `Keep` or `Cannot Modify` constraint? Does it change the evaluator, the data split, the gene or label set, the API contract, the regression suite, or the production path? If yes, escalate. Identity drift is not an amendment, it is a scope change that needs explicit user approval.

### 3. Metric tunnel vision

Does the proposal optimize one headline metric while ignoring or weakening protected metrics? Check whether the proposal mentions the protected gates by name and by current numerical status. If protected metrics are not mentioned, the proposal is incomplete. Send it back for revision.

### 4. Publication recency bias

Is the justification only "a new paper showed X"? A new paper is not a mechanism. It is an idea. The amendment must explain the mechanism in terms of the failure mode it addresses, not in terms of the paper that proposed it. Cite the paper, but argue from the mechanism.

### 5. Complexity creep

Does the proposal add multiple new mechanisms at once when one would suffice? Each added mechanism multiplies the diagnostic surface and makes attribution harder. If the proposal stacks two or three new mechanisms, ask which single one carries the hypothesis. If none of them does, the proposal is not testable.

### 6. Cost of being wrong

What fraction of the remaining experiment budget is consumed if this proposal fails? If the answer is more than 30 percent, the proposal is too expensive for the current budget and should either be downsized to a smaller test or deferred to the next phase.

### 7. Safety boundary

For biological projects, does the proposal drift toward wet-lab, clinical, or deployment-facing biological claims? Does it add a marker or pathway that requires human domain review? If yes, escalate regardless of confidence.

For non-bio projects, does the proposal weaken a safety, security, privacy, compliance, or deployment guardrail to improve a metric? If yes, escalate regardless of confidence.

### 8. Closure-action enforceability

If this amendment specifies any action that must execute at closure (a locked read, a final inference, a confirmation experiment, a registration step), is that action expressed as a concrete, machine-checkable procedure that will be enumerated as the first step of the closure procedure per `core_protocol.md §16`? Has a `CLOSURE_FALLBACK_READ_PENDING` (or equivalent) label been registered so the closure audit trail tracks whether the action executed? An amendment that promises a closure-time action without a registered pending label is incomplete; the action will be silently dropped when the loop closes. Send it back for revision.

---

## How To Use This In Supervised Mode

1. Draft the amendment as usual using `assets/session_amendment_template.md`.
2. Walk through the eight checks below the amendment.
3. For each check, write `pass`, `fail`, or `n/a` and a one-line reason.
4. If any check is `fail`, revise the amendment before pasting it into `autoresearch.md`.
5. Keep the check log in `research_journal.md` so future amendments can spot patterns.

---

## How To Use This In Council Mode

1. Each non-Monitor agent makes a proposal.
2. After scoring, the Monitor walks through the eight checks before calling the vote.
3. Any `fail` blocks the vote and forces another debate round or escalation.
4. The check log is attached to the `debate_council_<id>.md` document.

---

## What This Does Not Replace

This checklist is a process check. It does not replace:

- the protected gates on metrics;
- the pre-registered Tier 3 promotion criteria;
- the stop conditions in `autoresearch.md`;
- the lineage rules in `references/lineage.md`.

It is a final review before an amendment is encoded into the next plan. If a check fails, the right response is to fix the amendment, not to override the check.
