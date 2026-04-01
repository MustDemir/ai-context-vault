---
name: evidence-matrix-builder
description: >
  Erstellt strukturierte Evidenz-Matrizen für akademische Schreibprojekte im
  Elicit-Research-Table-Stil. Scannt lokale PDF-Quellen, bewertet Abdeckungstiefe
  pro Forschungsfrage, kategorisiert Quellen in 3 Tiers (Core/Empfohlen/Reserviert)
  und generiert sowohl Markdown- als auch HTML-Ausgaben mit dunklem Elicit-Theme.
  Verwende diesen Skill IMMER wenn der User eine Evidenz-Matrix, Quellen-Matrix,
  Quellen-Bewertung, Literatur-Mapping oder Source-Coverage-Analyse erstellen will —
  auch wenn er nur "welche Quellen passen" oder "zeig mir die Abdeckung" sagt.
  Trigger-Phrasen: "evidenz matrix", "evidence matrix", "quellen zuordnen",
  "quellen bewerten", "source coverage", "quellen mapping", "welche papers decken ab",
  "literatur mapping", "research table", "abdeckungsmatrix", "quellen scannen",
  "PDF ordner analysieren", "tier einteilung quellen". Auch triggern wenn der User
  nach einem Preflight fragt welche Quellen zu welchen Absätzen passen, oder wenn
  er systematisch PDFs einem Kapitel zuordnen will.
---

# Evidence-Matrix-Builder

Erstellt Elicit-Style Evidenz-Matrizen, die lokale PDFs systematisch gegen
kapitelspezifische Forschungsfragen bewerten. Das Ergebnis ist eine visuelle
Quellen-Landkarte: Wo ist die Evidenz stark, wo gibt es Lücken, welche Quellen
gehören in welchen Absatz?

## Warum dieser Skill existiert

Beim akademischen Schreiben muss man vor dem ersten Satz wissen: Welche Quellen
decken welche Aspekte meiner Argumentation ab? Ohne diese Übersicht schreibt man
entweder "ins Blaue" oder verbringt Stunden mit manuellem PDF-Durchsuchen.
Die Evidenz-Matrix löst das, indem sie den Elicit Research Table-Ansatz auf
lokale PDF-Sammlungen anwendet.

## Voraussetzungen

- **PDF-Ordner**: Zugang zu einem Ordner mit kuratierten PDFs für das Kapitel
- **Kapitel-Kontext**: Welches Kapitel/welcher Abschnitt wird geschrieben
- **Optional**: Zotero-Zugang für Metadaten, Elicit-Zugang für Gap-Filling

## Workflow

### Phase 1: Kontext erfassen

Ermittle diese Informationen (aus User-Input oder vorhandenem Preflight):

1. **Kapitel-ID** — z.B. "Kap. 2.4.2"
2. **Kapitel-Titel** — z.B. "EU AI Act: Regulatorischer Rahmen"
3. **PDF-Ordner-Pfad** — Wo liegen die kuratierten PDFs?
4. **Absatz-Struktur** — Wie viele Absätze sind geplant, welche Themen?
5. **Wortbudget** — Wie viele Wörter stehen zur Verfügung?

Wenn ein Preflight-Protokoll existiert, extrahiere daraus Absatz-Struktur und
Quellenempfehlungen. Frage den User nur nach fehlenden Informationen.

### Phase 2: Extraktionsfragen definieren

Formuliere 5-8 Extraktionsfragen (Q1-Qn), die als Spalten der Matrix dienen.
Jede Frage soll:

- Einen konkreten inhaltlichen Aspekt des Abschnitts adressieren
- Einem oder mehreren geplanten Absätzen zugeordnet sein
- So formuliert sein, dass die Abdeckungstiefe bewertbar ist

**Format pro Frage:**

```
| ID | Frage | Relevanz für [Kapitel] |
| Q1 | [Beschreibende Frage] | [Absatz X: Thema] |
```

Lege die Fragen dem User zur Bestätigung vor, bevor du fortfährst.

### Phase 3: PDFs scannen und bewerten

Für jedes PDF im angegebenen Ordner:

1. **Lese den Fulltext** (oder zumindest Abstract + Einleitung + Conclusion)
2. **Bewerte die Abdeckung** für jede Extraktionsfrage nach dieser Skala:

| Symbol | Bedeutung | Kriterium |
|--------|-----------|-----------|
| ⬛ | Nicht behandelt | Thema kommt nicht vor |
| 🟡 | Erwähnt | 1-2 Sätze, oberflächlich |
| 🟠 | Moderat | Eigener Abschnitt oder mehrere Absätze |
| 🟢 | Tiefgehend | Zentrales Thema des Papers |

3. **Bestimme die Rolle** der Quelle für den Abschnitt (1 Satz)

Wenn Zotero verfügbar ist, hole den Zotero-Key für jede erkannte Quelle.

### Phase 4: Tier-Kategorisierung

Kategorisiere jede Quelle basierend auf der Matrix:

| Tier | Bedeutung | Kriterium |
|------|-----------|-----------|
| **Tier 1: CORE** | Direkt zitierbar im Abschnitt | ≥2 🟢 oder ≥3 🟠 in relevanten Fragen |
| **Tier 2: EMPFOHLEN** | Konvergente Evidenz, Absicherung | ≥1 🟢 oder ≥2 🟠 |
| **Tier 3: RESERVIERT** | Für andere Kapitel vormerken | Keine starke Abdeckung der aktuellen Fragen, aber relevant für Thesis |

Für Tier-3-Quellen: Vermerke das Ziel-Kapitel und die Begründung, warum die
Quelle dort besser passt. Das verhindert Scope-Drift und sichert die Quelle
für spätere Verwendung.

### Phase 5: Evidenzstärke-Analyse

Analysiere die Matrix spaltenweise (pro Frage):

- **STARK**: ≥2 🟢 + ≥2 🟠 → Gut abgedeckt, solide Beleglage
- **MODERAT**: 1 🟢 + ≥2 🟠 → Machbar, aber eng
- **SCHWACH**: 0 🟢 + ≤2 🟠 → Lücke, ggf. Elicit-Suche oder Scope-Anpassung

Bei SCHWACH-Bewertungen: Schlage dem User vor, ob eine Elicit-Suche sinnvoll
ist (verwende dafür den `elicit-research` Skill) oder ob die Frage angepasst
werden sollte.

### Phase 6: Synthese-Mapping

Erstelle eine Zuordnungstabelle: Welche Quelle belegt welche Aussage in welchem
Absatz? Unterscheide zwischen Primärquelle (direkt zitiert) und Sekundärquelle
(konvergente Evidenz).

**Format:**

```
| Absatz | Aussage | Primärquelle | Sekundärquelle |
|--------|---------|-------------|----------------|
| Abs. 1 | [Claim] | [Autor (Jahr)] | [Autor (Jahr)] |
```

Die Synthese ist das Herzstück für den thesis-writer Skill: Sie definiert die
Belegstruktur, bevor ein einziges Wort geschrieben wird.

### Phase 7: Output generieren

Erzeuge zwei Dateien:

#### 1. Markdown-Datei (`EVIDENZ_MATRIX_[KAPITEL].md`)

Struktur:
```markdown
# Elicit-Style Evidenz-Matrix — [Kapitel]
## [Titel]

**Erstellt:** [Datum] | **Methode:** Elicit Research Table Approach
**Scope:** [N] PDFs ([Ordnername]) + Zotero + [ggf. Elicit Search]

## Spalten-Definitionen (Forschungsfragen)
[Tabelle Q1-Qn]

## Bewertungsskala
[4-stufige Skala]

## Evidenz-Matrix
### Tier 1: CORE-Quellen
[Matrix-Tabelle]
### Tier 2: EMPFOHLENE Quellen
[Matrix-Tabelle]
### Tier 3: RESERVIERT
[Zuordnungstabelle]

## Evidenzstärke pro Frage
[Analyse STARK/MODERAT/SCHWACH]

## Synthese: Quellen-Zuordnung zu Absätzen
[Mapping-Tabelle]

## [Optional] Elicit Search: Zusätzliche Papers
[Falls durchgeführt]

## Offene Fragen
[2-4 Fragen zur User-Entscheidung]
```

#### 2. HTML-Datei (`EVIDENZ_MATRIX_[KAPITEL].html`)

Lese das HTML-Template aus `assets/matrix_template.html` und befülle es mit
den generierten Daten. Das Template verwendet ein dunkles Elicit-Style-Theme
mit farbcodierten Zellen, Stats-Bar und interaktiven Elementen.

Die HTML-Generierung nutzt das Script `scripts/generate_html.py`:

```bash
python3 [skill-path]/scripts/generate_html.py \
  --template [skill-path]/assets/matrix_template.html \
  --data [json-daten] \
  --output [output-pfad]
```

Falls das Script nicht verfügbar ist, generiere das HTML inline basierend auf
dem Template-Stil (CSS-Variablen, Klassen, Tabellenstruktur aus dem Template).

### Phase 8: Speichern und Übergabe

1. Speichere beide Dateien in `docs/preflight/` des Thesis-Repos
2. Zeige dem User die Zusammenfassung: Anzahl PDFs, Tier-Verteilung, Evidenzstärke
3. Weise auf Lücken hin und schlage nächste Schritte vor (GO → thesis-writer)

## Qualitätskriterien

- **Vollständigkeit**: Jedes PDF im Ordner muss bewertet werden
- **Konsistenz**: Bewertungsskala einheitlich anwenden (Zweifel → niedrigere Stufe)
- **Scope-Kontrolle**: Tier-3-Quellen mit klarer Kapitelzuordnung versehen
- **Traceability**: Jede Bewertung muss aus dem PDF-Inhalt ableitbar sein
- **Synthese-Qualität**: Jede geplante Aussage braucht mindestens eine Primärquelle

## Integration mit anderen Skills

- **thesis-preflight** → liefert Absatz-Struktur und initiale Quellenempfehlung
- **evidence-matrix-builder** (dieser Skill) → erstellt die detaillierte Matrix
- **elicit-research** → füllt Lücken bei SCHWACH-bewerteten Fragen
- **thesis-writer** → nutzt Synthese-Mapping als Belegstruktur beim Schreiben

## CSS-Referenz für HTML-Output

Das dunkle Elicit-Theme verwendet folgende Farbcodierung:

| CSS-Klasse | Farbe | Verwendung |
|------------|-------|------------|
| `.cell-deep` | `#22c55e` (grün) | 🟢 Tiefgehend |
| `.cell-mod` | `#f97316` (orange) | 🟠 Moderat |
| `.cell-mention` | `#eab308` (gelb) | 🟡 Erwähnt |
| `.cell-none` | `#374151` (grau) | ⬛ Nicht behandelt |
| `.badge-core` | `#6366f1` (indigo) | Tier 1 |
| `.badge-rec` | `#22c55e` (grün) | Tier 2 |
| `.badge-reserved` | `#8b8fa3` (grau) | Tier 3 |

Hintergrund: `#0f1117`, Oberflächen: `#1a1d27`, Akzent: `#6366f1`
