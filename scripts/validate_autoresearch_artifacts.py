#!/usr/bin/env python3
"""Validate a generated autoresearch run directory.

Usage:
    python scripts/validate_autoresearch_artifacts.py /path/to/run

The script checks for the core documentation files and minimum results.tsv
columns including lineage columns. It does not judge scientific quality; it
catches process drift.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REQUIRED_FILES = [
    "results.tsv",
    "research_journal.md",
    "architectural_changes_log.md",
    "family_allocation.md",
    "BASELINE_REGISTRY.md",
    "papers_consulted.md",
    "external_resources.md",
    "identity_violations_considered.md",
]

REQUIRED_RESULTS_COLUMNS = [
    "commit",
    "experiment_num",
    "parent_experiment_ids",
    "branch_type",
    "subtree_status",
    "family",
    "tier_reached",
    "status",
    "primary_metric",
    "secondary_metric",
    "protected_metric_summary",
    "architectural_change",
    "description",
]

VALID_BRANCH_TYPES = {"root", "linear", "fork", "combine", "replay"}
VALID_SUBTREE_STATUS = {
    "active_leaf",
    "expanded",
    "pruned",
    "promoted",
    "retired_subtree",
}


def validate_results_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for i, row in enumerate(rows, start=2):  # row 2 is first data row (1 is header)
        branch_type = row.get("branch_type", "").strip()
        parent_ids = row.get("parent_experiment_ids", "").strip()
        subtree_status = row.get("subtree_status", "").strip()
        exp_num = row.get("experiment_num", "?")

        if branch_type and branch_type not in VALID_BRANCH_TYPES:
            errors.append(
                f"results.tsv row {i} (exp {exp_num}): invalid branch_type '{branch_type}'. "
                f"Must be one of {sorted(VALID_BRANCH_TYPES)}"
            )

        if subtree_status and subtree_status not in VALID_SUBTREE_STATUS:
            errors.append(
                f"results.tsv row {i} (exp {exp_num}): invalid subtree_status '{subtree_status}'. "
                f"Must be one of {sorted(VALID_SUBTREE_STATUS)}"
            )

        if branch_type == "root" and parent_ids:
            errors.append(
                f"results.tsv row {i} (exp {exp_num}): root branch_type must have empty parent_experiment_ids"
            )

        if branch_type in {"linear", "fork", "replay"} and parent_ids:
            parts = [p.strip() for p in parent_ids.split(",") if p.strip()]
            if len(parts) != 1:
                errors.append(
                    f"results.tsv row {i} (exp {exp_num}): branch_type '{branch_type}' must have exactly one parent"
                )

        if branch_type == "combine" and parent_ids:
            parts = [p.strip() for p in parent_ids.split(",") if p.strip()]
            if len(parts) < 2:
                errors.append(
                    f"results.tsv row {i} (exp {exp_num}): branch_type 'combine' must have two or more parents"
                )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "Usage: python scripts/validate_autoresearch_artifacts.py /path/to/run",
            file=sys.stderr,
        )
        return 2

    run_dir = Path(argv[1]).resolve()
    errors: list[str] = []

    if not run_dir.exists():
        print(f"Run directory does not exist: {run_dir}", file=sys.stderr)
        return 2

    for rel in REQUIRED_FILES:
        if not (run_dir / rel).exists():
            errors.append(f"Missing required file: {rel}")

    results_path = run_dir / "results.tsv"
    if results_path.exists():
        with results_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            header = reader.fieldnames or []
            missing = [col for col in REQUIRED_RESULTS_COLUMNS if col not in header]
            if missing:
                errors.append(f"results.tsv missing columns: {', '.join(missing)}")
            else:
                rows = list(reader)
                errors.extend(validate_results_rows(rows))

    baseline_path = run_dir / "BASELINE_REGISTRY.md"
    if baseline_path.exists():
        baseline_text = baseline_path.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in ["model", "metric", "direction", "seed", "source"]:
            if phrase not in baseline_text:
                errors.append(f"BASELINE_REGISTRY.md may be incomplete; missing term: {phrase}")

    if errors:
        print("Autoresearch artifact validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Autoresearch artifact validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
