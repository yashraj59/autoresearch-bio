# autoresearch-bio

A discipline protocol for running autonomous ML research with coding agents, with extra rules for biology and single-cell modeling.

This came from running 80+ autonomous experiments on a bio-specific ML model where I learned the hard way that AI coding agents need strict research discipline. Without it, the agents drift toward mechanisms that improve broad metrics while breaking protected behavior, saturating contribution caps, collapsing diversity, or overfitting to one dataset.

This repo is the protocol I use to make autoresearch less random, less reward-hacking, and more useful as actual science.

## What is in this repo

- `SKILL.md` is the short operational skill the agent reads first. It has the trigger boundaries, the golden path, the output contracts, and the final checklist.
- `references/` has the deep protocol broken into focused files. Read only what you need for the artifact you are making.
- `assets/` has paste-ready templates for the autoresearch.md prompt, amendments, decision memos, journal entries, baseline registries, and results.tsv schema.
- `evals/` has trigger prompts and a process checklist so you can spot-check whether the skill is doing its job.
- `scripts/` has two small validation scripts. One checks the skill repo structure. The other checks a generated autoresearch run directory.

## How to use

1. Read `SKILL.md` to understand the protocol.
2. Pick the closest example, or use the template skeleton in `assets/autoresearch_template.md`.
3. Fill in your model of record, datasets, metrics, families, stop conditions, and lineage rules.
4. Point your coding agent (Claude Code, Codex, or similar) at the prompt.
5. Watch the agent run experiments while protecting your baseline.

The protocol has three load-bearing elements:

- A protected model or system of record that never silently drifts.
- Tiered evaluation gates that allocate compute proportional to candidate strength.
- Pre-registered keep and discard criteria that prevent retroactive rationalization.

Everything else in the protocol exists to make these three work.

## What this is not

This is not a general brainstorming template. It is not random exploration. It is not "let the agent figure it out." It is a discipline system for letting an agent run experiments without silently drifting away from the scientific question.

## Bio-first, but not bio-only

I built this for biological ML, and the biology layer is the most opinionated part. But the same control system applies to non-bio ML, software engineering, agent benchmarks, performance loops, and developer tooling. For non-bio projects, you keep the same structure and swap the biology no-regression checks for whatever your project must not break. Things like correctness, latency, memory, robustness, safety, security, policy compliance, regression tests, and held-out benchmarks. The biology safety boundary becomes whatever your project's safety boundary is.

Read `references/domain_adaptation.md` if you are using this outside biology.

## Lineage tracking

This revision adds a lightweight DAG layer. Every experiment now records its parent experiments and whether it is a linear extension, a fork, or a combination of two or more parents. The flat `results.tsv` log was hiding real structure in the search, especially for combinatorial architectures where you are stacking many components and want to know which child came from which parent. Read `references/lineage.md` for the rules.

If your workflow is mostly linear extensions, the lineage layer adds very little overhead. If your workflow is combinatorial, it pays for itself the first time you want to reconstruct the actual chain that led to a Tier 3 win or prune a whole subtree at once.

## Debate Council is optional

This revision keeps the Debate Council mode as an opt-in option for fully autonomous runs, but the default is supervised mode. When a stop condition fires, the loop halts and waits for a human, unless you have explicitly enabled autonomous mode.

I kept the council because it can be useful for very long search arcs where the human is not in the inner loop. But I made it clearer that the council is not a substitute for domain expertise, especially for biology decisions, and the confidence thresholds inside the council are starting heuristics, not measurements. Read `references/debate_council.md` and `references/amendment_review_checklist.md` for the details.

## Acknowledgments

This work was inspired by Andrej Karpathy's autoresearch repo (https://github.com/karpathy/autoresearch). His simple but powerful idea of giving an agent a small training setup and letting it experiment overnight is what got me thinking about the discipline layer that makes this safer for higher-stakes biology research.

## License

MIT License. Use, modify, and redistribute freely. Attribution appreciated but not required.
