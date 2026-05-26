# Session Amendment Template

Paste under `## Session Amendments` in the active `autoresearch.md`.

```markdown
## Session Amendment <YYYY-MM-DD or N>: <Title>

### Status

Active model/system of record remains: `<checkpoint/commit/config/release>`.

No Tier 1 or Tier 2 result may rebase the model/system of record. Only a Tier 3 pass that satisfies all pre-registered gates may supersede it.

### Reason For Amendment

<Specific evidence that makes the current plan outdated: repeated failure, metric ambiguity, protected regression, cap-bound mechanism, new literature, or closure trigger.>

### Evidence Summary

- Experiments reviewed: `<range/list>`
- Key result pattern: `<summary>`
- Protected metrics: `<pass/fail/caveats>`
- Metric/provenance ambiguity: `<none/describe>`
- Remaining budget: `<count>`

### Updated Thesis

<New or narrowed hypothesis based on evidence.>

### Family Status Updates

| Family | Status | Reason | Allowed next action |
| --- | --- | --- | --- |
| `<family>` | `<active/cooldown/retired/reopened>` | `<evidence>` | `<exact action>` |

### Immediate Next Action

Run exactly this next step:

1. `<experiment/audit/investigation>`
2. Required files to read: `<list>`
3. Required diagnostics: `<list>`
4. Required output artifacts: `<list>`

### Updated Gates

- Primary gate: `<threshold>`
- Protected gate: `<threshold>`
- Catastrophic fail: `<threshold>`
- Statistical rule: `<minimum meaningful improvement / variance rule>`

### Decision Tree

- If `<outcome A>`, label `<decision_label>` and `<next action>`.
- If `<outcome B>`, label `<decision_label>` and `<next action>`.
- If `<outcome C>`, label `<decision_label>` and stop.

### Do-Not-Run List

Do not run:

- `<retired mechanism>`
- `<identity-violating change>`
- `<locked-file change>`
- `<metric-only loophole>`

### Stop / Review Trigger

Stop and write `final_report.md` if:

- `<trigger>`
- `<trigger>`

### Required Report

After this amendment's next action, update `research_journal.md`, `results.tsv`, `family_allocation.md`, and write `<specific report>`.
```
