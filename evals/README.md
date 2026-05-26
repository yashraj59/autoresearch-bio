# Evals

This folder contains lightweight skill-quality checks.

- `trigger_prompts.csv` tests whether the skill should or should not activate for both bio-first and general ML/dev autoresearch tasks.
- `process_checklist.md` tests whether the output preserves the protocol's core invariants and correctly swaps biology-specific validators for domain-specific validators when the task is not biological.

Suggested use: sample 10 prompts, run the skill, and score whether each output satisfies the checklist. Add new prompts whenever you notice false triggers, missed triggers, or recurring failure modes.
