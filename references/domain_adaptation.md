# Domain Adaptation Reference

`autoresearch-bio` is bio-first, but the core protocol is domain-general. Use this reference when the project is not biological ML or when the user wants to apply the same protected-baseline discipline to ordinary ML, software engineering, agent development, infrastructure, evaluation design, or benchmark optimization.

The name stays `autoresearch-bio`; the behavior adapts by replacing biological protected metrics with domain-specific protected metrics.

---

## When To Use This Reference

Read this reference when the user says the project is not biology, or when the task is about:

- language models, code-generation systems, retrieval systems, ranking, recommendation, search, forecasting, vision, robotics, simulation, reinforcement learning, chemistry, materials, or general ML;
- software or developer-tooling work where an agent will repeatedly change code and evaluate the result;
- performance optimization with correctness, safety, latency, memory, or compatibility no-regression gates;
- benchmark improvement where leakage, overfitting, and cherry-picked wins are risks;
- autonomous dev loops where the agent needs stop conditions and evidence-based amendments.

Do not use this protocol for ordinary one-off code review, single bug fixes, or generic brainstorming unless the user frames the task as a bounded experiment loop.

---

## Universal Translation Table

| Bio-first term | General term |
| --- | --- |
| Biological ML model | Model, agent, service, pipeline, library, tool, or system |
| Model of record | System of record, baseline implementation, reference config, blessed checkpoint |
| Perturbation/cell-state task | Target task, benchmark family, feature slice, scenario class |
| Biological no-regression | Protected domain no-regression |
| Marker/program coherence | Slice behavior, invariant, subsystem behavior, feature-family behavior |
| Direction-of-effect | Expected directionality, monotonicity, sign, ordering, ranking, or causal assumption |
| Population structure | Segment coverage, rare-case behavior, long-tail performance, scenario diversity |
| Pathway/program consistency | Mechanism consistency, architectural intent, subsystem alignment |
| Held-out biological validator | Held-out benchmark, traffic slice, simulator scenario, CI suite, regression pack |
| Wet-lab/clinical boundary | Safety, security, privacy, compliance, production, or deployment boundary |

---

## General Protected Metric Examples

Use protected metrics that can veto a headline metric improvement.

### Language, code, and agent systems

- held-out task pass rate;
- hallucination or unsupported-claim rate;
- tool-call correctness;
- instruction-following regressions;
- safety classifier or policy compliance gates;
- latency, token cost, and memory;
- rare task-family performance;
- benchmark contamination or leakage checks;
- human-eval or preference slice stability.

### Vision, speech, and multimodal systems

- rare-class performance;
- calibration and confidence reliability;
- subgroup or slice performance;
- robustness to augmentation, lighting, blur, noise, or domain shift;
- localization or segmentation consistency;
- false-positive and false-negative rates on protected slices.

### Recommendation, ranking, search, and retrieval

- precision/recall tradeoffs;
- tail-item coverage;
- query-family coverage;
- calibration;
- fairness or exposure constraints;
- latency and cache-hit behavior;
- regressions on high-value or safety-sensitive query classes.

### Forecasting and time-series systems

- horizon-specific error;
- seasonal or regime-change behavior;
- calibration and interval coverage;
- rare-event recall;
- leakage checks;
- degradation under missingness, sensor drift, or delayed data.

### Software and infrastructure loops

- correctness tests;
- regression test suites;
- performance benchmarks;
- p95/p99 latency;
- memory footprint;
- binary size or dependency footprint;
- compatibility across platforms;
- security checks;
- migration safety;
- observability and rollback readiness.

### Robotics, simulation, and control

- safety violations;
- constraint satisfaction;
- sim-to-real gap indicators;
- robustness across seeds and scenarios;
- recovery from disturbances;
- energy or resource use;
- catastrophic failure rate.

---

## General Autoresearch Setup

For non-bio projects, every generated `autoresearch.md` should still include:

1. **System of record.** The active implementation, checkpoint, config, commit, environment, and reason it is the protected baseline.
2. **Step 0 baselines.** Re-run or verify the system of record on every dataset, benchmark, CI suite, simulator scenario, or traffic slice used for gates.
3. **Metric stack.** Separate primary metrics, secondary metrics, protected metrics, catastrophic-fail metrics, and diagnostic metrics.
4. **Tiered gates.** Tier 1 cheap screen, Tier 2 multi-seed or multi-slice validation, Tier 3 no-regression/generalization/promotion validation.
5. **Architecture or mechanism families.** Pre-register the kinds of changes the agent may try.
6. **Identity constraints.** Lock files, APIs, evaluators, data splits, benchmark definitions, safety checks, and system boundaries that cannot change silently.
7. **Stop conditions.** Cap experiments, failed families, repeated pathologies, metric invalidation, budget exhaustion, and scope violations.
8. **Documentation.** Maintain results, journal entries, baseline registry, change logs, artifacts, and final report.

---

## Non-Bio Prompt Add-On

Paste this into an `autoresearch.md` when adapting the skill outside biology:

```markdown
## Domain Adaptation

This project is not biological ML. Use `autoresearch-bio` as a domain-general protected-baseline research protocol.

Replace biological no-regression metrics with protected domain metrics:

- Correctness / validity: `<TO_FILL_BEFORE_LAUNCH>`
- Robustness / slice behavior: `<TO_FILL_BEFORE_LAUNCH>`
- Latency / memory / cost: `<TO_FILL_BEFORE_LAUNCH>`
- Safety / security / policy: `<TO_FILL_BEFORE_LAUNCH>`
- Held-out benchmark or regression suite: `<TO_FILL_BEFORE_LAUNCH>`

A candidate that improves the headline metric while failing any protected domain gate is a useful failure, not a new baseline.
```

---

## Domain-Specific Stop Examples

Stop or amend when:

- a candidate improves the headline score by changing or weakening the evaluator;
- the system improves average performance but regresses a protected slice;
- gains are smaller than benchmark noise or run-to-run variance;
- the agent repeatedly proposes changes outside the locked identity constraints;
- a benchmark win appears caused by leakage, memorization, shortcut learning, or overfitting to the validation set;
- latency, cost, memory, safety, security, or compatibility gates regress;
- a production-facing change would require approvals outside the research loop.

---

## External Baseline Reproduction Provenance

When the non-bio project compares against an external published baseline (e.g. an open-source benchmark suite, a published agent harness, an upstream model implementation), apply the same provenance discipline as `biology_addendum.md`:

- declare `reproduction_mode` per row of any comparator TSV: `upstream_unchanged`, `upstream_patched`, or `full_reimplementation`;
- declare `claim_strength` and use only the matching wording in reports;
- declare `upstream_commit_or_release` even for reimplementations;
- declare `metric_selection_policy` (final epoch, last validation, best observed, single evaluation).

A non-bio `full_reimplementation` may not be reported as a published-baseline beat. Patches must live at `external_baselines/<name>/upstream.patch` with a diff. See `biology_addendum.md "External Baseline Reproduction Provenance"` for the full rule.

---

## Reporting Requirement

For non-bio final reports, include a short `Domain Adaptation` section:

```markdown
## Domain Adaptation

- Domain: `<language/code/vision/retrieval/software/etc.>`
- System of record: `<checkpoint/commit/config>`
- Headline metric: `<metric>`
- Protected domain gates: `<list>`
- Catastrophic-fail gates: `<list>`
- Held-out validators: `<list>`
- Main evidence for continue/amend/audit/close: `<summary>`
```
