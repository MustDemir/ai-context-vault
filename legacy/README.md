# Legacy — Archivierte Versionen

Dieses Verzeichnis enthaelt aeltere Versionen von Scripts und Plugins,
die durch neuere Versionen in `scripts/` und `plugins/` ersetzt wurden.

## Inhalt

### scripts_v1/ (vor 2026-03-13)
Originale Script-Versionen aus der Zwei-Repo-Aera (ai-context-vault als separates Tooling-Repo).
Diese Versionen hatten `REPO_ROOT = parent.parent` auf ai-context-vault bezogen.

- `resume.py` — Nur resume_context.txt, kein thesis_state.md
- `save.py` — Ohne chapter_state-Updates, ohne subprocess
- `reindex.py` — Ohne Input-Blob-Sync
- `workflow_lib.py` — 33KB vs 43KB (ohne lade_manifest, ohne thesis_state.md)

### plugins_v1/
- `thesis-workflow-v2.0.0.plugin` — 5 Skills (ohne thesis-reviewer), ohne lade_manifest

### README_v1.md
Original-README mit Zwei-Repo-Architektur-Dokumentation.

## Ersetzt durch (2026-03-13)

- Scripts v2: Ein-Repo-Architektur, lade_manifest in thesis_state.md, REPO_ROOT korrigiert
- Plugin v2.2.0: 6 Skills, lade_manifest in allen Skills, Ein-Repo-Pfade
- README v2: Portfolio-Showcase mit Skill-Dokumentation
