---
name: thesis-consistency
description: >
  Übergreifender Konsistenz-Check für die gesamte Masterarbeit. Scannt alle chapter_states,
  DRAFT-Dateien und Entscheidungsregister auf Widersprüche, Terminologie-Inkonsistenzen,
  Budget-Überschreitungen, tote Forward-References und Exposé-Drift.
  Trigger bei: "konsistenz prüfen", "cross-check", "terminologie check", "widersprüche finden",
  "alles konsistent?", "budget check", "gesamtübersicht", "forward references prüfen",
  "drift check", "ist alles stimmig", "kapitelübergreifend prüfen".
  Auch triggern wenn der User nach einem größeren Schreibblock (mehrere Abschnitte/Kapitel)
  eine Gesamtprüfung machen will oder vor einem Review-Meilenstein steht.
---

# Thesis Consistency Check — Kapitelübergreifende Qualitätssicherung

Dieser Skill deckt Inkonsistenzen auf, die innerhalb eines einzelnen Kapitels unsichtbar
bleiben: unterschiedliche Begriffe für dasselbe Konzept, widersprüchliche Designentscheidungen
zwischen Kapiteln, Seitenbudget-Überschreitungen, und Verweise ins Leere. Je mehr Kapitel
geschrieben sind, desto wichtiger wird dieser Check.

## Referenz-Dateien laden (PFLICHT bei jedem Aufruf)

Vor dem Konsistenz-Check diese Referenz-Datei lesen:
- `.skills/thesis-consistency/references/terminology_register.md` — Verbindliche Terminologie und Scope-Guards

## Wann diesen Skill nutzen

- Nach Abschluss eines Kapitels (bevor das nächste beginnt)
- Vor Review-Meilensteinen (Betreuer-Feedback, Peer-Review)
- Wenn Unsicherheit besteht ob eine Entscheidung andere Kapitel betrifft
- Auf explizite Anfrage ("ist alles stimmig?")

## Kontext-Setup via lade_manifest

Beim Consistency-Check werden ALLE Kapitel gescannt — das lade_manifest hilft dabei,
die **Abhaengigkeitsrichtung** zu verstehen:

- Lies ALLE `chapter_state.yaml` und extrahiere deren `lade_manifest`
- `pflicht`-Verknuepfungen zeigen harte Abhaengigkeiten (Volltext-Konsistenz pruefen)
- `kontext`-Verknuepfungen zeigen weiche Abhaengigkeiten (chapter_state-Konsistenz reicht)
- Asymmetrische Abhaengigkeiten aufdecken: Wenn Kap. A Kap. B in pflicht hat, aber Kap. B Kap. A nicht kennt → moegliche Luecke

Das lade_manifest ergaenzt die bestehenden Konsistenz-Dimensionen — es ersetzt sie nicht.

## Die 7 Konsistenz-Dimensionen

### K1 — Terminologie-Konsistenz

Lade die Critical Definitions aus `docs/thesis_state.md` und prüfe alle Volltexte
(`00_workspace/Fulltext_Kapitel/*.docx`) sowie DRAFT-Dateien (Fallback):

**Pflicht-Prüfungen:**
- "Quality Gate" = automatisierter, evidenzbasierter Kontrollpunkt (nicht nur Dokumentation)
- "Enforcement" ≠ "Dokumentation" — werden diese Begriffe korrekt unterschieden?
- "Referenzarchitektur" = Enterprise-tauglich, cloud-native, CI/CD/CT-integriert
- Deployer-Scope (Art. 26) konsistent — nirgends Provider-Perspektive (Art. 16)?
- Retirement-Phase nirgends behandelt?

**Vorgehen:**
1. `docs/thesis_state.md` lesen → Critical Definitions extrahieren
2. Alle DRAFT-Dateien scannen (3-Stufen-Schema pro Kapitel):
   `{kap}/arbeitsmaterial/drafts/Kap*_DRAFT.md` → `{kap}/KAPITEL_*_DRAFT.md` → `{kap}/legacy/*_DRAFT.md`
3. Für jeden Critical-Definition-Begriff: Wird er überall gleich verwendet?
4. Abweichungen als Tabelle ausgeben

**Ausgabe:**
```
| Begriff | Definition (SOT) | Kap. | Verwendung im Text | Status |
|---------|-------------------|------|-------------------|--------|
| Quality Gate | automatisiert, evidenzbasiert | 3.2 | "dokumentarischer Kontrollpunkt" | ⚠ Abweichung |
```

### K2 — Entscheidungs-Kohärenz

Prüfe ob Entscheidungen (D_xxx) über Kapitel hinweg konsistent sind:

1. `docs/thesis_state.md` → Alle D_xxx Entscheidungen laden
2. `docs/ENTSCHEIDUNGSPAPIER_KAP{N}.md` → Kapitelspezifische Decisions (N = alle vorhandenen, z.B. KAP4, KAP5)
3. `docs/SSOT_ROTER_FADEN_ANALYSE.md` → Cross-chapter Impacts
4. Alle `chapter_state.yaml` → `decisions` Feld prüfen

**Prüfungen:**
- Gibt es D_xxx die in mehreren Kapiteln referenziert werden mit unterschiedlicher Interpretation?
- Gibt es widersprüchliche Decisions (z.B. D_4.6 vs. D_5.3)?
- Sind alle Decisions die ein Kapitel betreffen auch in dessen chapter_state dokumentiert?
- Gibt es "verwaiste" Decisions (in thesis_state aber in keinem Kapitel referenziert)?

### K3 — Seitenbudget-Aggregation

Berechne die Gesamtseitenrechnung über alle Kapitel:

1. `00_admin/gliederung_v3.md` → Budget pro Kapitel (SOLL)
2. Alle DRAFT-Dateien → Wortanzahl pro Kapitel (IST)
3. Umrechnung: 1 Seite ≈ 300 Wörter

**Ausgabe:**
```
| Kapitel | Budget (Seiten) | IST (Wörter) | IST (Seiten) | Delta | Status |
|---------|----------------|-------------|-------------|-------|--------|
| Kap. 1 | 3 | 2.075 | ~6,9 | +3,9 | ⚠ Über Budget |
| Kap. 2 | 15 | 0 | 0 | -15 | ⬜ Nicht begonnen |
| GESAMT | 80 | ... | ... | ... | ... |
```

Warnung bei >10% Überschreitung pro Kapitel und bei Gesamtüberschreitung.

### K4 — Forward-Reference-Validation

Finde alle Querverweise in allen DRAFT-Dateien und prüfe ob die Ziele existieren:

**Muster suchen:**
- `(vgl. Kap. X.Y)` oder `(siehe Kap. X.Y)`
- `(vgl. Abschnitt X.Y)` oder `(s. Abschnitt X.Y)`
- Verweise auf Tabellen, Abbildungen, Anhänge

**Für jede Referenz prüfen:**
- Existiert der Zielabschnitt in der Gliederung (`gliederung_v3.md`)?
- Existiert bereits ein DRAFT dafür?
- Wenn nicht: Ist er als "geplant" in einem chapter_state markiert?

**Ausgabe:**
```
| Quelle | Verweis auf | Ziel existiert? | Status |
|--------|-----------|----------------|--------|
| Kap. 1.3, Abs. 2 | Kap. 4.2 | ✅ DRAFT vorhanden | OK |
| Kap. 3.1, Abs. 5 | Kap. 7.3 | ⬜ Geplant (chapter_state) | Warnung |
| Kap. 4.1, Abs. 3 | Kap. 5.4 | ❌ Nicht in Gliederung | Fehler |
```

### K5 — Entscheidungspapiere-Drift + chapter_state-Drift

Vergleiche Entscheidungspapiere und chapter_states mit den tatsaechlichen Kapiteltexten:

**Quellen laden:**
1. `docs/ENTSCHEIDUNGSPAPIER_KAP{N}.md` → Alle vorhandenen Entscheidungspapiere
2. Alle `{kapitel_ordner}/chapter_state.yaml` → Kapitel-Status und Decisions
3. `00_admin/gliederung_v3.md` → Aktuelle Struktur
4. Alle bisherigen Volltexte in `00_workspace/Fulltext_Kapitel/*.docx`

**Entscheidungspapiere-Drift pruefen:**
- Werden alle D_xxx aus ENTSCHEIDUNGSPAPIER_KAP{N} im zugehoerigen Kapiteltext umgesetzt?
- Gibt es Entscheidungen im Text, die NICHT im Entscheidungspapier dokumentiert sind?
- Widersprechen sich Entscheidungen zwischen verschiedenen Entscheidungspapieren?

**chapter_state-Drift pruefen:**
- Stimmt `status` und `progress` mit dem tatsaechlichen Textumfang ueberein?
- Stimmt `word_count` mit dem Volltext ueberein?
- Sind alle im Text behandelten Themen in `done` aufgefuehrt?
- Gibt es `next_steps` die bereits im Text bearbeitet wurden?
- Sind `decisions` in chapter_state synchron mit ENTSCHEIDUNGSPAPIER_KAP{N}?

**Kumulative Drift-Tabelle:**
```
| Kapitel | Quelle | Aspekt | Dokumentiert | Tatsaechlich | Drift | Aktion |
|---------|--------|--------|-------------|-------------|-------|--------|
| Kap. 4 | ENTSCH_KAP4 | D_4.6 Scope | Deployer-only | Deployer-only | ✅ Kein Drift | — |
| Kap. 5 | chapter_state | progress | 60% | 80% | ⚠ Drift | chapter_state updaten |
```

Jede undokumentierte Abweichung erzeugt eine Warnung mit Empfehlung:
- Fehlende Entscheidung → D_xxx im Entscheidungspapier anlegen
- Veralteter chapter_state → chapter_state.yaml aktualisieren

### K6 — DSR-Kohärenz

Prüfe ob der Design-Science-Research-Rahmen konsistent durchgehalten wird:

- Werden Hevner (2004), Peffers et al. (2007) und vom Brocke et al. (2020) konsistent zitiert?
- Ist jedes Kapitel korrekt einer DSR-Phase zugeordnet?
- Stimmen die Rigor-Cycle-Referenzen (Wissensbasis) mit den tatsächlichen Quellen überein?
- Relevance-Cycle: Ist die Praxisrelevanz in jedem Kapitel erkennbar?

---

## Ausgabeformat: Konsistenz-Report

```markdown
## Konsistenz-Report: [Datum]

### K1 Terminologie: [✅ konsistent / ⚠ X Abweichungen]
[Tabelle mit Abweichungen]

### K2 Entscheidungen: [✅ kohärent / ⚠ X Konflikte]
[Tabelle mit Konflikten]

### K3 Seitenbudget: [✅ im Rahmen / ⚠ X Kapitel über Budget]
[Budget-Tabelle]

### K4 Forward-References: [✅ alle valide / ❌ X tote Verweise]
[Referenz-Tabelle]

### K5 Entscheidungspapiere-/chapter_state-Drift: [✅ kein Drift / ⚠ X Abweichungen]
[Drift-Tabelle]

### K6 DSR-Kohärenz: [✅ konsistent / ⚠ Issues]
[Findings]

### Zusammenfassung:
- Kritische Issues (sofort beheben): ...
- Warnungen (vor nächstem Kapitel klären): ...
- Empfehlungen (bei Gelegenheit): ...
```

---

### K7 — Stil- und Formalia-Compliance (Uni-Vorgaben)

Lade den Pruefkatalog aus `docs/uni_vorgaben/pruefkatalog.md` und pruefe alle Volltexte:

1. Alle Volltexte in `00_workspace/Fulltext_Kapitel/*.docx` scannen nach:
   - Verbotene Formulierungen (PK-V1 bis PK-V6)
   - Gliederungstiefe max. 4 Ebenen (PK-F2)
   - Zitationsdichte pro Absatz (PK-Z3)
2. Gesamt-Seitenbudget aggregieren: 60–80 Textseiten (PK-F3)
3. SRH 50/30/20 Bewertungskriterien-Alignment pruefen

**Ausgabe:**
```
| Kapitel | Verbotene Formulierungen | Gliederungstiefe | Zitationsdichte | Seitenbudget | Status |
|---------|-------------------------|-----------------|----------------|-------------|--------|
```

---

## Zusaetzliche Regeln

- Dieser Skill produziert KEINEN Fliesstext — nur den Konsistenz-Report
- **Primaeres Pruefobjekt:** Volltexte in `00_workspace/Fulltext_Kapitel/*.docx`
- Fallback DRAFT-Pfad-Aufloesung (3-Stufen pro Kapitel):
  1. `{kapitel_ordner}/arbeitsmaterial/drafts/Kap{N}_*_DRAFT.md`
  2. `{kapitel_ordner}/KAPITEL_{N}_*_DRAFT.md`
  3. `{kapitel_ordner}/legacy/*_DRAFT.md` (nur lesen)
- SOT-Hierarchie beachten: `gliederung_v3.md > Kap. 3 > Kap. 4 > Entscheidungsregister > Expose`
- Bei Widerspruechen: hoeherrangige Quelle gewinnt, Abweichung dokumentieren
- Roter Faden pruefen via `docs/roter_faden_tracker.md`
- Report speichern als `docs/consistency/CONSISTENCY_REPORT_[DATUM].md`
