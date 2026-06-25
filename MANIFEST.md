# Manifest

This is the intended skill archive surface produced by:

```bash
git archive --format=zip --prefix=autoresearch-bio/ HEAD -o ../autoresearch-bio-skill.zip
```

Repository-only files such as `.github/`, `autoresearch_demo/`, and `requirements-demo.txt` are excluded from that archive by `.gitattributes`.

```text
.gitattributes
.gitignore
CHANGELOG.md
LICENSE
MANIFEST.md
QUICKSTART.md
README.md
SKILL.md
assets/autoresearch_template.md
assets/baseline_registry_template.md
assets/calibration_audit_template.md
assets/debate_council_template.md
assets/decision_memo_template.md
assets/executor_instructions.md
assets/external_resources_template.md
assets/final_report_template.md
assets/insight_brief_template.md
assets/metric_investigation_prompt_template.md
assets/papers_consulted_starter.md
assets/reopen_authorization_template.md
assets/research_journal_entry_template.md
assets/results_tsv_schema.tsv
assets/session_amendment_template.md
assets/split_manifest.schema.json
evals/README.md
evals/process_checklist.md
evals/trigger_prompts.csv
references/amendment_review_checklist.md
references/artifact_retention.md
references/biology_addendum.md
references/core_protocol.md
references/debate_council.md
references/decision_labels.md
references/domain_adaptation.md
references/lineage.md
references/metric_calibration_audit.md
references/metric_investigation.md
references/planner_workflow.md
references/skill_anti_patterns.md
references/statistical_promotion.md
scripts/validate_autoresearch_artifacts.py
scripts/validate_skill_repo.py
```
