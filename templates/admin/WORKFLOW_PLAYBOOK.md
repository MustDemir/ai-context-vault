# Workflow Playbook (Projektgedaechtnis)

## Ziel
Kompakte, strukturierte Session-Summaries speichern (statt Vollchat),
damit jedes KI-Modell schnell dort weitermachen kann, wo du aufgehoert hast.

## Prinzip
- Source of Truth = Dateien im Repo
- Keine langen Chat-Logs als Dauerkontext
- Jede Session endet mit kurzer Summary in YAML + Reindex

## End-of-Session Workflow
```bash
python3 scripts/save.py --input <NOTES_FILE> --source claude
git add -A && git commit -m "save session"
python3 scripts/reindex.py
```

## Neue Session starten
```bash
python3 scripts/resume.py
```
Output in den neuen Chat einfuegen.

## Topic-Routing (automatisch)
`scripts/save.py` erkennt Thema automatisch (`--topic auto`) und speichert in:
- Thema A -> `<kapitel_A>/session_summaries/`
- Thema B -> `<kapitel_B>/session_summaries/`
- Sonstiges -> `99_inbox_unsorted/session_summaries/`

## Azure RAG Reindex
`scripts/reindex.py` macht lokalen Index + Resume neu.
Azure Push mit `--azure` wenn konfiguriert:
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_ADMIN_KEY`
- `AZURE_SEARCH_INDEX_NAME`

Blob Sync mit `--blob`:
- `AZURE_STORAGE_ACCOUNT`
- `AZURE_STORAGE_KEY`
- optional: `AZURE_BLOB_CONTAINER`

Budget-Schutz:
- Blob-Sync nur neue/geaenderte Dateien (Hash-Vergleich)
- Sync-Status lokal in `.memory/blob_sync_state.json`

## Azure OpenAI Summary (optional)
`scripts/save.py` nutzt Azure OpenAI wenn gesetzt:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_DEPLOYMENT`

Lokal erzwingen: `python3 scripts/save.py --no-llm ...`
