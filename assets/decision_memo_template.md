# Decision Memo Template

```markdown
# Autoresearch Decision Memo: <Project / Run>

## Recommendation

Decision: `<continue | amend | metric-audit | close | escalate>`

## Evidence Reviewed

- Active model/system of record: `<checkpoint/commit/config/release>`
- Experiments reviewed: `<range/list>`
- Current best candidate: `<candidate or none>`
- Tier reached: `<Tier 1/2/3>`
- Protected metrics: `<pass/fail/caveats>`
- Baseline/provenance status: `<clean/ambiguous>`

## Key Findings

1. `<finding tied to metric/result>`
2. `<finding tied to mechanism/diagnostic>`
3. `<finding tied to protected biology/domain behavior/statistics>`

## Risks

- `<risk: metric loophole / high variance / cap-bound / identity drift / biological or domain regression>`

## What Must Not Be Done Next

- `<e.g., do not promote Tier 2 near-miss>`
- `<e.g., do not keep running retired family>`
- `<e.g., do not change locked evaluator>`

## Required Next Artifact

- `<session amendment | metric investigation prompt | final report | Debate Council document>`

## Rationale

<Concise explanation connecting evidence to decision.>
```
