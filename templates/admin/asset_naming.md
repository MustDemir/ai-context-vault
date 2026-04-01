# Asset Naming Convention

## Ziel
Einheitliche Benennung fuer alle Abbildungen und Assets im Projekt.

## Ordnerkonvention
```
{kapitel}/images/work/   → Entwuerfe, Iterationen
{kapitel}/images/final/  → Freigegebene Versionen
```

## Dateinamen-Format
```
<kapitel>_<abschnitt>_<typ>_<kurztitel>_vNN.png
```

- `<kapitel>`: Kapitelnummer (z.B. `kap2`, `kap5`)
- `<abschnitt>`: Abschnittsnummer (z.B. `4_2`, `5_3`)
- `<typ>`: `diag` (Diagramm), `tab` (Tabelle), `flow` (Flowchart), `arch` (Architektur)
- `<kurztitel>`: max. 40 Zeichen, lowercase, `_` oder `-`
- `vNN`: Versionsnummer, immer zwei Stellen (`v01`, `v02`)

## Regeln
- Lowercase, keine Leerzeichen
- Nur `_` oder `-` als Trennzeichen
- Entwuerfe in `work/`, finale Version in `final/`
- `work/` wird per `.gitignore` ausgeschlossen (optional)
