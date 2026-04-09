# AI Context Vault

**Context engineering toolkit for structured, searchable AI-assisted project work**

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![Azure](https://img.shields.io/badge/Azure-Blob%20%2B%20AI%20Search-0078D4.svg)](https://azure.microsoft.com)

---

## What This Is

A toolkit that turns AI chat sessions into structured, versioned, searchable artifacts. Built to solve three recurring problems in long-running AI-assisted projects: unstructured outputs, isolated knowledge silos across models, and missing audit trails.

The repo contains CLI scripts for session persistence and cloud sync, a plugin system with custom Cowork skills for workflow support, and MCP connector integrations for academic research tooling.

**Core use case:** Daily workflow support for a DSR master's thesis — session management, evidence handling, consistency checks, and structured quality assurance across 100+ sessions.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│               Local Machine                       │
│                                                   │
│  Git Repo (YAML + MD) ──→ resume.py ──→ AI Model │
│       ↑                            ↓              │
│  save.py ←── AI Chat + Cowork Skills + MCP       │
└──────────────────┬───────────────────────────────┘
                   │ reindex.py
┌──────────────────▼───────────────────────────────┐
│               Azure Cloud                         │
│  Blob Storage (versioned artifacts)               │
│  AI Search (full-text + semantic, cross-session)  │
└──────────────────────────────────────────────────┘
```

**Key design decisions:** YAML over database (git-diffable, human-readable), Azure as model-agnostic cloud layer, local-first context generation (resume.py costs $0 API), SHA-256 dedup for incremental sync.

---

## Daily Workflow

```
resume.py → load context → work in AI session → save.py → git commit → reindex.py (optional)
```

Within each session, Cowork skills provide structured support:

```
Session Start (session-manager S1–S5)
    → Preflight Check (P1–P6) before each work section
    → Evidence support: source lookup, consistency checks, review scaffolding
    → Post-Session Verification (A–F)
Session End (session-manager E1–E4) → save.py
```

The human author controls all content decisions. Skills provide context loading, checklists, evidence verification, and quality assurance scaffolding.

---

## Plugins & Skills

5 custom-built Cowork plugins with 14 skills total. All `.plugin` files included. Full inventory: [docs/CAPABILITIES.md](docs/CAPABILITIES.md)

| Plugin | Version | Skills | Purpose |
|--------|---------|--------|---------|
| **thesis-workflow** | 2.3.0 | 7 | Session orchestration, preflight, evidence support, review, consistency |
| **consensus-plugin** | 0.1.0 | 4 | Academic paper search via Consensus (220M+ papers) |
| **elicit-research** | 0.1.0 | 1 | Paper search + research reports via Elicit (138M+ papers) |
| **related-work-comparator** | 0.1.0 | 1 | Structured paper comparison with feature matrix |

### MCP Connectors

Consensus, Elicit, Zotero, Semantic Scholar — integrated via Model Context Protocol for direct tool access from within AI sessions. Details in [CAPABILITIES.md](docs/CAPABILITIES.md).

### Source Lookup Chain (priority order)

```
zitations-finder → Zotero MCP → Elicit → Semantic Scholar → Consensus
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `save.py` | End-of-session: generates structured YAML summary, auto-routes to correct folder, optional blob sync |
| `resume.py` | Session start: parses all chapter states into compact context (~600 tokens vs. ~30k full load) |
| `reindex.py` | Syncs artifacts to Azure Blob + AI Search (SHA-256 dedup) |
| `search.py` | Cross-session RAG queries via Azure AI Search + Claude |
| `workflow_lib.py` | Shared logic, lade_manifest support, path resolution |

Supporting scripts: `create_index.py`, `validate_structure.py`, `weekly_audit.py`, `weekly_branch_drift.py`, `update_progress.py`, `workflow_smoke.py`

---

## Context Efficiency

| Approach | Tokens/Session | 10 Sessions |
|----------|---------------:|------------:|
| Full project context | ~30,000 | 300,000 |
| resume.py (structured) | ~600 | 6,000 |
| + lade_manifest (focused) | ~400 | 4,000 |

`lade_manifest` is a per-chapter dependency declaration in `chapter_state.yaml`: `pflicht` (load as fulltext) and `kontext` (metadata only). This keeps context windows focused without losing cross-chapter awareness.

---

## Project Structure

```
ai-context-vault/
├── scripts/           CLI toolkit (save, resume, reindex, search, CI)
├── skills/            7 skill source definitions (thesis-workflow v2.3.0)
│   └── SKILL_OVERVIEW.md
├── plugins/           Distributable .plugin files (ZIP)
│   ├── thesis-workflow.plugin
│   ├── consensus-plugin.plugin
│   ├── elicit-research.plugin
│   ├── related-work-comparator.plugin
│   └── zitations-finder.plugin
├── templates/         Starter-Kit for new projects
│   ├── admin/         SOURCE_OF_TRUTH, WORKFLOW_PLAYBOOK, gliederung, asset_naming
│   ├── docs/          roter_faden_tracker, pruefkatalog, WORKFLOW_OUTPUT_SCHEMA
│   └── chapter/       chapter_state.yaml template, project_scaffold guide
├── docs/
│   ├── CAPABILITIES.md        Full plugin/skill/MCP inventory
│   ├── ARCHITECTURE.md        Design decisions
│   ├── ACADEMIC_VALIDATION.md Research backing
│   └── diagrams/              Technical overview diagrams
├── examples/          YAML templates and sample artifacts
├── legacy/            Archived older versions
├── .github/workflows/ CI: structure validation, weekly audit
└── .memory/           Local cache (gitignored)
```

---

## Quick Start

```bash
git clone https://github.com/MustDemir/ai-context-vault.git
cd ai-context-vault
pip install -r requirements.txt
cp .env.example .env   # Add Azure credentials

# Daily use
python3 scripts/resume.py                           # Load context
python3 scripts/save.py --input notes.txt --topic auto  # Save session
python3 scripts/reindex.py --azure --blob           # Sync to cloud
python3 scripts/search.py "query across all sessions"   # RAG search
```

**Plugin installation:** Drag `.plugin` files from `plugins/` into Claude.ai Cowork.

---

## Cross-Model Compatibility

The toolkit is model-agnostic. Azure Cloud serves as neutral storage layer — artifacts are accessible from Claude, ChatGPT, Gemini, or any other model via `resume.py` output. No vendor lock-in.

Cowork plugins and MCP connectors are Claude-specific. The underlying data (YAML, Markdown, git history) remains portable.

---

## License

MIT — see [LICENSE](LICENSE)

## Author

**Mustafa Demir** — SRH Fernhochschule, M.Sc. Digital Management & Transformation

[![GitHub](https://img.shields.io/badge/GitHub-MustDemir-181717?style=flat&logo=github)](https://github.com/MustDemir)
