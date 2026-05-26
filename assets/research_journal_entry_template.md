# Research Journal Entry Template

```markdown
## Experiment <N>: <Title>

**Parents**: <comma-separated parent experiment_num list, or "none" for root>

**Branch type**: <root | linear | fork | combine | replay>

**Lineage note**: <one line: why these parents and why this branch type. Example: "Parents: 12, 23. Branch type: combine. Reason: stack the gating mechanism from exp 12 with the auxiliary loss from exp 23.">

**Hypothesis**: <failure mode + why mechanism might help>

**Family**: <family name and allocation count>

**Implementation**: <specific code change, commit, config, parameter count>

**Initialization / identity preservation**: <how baseline behavior is preserved at init; smoke-test result>

**Tier result**: <Tier 1/2/3 result with metrics>

**Statistics**: <per-seed values, mean/std, effect size, noise comparison>

**Diagnostics**: <contribution ratios, cap-hit fraction, variance, marker/program effects, slice behavior, latency, memory, safety/correctness, etc.>

**Protected biology/domain behavior**: <directionality, marker/program, population, pathway, held-out validator status, or non-bio protected gates such as correctness/safety/latency/memory/slices>

**Decision**: <exact decision label>

**Subtree status update**: <how this experiment changes the lineage DAG. Example: "Parent exp 12 changed from active_leaf to expanded. This node starts as active_leaf.">

**Learning**: <what this teaches; what to retire/cool down/reopen>

**Artifact retention**: <checkpoint deleted/retained/audit-relevant>
```
