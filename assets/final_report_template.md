# Final Report Template

```markdown
# Final Report: <Project / Run>

## Closure Trigger

<Which stop condition fired and when.>

## Model/System Of Record At Closure

- Checkpoint:
- Commit/config:
- Baseline registry:
- Promotion status:

## Experiment Summary

| Count | Value |
| --- | --- |
| Total experiments | `<n>` |
| Tier 1 keeps | `<n>` |
| Tier 2 passes | `<n>` |
| Tier 3 passes | `<n>` |
| Useful failures | `<n>` |
| Families retired | `<n>` |
| Subtrees pruned | `<n>` |

## Family-By-Family Findings

| Family | Experiments | Best result | Status | Lesson |
| --- | --- | --- | --- | --- |

## Search Tree Summary

Walk the lineage DAG and summarize:

- Roots (Step 0 baselines and family root experiments).
- Deeply explored subtrees: which roots produced the most descendants and why.
- One-and-done subtrees: which roots had no children and why.
- Pruned subtrees: which subtrees were pruned and which prune reason applied.
- Combination experiments: which `combine` nodes existed and what they merged.
- Path to the promoted node: if a Tier 3 winner was promoted, list its parent chain from root to promoted node.

Include or reference a search-tree visualization if available.

## Strongest Wins

<Only include candidates with evidence and caveats.>

## Strongest Useful Failures

<Failures that taught something important about metrics, mechanisms, representation, biology/domain behavior, software behavior, or data.>

## Protected No-Regression Status

| Protected metric | Baseline | Best candidate | Gate | Status |
| --- | --- | --- | --- | --- |

## Statistical Evidence

<Seed variance, effect sizes, confidence intervals when available, multiple-comparison caveats.>

## Biological Evidence And Caveats

<For biology: directionality, marker/program behavior, population structure, pathway coherence, generalization, safety/provenance notes. For non-bio: protected slices, correctness, latency, memory, safety/security, robustness, held-out benchmarks, compatibility, and provenance notes.>

## Metric / Evaluation Caveats

<Metric ambiguity, null baseline concerns, technical duplicate headroom, mode-collapse risks.>

## Artifact Retention Summary

- Retained model-of-record checkpoint:
- Retained Tier 3 winner checkpoint:
- Audit-relevant near-misses:
- Deleted checkpoints:
- Retained metrics/logs/predictions:

## Recommended Next Phase

One of:

- self-supervised or broader-data pretraining;
- metric/evaluation reform;
- dataset expansion or better labels;
- internal-state diagnostic audit;
- representation analysis;
- finalization/reporting;
- human expert review;
- new model class requiring identity amendment.

## Loop Status

The autonomous loop is stopped. Do not launch another experiment without an explicit amendment or Debate Council execution decision if autonomous mode is enabled.
```
