# Debate Council Template

For any decision invoking five or more council calls, write this as `outputs/council_traces/debate_council_<node_id>.md` (see `references/debate_council.md "Trace Preservation Requirement"`). Each role's position statement is full, not summarized; the per-role minimum is 100 words. The corresponding `research_journal.md` entry references this file by path and includes only the decision plus the one-sentence dispositive argument.

```markdown
# Debate Council <node_id>

**Trigger**: <stop condition or decision point that opened this council>
**Active model/system of record**: <name and metrics>
**Remaining experiment budget**: <count>
**Prior councils**: <list of ids>
**Mode**: <strict | permissive>
**council_diversity**: <single_vendor | the per-role vendor list>

## Briefing Summary

<one paragraph from the Monitor>

## Independent Proposals

Each non-Monitor role: full position statement (100+ words), then its self-identified weakness, then its steelman of the strongest opposing argument.

### Architect

- **Position**: <full statement>
- **self_identified_weakness**: <concrete failure mode tied to this proposal, not boilerplate>
- **Steelman of strongest opposing argument**: <...>

### Skeptic

- **Position**: <full statement; must engage the builder's specific claim being challenged>
- **self_identified_weakness**: <...>
- **Steelman of strongest opposing argument**: <...>

### Methodologist

- **Position**: <full statement>
- **self_identified_weakness**: <...>
- **Steelman of strongest opposing argument**: <...>

### Biologist or domain specialist

- **Position**: <full statement>
- **self_identified_weakness**: <...>
- **Steelman of strongest opposing argument**: <...>

## Debate Rounds

### Round 1
### Round 2
### Round 3

## Monitor Failure-Mode Checks

| Check | Status | Notes |
| --- | --- | --- |
| Monoculture lock-in | `<pass/fail>` |  |
| Identity drift | `<pass/fail>` |  |
| Metric tunnel vision | `<pass/fail>` |  |
| Publication recency bias | `<pass/fail>` |  |
| Complexity creep | `<pass/fail>` |  |
| Cost of being wrong | `<pass/fail>` |  |
| Safety boundary | `<pass/fail>` |  |
| Closure-action enforceability | `<pass/fail/n/a>` |  |

## Scoring Table

| Proposal | Architect | Skeptic | Methodologist | Biologist | Avg | Avg conf | Lowest dimension |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Vote Result

- Top proposal:
- Average confidence:
- Dissent register:

## Decision

- [ ] EXECUTE
- [ ] ITERATE
- [ ] ESCALATE

**Dispositive argument** (the one the Monitor cited; the methodologist's call must reference the strongest skeptic argument, not just "weighed concerns"): <one sentence>

## Amendment If EXECUTE

<paste-ready Session Amendment block>

## Escalation Reason If ESCALATE

<specific hard trigger>
```
