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
    "leakage_preflight.md",
    "split_manifest.json",
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
    "leakage_guard",
]

VALID_BRANCH_TYPES = {"root", "linear", "fork", "combine", "replay"}
VALID_SUBTREE_STATUS = {
    "active_leaf",
    "expanded",
    "pruned",
    "promoted",
    "retired_subtree",
}
VALID_LEAKAGE_GUARDS = {
    "PASS_NO_TEST_SELECTION",
    "WARN_TEST_READ_FOR_DIAGNOSTICS_ONLY",
    "FAIL_TEST_IN_SELECTION",
}

# Reserved substrings forbidden in any auto-emitted status label
# (see references/decision_labels.md "Reserved Strings In Automated Status Labels").
RESERVED_STATUS_SUBSTRINGS = (
    "BEAT",
    "SOTA",
    "WINS",
    "OUTPERFORMS",
    "SURPASSES",
    "STATE_OF_THE_ART",
    "BENCHMARK_WIN",
    "ABOVE_REFERENCE",
    "BELOW_REFERENCE",
    "MATCHES_REFERENCE",
    "WITHIN_X_OF",
    "EXCEEDS_REFERENCE",
    "MISSES_REFERENCE",
)


def validate_results_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for i, row in enumerate(rows, start=2):  # row 2 is first data row (1 is header)
        branch_type = row.get("branch_type", "").strip()
        parent_ids = row.get("parent_experiment_ids", "").strip()
        subtree_status = row.get("subtree_status", "").strip()
        leakage_guard = row.get("leakage_guard", "").strip()
        status = row.get("status", "")
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

        if not leakage_guard:
            errors.append(
                f"results.tsv row {i} (exp {exp_num}): missing leakage_guard column "
                f"(default treats missing as FAIL_TEST_IN_SELECTION)"
            )
        elif leakage_guard not in VALID_LEAKAGE_GUARDS:
            errors.append(
                f"results.tsv row {i} (exp {exp_num}): invalid leakage_guard '{leakage_guard}'. "
                f"Must be one of {sorted(VALID_LEAKAGE_GUARDS)}"
            )

        status_upper = status.upper()
        for reserved in RESERVED_STATUS_SUBSTRINGS:
            if reserved in status_upper:
                errors.append(
                    f"results.tsv row {i} (exp {exp_num}): status '{status}' contains reserved substring "
                    f"'{reserved}' (see decision_labels.md 'Reserved Strings In Automated Status Labels')"
                )
                break

    return errors


def validate_architectural_log(path: Path) -> list[str]:
    """Reject a stub log where every entry repeats template prose with no real metadata."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = [block for block in text.split("\n## ") if block.strip()]
    if len(entries) < 5:
        return []  # too few entries to judge template-only
    informative_terms = (
        "parameter_delta",
        "parameter delta",
        "lines_touched",
        "lines touched",
        "gradient_flow_smoke",
        "gradient flow smoke",
        "contribution_ratio_at_init",
        "contribution ratio",
        "observed_effect_post_tier1",
        "observed effect",
        "params=",
        "params =",
    )
    informative_count = sum(
        any(term.lower() in entry.lower() for term in informative_terms)
        for entry in entries
    )
    if informative_count == 0:
        return [
            f"architectural_changes_log.md is template-only ({len(entries)} entries, "
            f"none records parameter_delta / lines_touched / smoke-test / "
            f"contribution_ratio_at_init / observed_effect_post_tier1). "
            f"Label: ARCHITECTURAL_LOG_TEMPLATE_ONLY."
        ]
    return []


def validate_papers_consulted(run_dir: Path, repo_assets: Path | None) -> list[str]:
    """Compare papers_consulted.md against the canonical starter in assets/."""
    working = run_dir / "papers_consulted.md"
    if not working.exists() or repo_assets is None:
        return []
    starter = repo_assets / "papers_consulted_starter.md"
    if not starter.exists():
        return []  # no canonical starter to diff against; skip
    if working.read_bytes() == starter.read_bytes():
        return [
            "papers_consulted.md is byte-identical to assets/papers_consulted_starter.md. "
            "Label: LITERATURE_DISCIPLINE_VIOLATION."
        ]
    return []


def validate_identity_violations(path: Path, experiment_count: int) -> list[str]:
    """A one-line skeleton file is implausible after 50+ experiments."""
    if not path.exists() or experiment_count < 50:
        return []
    body = path.read_text(encoding="utf-8", errors="replace").strip()
    # Strip trivial heading-only files.
    non_heading = [
        line for line in body.splitlines() if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(body) < 500 or len(non_heading) < 3:
        return [
            f"identity_violations_considered.md is implausibly thin after {experiment_count} experiments "
            f"({len(body)} bytes, {len(non_heading)} content lines). "
            f"Label: IDENTITY_VIOLATIONS_LOG_SKELETON."
        ]
    return []


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

    experiment_count = 0
    results_path = run_dir / "results.tsv"
    if results_path.exists():
        with results_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            header = reader.fieldnames or []
            missing = [col for col in REQUIRED_RESULTS_COLUMNS if col not in header]
            if missing:
                errors.append(f"results.tsv missing columns: {', '.join(missing)}")
                rows = []
            else:
                rows = list(reader)
                errors.extend(validate_results_rows(rows))
            experiment_count = len(rows)

    baseline_path = run_dir / "BASELINE_REGISTRY.md"
    if baseline_path.exists():
        baseline_text = baseline_path.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in ["model", "metric", "direction", "seed", "source"]:
            if phrase not in baseline_text:
                errors.append(f"BASELINE_REGISTRY.md may be incomplete; missing term: {phrase}")

    # Stub-compliance machine checks (see evals/process_checklist.md).
    errors.extend(validate_architectural_log(run_dir / "architectural_changes_log.md"))

    # Look for the skill's canonical starter, either in this repo (if run alongside it)
    # or in an explicit AUTORESEARCH_BIO_ASSETS env var. Skip silently if neither exists.
    skill_assets: Path | None = None
    here = Path(__file__).resolve().parent.parent / "assets"
    if here.exists():
        skill_assets = here
    import os
    env_assets = os.environ.get("AUTORESEARCH_BIO_ASSETS")
    if env_assets and Path(env_assets).exists():
        skill_assets = Path(env_assets)
    errors.extend(validate_papers_consulted(run_dir, skill_assets))

    errors.extend(
        validate_identity_violations(
            run_dir / "identity_violations_considered.md", experiment_count
        )
    )

    if errors:
        print("Autoresearch artifact validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Autoresearch artifact validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
