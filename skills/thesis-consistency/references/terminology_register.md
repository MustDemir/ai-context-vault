# Terminologie-Register — Critical Definitions

Diese Definitionen sind verbindlich für die gesamte Arbeit. Bei Abweichungen in einem
DRAFT muss der Text korrigiert werden, nicht die Definition.

Quelle: `docs/thesis_state.md` → Critical Definitions

## Pflicht-Begriffe

| Begriff | Definition | Abgrenzung | Quelle |
|---------|-----------|-----------|--------|
| **Quality Gate** | Automatisierter, evidenzbasierter Kontrollpunkt in CI/CD/CT | ≠ manuelle Dokumentation, ≠ Review-Meeting | D_xxx |
| **Enforcement** | Technische Durchsetzung von Policies via Code | ≠ Dokumentation, ≠ Empfehlung | D_xxx |
| **Referenzarchitektur** | Enterprise-tauglich, cloud-native, CI/CD/CT-integriert | ≠ Proof-of-Concept, ≠ theoretisches Modell | Exposé |
| **Deployer** | Betreiber eines KI-Systems (Art. 26 EU AI Act) | ≠ Provider (Art. 16), ≠ Nutzer | EU AI Act |
| **GenAIOps** | Operationalisierung generativer KI-Systeme | ≠ MLOps (nur klassisches ML), ≠ LLMOps (nur LLMs) | D_xxx |
| **Policy-as-Code** | Compliance-Regeln als maschinenlesbare Policies | ≠ Checkliste, ≠ Richtliniendokument | D_xxx |

## Scope-Guards

- **Deployer-Scope (Art. 26):** Die Arbeit betrachtet AUSSCHLIESSLICH die Perspektive des
  Betreibers (Deployers). Provider-Pflichten (Art. 16) werden nicht behandelt.
- **Retirement-Ausschluss:** Die Retirement/Decommissioning-Phase ist explizit ausgeschlossen.
- **Keine formalen Überleitungen:** SRH-Leitfaden verbietet "Im Folgenden wird..."

## Aktualisierung

Wenn in `docs/thesis_state.md` eine neue Critical Definition hinzugefügt wird,
muss sie auch hier eingepflegt werden. Dieses Register ist eine Kopie für schnellen
Zugriff — die SOT bleibt `docs/thesis_state.md`.
