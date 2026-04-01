# Roter Faden Tracker — Kapiteluebergreifende Argumentationskette

> **SSOT fuer inhaltliche Konsistenz.** Definiert fuer jedes Kapitel die
> Bruecke zum Vorgaenger, die Kernthese, die Bruecke zum Nachfolger.
> Referenz fuer: thesis-reviewer (R2), thesis-preflight (P2).

---

## Status-Enum (verbindlich)

| Status | Bedeutung |
|--------|-----------|
| `planned` | Noch nicht begonnen |
| `in_progress` | Aktiv in Arbeit |
| `draft` | Erster Entwurf, nicht reviewed |
| `review` | Entwurf geschrieben, Review-Phase |
| `final` | Abgeschlossen und freigegeben |

---

## Kap. 1 — [Titel]

**Status:** `planned` (0%)
**Volltextquelle:** `00_workspace/Fulltext_Kapitel/[Dateiname].docx`

### Bruecke von: (kein Vorgaenger)
[Einstiegspunkt. Problem darstellen und Arbeit motivieren.]

### Kernthese:
[2-3 Saetze: Was ist die zentrale Aussage dieses Kapitels?]

### Bruecke zu Kap. 2:
[Wie leitet dieses Kapitel zum naechsten ueber?]

### Abhaengige Decisions:
- [Decision-ID aus chapter_state.yaml]

### Forward-References:
- [Verweis] → Kap. [N]

---

## Kap. 2 — [Titel]

**Status:** `planned` (0%)
**Volltextquelle:** `00_workspace/Fulltext_Kapitel/[Dateiname].docx`

### Bruecke von Kap. 1:
[Anknuepfung an vorheriges Kapitel]

### Kernthese:
[2-3 Saetze]

### Bruecke zu Kap. 3:
[Ueberleitung]

### Cross-Chapter-Dependencies:
- [Abschnitt X.Y] → [Abschnitt A.B]

---

<!-- Fuer jedes weitere Kapitel wiederholen -->
