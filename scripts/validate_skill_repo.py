#!/usr/bin/env python3
"""Validate the autoresearch-bio skill repository structure.

This script is intentionally small and deterministic. It checks that the skill
bundle contains the expected files and that SKILL.md has valid frontmatter with
name and description.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "references/core_protocol.md",
    "references/domain_adaptation.md",
    "references/biology_addendum.md",
    "references/metric_investigation.md",
    "references/debate_council.md",
    "references/decision_labels.md",
    "references/artifact_retention.md",
    "references/statistical_promotion.md",
    "references/lineage.md",
    "references/amendment_review_checklist.md",
    "assets/autoresearch_template.md",
    "assets/session_amendment_template.md",
    "assets/decision_memo_template.md",
    "assets/metric_investigation_prompt_template.md",
    "assets/final_report_template.md",
    "assets/research_journal_entry_template.md",
    "assets/debate_council_template.md",
    "assets/baseline_registry_template.md",
    "assets/external_resources_template.md",
    "assets/results_tsv_schema.tsv",
    "evals/trigger_prompts.csv",
    "evals/process_checklist.md",
]


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        raise ValueError("SKILL.md is missing YAML-style frontmatter")

    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"Missing required file: {rel}")

    skill_path = ROOT / "SKILL.md"
    if skill_path.exists():
        try:
            fields = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
            if fields.get("name") != "autoresearch-bio":
                errors.append("SKILL.md frontmatter name must be 'autoresearch-bio'")
            description = fields.get("description", "")
            if len(description) < 120:
                errors.append("SKILL.md description is too short to be a reliable trigger")
            skill_text = skill_path.read_text(encoding="utf-8").lower()
            for phrase in ["Step 0", "tiered", "biological", "domain", "Do not use", "lineage"]:
                if phrase.lower() not in skill_text:
                    errors.append(f"Expected phrase not found in SKILL.md: {phrase}")
        except ValueError as exc:
            errors.append(str(exc))

    # Check that autoresearch_template.md does NOT contain a launch instruction block
    template_path = ROOT / "assets" / "autoresearch_template.md"
    if template_path.exists():
        template_text = template_path.read_text(encoding="utf-8").lower()
        if "## launch instruction" in template_text or "## launch message" in template_text:
            errors.append("autoresearch_template.md must not contain a launch instruction block; launch message is emitted separately as chat text")

    if errors:
        print("Skill repo validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Skill repo validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
