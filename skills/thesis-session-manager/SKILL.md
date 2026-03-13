---
name: thesis-session-manager
description: >
  Orchestriert Session-Start und Session-Ende für die Masterarbeit. Bei Session-Start:
  lädt Kontext via resume.py, zeigt Fortschritt, schlägt nächsten Abschnitt vor und triggert
  Preflight. Bei Session-Ende: orchestriert Post-Session-Check und save.py.
  Trigger bei: "neue session", "session starten", "wo waren wir", "resume", "weiter machen",
  "was steht an", "lass uns anfangen", "wo stehen wir", "guten morgen" (im Thesis-Kontext),
  "fortschritt zeigen", "überblick", "dashboard", "nächster schritt".
  Auch triggern wenn der User nach einer Pause zurückkommt und Kontext braucht,
  oder wenn er fragt was als nächstes zu tun ist.
---

# Thesis Session Manager — Orchestrierung von Start bis Ende

Dieser Skill ist der Einstiegspunkt für jede Arbeitssession an der Masterarbeit. Er sorgt
dafür, dass Claude beim Session-Start den vollständigen Kontext hat (wo stehen wir, was kommt
als nächstes, welche Entscheidungen sind offen) und beim Session-Ende alle Artefakte
konsistent gesichert werden. Ohne diese Orchestrierung startet jede Session mit einem
zeitraubenden "wo waren wir nochmal?"-Moment.

## Session-Start Workflow

Wenn der User eine neue Arbeitssession beginnt (oder nach einer Pause zurückkommt):

### S1 — Kontext laden

Führe `resume.py` aus dem `genaiops-thesis` Repo aus um den aktuellen Stand zu laden:

```bash
python3 scripts/resume.py
```

Das erzeugt u.a. `.memory/resume_context.txt` (Legacy-Cache, gitignored).

**Primär lesen (SSOT):**
- `docs/thesis_state.md` — Entscheidungsregister, Critical Definitions, Gesamtstatus (git-tracked SSOT)
- Alle `*/chapter_state.yaml` — Kapitelspezifischer Status, Decisions, Fortschritt
- `00_admin/README.md` — Projektübersicht und Repo-Struktur

**Fallback** (nur wenn thesis_state.md veraltet oder unvollständig):
- `.memory/resume_context.txt` — kompakter Resume-Cache (recency-first, konfigurierbar via `RESUME_WINDOW_HOURS` / `RESUME_MIN_ITEMS` / `RESUME_MAX_ITEMS`)

Optional: Für semantische Suche nach vorherigen Sessions:
```bash
python3 scripts/search.py "Frage zum Kontext"
```
(Nutzt Azure AI Search + Claude RAG, braucht Azure + Anthropic Keys.)

### S2 — Fortschritts-Dashboard

Erstelle eine kompakte Übersicht des aktuellen Stands:

```markdown
## Thesis-Dashboard: [Datum]

### Gesamtfortschritt
| Kapitel | Status | Fortschritt | Wörter | Budget |
|---------|--------|-------------|--------|--------|
| Kap. 1 Einleitung | ✅ Fertig | 100% | ~2.075W | 3S |
| Kap. 2 Grundlagen | 🔄 In Arbeit | 30% | ~1.200W | 15S |
| ... | ... | ... | ... | ... |

### Offene Entscheidungen
- D_xxx: [Titel] — betrifft Kap. X

### Letzte Session
- Datum: [aus letztem Session Summary]
- Thema: [was wurde gemacht]
- Nächster Schritt: [aus chapter_state next_steps]
```

Daten kommen aus (Priorität):
1. **Primär:** `docs/thesis_state.md` — Gesamtstatus, offene Decisions, Critical Definitions (git-tracked SSOT)
2. **Primär:** Alle `*/chapter_state.yaml` — progress, status, word_count, kapitelspezifische Decisions
3. **Fallback:** `.memory/resume_context.txt` — Legacy-Cache, nur wenn thesis_state.md unvollständig
4. **Optional:** RAG via `python3 scripts/search.py "Frage"` (braucht Azure + Anthropic Keys)

### S3 — Nächsten Abschnitt vorschlagen

Basierend auf den chapter_states und der Gliederung:

1. Finde das Kapitel mit Status "In Arbeit" oder das nächste mit Status "Nicht begonnen"
2. Lies dessen `chapter_state.yaml` → `next_steps` UND `lade_manifest`
3. Zeige die `lade_manifest.pflicht`-Dateien im Dashboard (so weiss der User welche Dateien geladen werden)
4. Prüfe ob ein Preflight-Protokoll existiert (`docs/preflight/PREFLIGHT_KAP*`)

**Ausgabe:**
```
### Empfohlener nächster Schritt:
→ Kap. X.Y — [Titel]
→ Preflight: [✅ vorhanden / ⬜ fehlt — soll ich einen erstellen?]
→ Geschätzte Wörter: [Budget aus Gliederung]
→ Offene Fragen: [aus chapter_state open_questions]
```

### S4 — chapter_state Gesundheits-Check

Prüfe ob das Zielkapitel eine vollständige chapter_state hat ("Definition of Ready"):

**Pflichtfelder:**
- `status` — nicht leer
- `progress` — numerisch
- `current_focus` — beschrieben
- `key_sources` — mindestens 1 Quelle
- `next_steps` — definiert

Wenn Felder fehlen: Warnung ausgeben und vorschlagen, die chapter_state zuerst zu füllen,
bevor mit dem Schreiben begonnen wird. Leere chapter_states (Skelette) sind ein häufiges
Problem bei Kap. 1, 2 und 5–8.

### S5 — Preflight triggern

Wenn kein Preflight-Protokoll für den nächsten Abschnitt existiert:
- Frage den User: "Soll ich den Preflight für Kap. X.Y starten?"
- Bei "ja": Verweise auf den `thesis-preflight` Skill

---

## Session-Ende Workflow

Wenn der User signalisiert dass die Session endet ("fertig für heute", "save session", etc.):

### E1 — Post-Session-Check triggern

Verweise auf den `thesis-post-session` Skill für den vollständigen 6-Punkte-Check (A–F).

### E2 — Save-Workflow ausführen

Nach dem Post-Session-Check:

```bash
python3 scripts/save.py --topic [kapitelthema] --text "[Summary]" --title "[Titel]" --tags "[tags]" --no-llm
```

**Hinweise zu save.py (aktuelle Version):**
- Summary-Engine: 3-Tier-Fallback (Anthropic Claude → Azure OpenAI → local_rules)
- `--no-llm` deaktiviert beide LLM-Engines, nutzt nur lokale Regel-basierte Extraktion
- Blob-Sync ist jetzt OPT-IN: `--blob` Flag oder `SAVE_AUTO_BLOB_SYNC=1` in .env
- Azure Search Push: `--azure` Flag (optional)
- Topic-Routing: auto (keyword-basiert) oder explizit (architecture/requirements/evaluation/methodology)

Nach save.py: Index und Resume werden automatisch aktualisiert (kein separater reindex nötig).

### E3 — Git-Status prüfen

```bash
git status
git diff --stat
```

Falls uncommitted Changes: User fragen ob committet werden soll.
Commit-Message-Format: `feat(kapitel): Kap. X.Y [Titel] — [kurze Beschreibung]`

### E4 — Next-Session Briefing generieren

Erstelle ein kompaktes Briefing für die nächste Session:

```markdown
### Next-Session Briefing
1. chapter_state.yaml lesen: {kapitel_ordner}/chapter_state.yaml
2. Nächster Abschnitt: Kap. X.Y — [Titel]
3. Preflight-Status: [vorhanden/fehlt]
4. Offene Fragen: [Liste]
5. Verbleibendes Seitenbudget: [N] Wörter / [M] Seiten
6. Offene Entscheidungen: [D_xxx Liste]
```

---

## Orchestrierungs-Logik

Dieser Skill orchestriert die anderen 4 Skills. Die Interaktion folgt diesem Muster:

```
Session Start:
  session-manager (S1–S5)
    → schlägt Preflight vor
      → thesis-preflight (P1–P6)
        → User sagt "GO"
          → thesis-writer (Absatz für Absatz)

Session Ende:
  session-manager (E1–E4)
    → triggert Post-Session
      → thesis-post-session (A–F)
        → save.py + git

Bei Bedarf (kapitelübergreifend):
  → thesis-consistency (K1–K6)
```

Der Session-Manager greift nie direkt in den Schreibprozess ein — er stellt nur sicher,
dass der richtige Skill zum richtigen Zeitpunkt aktiviert wird.

---

## Zusätzliche Regeln

- Kein Fließtext produzieren — nur Dashboard, Empfehlungen und Briefings
- Bei Session-Start: Immer zuerst `python3 scripts/resume.py` ausführen
- Bei Session-Ende: Immer `python3 scripts/save.py` anbieten
- Deployer-Scope beachten (Art. 26, nicht Art. 16)
- SOT-Hierarchie: `gliederung_v3.md > Kap. 3 > Kap. 4 > Entscheidungsregister > Exposé`

## Repo-Architektur

```
genaiops-thesis/          ← Alles in einem Repo
  .skills/                ← Diese 6 Skills
  01_einleitung/          ← Kapitel-Ordner mit chapter_state.yaml
  docs/                   ← thesis_state.md, Entscheidungspapiere, Preflight-Protokolle
  scripts/                ← Workflow-Tooling
    resume.py             ← Kontext laden → .memory/ + docs/thesis_state.md
    save.py               ← Session Summary speichern (3-Tier LLM Fallback)
    reindex.py            ← Index neu bauen + optional Azure/Blob sync
    workflow_lib.py       ← Shared Helpers (build_index, push_azure, push_blob)
    update_progress.py    ← README-Fortschrittsbalken aktualisieren
    validate_structure.py ← CI Strukturvalidierung
    weekly_audit.py       ← Wöchentlicher GitHub Issue Audit
  .memory/                ← index.json, resume_context.txt (gitignored, Cache)
  .github/workflows/      ← CI (validate-structure, weekly-audit, update-progress)
```
