# Template Repository Specification

## 1. Ziel

Dieses Dokument beschreibt die konkrete Zielstruktur eines wiederverwendbaren Template-Repositories auf Basis des definierten Goldstandards.

Das Template-Repository soll dazu dienen, neue Projekte mit konsistenter Struktur, Dokumentation, Governance und Agentenfähigkeit schnell zu initialisieren.

---

## 2. Ziel des Template-Repositories

Das Template-Repository soll enthalten:

- eine wiederverwendbare Repository-Struktur
- vorbereitete GitHub-Governance-Dateien
- vorbereitete Agenten-Regeln
- vorbereitete Dokumentationsstruktur
- neutrale technische Platzhalter für Backend und Frontend

Es soll NICHT enthalten:

- projektspezifische Fachlogik
- projektspezifische Business-Regeln
- projektspezifische Integrationen
- projektspezifische Screenshots oder PDFs

---

## 3. Verzeichnisstruktur des Template-Repositories

Das Template soll mindestens folgende Struktur enthalten:

- .github/
- .cursor/
- docs/
- backend/
- frontend/
- infra/
- scripts/

Optional:
- uploads/
- backups/

nur wenn dies bewusst Teil des Standards ist.

---

## 4. Inhalte, die 1:1 übernommen werden sollen

Diese Bestandteile sollen unverändert in neue Projekte übernommen werden:

- .github/CODEOWNERS
- .github/PULL_REQUEST_TEMPLATE.md
- .github/ISSUE_TEMPLATE/feature.md
- .github/workflows/ci.yml
- docs/github-setup-checklist.md
- docs/goldstandard-template-plan.md
- docs/master-start-prompt.md
- docs/bootstrap-system-plan.md

---

## 5. Inhalte, die als Template-Platzhalter angelegt werden sollen

Diese Dateien sollen im Template vorhanden sein, aber projektspezifisch befüllt werden:

- README.md
- docs/projektrules.md
- docs/projectstructure.md
- docs/architecture.md
- docs/pflichtenheft.md
- docs/datenbankmodell.md
- .cursor/cursor.rules

Diese Dateien müssen klar kennzeichnen:
- was generisch ist
- was pro Projekt ersetzt oder ergänzt werden muss

---

## 6. Backend- und Frontend-Platzhalter

### Backend
Das Template soll eine neutrale Backend-Grundstruktur enthalten, z. B.:

- backend/src/
- backend/tests/

ohne projektspezifische Domain-Logik.

### Frontend
Das Template soll eine neutrale Frontend-Grundstruktur enthalten, z. B.:

- frontend/src/
- frontend/tests/

ohne projektspezifische UI oder Fachprozesse.

---

## 7. GitHub-Governance im Template

Im Template enthalten:
- .github-Dateien
- CI-Grundworkflow

Nicht im Template automatisch enthalten:
- GitHub Rulesets / Branch Protection in den Repo-Settings

Diese müssen:
- über Checkliste manuell gesetzt
oder
- später automatisiert via GitHub CLI / API eingerichtet werden

---

## 8. Rolle des Pflichtenhefts

Das Pflichtenheft ist der zentrale projektspezifische Input.

Aus dem Pflichtenheft werden abgeleitet:
- Architektur
- Datenmodell
- Fachbegriffe
- API-/Use-Case-Struktur
- Feature-Struktur
- Regeln in `.cursor/cursor.rules`

Das Template liefert nur die Struktur, nicht den fachlichen Inhalt.

---

## 9. Rolle des Master Start Prompts

Der Master Start Prompt dient dazu, aus:
- Template-Struktur
- GitHub-Setup
- Pflichtenheft

ein konkretes neues Projekt abzuleiten.

Das Template und der Prompt ergänzen sich:
- Template = statische Basis
- Prompt = projektspezifische Initialisierung

---

## 10. Grenzen des Template-Repositories

Das Template-Repository ersetzt nicht:
- fachliche Analyse
- Pflichtenheft
- Architekturentscheidungen im Detail
- projektspezifische technische Wahlentscheidungen

Es ist ein Startsystem, kein fertiges Produkt.

---

## 11. Zielzustand

Nach Verwendung des Template-Repositories soll ein neues Projekt besitzen:

- professionelle Grundstruktur
- reproduzierbare Governance
- vorbereitete Dokumentation
- klare Trennung zwischen Standard und projektspezifischem Inhalt
- gute Voraussetzungen für Agenten und Teamarbeit

---

## 12. Nächster Schritt

Auf Basis dieser Spezifikation können später erstellt werden:

- ein echtes GitHub Template Repository
- ein Bootstrap-Skript
- eine GitHub-CLI-gestützte Setup-Automatisierung
- eine Prompt-Bibliothek für verschiedene Projekttypen

---

## 6. Abschlussprüfung

- Es existiert genau eine neue Datei:
  docs/template-repository-spec.md
- Keine bestehenden Dateien wurden verändert
- Arbeitsverzeichnis ist sauber

---

## Verboten

- keine Änderungen an anderen Dateien
- kein Commit von Build-Artefakten
- keine weiteren Dokumente erstellen

---

## 7. Nur Erstellung, noch kein Commit

- Datei erstellen
- Branch korrekt vorbereiten
- keine weiteren Git-Schritte durchführen
