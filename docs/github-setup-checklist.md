# GitHub Setup Checklist (Goldstandard)

## Ziel
Diese Checkliste beschreibt alle notwendigen Schritte, um ein neues Repository auf den definierten Goldstandard zu bringen.

---

## 1. Repository erstellen
- Neues Repository auf GitHub anlegen
- Sichtbarkeit festlegen (private/public)
- Default Branch: main

---

## 2. Template-Struktur übernehmen
- Repository aus Template erstellen ODER Struktur manuell übernehmen:
  - .github/
  - docs/
  - backend/
  - frontend/
  - .cursor/

---

## 3. GitHub Ruleset konfigurieren (Branch Protection)

Pfad:
Settings → Rules → Rulesets → New branch ruleset

Name:
main-protection

Einstellungen:

### Target
- Include default branch (main)

### Branch rules
- Restrict deletions ✅
- Require linear history ✅

### Pull Request Regeln
- Require a pull request before merging ✅
- Required approvals: 1
- Require conversation resolution before merging ✅

### Status Checks
- Require status checks to pass ✅
- Required check:
  - basic-checks

### Weitere Regeln
- Block force pushes ✅

---

## 4. CI überprüfen
- .github/workflows/ci.yml vorhanden
- Workflow läuft erfolgreich auf:
  - Push
  - Pull Request

---

## 5. PR-Workflow sicherstellen
- PR Template vorhanden (.github/PULL_REQUEST_TEMPLATE.md)
- CODEOWNERS vorhanden
- Merge Strategy:
  - Squash and merge

---

## 6. Branch-Workflow
- Kein direktes Arbeiten auf main
- Für jede Änderung:
  - neuen Branch erstellen
  - PR öffnen
  - nach Merge Branch löschen

---

## 7. Erste Validierung
- Test-PR erstellen
- CI läuft durch
- Merge funktioniert nur über PR
- Status Checks greifen korrekt

---

## 8. Optional (zukünftige Automatisierung)
- GitHub CLI / API zur Automatisierung der Rulesets
- Template Repository für sofortige Wiederverwendung

---

## Ergebnis
Nach Durchführung dieser Schritte entspricht das Repository dem definierten Goldstandard für:
- Codequalität
- Zusammenarbeit
- Nachvollziehbarkeit
- Skalierbarkeit
