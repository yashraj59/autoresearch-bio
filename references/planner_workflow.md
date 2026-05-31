# Planner / Executor Workflow

This reference describes the **two-role workflow** for producing and running an `autoresearch.md`: a strong **planner** model authors the plan, and a separate **executor** agent runs it. The skill has always supported this implicitly; this module makes it an explicit, recommended path and tells you how to prompt the planner.

## Why split planning from execution

The `autoresearch.md` is a research design document. Writing it well requires the things frontier chat models are currently best at: reading a messy repo and a pile of prior results, reasoning about what is actually unproven, designing families and falsifiable gates, anticipating failure modes, and choosing honest baselines. The agent harnesses are optimized for a different thing: executing a well-specified plan against a filesystem, running code, and iterating on tool output. They are competent planners, but a top reasoning chat model in a reasoning-heavy session is usually the stronger *planner*, and the agent is the stronger *executor*.

So the recommended division of labor is:

- **Planner** (chat model, no execution): reads context, **defines the families, tiers, metrics, baselines, lineage rules, stop conditions, and safety boundary**, and emits the `autoresearch.md` as text. The planner does not run anything.
- **Executor** (coding agent): receives the finished `autoresearch.md`, reads the referenced skill modules, and runs the loop under the discipline the planner specified.

This is the same separation a careful human PI/engineer pairing uses: the design is fixed and reviewable before any compute is spent, and the executor is held to a plan it did not get to weaken.

Capability, not a specific vendor. The planner wants strong reasoning and a large enough context window to digest prior runs; current frontier chat models (Claude Opus, ChatGPT Pro / GPT-class, Gemini Pro) are examples, not requirements. The executor wants a solid coding agent (Codex, Claude Code, Cursor, Aider) again as examples. The skill is vendor-agnostic; pick whatever is strongest at each role when you run it.

The planner role does **not** relax any invariant. The planner still owes a protected model of record, Step 0 baselines, the four-role split and leakage pre-flight (`core_protocol.md §3.5`), tiered gates, exact decision labels (`decision_labels.md`), lineage rules (`lineage.md`), the statistical floor (`statistical_promotion.md`), and the safety boundary. The planner *designs* these; it does not get to omit them.

## Who designs the families: three first-class modes

The skill governs the method, not the science. *What* the families, tiers, and metrics are is the user's call; the discipline around them is the skill's. There are three ways the design gets written, all fully supported (see `core_protocol.md §5` for the family-set switches):

- **You design it.** You hand the planner the families (and possibly tiers and metrics) you want tested. The planner adopts them and formalizes them into the disciplined structure rather than inventing its own. A `user_fixed` family can be retired or replaced only by you, never by the loop.
- **The planner designs it.** You hand over only the problem and the context and propose nothing. The planner designs the full family set, the tiers, the metrics, and the baselines. This is a primary mode, not a fallback. Handing over a bare problem and letting the planner propose everything is exactly the planner doing its job; it is not the deferral the anti-abdication rule forbids (that rule is about the executor, see below). The catch: the proposed families are only as good as the context you give. A one-line problem yields generic families; paste the repo layout, prior results, what is proven vs unproven, the model of record, and the known failure modes.
- **Hybrid.** You fix some families and let the planner propose the rest. Each family is tagged `origin: user_fixed` or `origin: planner_proposed` so both you and the loop know which is which.

In all three, the planner owes you a *complete* design and the discipline; the difference is only who chose the families.

## When to use the split (and when not to)

Use the planner/executor split when:

- the design space is non-obvious and the family/tier choices materially affect the outcome (most real research loops);
- there is substantial prior context to digest (previous runs, reports, code, failed mechanisms) before a good plan can be written;
- the run is expensive or long, so a reviewable design before launch is worth a planning session;
- you want a human to read and approve the full plan before any agent touches the repo.

A single agent doing both planning and execution is fine when:

- the loop is small and the design is already obvious (low-compute mode, one or two families);
- you are iterating quickly and the cost of a weaker plan is low;
- the executor agent is itself a frontier reasoning model and the task is routine.

Even then, the invariants are identical; only who-writes-the-plan changes.

## The planner's deliverable

The planner produces exactly the artifact in `SKILL.md` "Output Shapes A" — a self-contained `autoresearch.md` — plus the separate launch message as chat text (never inside the file). Concretely, before the planner finishes it must have decided and written, with no placeholders left except genuine `TO_FILL_BEFORE_LAUNCH` values:

- the model or system of record and why it is active;
- the datasets/benchmarks/splits and their four roles;
- the Step 0 baseline plan (and exact baseline values where known; never invented);
- primary, secondary, protected, and catastrophic-fail metrics with directionality;
- **the families** — one to five, each with motivation, hypothesis, suggested experiments, constraints, a stop/pivot rule, and an `origin` tag;
- the `family_set` mode (`fixed` or `open`) and the autonomy mode;
- **the tiers** — what Tier 1 filters, what Tier 2 validates across, what Tier 3 requires for promotion/no-regression, including the seed/slice counts;
- lineage rules, documentation files, artifact retention, stop conditions, and the safety boundary.

The planner owns these design choices in the sense that it must *produce* a complete design rather than defer it downward to the executor. That is the abdication this workflow exists to prevent: a plan that says "the agent will decide the families later" is incomplete and fails the prompt-completeness check (`validate_autoresearch_prompt()`, label `AUTORESEARCH_PROMPT_DESIGN_INCOMPLETE`). If the planner lacks the information to choose, it asks (at most five prioritized questions per `SKILL.md`) rather than punting the decision to the executor.

"The planner owns the design" does not mean the design is fixed against the user. The families, tiers, metrics, baselines, lineage rules, and stop conditions the planner proposes are a starting point you can edit, replace wholesale, or pre-empt by handing the planner your own. What the skill enforces is the *discipline* — protected baseline, Step 0, four-role split and leakage pre-flight, tiered gates, lineage, honest labels, stop conditions, safety boundary. *What* the families/tiers/metrics are is your call; the invariants are not.

## Prompting the planner

A good planner prompt gives the model the role, the context, the binding modules, and the deliverable. Skeleton:

```text
You are designing a bounded autoresearch experiment plan. You are the PLANNER, not the
executor: you will read context and reason, then emit a complete autoresearch.md as text.
You will NOT run code. A separate coding agent (Codex / Claude Code) will execute your plan.

Use the autoresearch-bio framework as authoritative. Read these modules before designing
(they are mounted at <path>, or clone github.com/yashraj59/autoresearch-bio):
  references/core_protocol.md  (esp. §2 protected baseline, §3 Step 0, §3.5 four-role split +
    leakage pre-flight, §5 families + family_set modes, §13 literature, §14 stop conditions)
  references/biology_addendum.md   (if biology)  OR  references/domain_adaptation.md (if not)
  references/statistical_promotion.md
  references/lineage.md
  references/decision_labels.md
  references/debate_council.md + references/amendment_review_checklist.md  (if autonomous)
Base the file on assets/autoresearch_template.md and use the assets/*.md templates for the
artifacts the plan will require.

Context you must digest before designing:
  <repo layout / model of record / prior runs / reports / known failure modes / datasets /
   compute budget / locked files / what is already proven vs unproven>

If I have given you families/tiers/metrics to use, adopt them and formalize them; tag those
families origin=user_fixed. If I have given only a problem, design the families yourself and
tag them origin=planner_proposed. Either way:
  - name the protected model/system of record and exact baseline values (never invent numbers)
  - define the Step 0 baselines and the four-role split
  - define 1-5 FAMILIES with hypothesis, suggested experiments, constraints, stop/pivot rule, origin
  - set family_set (fixed or open) and the autonomy mode
  - define the TIERED GATES (what each tier tests, seed/slice counts, promotion rule)
  - define primary/secondary/protected/catastrophic-fail metrics with directionality
  - define lineage rules, stop conditions, documentation, retention, safety boundary
Do not defer any of this to the executor.

Deliverable:
  1. The complete autoresearch.md as a single code block (self-contained, paste-ready).
  2. SEPARATELY, the launch message I paste into the coding agent — NOT inside the file.
If you are missing something essential, ask at most five prioritized questions first; otherwise
produce the file with explicit assumptions and mark unknown thresholds TO_FILL_BEFORE_LAUNCH.
```

Notes:

- **Give the planner the context, not just the task.** The quality of the families and tiers is bounded by what the planner knows about prior results and failure modes. A planner with no context produces generic families.
- **Make the planner read the modules.** If the chat model has the skill installed, invoke it by name. If not, point it at the cloned repo paths or paste the key module text. Either way the plan must be designed *against* the modules, not from the model's memory of them.
- **Require the two-part deliverable.** The file, plus the launch message as separate chat text. This keeps the launch instruction out of the committed file.
- **Review before launch.** The point of the split is that you can read the whole design before any compute is spent. Read the families and tiers especially.

## Handing the plan to the executor

Once the planner emits the `autoresearch.md`:

1. Save it into the run repo (the executor's working repo, never a read-only source).
2. Paste the planner's separate launch message into the coding agent.
3. The executor reads the `autoresearch.md` and the referenced skill modules, runs the leakage pre-flight and Step 0 baselines first, and only then begins Tier 1.

The executor follows the plan as written. It does not redesign the families or relax the tiers; if it believes the plan is wrong, that is a stop-and-amend event (`core_protocol.md §14`), and in autonomous mode the amendment-origin rule applies — a fired stop cannot be overridden by the same process that hit it. The executor can flag a broken plan but cannot quietly rewrite the design the planner fixed. If `family_set: fixed`, the executor may not add a family at all without an explicit user re-grant.

## Multi-vendor planning (optional)

Just as the Debate Council supports assigning roles to different vendors, you can use **two different planners** for closure-critical or high-stakes designs: have one frontier model draft the `autoresearch.md` and a different-vendor model red-team it against the same modules before launch. This is the design-time analogue of the multi-vendor council and breaks single-model blind spots in the plan itself. Log which model authored and which red-teamed in `external_resources.md`. This is optional and costs an extra planning pass; it is most worth it when the run is expensive or the family choices are contested.

## What this does not change

- The invariants in `core_protocol.md` are identical regardless of who writes the plan.
- The executor is still bound by every gate, label, and stop condition the planner specified.
- The safety boundary is unchanged: planners, like executors, do not produce wet-lab protocols, clinical recommendations, or instructions that weaken a protected system.
- This is a workflow recommendation, not a new artifact type. The artifact is still the `autoresearch.md` defined in `SKILL.md`.
