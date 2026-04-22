# Template Repository File Map (Goldstandard)

## Ziel

Diese Datei definiert die konkrete Struktur des zukünftigen Template-Repositories.

Sie legt fest:

- welche Dateien enthalten sind
- welche direkt übernommen werden
- welche als Platzhalter dienen
- welche projektspezifisch angepasst werden müssen

---

## 1. Root-Struktur

| Pfad | Typ | Status | Beschreibung |
|------|-----|--------|-------------|
| README.md | Datei | Platzhalter | Projektbeschreibung, wird projektspezifisch ersetzt |
| .gitignore | Datei | Übernehmen | Standard Ignore-Regeln |
| .env.example | Datei | Platzhalter | Beispiel für Umgebungsvariablen |

---

## 2. .github/

| Pfad | Typ | Status | Beschreibung |
|------|-----|--------|-------------|
| .github/workflows/ci.yml | Datei | Übernehmen | Standard CI Pipeline |
| .github/PULL_REQUEST_TEMPLATE.md | Datei | Übernehmen | PR Struktur |
| .github/CODEOWNERS | Datei | Anpassen | Verantwortlichkeiten pro Projekt |

---

## 3. docs/

| Pfad | Typ | Status | Beschreibung |
|------|-----|--------|-------------|
| docs/github-setup-checklist.md | Datei | Übernehmen | Setup-Anleitung |
| docs/master-start-prompt.md | Datei | Übernehmen | Agent Startpunkt |
| docs/bootstrap-system-plan.md | Datei | Übernehmen | Systemarchitektur |
| docs/template-repository-spec.md | Datei | Übernehmen | Template Definition |
| docs/project-scope.md | Datei | Platzhalter | Projektspezifische Anforderungen |

---

## 4. Backend (backend/)

| Pfad | Typ | Status | Beschreibung |
|------|-----|--------|-------------|
| backend/ | Ordner | Platzhalter | Backend-Struktur |
| backend/tests/ | Ordner | Übernehmen | Teststruktur |
| requirements.txt / pyproject.toml | Datei | Anpassen | Abhängigkeiten |

---

## 5. Frontend (frontend/)

| Pfad | Typ | Status | Beschreibung |
|------|-----|--------|-------------|
| frontend/ | Ordner | Platzhalter | Frontend-App |
| package.json | Datei | Anpassen | Abhängigkeiten |
| tsconfig.json | Datei | Übernehmen | TypeScript Setup |

---

## 6. .cursor/

| Pfad | Typ | Status | Beschreibung |
|------|-----|--------|-------------|
| .cursor/rules/ | Ordner | Übernehmen | Coding-/Agent-Regeln |
| .cursor/prompts/ | Ordner | Übernehmen | Wiederverwendbare Prompts |

---

## 7. Klassifikation

### Übernehmen
- CI
- GitHub-Struktur
- Regeln
- Dokumentations-Framework

### Platzhalter
- README
- Projektbeschreibung
- Architekturdetails

### Anpassen
- Abhängigkeiten
- Services
- Domain-Logik

---

## Ergebnis

Das Template-Repository ist:

- sofort nutzbar
- klar strukturiert
- flexibel für neue Projekte
- kompatibel mit dem definierten Goldstandard

---

## 4. Abschlussprüfung

- git status prüfen
→ Es darf nur diese Datei neu sein:

docs/template-repository-file-map.md

- KEIN Commit
- KEIN Push
- KEINE PR
