---
name: thesis-writer
description: >
  Akademischer Schreib-Skill für Masterarbeit-Abschnitte mit integrierter Belegprüfung.
  Schreibt Absatz für Absatz mit automatischem Prüfprotokoll (BELEG/CLAIM/MATCH),
  APA7-Enforcement mit Seitenangaben, Zotero-Integration und Wortanzahl-Tracking.
  Trigger bei: "GO", "FINAL", "schreib absatz", "weiter schreiben", "nächster absatz",
  "schreib kap", "text für abschnitt", "fließtext", "formuliere".
  Auch triggern wenn der User nach einem Preflight-Protokoll "GO" sagt — das ist das
  Signal zum Schreiben. Jeder Schreibauftrag für Thesis-Fließtext sollte diesen Skill nutzen.
---

# Thesis Writer — Absatz für Absatz mit Belegprüfung

Dieser Skill steuert den eigentlichen Schreibprozess der Masterarbeit. Das Prinzip:
Nie mehr als einen Absatz auf einmal schreiben, und jeden Absatz sofort mit einem
Prüfprotokoll absichern. So entstehen keine unbelegten Behauptungen und die
Zitationsqualität bleibt durchgehend hoch.

## Referenz-Dateien laden (PFLICHT bei jedem Aufruf)

Vor dem ersten Absatz diese Referenz-Dateien lesen:
- `.skills/thesis-writer/references/apa7_rules.md` — APA7-Zitationsregeln und Pflichtformat
- `.skills/thesis-writer/references/pruefprotokoll_format.md` — Pruefprotokoll-Tabellenformat und MATCH-Regeln

## Voraussetzung

Ein Preflight-Protokoll für den Zielabschnitt sollte existieren (thesis-preflight Skill).
Falls nicht vorhanden: kurz prüfen ob die Kerninfos (Argumentationsstruktur, Pflicht-Zitate,
Seitenbudget) bekannt sind, sonst zuerst Preflight durchführen.

### Kontext via lade_manifest

Lies VOR dem ersten Absatz das `lade_manifest` aus dem Zielkapitel-`chapter_state.yaml`:

- **`pflicht`-Dateien** → als VOLLTEXT laden. Enthaelt die DOCXs, DRAFTs, Entscheidungspapiere und Uni-Vorgaben die fuer dieses Kapitel inhaltlich relevant sind.
- **`kontext`-Kapitel** → nur deren `chapter_state.yaml` lesen (Ueberblick ohne Volltext).

So sind alle Abhaengigkeiten, Definitionen und Entscheidungen geladen BEVOR der erste Absatz geschrieben wird. Das lade_manifest ergaenzt die bestehenden Schreib-Regeln — es ersetzt sie nicht.

## Schreib-Workflow pro Absatz

### Schritt 1: Absatz schreiben

Schreibe **einen** Absatz Fließtext. Dabei beachten:

**Stil-Regeln:**
- Akademischer Stil, sachlich, keine Ich-Form
- Nummerierung nur bis 2. Ebene (1, 1.1 — NICHT 1.1.1)
- Sub-Gliederungen als **Fettdruck**, nicht als Heading
- Keine formalen Überleitungen ("Im Folgenden wird...")
- SRH-Leitfaden: "Formales Vorgehen NICHT explizit beschreiben"
- Hohe Zitationsdichte — jede Behauptung belegen

**Scope-Guards:**
- Deployer-Scope (Art. 26 EU AI Act) — keine Provider-Perspektive (Art. 16)
- Retirement-Phase ist ausgeschlossen
- Terminologie konsistent mit Critical Definitions in `docs/thesis_state.md`
  - "Enforcement" ≠ "Dokumentation"
  - Quality Gate = automatisierter, evidenzbasierter Kontrollpunkt
  - Referenzarchitektur = Enterprise-tauglich, cloud-native, CI/CD/CT-integriert

**Zitations-Regeln:**
- Jedes Zitat: APA7 mit Seitenangabe → `(Autor, Jahr, S. X)`
- Zotero-Key muss nachschlagbar sein
- Keine erfundenen Quellen/DOIs/Seiten
- Unsicherheit klar als Hypothese markieren

### Schritt 2: Prüfprotokoll erstellen

Direkt nach dem Absatz eine Prüfprotokoll-Tabelle einfügen:

```markdown
### Prüfprotokoll Absatz N — [Thema]

| Zitation | Zotero-Key | BELEG (exakt aus Quelle) | CLAIM (im Text) | MATCH |
|---|---|---|---|---|
| (Autor, Jahr, S. X) | `KEY` | "exakter Satz — Copy-Paste aus Paper" | Paraphrase wie im Fließtext | ✅ / ⚠ / ❌ |
```

**Regeln für das Prüfprotokoll:**

1. **BELEG = exakter Satz** aus dem Paper (Copy-Paste, keine Paraphrase der Quelle)
2. **Seitenangabe ist Pflicht** — immer `S. X`
3. **Zotero-Key** für Rückverfolgbarkeit angeben
4. **MATCH-Bewertung:**
   - ✅ = Claim deckt sich inhaltlich mit Beleg
   - ⚠ = Claim weicht ab oder ist interpretativ → Anmerkung + ggf. Korrektur
   - ❌ = Kein Beleg gefunden → Zitation entfernen oder Alternative suchen
5. **Strukturabsätze ohne Zitationen:** "Keine Zitationen (Strukturabsatz). Terminologie konsistent mit Kap. X/Y."
   - Forward-References prüfen: Verweis auf Kap. X.Y → existiert oder geplant?
6. **Prüfprotokoll bleibt sichtbar** — wird nicht gelöscht aus der DRAFT-Datei

**Quellen-Lookup-Reihenfolge:**
1. `zitations-finder` Skill — Belegstellen im PDF finden und verifizieren (IMMER zuerst!)
2. `zotero_search_items` → `zotero_item_fulltext` (Zotero MCP)
3. Uploads-Ordner: `/sessions/.../mnt/uploads/`
4. `elicit-research` Skill (Elicit-Suche fuer neue/fehlende Quellen)
5. `semanticSearch` MCP Tool (Semantic Scholar)
6. `mcp__claude_ai_Consensus__search` (Consensus API)

### Schritt 3: MATCH-Bewertung prüfen

- Bei ⚠: Absatz anpassen oder Anmerkung für User
- Bei ❌: Absatz korrigieren BEVOR der nächste Absatz geschrieben wird
- Keine ❌ dürfen stehen bleiben

### Schritt 4: Wortanzahl + Budget tracken

Nach jedem Absatz:
- Aktuelle Wortanzahl des Abschnitts berechnen
- Gegen Seitenbudget aus `gliederung_v3.md` prüfen (1 Seite ≈ 300 Wörter)
- Bei >90% Budget: User warnen
- Wortanzahl in BILANZ-Block am Ende des Abschnitts aktualisieren

### Schritt 5: In DRAFT-Datei speichern

**DRAFT-Pfad-Aufloesung (3-Stufen-Schema):**

Die DRAFT-Datei wird in dieser Reihenfolge gesucht/erstellt:
1. **Primaer:** `{kapitel_ordner}/arbeitsmaterial/drafts/Kap{N}_{Thema}_DRAFT.md`
2. **Fallback:** `{kapitel_ordner}/KAPITEL_{N}_GESAMT_DRAFT.md` (Root des Kapitelordners)
3. **Legacy (nur lesen):** `{kapitel_ordner}/legacy/*_DRAFT.md`

**Beim Schreiben:**
- Neue DRAFTs IMMER in Stufe 1 anlegen: `{kapitel_ordner}/arbeitsmaterial/drafts/`
- Falls der Ordner `arbeitsmaterial/drafts/` nicht existiert: anlegen
- Bestehende DRAFTs an ihrem aktuellen Ort weiterschreiben (nicht verschieben)

**Beispiele:**
- Kap. 1: `01_einleitung/arbeitsmaterial/drafts/Kap1_Einleitung_DRAFT.md` (existiert)
- Kap. 4: `04_anforderungsanalyse_RQ1/KAPITEL_4_GESAMT_DRAFT.md` (Fallback, existiert)
- Kap. 6 neu: `06_evaluation_RQ3/arbeitsmaterial/drafts/Kap6_Evaluation_DRAFT.md` (neu anlegen)

- Absatz + Pruefprotokoll in die aufgeloeste DRAFT-Datei einfuegen
- BILANZ-Block aktualisieren: `~XW (≈Y Seiten), Z Quellen`
- Naechsten Absatz nur auf User-Anfrage ("weiter", "naechster absatz", "GO")

---

## BILANZ-Block Format

Am Ende jedes Abschnitts steht ein BILANZ-Block:

```markdown
---
**BILANZ Kap. X.Y:** ~[Wörter]W (≈[Seiten] Seiten), [Anzahl] Quellen + [Anzahl] Gesetzestexte
```

Nach jedem neuen Absatz aktualisieren.

---

## Abschnitts-Header Format

Am Anfang der DRAFT-Datei steht ein Header mit Status aller Abschnitte:

```markdown
---
Status: Kap. X.1 ✅ | Kap. X.2 🔄 | Kap. X.3 ⬜
Wörter: ~[Gesamt]W (≈[Seiten] Seiten) — Budget: [Budget aus Gliederung]
---
```

---

## Confidence-Scoring (optional, bei komplexen Claims)

Für besonders wichtige oder umstrittene Claims kann ein erweitertes Scoring verwendet werden:

| Level | Bedeutung | Aktion |
|-------|-----------|--------|
| **Supported** | Beleg deckt Claim vollständig | ✅ Keine Aktion |
| **Partially** | Beleg deckt Claim teilweise | ⚠ Einschränkung im Text formulieren |
| **Unsupported** | Kein Beleg gefunden | ❌ Claim entfernen oder als Hypothese markieren |
| **Uncertain** | Beleg unklar/interpretativ | ⚠ Transparenz: "Interpretation des Autors" |
