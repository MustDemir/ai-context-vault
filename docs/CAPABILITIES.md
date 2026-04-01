# Capabilities — Plugins, Skills & MCP Connectors

> Stand: 2026-04-01 | Plattform: Claude.ai (Cowork Mode)

Dieses Dokument listet alle selbst gebauten und extern genutzten Capabilities,
die im täglichen Workflow aktiv eingesetzt werden.

---

## Eigene Plugins (self-built, im Vault getrackt)

### thesis-workflow v2.3.0

Akademischer Workflow-Support für DSR-Masterarbeit. 7 Skills, die den gesamten
Arbeitszyklus abdecken — von Session-Start über Evidenz-Support bis
Post-Session-Verifikation.

| Skill | Funktion |
|-------|----------|
| thesis-session-manager | Session-Orchestrierung (Start S1–S5, Ende E1–E4) |
| thesis-preflight | 6-Punkt Pre-Check vor jedem Arbeitsabschnitt (P1–P6) |
| thesis-evidence-support | Belegprüfung und Quellenverifikation (BELEG/CLAIM/MATCH) |
| thesis-post-session | Post-Session-Verifikation (A–F), Repo-Konsistenz |
| thesis-consistency | 7-Dimensionen Cross-Chapter-Konsistenz (K1–K7) |
| thesis-reviewer | Akademische Volltext-Bewertung gegen SSOTs und Uni-Vorgaben (R1–R6) |
| evidence-matrix-builder | Strukturierte Evidenz-Matrizen im Elicit-Research-Table-Stil |

### consensus-plugin v0.1.0

Akademisches Recherche-Toolkit via Consensus API (220M+ Peer-Reviewed Papers).
MCP-Connector: `https://mcp.consensus.app/mcp`

| Skill | Funktion |
|-------|----------|
| consensus-evidence-finder | Evidenz-Discovery + Gap-Filling (3 Workflows: Chapter Research, Gap Fill, Related Work) |
| consensus-grant-finder | NIH-Grant-Recherche mit 5-Facet Positioning |
| literature-review-helper | Systematische Literaturrecherche mit Suchstrategie und DOCX-Output |
| recommended-reading-list | Kuratierte Leselisten aus Syllabi |

### elicit-research v0.1.0

Zugang zur Elicit API (138M+ Papers). Suche, Reports, systematische Reviews.

| Skill | Funktion |
|-------|----------|
| elicit-research | Paper-Suche und Research Reports via Elicit API |

### related-work-comparator v0.1.0

Systematischer Feature-Matrix-Vergleich eines Papers gegen die eigene Arbeit.

| Skill | Funktion |
|-------|----------|
| related-work-comparator | Strukturierter Vergleich mit Abgrenzungs-Matrix |

### zitations-finder v0.1.0

Belegstellen in PDFs lokalisieren und APA-7-konforme Zitate generieren.

| Skill | Funktion |
|-------|----------|
| zitations-finder | PDF-basierte Belegstellen-Suche + APA-7 In-Text-Zitate |

---

## MCP Connectors (aktiv in Cowork-Projekten)

| Connector | Typ | Zweck |
|-----------|-----|-------|
| Consensus | HTTP | Akademische Paper-Suche (220M+ Papers) |
| Elicit | HTTP | Paper-Suche + Research Reports (138M+ Papers) |
| Zotero | HTTP | Literaturverwaltung, Fulltext-Zugriff, Metadaten |
| Semantic Scholar | HTTP | Semantische Paper-Suche |
| Chrome Control | Local | Browser-Automatisierung |
| Desktop Commander | Local | Dateisystem, Prozesse, Suche |
| PDF Tools | Local | PDF-Analyse, Formular-Befüllung, Extraktion |
| Microsoft Docs | HTTP | Microsoft-Dokumentation-Suche |

---

## Plattform-Skills (Anthropic built-in, nicht im Vault getrackt)

Für Referenz — diese sind Teil der Cowork-Plattform und werden nicht versioniert:

docx, xlsx, pptx, pdf, doc-coauthoring, web-artifacts-builder, theme-factory,
algorithmic-art, canvas-design, brand-guidelines, slack-gif-creator, mcp-builder,
internal-comms, skill-creator, schedule

---

## Quellen-Lookup-Kette (Prioritätsreihenfolge)

```
1. zitations-finder     → Belegstelle direkt im PDF verifizieren
2. Zotero MCP           → Metadaten + Fulltext aus Bibliothek
3. elicit-research      → Elicit-Suche (138M+ Papers)
4. Semantic Scholar MCP → Semantische Suche
5. Consensus MCP        → Consensus-Suche (220M+ Papers)
```
