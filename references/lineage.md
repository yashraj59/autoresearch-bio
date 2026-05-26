# Lineage And Search Tree

This reference defines the lightweight DAG layer that tracks how experiments relate to each other. Every experiment must record its parents and its branch type. This turns the flat `results.tsv` log into a directed acyclic graph where each node is an experiment and each edge points from a parent experiment to a child experiment.

The goal is to track structure that already exists in the search but was previously only captured in journal prose.

---

## When To Read This

Read this reference when:

- drafting an `autoresearch.md` for a project that involves combining components from multiple parent experiments;
- writing a journal entry for a new experiment;
- updating `results.tsv` after a Tier 1, Tier 2, or Tier 3 result;
- deciding whether to retire a family and prune its subtree;
- writing the closure section of a final report.

---

## What Is A Node

A node is one experiment row in `results.tsv`. Every node has:

- `experiment_num`;
- `parent_experiment_ids` (comma-separated list, can be empty for Step 0 baselines and for root experiments inside a new family);
- `branch_type` (one of `root`, `linear`, `fork`, `combine`, `replay`);
- `subtree_status` (one of `active_leaf`, `expanded`, `pruned`, `promoted`, `retired_subtree`);
- all the usual columns: tier reached, status, primary metric, protected metric summary, architectural change, description.

A node is identified by its `experiment_num`. Parents are identified by their `experiment_num` values.

---

## Branch Types

| Type | When to use | Parent count |
| --- | --- | --- |
| `root` | First experiment in a family, or a Step 0 baseline | 0 |
| `linear` | Direct extension of one parent. The most common case | 1 |
| `fork` | Two or more sibling variants from the same single parent, exploring different directions | 1 |
| `combine` | Combines mechanisms from two or more parents into one child | 2 or more |
| `replay` | Re-runs a previous experiment with a different seed, split, or evaluation. Same architecture as parent | 1 |

Notes:

- Tier 2 validation of a Tier 1 keep is a `replay`, not a `linear`, because the architecture did not change. Only the seed count and tier did.
- Tier 3 generalization of a Tier 2 pass is also a `replay`, for the same reason.
- A `combine` node must list all parents whose mechanisms were used. Listing only one parent and mentioning the others in prose breaks the lineage.
- A `fork` and a `linear` look similar but the semantic intent is different. `fork` means you intentionally created sibling variants at the same time. `linear` means you extended one experiment with one new mechanism. Use the labels honestly.

---

## Subtree Status

| Status | Meaning |
| --- | --- |
| `active_leaf` | Open for expansion. The agent may pick this node and propose a child |
| `expanded` | Already has at least one child. Not a leaf anymore |
| `pruned` | This node and all its descendants are out of the search. Do not extend |
| `promoted` | A Tier 3 winner. This becomes the new model or system of record |
| `retired_subtree` | This node and all descendants are retired together because the family or mechanism class was retired |

A node's subtree status updates over time. A node that was `active_leaf` becomes `expanded` once a child appears. A node that was `expanded` can become `retired_subtree` if its family is retired.

When you mark a node `pruned` or `retired_subtree`, every descendant inherits the same status by default. Do not extend pruned subtrees without an explicit amendment that documents why the prune is being reversed.

---

## Agent Scheduling Rule

When the agent picks the next experiment, it should follow this order:

1. If the family allocation plan explicitly requires a specific family next, follow the plan.
2. Otherwise, pick the `active_leaf` node with the strongest Tier 1 signal across all non-pruned subtrees, and propose a `linear` or `fork` child.
3. Periodically, the agent may propose a `combine` child that takes mechanisms from two or more `active_leaf` or `expanded` nodes.
4. The agent must never extend a `pruned` or `retired_subtree` node.

This is more opportunistic than strict family-by-family allocation but stays within the pre-registered families. The agent does not invent a new family without an amendment.

---

## Logging Rules

For every new experiment, the agent must:

1. State the parent experiment numbers before changing code.
2. State the branch type (`root`, `linear`, `fork`, `combine`, `replay`) before changing code.
3. Add the row to `results.tsv` with `parent_experiment_ids` and `branch_type` filled.
4. Update the parent's `subtree_status` from `active_leaf` to `expanded` if this is the first child.
5. Add a one-line lineage note in the journal entry: "Parents: 12, 23. Branch type: combine. Reason: stack gating from 12 with aux loss from 23."

If the agent cannot identify parents, the experiment is a `root`. Do not invent parents.

---

## Pruning Rules

Prune a subtree when:

- the parent family is retired;
- the parent shows a persistent cap-bound or mode-collapse pathology across two or more children;
- the parent's mechanism class has been ruled out by a metric investigation;
- the parent's identity was deprecated by an amendment.

When pruning, mark the parent and every descendant `pruned` or `retired_subtree`. Add one entry to `family_allocation.md` that records why the subtree was pruned.

Do not prune a Tier 3 winner. A Tier 3 winner is `promoted`, not pruned, even if it is no longer the active model of record.

---

## Visualization

A DAG can be rendered as a tree or graph using the existing `results.tsv`. A small helper script can produce a `lineage.dot` or `lineage.svg` from `results.tsv` columns. This is optional.

When closing the loop, the final report should include or reference a search-tree visualization showing:

- which families were explored deeply versus one-and-done;
- where the Tier 3 win came from;
- which subtrees were pruned and why;
- which subtrees were `replay` chains versus genuinely new mechanism chains.

---

## What This Replaces

The lineage layer replaces three pieces of the older flat-log approach:

- "Which experiments did this build on?" used to live only in journal prose. Now it is structured data.
- "Should we retire this whole branch?" used to be a family-level decision. Now it is also a subtree-level operation.
- "What was the actual path to this Tier 3 win?" used to require reading the journal sequentially. Now it is a parent-chain walk.

The cost is one column in `results.tsv` (`parent_experiment_ids`), one more column (`branch_type`), one more column (`subtree_status`), and one extra rule the agent must follow per experiment. That is the full overhead.

---

## What This Does Not Replace

The lineage layer is not a substitute for:

- `research_journal.md`. Narrative prose is still the place where the agent explains why a child was proposed.
- `architectural_changes_log.md`. Code-level details still live there.
- `family_allocation.md`. Family-level allocation still governs which areas of the search get compute.
- The model of record. Promotion still requires a Tier 3 pass, regardless of lineage structure.

The lineage layer is a structural overlay on top of the existing protocol, not a replacement for it.
