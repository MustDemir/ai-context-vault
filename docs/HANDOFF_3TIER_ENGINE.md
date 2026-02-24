# Übergabebericht: 3-Tier Summary Engine

**Datum:** 2026-02-24
**Commit:** `1fc7dcf` – `feat: add 3-tier summary engine (Claude → AOAI → local rules)`
**Status:** Code fertig, gepusht — `.env` fehlt noch

---

## Was wurde gemacht

### Ausgangslage

`save.py` konnte Session-Zusammenfassungen nur über zwei Wege erzeugen:

1. **Azure OpenAI** (GPT-4o-mini) — als primäre LLM-Engine
2. **Lokale Regeln** — einfaches Regex/Keyword-Parsing als Fallback

**Problem:** Der Nutzer hat kein Azure OpenAI Resource, weil GPT-4o-mini in der Region West Europe nicht verfügbar ist. Damit war die LLM-Engine faktisch nicht nutzbar — jede Zusammenfassung fiel auf die einfachen lokalen Regeln zurück.

### Lösung: 3-Tier Fallback

Es wurde **Claude Haiku** (Anthropic API) als primäre Summary-Engine eingebaut. Der `ANTHROPIC_API_KEY` war bereits für `search.py` und `extract_yamls.py` im Projekt vorhanden.

**Neue Fallback-Kette:**

```
save_session_summary(use_llm=True)
  └─ 1. if anthropic_configured():
       └─ summarize_with_claude()      → summary_engine: "anthropic_claude"
  └─ 2. elif azure_openai_configured():
       └─ summarize_with_azure_openai() → summary_engine: "azure_openai"
  └─ 3. else: lokale Regeln            → summary_engine: "local_rules"
```

### Geänderte Dateien

| Datei | Änderung |
|---|---|
| `scripts/workflow_lib.py` | 3 neue Funktionen + Fallback-Logik in `save_session_summary()` |
| `.env.example` | Neue optionale Konfigurationsvariablen für Claude |
| `README.md` | save.py-Beschreibung aktualisiert |

### Neue Funktionen in `workflow_lib.py`

**1. `anthropic_configured()` (Zeile 166)**
- Prüft ob `ANTHROPIC_API_KEY` in `.env` oder Umgebung gesetzt ist
- Gibt `True/False` zurück

**2. `_anthropic_chat_complete()` (Zeile 171)**
- Raw HTTP-Call an `https://api.anthropic.com/v1/messages`
- Nutzt `urllib.request` (keine externe SDK-Abhängigkeit)
- Konfigurierbar: Model, Temperature, Max Tokens
- Default-Model: `claude-haiku-4-5-20251001`

**3. `summarize_with_claude()` (Zeile 215)**
- Spiegelt die Struktur von `summarize_with_azure_openai()`
- Prompt: Session-Text → JSON mit `title`, `summary_bullets`, `decisions`, `next_steps`
- Input wird auf `ANTHROPIC_MAX_INPUT_CHARS` (default: 6000) begrenzt
- Robustes Parsing: Markdown-Fences werden entfernt, Dedup, Längenbegrenzung

**4. Fallback-Logik in `save_session_summary()` (Zeile 367)**
- Sequentieller Try: Claude → AOAI → local
- Fehler werden in `summary_engine_error` protokolliert
- `engine_name` wird im YAML gespeichert

### Neue Konfigurationsvariablen (.env.example)

```env
# Bereits vorhanden:
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE

# Neu (optional):
ANTHROPIC_SUMMARY_MODEL=claude-haiku-4-5-20251001
ANTHROPIC_MAX_INPUT_CHARS=6000
ANTHROPIC_MAX_OUTPUT_TOKENS=300
ANTHROPIC_TEMPERATURE=0.1
```

---

## Was ist das Problem

### `.env` Datei existiert nicht

Die `.env` Datei wurde **nie erstellt**. Es existiert nur `.env.example`. Ohne `.env` findet kein Script den `ANTHROPIC_API_KEY`, und alle LLM-Engines fallen auf `local_rules` zurück.

### Beweis (Test vom 24.02.2026)

```
$ python3 scripts/save.py --text "Test" --title "Test" --topic auto
Summary engine: local_rules    ← Fallback, weil kein API Key
```

```
$ python3 -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"
None                           ← Key nicht gefunden
```

```
$ ls .env
ls: .env: No such file or directory   ← Datei fehlt
```

### Lösung

```bash
cd /Users/mustafademir/Projects/ai-context-vault
cp .env.example .env
# Dann in .env den echten ANTHROPIC_API_KEY eintragen
```

Danach wird `save.py` automatisch Claude Haiku nutzen:

```
$ python3 scripts/save.py --text "Test" --title "Test" --topic auto
Summary engine: anthropic_claude   ← Erwartet nach .env-Setup
```

---

## Zusammenfassung

| Was | Status |
|---|---|
| `anthropic_configured()` | Implementiert (Zeile 166) |
| `_anthropic_chat_complete()` | Implementiert (Zeile 171) |
| `summarize_with_claude()` | Implementiert (Zeile 215) |
| 3-Tier Fallback-Logik | Implementiert (Zeile 367) |
| `.env.example` aktualisiert | Fertig |
| `README.md` aktualisiert | Fertig |
| Git commit + push | Fertig (`1fc7dcf`) |
| `.env` Datei erstellen | **Offen — muss manuell gemacht werden** |
| End-to-End Test mit Claude API | **Offen — wartet auf `.env`** |

### Kosteneinschätzung

| Engine | Kosten pro Summary |
|---|---|
| Claude Haiku | ~$0.001 |
| Azure OpenAI (gpt-4o-mini) | ~$0.001 |
| Lokale Regeln | $0 |

---

**Nächster Schritt:** `.env` Datei erstellen und `ANTHROPIC_API_KEY` eintragen, dann `save.py` erneut testen.
