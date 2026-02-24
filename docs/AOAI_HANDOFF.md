# AOAI Handoff (kurz)

## Was bereits gemacht wurde
- AOAI-Logik ist im Workflow-Code eingebaut (`scripts/workflow_lib.py`, `scripts/save.py`).
- `save.py` kann Azure OpenAI fuer bessere Summaries nutzen.
- Fallback ist vorhanden: wenn AOAI nicht verfuegbar ist, nutzt `save.py` lokale Regeln (`summary_engine: local_rules`).
- `reindex.py` und `resume.py` sind auf den neuen Save/Summary-Workflow angepasst.

## Auftrag an das naechste KI-Modell
Bitte fuehre diese Schritte in exakt dieser Reihenfolge aus:

1. **Aktuellen Stand erzeugen**
- `python3 scripts/resume.py`
- Ergebnis lesen/sichern als aktueller Projektkontext.

2. **Pruefen, ob AOAI schon aktiv ist (wichtig: zuerst pruefen, nichts blind aendern)**
- `.env` auf folgende Keys pruefen:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_KEY` oder `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_DEPLOYMENT`
- Testlauf:
  - `python3 scripts/save.py --text "AOAI connectivity test" --title "AOAI Test" --topic auto`
- Danach erzeugte YAML pruefen:
  - Wenn `summary_engine: azure_openai` -> AOAI ist bereits verbunden, **keine Neuanbindung noetig**.
  - Wenn `summary_engine: local_rules` oder Fehler -> AOAI nicht aktiv, weiter mit Schritt 3.

3. **Falls nicht aktiv: AOAI mit meinem API-Key verbinden**
- API-Key in `.env` setzen (`AZURE_OPENAI_KEY` oder `AZURE_OPENAI_API_KEY`).
- Endpoint und Deployment korrekt setzen:
  - `AZURE_OPENAI_ENDPOINT=...`
  - `AZURE_OPENAI_DEPLOYMENT=...` (Chat-Deployment)
- Optional Kostenbremse setzen:
  - `AZURE_OPENAI_MAX_INPUT_CHARS=6000`
  - `AZURE_OPENAI_MAX_OUTPUT_TOKENS=300`

4. **Erneut testen und verifizieren**
- `python3 scripts/save.py --text "AOAI final test" --title "AOAI Final" --topic auto`
- In der erzeugten Summary muss stehen: `summary_engine: azure_openai`.

5. **Falls Deployment/Quota fehlt**
- Klar dokumentieren, was fehlt (z. B. kein Chat-Deployment oder Quota=0 TPM).
- Workflow lauffaehig lassen (Fallback `local_rules`), nichts kaputt machen.

## Zielzustand
- `save.py` erzeugt Summaries standardmaessig ueber AOAI.
- Bei AOAI-Problemen faellt der Workflow robust auf lokale Summary-Regeln zurueck.
