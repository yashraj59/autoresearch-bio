# BASELINE_REGISTRY.md Template

```markdown
# Baseline Registry

## Model Or System Of Record

- Checkpoint/system/release:
- Commit:
- Config:
- Date:
- Why active:

## Baseline Table

| Dataset/benchmark/suite | Split/version | Role | Seed/scenario/slice list | Metric | Direction | Mean | Std | Per-seed values | Source file | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Metric Directionality

| Metric | Direction | Interpretation | Protected? | Catastrophic fail threshold |
| --- | --- | --- | --- | --- |

## Provenance Notes

- Raw per-seed metric files:
- Summary files:
- Evaluation script commit:
- Data split / benchmark / regression-suite file:
- Preprocessing config:

## Ambiguities

| Issue | Affected metric/dataset | Resolution | Remaining caveat |
| --- | --- | --- | --- |
```
