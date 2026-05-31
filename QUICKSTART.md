# Quickstart

How to get an `autoresearch.md` for your project and run it. Five minutes to read.

**Mental model:** you don't hand-write the `autoresearch.md`. A strong chat model writes it for you (the **planner**), you review it, then a coding agent runs it (the **executor**). You bring the context and decide how much of the design you want to control; the skill brings the discipline.

---

## Step 0 — put the skill in front of a chat model

Two ways.

**Installed as a skill (cleanest).** Package once and upload:

```bash
git clone https://github.com/yashraj59/autoresearch-bio.git
cd autoresearch-bio
git archive --format=zip --prefix=autoresearch-bio/ HEAD -o ../autoresearch-bio-skill.zip
```

Upload `autoresearch-bio-skill.zip` to ChatGPT (Skills) or Claude (Customize → Skills). Then you can say "use autoresearch-bio to plan…" and the model loads the modules itself. Full upload steps are in `README.md`.

**Not installed (works anywhere).** Clone the repo where the model can read it (a Claude Code / Codex session, or paste the key module text into a bare chat window) and point the planner at the cloned paths.

---

## Step 1 — plan it

Open a session with a strong reasoning model (the planner). Paste this and fill the brackets:

```text
Use autoresearch-bio to PLAN (not run) an autoresearch.md. You're the planner; a coding
agent will execute it. Read the skill's modules and follow them. If the skill isn't
installed, clone github.com/yashraj59/autoresearch-bio and read the modules from there.

Context:
<your repo layout, the model of record + its baseline numbers, prior runs/results,
 datasets and their splits, known failure modes, compute budget, locked files, safety boundary>

Design choice (pick one):
  - "Here are the families I want tested: <list>. Formalize them, tag origin=user_fixed."
  - "Here's my problem, design the families yourself, tag origin=planner_proposed."
  - "Use these families <list> and propose 1-2 more." (hybrid)
Set family_set=<fixed|open> and autonomy=<supervised|autonomous>.

Design the Step 0 baselines, four-role split, tiers, metrics, lineage, and stop conditions
yourself — don't defer them to the executor. Deliver the autoresearch.md as one paste-ready
block, plus the launch message separately. Ask up to 5 questions if needed; never invent
baseline numbers.
```

The **design choice** block is the part that matters most. You decide how much you hand over:

- You have a thesis and the families → give them; the planner just formalizes them.
- You only have a problem → let the planner propose everything. This is a primary mode, not a fallback.
- Somewhere between → hybrid.

In every case the planner produces a *complete* design and the discipline; *what* the families are is your call. The quality of proposed families scales with the context you give — a one-line problem yields generic families, so paste the repo, the prior results, and the failure modes.

`family_set: fixed` means the loop runs exactly your families and never adds one on its own. `open` lets the planner (or an autonomous council) propose more through the amendment path. See `references/core_protocol.md §5`.

---

## Step 2 — review

The planner gives you two things:

1. the **`autoresearch.md`** as one code block (families, tiers, metrics, baselines, splits, stop conditions);
2. **separately**, a launch message to paste into the agent.

Read the families and tiers especially — that is where a weak plan hides, and the whole point of the split is that you see the full design before any compute runs. Edit anything, or tell the planner to change it ("make Family 3 a grid sweep", "drop the CVAE family"). If the planner was missing something essential it will have asked up to five questions first instead of guessing.

---

## Step 3 — save it and hand it to the executor

```bash
cp autoresearch.md /path/to/your-run-repo/
```

Paste the planner's **launch message** into your coding agent (Codex, Claude Code, Cursor, Aider). The agent reads the `autoresearch.md` and the skill modules, runs the leakage pre-flight and Step 0 baselines first, then begins Tier 1. It follows the plan as written; if it thinks the plan is wrong, that is a stop-and-amend event, not a quiet rewrite.

---

## Step 4 — (optional) sanity-check

```bash
# checks the prompt is complete (families fixed, family_set declared, no deferral)
# and the run directory as it fills up
python autoresearch-bio/scripts/validate_autoresearch_artifacts.py /path/to/your-run-repo/outputs
```

A complete plan passes whether you or the planner designed it. A plan that punts the families to runtime fails.

---

## Single-agent shortcut

For a small or obvious loop (low-compute mode, one or two families), one capable agent can both plan and run. Skip the separate planner session: open a coding agent, say "use autoresearch-bio to draft and then run an autoresearch.md for …", and review the file before you let it start Tier 1. The discipline is identical; only who-writes-the-plan changes.

---

## What you get

A `autoresearch.md` follows `assets/autoresearch_template.md` and contains: model of record, datasets and four-role split, Step 0 baseline plan, primary/secondary/protected/catastrophic-fail metrics, the families (with `origin` tags), the tiered gates, lineage rules, documentation files, retention rules, stop conditions, and the safety boundary. The launch message is separate chat text — never inside the file.

## Common mistakes

- **Giving the planner the task but not the context.** "Improve my model" with no repo, no prior results, no baselines → generic families. Paste the real context.
- **Letting the executor redesign.** The executor runs the plan; if it wants to change the families that is a stop-and-amend, in supervised mode authored by you. Do not let it quietly rewrite the design.
- **Skipping the review.** The point of the planner/executor split is the reviewable design before compute. Read the families and tiers.
- **Treating "make it better" as a plan.** No metrics, no stop conditions, no protected behavior is out of scope for this skill — that is the unrestricted prompt the discipline exists to prevent.

See `references/planner_workflow.md` for the full role split and `references/core_protocol.md` for the protocol it enforces.
