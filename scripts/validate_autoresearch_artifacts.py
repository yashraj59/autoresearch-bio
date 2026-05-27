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

VALID_BRANCH_TYPES = {"root", "linear", "fork", "grid_sweep", "combine", "replay"}
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

import re

# Reserved tokens forbidden in any auto-emitted status label
# (see references/decision_labels.md "Reserved Strings In Automated Status Labels").
# Claim-strength tokens match as bare uppercase words.
RESERVED_STATUS_CLAIM_TOKENS = (
    "BEAT",
    "SOTA",
    "WINS",
    "OUTPERFORMS",
    "SURPASSES",
    "STATE_OF_THE_ART",
    "BENCHMARK_WIN",
)
# Comparator-relative tokens match (ABOVE|BELOW|MATCHES|WITHIN|EXCEEDS|MISSES) followed
# by zero or more uppercase qualifier segments, ending in a reference noun. This catches
# both direct forms (BELOW_REFERENCE) and qualified forms (BELOW_PUBLIC_REFERENCE).
# We anchor on `_` rather than `\b` because underscore is a regex word char.
RESERVED_RELATIVE_PATTERN = re.compile(
    r"(?:^|_)(ABOVE|BELOW|MATCHES|WITHIN|EXCEEDS|MISSES)"
    r"(?:_[A-Z][A-Z0-9_]*?)?_"
    r"(REFERENCE|BENCHMARK|BASELINE|TARGET|PUBLIC|UPSTREAM|SOTA)"
    r"(?=_|$|[^A-Z0-9_])"
)


def _reserved_violation(status: str) -> str | None:
    """Return the offending substring if `status` violates either reserved rule.

    Claim tokens (BEAT, SOTA, ...) match as substrings since they tend to appear
    surrounded by underscores in compound labels like `*_REFERENCE_BEAT`. The
    relative pattern uses a regex to catch both `*_BELOW_REFERENCE` and the
    qualified `*_BELOW_PUBLIC_REFERENCE` variant.
    """
    upper = status.upper()
    for token in RESERVED_STATUS_CLAIM_TOKENS:
        if token in upper:
            return token
    match = RESERVED_RELATIVE_PATTERN.search(upper)
    if match:
        return match.group(0)
    return None


def validate_results_rows(
    rows: list[dict[str, str]],
    header_columns: set[str] | None = None,
) -> list[str]:
    """Run per-row checks. Skips per-row checks for columns missing from the header
    (those are already reported once at header level)."""
    errors: list[str] = []
    header_columns = header_columns if header_columns is not None else set()
    has_leakage_guard = "leakage_guard" in header_columns or not header_columns
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

        if branch_type in {"linear", "fork", "grid_sweep", "replay"} and parent_ids:
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

        if has_leakage_guard:
            if not leakage_guard:
                errors.append(
                    f"results.tsv row {i} (exp {exp_num}): empty leakage_guard cell "
                    f"(treated as FAIL_TEST_IN_SELECTION)"
                )
            elif leakage_guard not in VALID_LEAKAGE_GUARDS:
                errors.append(
                    f"results.tsv row {i} (exp {exp_num}): invalid leakage_guard '{leakage_guard}'. "
                    f"Must be one of {sorted(VALID_LEAKAGE_GUARDS)}"
                )

        offender = _reserved_violation(status)
        if offender is not None:
            errors.append(
                f"results.tsv row {i} (exp {exp_num}): status '{status}' contains reserved token "
                f"'{offender}' (see decision_labels.md 'Reserved Strings In Automated Status Labels')"
            )

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


# Soft caps from references/artifact_retention.md "Resumability Discipline".
STATE_OF_PLAY_MAX_BYTES = 2 * 1024
HANDOFF_MAX_BYTES = 8 * 1024
INSIGHT_BRIEF_CADENCE = 10
INSIGHT_BRIEF_RAMP = 1  # require ceil(N/10) - INSIGHT_BRIEF_RAMP briefs


def validate_resumability(run_dir: Path, experiment_count: int) -> list[str]:
    """STATE_OF_PLAY.md presence, INSIGHT_BRIEF cadence, handoff size caps."""
    errors: list[str] = []
    state_of_play = run_dir / "STATE_OF_PLAY.md"
    if experiment_count >= 1 and not state_of_play.exists():
        errors.append(
            "STATE_OF_PLAY.md is missing. Required after any experiment runs. "
            "Label: RESUMABILITY_STATE_OF_PLAY_STALE."
        )
    elif state_of_play.exists() and state_of_play.stat().st_size > STATE_OF_PLAY_MAX_BYTES:
        errors.append(
            f"STATE_OF_PLAY.md exceeds {STATE_OF_PLAY_MAX_BYTES} bytes "
            f"({state_of_play.stat().st_size} bytes). It is state, not history. "
            f"Label: RESUMABILITY_STATE_OF_PLAY_OVERSIZED."
        )

    insights = run_dir / "insights"
    if experiment_count >= 100:
        brief_count = (
            len(list(insights.glob("INSIGHT_BRIEF_*.md"))) if insights.exists() else 0
        )
        expected = max(0, (experiment_count // INSIGHT_BRIEF_CADENCE) - INSIGHT_BRIEF_RAMP)
        if brief_count < expected:
            errors.append(
                f"insights/ has {brief_count} INSIGHT_BRIEF_*.md files; "
                f"expected >= {expected} after {experiment_count} experiments. "
                f"Label: RESUMABILITY_INSIGHT_BRIEFS_MISSING."
            )

    for handoff in run_dir.glob("*HANDOFF*.md"):
        if handoff.stat().st_size > HANDOFF_MAX_BYTES:
            errors.append(
                f"{handoff.name} is {handoff.stat().st_size} bytes "
                f"(cap {HANDOFF_MAX_BYTES}). Handoff is state, not history. "
                f"Label: HANDOFF_DOCUMENT_OVERSIZED."
            )

    return errors


# Append-only log orphan markers (see references/artifact_retention.md).
ORPHAN_TITLE_PATTERN = re.compile(
    r"^#+\s*(TMP|TODO|XXX|FIXME|<\.\.\.>|<TBD>)\s*$",
    re.MULTILINE,
)


def validate_append_only_logs(run_dir: Path) -> list[str]:
    errors: list[str] = []
    targets = [
        "architectural_changes_log.md",
        "family_allocation.md",
        "papers_consulted.md",
        "research_journal.md",
    ]
    for name in targets:
        path = run_dir / name
        if not path.exists():
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        matches = ORPHAN_TITLE_PATTERN.findall(body)
        if matches:
            errors.append(
                f"{name} contains orphan markers ({len(matches)}): "
                f"{', '.join(sorted(set(matches)))}. "
                f"Label: APPEND_ONLY_LOG_ORPHAN_UNRESOLVED."
            )
    return errors


# External baseline reproduction-provenance columns.
EXTERNAL_BASELINE_REQUIRED_COLUMNS = (
    "reproduction_mode",
    "claim_strength",
    "upstream_commit_or_release",
    "metric_selection_policy",
    "eval_split",
    "split_parity",
)
VALID_REPRODUCTION_MODES = {
    "upstream_unchanged",
    "upstream_patched",
    "full_reimplementation",
}
VALID_SPLIT_PARITY = {
    "same_train_same_eval",
    "same_train_different_eval",
    "different_train_different_eval",
}


PROVENANCE_COLUMNS = {
    "reproduction_mode",
    "claim_strength",
    "upstream_commit_or_release",
    "metric_selection_policy",
}
SPLIT_PARITY_COLUMNS = {"eval_split", "split_parity"}


def validate_external_baselines_tsv(path: Path) -> list[str]:
    if not path.exists():
        return []
    errors: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        header = reader.fieldnames or []
        missing_provenance = [
            c for c in EXTERNAL_BASELINE_REQUIRED_COLUMNS
            if c in PROVENANCE_COLUMNS and c not in header
        ]
        missing_parity = [
            c for c in EXTERNAL_BASELINE_REQUIRED_COLUMNS
            if c in SPLIT_PARITY_COLUMNS and c not in header
        ]
        if missing_provenance:
            errors.append(
                f"{path.name} missing reproduction-provenance columns: "
                f"{', '.join(missing_provenance)}. "
                f"Label: REPRODUCTION_PROVENANCE_MISSING."
            )
        if missing_parity:
            errors.append(
                f"{path.name} missing split-parity columns: "
                f"{', '.join(missing_parity)}. "
                f"Label: EXTERNAL_BASELINE_SPLIT_PARITY_UNDOCUMENTED."
            )
        if missing_provenance or missing_parity:
            return errors
        for i, row in enumerate(reader, start=2):
            mode = row.get("reproduction_mode", "").strip()
            claim = row.get("claim_strength", "").strip().lower()
            if mode and mode not in VALID_REPRODUCTION_MODES:
                errors.append(
                    f"{path.name} row {i}: invalid reproduction_mode '{mode}'. "
                    f"Must be one of {sorted(VALID_REPRODUCTION_MODES)}."
                )
            if mode == "full_reimplementation":
                # Affirmative reproduction claim: "reproduced upstream X" or
                # "reproduction of upstream X". The canonical correct wording is
                # "compat-equivalent reimplementation, not a reproduction of the
                # published numbers" — that contains "reproduction" only inside the
                # negation phrase "not a reproduction", which is the correct form.
                has_affirmative_claim = (
                    "reproduced" in claim
                    or re.search(r"\breproduction\s+of\b", claim) is not None
                )
                has_negation = (
                    "not a reproduction" in claim
                    or "not reproduced" in claim
                    or "not a reproduc" in claim  # tolerate truncations
                )
                if has_affirmative_claim and not has_negation:
                    errors.append(
                        f"{path.name} row {i}: reproduction_mode='full_reimplementation' but "
                        f"claim_strength reads as 'reproduced …'. A reimplementation is not a "
                        f"reproduction of the published numbers. "
                        f"Label: EXTERNAL_BASELINE_REIMPLEMENTATION_MISLABELED."
                    )
            parity = row.get("split_parity", "").strip()
            if parity and parity not in VALID_SPLIT_PARITY:
                errors.append(
                    f"{path.name} row {i}: invalid split_parity '{parity}'. "
                    f"Must be one of {sorted(VALID_SPLIT_PARITY)}. "
                    f"Label: EXTERNAL_BASELINE_SPLIT_PARITY_UNDOCUMENTED."
                )
            for col in EXTERNAL_BASELINE_REQUIRED_COLUMNS:
                if not row.get(col, "").strip():
                    label = (
                        "EXTERNAL_BASELINE_SPLIT_PARITY_UNDOCUMENTED"
                        if col in {"eval_split", "split_parity"}
                        else "REPRODUCTION_PROVENANCE_MISSING"
                    )
                    errors.append(
                        f"{path.name} row {i}: empty {col}. Label: {label}."
                    )
                    break
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

    experiment_count = 0
    results_path = run_dir / "results.tsv"
    if results_path.exists():
        with results_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            header = reader.fieldnames or []
            missing = [col for col in REQUIRED_RESULTS_COLUMNS if col not in header]
            if missing:
                errors.append(f"results.tsv missing columns: {', '.join(missing)}")
            # Always parse rows, even when columns are missing — row-level checks
            # for non-missing columns (e.g. reserved-substring scan over `status`)
            # still apply, and DictReader returns "" for any missing field.
            rows = list(reader)
            errors.extend(validate_results_rows(rows, header_columns=set(header)))
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

    errors.extend(validate_resumability(run_dir, experiment_count))
    errors.extend(validate_append_only_logs(run_dir))
    errors.extend(
        validate_external_baselines_tsv(run_dir / "external_public_baselines.tsv")
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
