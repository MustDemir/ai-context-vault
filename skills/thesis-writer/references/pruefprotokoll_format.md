# Prüfprotokoll-Format — Referenz

## Tabellenformat

```markdown
### Prüfprotokoll Absatz N — [Thema]

| Zitation | Zotero-Key | BELEG (exakt aus Quelle) | CLAIM (im Text) | MATCH |
|---|---|---|---|---|
| (Autor, Jahr, S. X) | `KEY` | "exakter Satz — Copy-Paste aus Paper" | Paraphrase wie im Fließtext | ✅ / ⚠ / ❌ |
```

## Regeln

1. **BELEG** = exakter Satz aus dem Paper (Copy-Paste, keine Paraphrase der Quelle)
2. **Seitenangabe ist Pflicht** — immer `S. X`
3. **Zotero-Key** für Rückverfolgbarkeit
4. **MATCH-Bewertung:**
   - ✅ = Claim deckt sich inhaltlich mit Beleg
   - ⚠ = Claim weicht ab oder ist interpretativ → Anmerkung + ggf. Korrektur
   - ❌ = Kein Beleg gefunden → Zitation entfernen oder Alternative suchen
5. **Strukturabsätze ohne Zitationen:** "Keine Zitationen (Strukturabsatz). Terminologie konsistent mit Kap. X/Y."
6. **Forward-References prüfen:** Verweis auf Kap. X.Y → existiert oder geplant?
7. **Prüfprotokoll bleibt sichtbar** — wird nicht gelöscht aus der DRAFT-Datei

## Quellen-Lookup-Reihenfolge (Fallback-Kette)

1. `zitations-finder` Skill (Belegstellen im PDF finden)
2. `zotero_search_items` → `zotero_item_fulltext` (Zotero MCP)
3. Uploads-Ordner: `/sessions/.../mnt/uploads/`
4. `elicit-research` Skill / `semanticSearch` MCP (neue Quellen)
5. Wenn nirgends auffindbar: ❌ markieren, Alternative suchen

## Confidence-Scoring (optional)

| Level | Bedeutung | Aktion |
|-------|-----------|--------|
| **Supported** | Beleg deckt Claim vollständig | ✅ Keine Aktion |
| **Partially** | Beleg deckt Claim teilweise | ⚠ Einschränkung im Text formulieren |
| **Unsupported** | Kein Beleg gefunden | ❌ Claim entfernen oder als Hypothese markieren |
| **Uncertain** | Beleg unklar/interpretativ | ⚠ Transparenz: "Interpretation des Autors" |
