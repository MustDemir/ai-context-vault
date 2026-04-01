#!/usr/bin/env python3
"""Weekly audit script for genaiops-thesis. Read-only. Posts findings as GitHub Issue."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import NamedTuple

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML fehlt: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
PRIMARY_EXPOSE = ROOT / "docs" / "expose" / "Expose_v4_final_2026-02-28_encrypted.pdf"
LEGACY_EXPOSE_DIR = ROOT / "docs" / "expose" / "legacy"
STALE_DAYS = 14

ERROR = "error"
WARNING = "warning"
INFO = "info"


class Finding(NamedTuple):
    severity: str
    category: str
    message: str


# ── Section 1: Structure & Convention Checks ─────────────────────────────────


def check_session_summaries() -> list[Finding]:
    findings: list[Finding] = []
    for d in ROOT.rglob("session_summaries"):
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if p.is_dir():
                findings.append(Finding(ERROR, "structure",
                    f"Directory inside session_summaries not allowed: {p.relative_to(ROOT)}"))
                continue
            if p.name in {".DS_Store", ".gitkeep"}:
                continue
            if p.suffix.lower() != ".yaml":
                findings.append(Finding(ERROR, "structure",
                    f"Non-YAML in session_summaries: {p.relative_to(ROOT)}"))
    return findings


def check_expose_locations() -> list[Finding]:
    findings: list[Finding] = []
    if not PRIMARY_EXPOSE.exists():
        findings.append(Finding(ERROR, "structure",
            f"Primary expose missing: {PRIMARY_EXPOSE.relative_to(ROOT)}"))
    for p in ROOT.rglob("*.docx"):
        if not _is_tracked_by_git(p):
            continue
        name = p.name.lower()
        if "expose" not in name and "expos" not in name:
            continue
        if LEGACY_EXPOSE_DIR in p.parents:
            continue
        if p.name.startswith("~$"):
            findings.append(Finding(WARNING, "structure",
                f"Temporary lock file (close Word): {p.relative_to(ROOT)}"))
            continue
        findings.append(Finding(ERROR, "structure",
            f"Expose outside primary/legacy: {p.relative_to(ROOT)}"))
    return findings


def check_final_images() -> list[Finding]:
    findings: list[Finding] = []
    pattern = re.compile(r"_v\d{2}\.png$", re.IGNORECASE)
    for p in ROOT.rglob("images/final/*.png"):
        if not pattern.search(p.name):
            findings.append(Finding(WARNING, "structure",
                f"Final image missing _vNN suffix: {p.relative_to(ROOT)}"))
    return findings


def check_chapter_state_format() -> list[Finding]:
    """Prueft chapter_state.yaml (bevorzugt) oder _status.yml als Fallback."""
    findings: list[Finding] = []
    seen_dirs: set[str] = set()
    for pattern in ("chapter_state.yaml", "_status.yml"):
        for p in ROOT.rglob(pattern):
            if ".git" in p.parts or ".memory" in p.parts:
                continue
            chapter_dir = str(p.parent.relative_to(ROOT))
            if chapter_dir in seen_dirs:
                continue
            seen_dirs.add(chapter_dir)
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8"))
            except Exception as exc:
                findings.append(Finding(ERROR, "structure",
                    f"{p.relative_to(ROOT)}: YAML parse error: {exc}"))
                continue
            if not isinstance(data, dict):
                findings.append(Finding(ERROR, "structure",
                    f"{p.relative_to(ROOT)}: not a YAML mapping"))
                continue
            # kapitel oder chapter muss vorhanden sein
            if "kapitel" not in data and "chapter" not in data:
                findings.append(Finding(ERROR, "structure",
                    f"{p.relative_to(ROOT)}: missing required field 'kapitel' or 'chapter'"))
            # progress oder progress_pct muss vorhanden sein
            prog_val = data.get("progress", data.get("progress_pct"))
            if prog_val is None:
                findings.append(Finding(ERROR, "structure",
                    f"{p.relative_to(ROOT)}: missing required field 'progress' or 'progress_pct'"))
            elif not isinstance(prog_val, (int, float)):
                findings.append(Finding(ERROR, "structure",
                    f"{p.relative_to(ROOT)}: 'progress' must be int, got {type(prog_val).__name__}"))
            elif not (0 <= prog_val <= 100):
                findings.append(Finding(WARNING, "structure",
                    f"{p.relative_to(ROOT)}: 'progress' out of range: {prog_val}"))
            if "status" not in data:
                findings.append(Finding(ERROR, "structure",
                    f"{p.relative_to(ROOT)}: missing required field 'status'"))
    return findings


def check_gitignore_rules() -> list[Finding]:
    findings: list[Finding] = []
    gi = ROOT / ".gitignore"
    if not gi.exists():
        findings.append(Finding(ERROR, "security", ".gitignore not found"))
        return findings
    content = gi.read_text(encoding="utf-8")
    required = {
        "docs/expose/*.pdf": "Block unencrypted expose PDFs",
        "!docs/expose/*_encrypted.pdf": "Allow encrypted expose PDFs",
        "docs/expose/legacy/": "Block legacy expose folder",
        ".env": "Block .env secrets file",
    }
    for rule, desc in required.items():
        if rule not in content:
            findings.append(Finding(ERROR, "security",
                f".gitignore missing rule '{rule}' ({desc})"))
    return findings


# ── Section 2: Security Checks ───────────────────────────────────────────────


def check_no_unencrypted_pdfs_in_expose() -> list[Finding]:
    findings: list[Finding] = []
    expose_dir = ROOT / "docs" / "expose"
    if not expose_dir.exists():
        return findings
    for p in expose_dir.glob("*.pdf"):
        if not p.name.endswith("_encrypted.pdf"):
            findings.append(Finding(ERROR, "security",
                f"Unencrypted PDF in docs/expose/: {p.name}"))
    return findings


def _is_tracked_by_git(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path)],
        capture_output=True, cwd=ROOT,
    )
    return result.returncode == 0


def check_no_secrets_committed() -> list[Finding]:
    findings: list[Finding] = []
    secret_patterns = {"*.key", "*.pem", "*.token", "credentials.json", "secrets.json"}
    skip_dirs = {".git", ".memory", "__pycache__", "node_modules", ".venv", "venv"}

    for p in ROOT.rglob("*"):
        if any(skip in p.parts for skip in skip_dirs):
            continue
        if not p.is_file():
            continue
        if p.name == ".env" or p.name.startswith(".env."):
            if _is_tracked_by_git(p):
                findings.append(Finding(ERROR, "security",
                    f"Secret file tracked by git: {p.relative_to(ROOT)}"))
            continue
        for pat in secret_patterns:
            if p.match(pat) and _is_tracked_by_git(p):
                findings.append(Finding(ERROR, "security",
                    f"Secret file tracked by git: {p.relative_to(ROOT)}"))
                break
    return findings


# ── Section 3: Artifact Completeness ─────────────────────────────────────────


def check_requirements_completeness() -> list[Finding]:
    findings: list[Finding] = []
    req_dir = ROOT / "04_anforderungsanalyse_RQ1" / "requirements"
    if not req_dir.exists():
        findings.append(Finding(INFO, "artifacts", "Requirements directory not found"))
        return findings
    text_fields = ("title", "kontrollmechanismus", "description")
    choice_fields = ("lifecycle_phase", "governance_dimension", "must_should")
    for p in sorted(req_dir.glob("R*.yaml")):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:
            findings.append(Finding(ERROR, "artifacts", f"{p.name}: YAML parse error"))
            continue
        if not isinstance(data, dict):
            continue
        rid = data.get("id", p.stem)
        empty = 0
        total = len(text_fields) + len(choice_fields)
        for f in text_fields:
            if not data.get(f, "").strip():
                empty += 1
        for f in choice_fields:
            val = data.get(f, "")
            if "|" in str(val) or not str(val).strip():
                empty += 1
        if empty == total:
            findings.append(Finding(WARNING, "artifacts",
                f"{rid}: alle {total} Pflichtfelder leer (Draft)"))
        elif empty > 0:
            findings.append(Finding(INFO, "artifacts",
                f"{rid}: {empty}/{total} Pflichtfelder leer"))
    return findings


def check_gates_completeness() -> list[Finding]:
    findings: list[Finding] = []
    gates_dir = ROOT / "05_referenzarchitektur_RQ2" / "05_03_quality_gates"
    if not gates_dir.exists():
        findings.append(Finding(INFO, "artifacts", "Quality Gates directory not found"))
        return findings
    text_fields = ("name", "trigger", "owner")
    choice_fields = ("dimension", "lifecycle_phase", "decision")
    for p in sorted(gates_dir.rglob("G*.yaml")):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:
            findings.append(Finding(ERROR, "artifacts", f"{p.name}: YAML parse error"))
            continue
        if not isinstance(data, dict):
            continue
        gid = data.get("id", p.stem)
        empty = 0
        total = len(text_fields) + len(choice_fields)
        for f in text_fields:
            if not data.get(f, "").strip():
                empty += 1
        for f in choice_fields:
            val = data.get(f, "")
            if "|" in str(val) or not str(val).strip():
                empty += 1
        if empty == total:
            findings.append(Finding(WARNING, "artifacts",
                f"{gid}: alle {total} Pflichtfelder leer (Draft)"))
        elif empty > 0:
            findings.append(Finding(INFO, "artifacts",
                f"{gid}: {empty}/{total} Pflichtfelder leer"))
    return findings


def check_traceability() -> list[Finding]:
    findings: list[Finding] = []
    req_dir = ROOT / "04_anforderungsanalyse_RQ1" / "requirements"
    gates_dir = ROOT / "05_referenzarchitektur_RQ2" / "05_03_quality_gates"
    if not req_dir.exists() or not gates_dir.exists():
        return findings

    req_ids: set[str] = set()
    gate_ids: set[str] = set()

    for p in req_dir.glob("R*.yaml"):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                req_ids.add(data.get("id", ""))
                for gref in data.get("linked_gates", []) or []:
                    if gref and gref not in gate_ids:
                        # Collect for later check
                        pass
        except Exception:
            pass

    for p in gates_dir.rglob("G*.yaml"):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                gate_ids.add(data.get("id", ""))
        except Exception:
            pass

    # Forward check: R -> G
    for p in req_dir.glob("R*.yaml"):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            rid = data.get("id", p.stem)
            for gref in data.get("linked_gates", []) or []:
                if gref and gref not in gate_ids:
                    findings.append(Finding(WARNING, "traceability",
                        f"{rid} referenziert Gate '{gref}' das nicht existiert"))
        except Exception:
            pass

    # Reverse check: G -> R
    for p in gates_dir.rglob("G*.yaml"):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            gid = data.get("id", p.stem)
            links = data.get("links", {}) or {}
            for rref in links.get("requirements", []) or []:
                if rref and rref not in req_ids:
                    findings.append(Finding(WARNING, "traceability",
                        f"{gid} referenziert Requirement '{rref}' das nicht existiert"))
        except Exception:
            pass

    return findings


# ── Section 4: Freshness & Activity ──────────────────────────────────────────


def _git_last_commit_date(path: Path) -> datetime | None:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", str(path)],
        capture_output=True, text=True, cwd=ROOT,
    )
    datestr = result.stdout.strip()
    if not datestr:
        return None
    try:
        return datetime.fromisoformat(datestr)
    except ValueError:
        return None


def check_stale_status_files() -> list[Finding]:
    findings: list[Finding] = []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=STALE_DAYS)

    chapter_dirs = [
        "01_einleitung", "02_rigor_theorie_stand_forschung",
        "03_forschungsdesign_methodik", "04_anforderungsanalyse_RQ1",
        "05_referenzarchitektur_RQ2", "06_evaluation_RQ3",
        "07_diskussion", "08_fazit_ausblick",
        "docs/expose", "poc",
    ]

    for cdir in chapter_dirs:
        cpath = ROOT / cdir
        status_file = cpath / "chapter_state.yaml"
        if not status_file.exists():
            status_file = cpath / "_status.yml"
        summaries_dir = cpath / "session_summaries"
        if not status_file.exists() or not summaries_dir.exists():
            continue

        recent_summaries = 0
        for s in summaries_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(s.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "created_at" in data:
                    created = datetime.fromisoformat(str(data["created_at"]))
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                    if created >= cutoff:
                        recent_summaries += 1
                        continue
            except Exception:
                pass
            if s.stat().st_mtime >= cutoff.timestamp():
                recent_summaries += 1

        if recent_summaries == 0:
            continue

        last_status_change = _git_last_commit_date(status_file)
        if last_status_change is None:
            continue
        if last_status_change.tzinfo is None:
            last_status_change = last_status_change.replace(tzinfo=timezone.utc)

        if last_status_change < cutoff:
            findings.append(Finding(WARNING, "freshness",
                f"{cdir}: {recent_summaries} neue Session-Summaries "
                f"in den letzten {STALE_DAYS} Tagen aber chapter_state "
                f"seit {last_status_change.strftime('%Y-%m-%d')} unveraendert"))

    return findings


def check_blob_sync_freshness() -> list[Finding]:
    sync_file = ROOT / ".memory" / "blob_sync_state.json"
    if not sync_file.exists():
        return [Finding(INFO, "freshness",
            ".memory/ nicht vorhanden (gitignored) — Blob-Sync-Check uebersprungen")]
    try:
        mtime = datetime.fromtimestamp(sync_file.stat().st_mtime, tz=timezone.utc)
        age_days = (datetime.now(timezone.utc) - mtime).days
        if age_days > 14:
            return [Finding(WARNING, "freshness",
                f"blob_sync_state.json ist {age_days} Tage alt — reindex.py ausfuehren?")]
    except Exception:
        pass
    return []


# ── Section 5: Cross-Repo Script Lint ────────────────────────────────────────


def check_vault_scripts_syntax() -> list[Finding]:
    vault_path = ROOT.parent / "ai-context-vault" / "scripts"
    if not vault_path.exists():
        return [Finding(INFO, "cross-repo",
            "ai-context-vault/scripts nicht gefunden — Syntax-Check uebersprungen")]
    findings: list[Finding] = []
    for script in sorted(vault_path.glob("*.py")):
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            findings.append(Finding(ERROR, "cross-repo",
                f"{script.name}: Syntax-Fehler: {result.stderr.strip()[:200]}"))
    if not findings:
        findings.append(Finding(INFO, "cross-repo",
            "ai-context-vault Scripts: alle Syntax-Checks OK"))
    return findings


# ── Orchestration ─────────────────────────────────────────────────────────────


ALL_CHECKS = [
    check_session_summaries,
    check_expose_locations,
    check_final_images,
    check_chapter_state_format,
    check_gitignore_rules,
    check_no_unencrypted_pdfs_in_expose,
    check_no_secrets_committed,
    check_requirements_completeness,
    check_gates_completeness,
    check_traceability,
    check_stale_status_files,
    check_blob_sync_freshness,
    check_vault_scripts_syntax,
]


def run_all_checks() -> list[Finding]:
    all_findings: list[Finding] = []
    for check_fn in ALL_CHECKS:
        try:
            all_findings.extend(check_fn())
        except Exception as exc:
            all_findings.append(Finding(ERROR, "audit-internal",
                f"Check {check_fn.__name__} raised: {exc}"))
    return all_findings


def render_issue_body(findings: list[Finding], run_url: str = "") -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    counts = {ERROR: 0, WARNING: 0, INFO: 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    lines = [
        f"## Weekly Audit Report — {date_str}",
        "",
    ]
    if run_url:
        lines.append(f"> Automated audit run: [View workflow run]({run_url})")
        lines.append("")

    lines.extend([
        "### Summary",
        "",
        "| Severity | Count |",
        "|----------|-------|",
        f"| error | {counts[ERROR]} |",
        f"| warning | {counts[WARNING]} |",
        f"| info | {counts[INFO]} |",
        "",
    ])

    for severity, label in [(ERROR, "Errors"), (WARNING, "Warnings"), (INFO, "Info")]:
        items = [f for f in findings if f.severity == severity]
        if not items:
            continue
        lines.append(f"### {label}")
        lines.append("")
        for f in items:
            lines.append(f"- **[{f.category}]** {f.message}")
        lines.append("")

    if counts[ERROR] == 0 and counts[WARNING] == 0:
        lines.extend(["### Alles OK", "", "Keine Fehler oder Warnungen gefunden.", ""])

    lines.append("---")
    lines.append("*Generated by `scripts/weekly_audit.py`. Read-only — no files were modified.*")
    return "\n".join(lines)


def render_terminal(findings: list[Finding]) -> str:
    counts = {ERROR: 0, WARNING: 0, INFO: 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    lines = ["", "=== Weekly Audit Report ===", ""]
    lines.append(f"  Errors:   {counts[ERROR]}")
    lines.append(f"  Warnings: {counts[WARNING]}")
    lines.append(f"  Info:     {counts[INFO]}")
    lines.append("")

    for f in findings:
        icon = {"error": "X", "warning": "!", "info": "-"}[f.severity]
        lines.append(f"  [{icon}] [{f.category}] {f.message}")

    lines.append("")
    if counts[ERROR] > 0:
        lines.append("RESULT: FAILED")
    elif counts[WARNING] > 0:
        lines.append("RESULT: OK (with warnings)")
    else:
        lines.append("RESULT: OK")
    return "\n".join(lines)


def post_issue(findings: list[Finding], repo: str, run_url: str) -> None:
    body = render_issue_body(findings, run_url)
    has_errors = any(f.severity == ERROR for f in findings)

    labels = ["audit"]
    if has_errors:
        labels.append("audit:errors")

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title = f"Weekly Audit — {date_str}"
    if has_errors:
        title += " [ERRORS FOUND]"

    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", title,
        "--body", body,
        "--label", ",".join(labels),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Weekly audit for genaiops-thesis")
    parser.add_argument("--json-out", help="Write findings as JSON to file")
    parser.add_argument("--json-in", help="Read findings from JSON file (skip checks)")
    parser.add_argument("--post-issue", action="store_true", help="Post as GitHub Issue")
    parser.add_argument("--repo", help="GitHub repo (owner/name) for issue creation")
    parser.add_argument("--run-url", default="", help="Actions run URL for issue body")
    args = parser.parse_args()

    if args.json_in:
        raw = json.loads(Path(args.json_in).read_text(encoding="utf-8"))
        findings = [Finding(**f) for f in raw]
    else:
        findings = run_all_checks()

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps([f._asdict() for f in findings], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    if args.post_issue:
        if not args.repo:
            print("ERROR: --repo required for --post-issue", file=sys.stderr)
            return 1
        post_issue(findings, args.repo, args.run_url)
    elif not args.json_out:
        print(render_terminal(findings))

    return 1 if any(f.severity == ERROR for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
