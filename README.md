# autoresearch-bio

A discipline protocol for running autonomous ML research with coding agents — **any coding agent**. The skill's output is a paste-ready Markdown prompt that drives Claude Code, ChatGPT (Codex / GPT agent harnesses), Cursor, Aider, custom SDK loops, or you-yourself-at-a-keyboard. There are no vendor-specific tool calls in the prompts it produces; portability is by design.

It is **bio-first** (with extra rules for biology and single-cell modeling) but **domain-general** — the same control system applies to non-bio ML, software engineering, agent benchmarking, and infrastructure experiments.

This came from repeated autonomous experiments on bio-specific ML models where I learned the hard way that AI coding agents need strict research discipline. Without it, the agents drift toward mechanisms that improve broad metrics while breaking protected behavior, saturating contribution caps, collapsing diversity, or overfitting to one dataset.

This repo is the protocol I use to make autoresearch less random, less reward-hacking, and more useful as actual science.

## Case studies

- **[MoFNet POC](https://github.com/yashraj59/MoFNet)** — applied to a multi-omic BRCA-subtype model. The first run produced a candidate that scored +0.024 accuracy over baseline; a post-hoc audit found the loop had used the locked test split as a selection oracle across 123 trials. The audit, the leakage-corrected re-run, and the resulting patch to this skill (the `§3.5` pre-flight check and the `leakage_guard` column) are documented in the MoFNet repo and in this changelog.

## What is in this repo

- `SKILL.md` is the short operational skill the agent reads first. It has the trigger boundaries, the golden path, the output contracts, and the final checklist.
- `references/` has the deep protocol broken into focused files. Read only what you need for the artifact you are making.
- `assets/` has paste-ready templates for the autoresearch.md prompt, amendments, decision memos, journal entries, baseline registries, and results.tsv schema.
- `evals/` has trigger prompts and a process checklist so you can spot-check whether the skill is doing its job.
- `scripts/` has two small validation scripts. One checks the skill repo structure. The other checks a generated autoresearch run directory.
- `autoresearch_demo/` has a synthetic MoFNet-shaped reference run. It is useful for humans and CI, but excluded from the packaged skill archive.

## How to use

New here? **[`QUICKSTART.md`](QUICKSTART.md)** is the five-minute path: how to get an `autoresearch.md` for your project (a chat model plans it, you review, a coding agent runs it) and the common mistakes to avoid.

The longer version:

1. Read `SKILL.md` to understand the protocol.
2. Pick the closest example, or use the template skeleton in `assets/autoresearch_template.md`.
3. Fill in your model of record, datasets, metrics, families, stop conditions, and lineage rules.
4. Point your coding agent (Claude Code, Codex, or similar) at the prompt.
5. Watch the agent run experiments while protecting your baseline.

### Who writes the plan vs who runs it

Writing the `autoresearch.md` and running it are two different jobs, usually best done by two different models: a strong reasoning chat model is the better **planner** (it reads your repo and prior runs and designs the families, tiers, metrics, baselines, and stop conditions), and a coding agent is the better **executor** (it runs the loop against your filesystem). You get a complete, reviewable design before any compute is spent, and the executor is held to a plan it cannot quietly weaken.

The design is yours. You can hand the planner the exact families and metrics you want tested, hand it only a problem and let it design everything, or do a hybrid — all three are first-class. The planner must produce a *complete* design (it can't punt the families to the executor), but *what* the families and metrics are is your call; the skill enforces the discipline (protected baseline, Step 0, four-role split, leakage pre-flight, tiered gates, lineage, honest labels, stop conditions), not the science. If you fix the family set, the loop won't add families on its own.

See `references/planner_workflow.md` for the role split, the three input modes, the `family_set` switches, and a paste-ready planner prompt.

The protocol has three load-bearing elements:

- A protected model or system of record that never silently drifts.
- Tiered evaluation gates that allocate compute proportional to candidate strength.
- Pre-registered keep and discard criteria that prevent retroactive rationalization.

Everything else in the protocol exists to make these three work.

## Install as a skill

This repository is an Agent Skill. The skill folder is the repo root: it contains `SKILL.md`, plus supporting `references/`, `assets/`, and `scripts/`.

Package it first:

```bash
git clone https://github.com/yashraj59/autoresearch-bio.git
cd autoresearch-bio
git archive --format=zip --prefix=autoresearch-bio/ HEAD -o ../autoresearch-bio-skill.zip
```

The ZIP should contain a top-level `autoresearch-bio/` folder, with `autoresearch-bio/SKILL.md` inside it. Do not zip the files directly at the archive root.
The repository's `.gitattributes` keeps GitHub workflow files and the synthetic demo out of the skill archive.

### ChatGPT

ChatGPT Skills are available on supported workspace plans. In ChatGPT:

1. Select your profile icon.
2. Open **Skills**.
3. Select **New skill**.
4. Select **Upload from your computer**.
5. Upload `autoresearch-bio-skill.zip`.
6. Install or enable the skill.

Then ask for it naturally:

```text
Use autoresearch-bio to draft an autoresearch.md for a bounded ML experiment.
```

Workspace admins may need to enable skill creation, installation, or publishing before members can install and share skills. See OpenAI's Skills documentation for current plan and admin details: https://help.openai.com/en/articles/20001066-skills-in-chatgpt

### Claude

Claude Skills require code execution and file creation to be enabled. In Claude:

1. Enable code execution and file creation in **Settings > Capabilities**, or ask an organization owner to enable it in **Organization settings > Skills**.
2. Open **Customize > Skills**.
3. Click the **+** button, then select **Create skill**.
4. Select **Upload a skill**.
5. Upload `autoresearch-bio-skill.zip`.
6. Toggle the skill on.

Then ask for it naturally:

```text
Use autoresearch-bio to audit this autonomous experiment plan.
```

Claude can also use skills shared or provisioned by a Team or Enterprise organization. See Anthropic's Skills documentation for current plan, sharing, and upload details: https://support.claude.com/en/articles/12512180-use-skills-in-claude

For coding agents that do not support skill upload yet, clone this repo and point the agent at `SKILL.md` directly.

## What this is not

This is not a general brainstorming template. It is not random exploration. It is not "let the agent figure it out." It is a discipline system for letting an agent run experiments without silently drifting away from the scientific question.

## Bio-first, but not bio-only

I built this for biological ML, and the biology layer is the most opinionated part. But the same control system applies to non-bio ML, software engineering, agent benchmarks, performance loops, and developer tooling. For non-bio projects, you keep the same structure and swap the biology no-regression checks for whatever your project must not break. Things like correctness, latency, memory, robustness, safety, security, policy compliance, regression tests, and held-out benchmarks. The biology safety boundary becomes whatever your project's safety boundary is.

Read `references/domain_adaptation.md` if you are using this outside biology.

## Lineage tracking

Every experiment records its parent IDs and a branch type. A linear extension has one parent, a fork creates sibling variants from one parent, and a combine merges mechanisms from two or more parents. The flat `results.tsv` log hides this structure in combinatorial search where you stack components and lose track of which child came from which parent. If your search is mostly linear extensions, the layer is light overhead. If your search combines mechanisms across families, it pays for itself the first time you reconstruct the path to a Tier 3 win or prune a whole subtree at once. See `references/lineage.md` for the rules and the full list of branch types.

## Debate Council

The default is supervised mode: when a stop condition fires the loop halts and waits for a human. There is also an opt-in autonomous mode called the Debate Council, useful for long search arcs where you cannot stay in the inner loop yourself. The council runs five role-prompted agents (Architect, Skeptic, Methodologist, Biologist or domain specialist, plus a non-voting Monitor) that propose, steelman, debate, score, and vote on the next amendment that continues, escalates, or closes the loop. By default all five are instances of the same underlying LLM with different role prompts, so their confidence is correlated and consensus is not independent evidence. The council also supports an opt-in multi-vendor configuration where you assign different roles to different model vendors (e.g. Architect on Claude, Skeptic on GPT, Methodologist on Gemini) when you have multiple API keys; this breaks the correlation and is recommended for closure-critical decisions. The council is a heuristic, not a measurement, and is not a substitute for domain expertise, especially for biology decisions where the Biologist role must escalate to a real human. See `references/debate_council.md` and `references/amendment_review_checklist.md`.

## Acknowledgments

This work was inspired by Andrej Karpathy's autoresearch repo (https://github.com/karpathy/autoresearch). His simple but powerful idea of giving an agent a small training setup and letting it experiment overnight is what got me thinking about the discipline layer that makes this safer for higher-stakes biology research.

## License

MIT License. Use, modify, and redistribute freely. Attribution appreciated but not required.
