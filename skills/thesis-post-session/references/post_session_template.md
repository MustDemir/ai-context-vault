# Post-Session-Protokoll Template

```markdown
## Post-Session-Protokoll: [Datum] — [Thema]

### Geschriebene Abschnitte: Kap. X.Y, X.Z
### Wortanzahl-Delta: +[N] Wörter (Gesamt: [M] Wörter)
### Neue Entscheidungen: D_xxx, D_yyy (oder: keine)
### chapter_state Updates: [✅ aktualisiert / ❌ fehlt noch: ...]
### Session Summary: [✅ gespeichert als [Dateiname] / ❌ fehlt noch]
### Entscheidungsregister: [✅ synchron / ⚠ X Decisions fehlen]
### Exposé-Delta: [✅ keine neue Abweichung / ⚠ Dx neu: ...]
### Konsistenz-Check: [✅ keine Widersprüche / ⚠ Issue: ...]
### Git-Status: [✅ committed / ⬜ uncommitted changes]

### Nächste Session — Startpunkt:
- Nächster Abschnitt: Kap. X.Y
- Offene Fragen: ...
- Preflight bereits vorhanden: [ja/nein]
```

## save.py Aufruf (aus genaiops-thesis Root)

```bash
python3 scripts/save.py --topic [kapitelthema] --text "[Summary-Text]" --title "[Titel]" --tags "[tags]" --no-llm
```

**Optionale Flags:**
- `--blob` → Push Session Summaries zu Azure Blob (oder `SAVE_AUTO_BLOB_SYNC=1`)
- `--azure` → Push Index zu Azure AI Search
- Ohne `--no-llm`: 3-Tier-Fallback (Claude → Azure OpenAI → local_rules)
- Index + Resume werden automatisch aktualisiert.

## Git-Commit Format

```bash
git add [DRAFT-Datei] [chapter_state.yaml] [session_summary] [thesis_state.md]
git commit -m "feat(kapitel): Kap. X.Y [Titel] — [kurze Beschreibung]"
```
