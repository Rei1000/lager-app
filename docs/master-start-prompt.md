# Master Start Prompt (Goldstandard)

## Ziel

Dieser Prompt dient dazu, ein neues Projekt auf Basis des definierten Goldstandards zu initialisieren.

Er soll sicherstellen, dass:
- die Projektstruktur konsistent ist
- GitHub-Governance sauber vorbereitet ist
- Dokumentation und Regeln von Anfang an vorhanden sind
- Agenten in einem klar strukturierten Umfeld arbeiten können

---

## Verwendung

Dieser Prompt wird verwendet, wenn ein neues Projekt gestartet wird.

Input für das neue Projekt:
- Projekttitel
- Ziel / Problemstellung
- Zielgruppe
- fachlicher Kontext
- Pflichtenheft oder erste fachliche Anforderungen
- gewünschter Technologie-Stack (falls bereits bekannt)

---

## Anweisung an den Agenten

Initialisiere ein neues Projekt auf Basis des Goldstandards.

WICHTIG:
- Arbeite nicht direkt auf `main`
- Lege für jede Initialisierung einen neuen Branch an
- Verwende Pull Requests
- Verändere nur die Dateien, die für das Initial-Setup notwendig sind

---

## 1. Repository-Grundstruktur anlegen

Erstelle mindestens folgende Struktur:

- .github/
- .cursor/
- docs/
- backend/
- frontend/
- infra/
- scripts/

---

## 2. GitHub-Governance vorbereiten

Erstelle oder übernehme:

- .github/CODEOWNERS
- .github/PULL_REQUEST_TEMPLATE.md
- .github/ISSUE_TEMPLATE/feature.md
- .github/workflows/ci.yml

Ziel:
- Pull-Request-basierte Entwicklung
- reproduzierbare Checks
- klare Verantwortlichkeiten

---

## 3. Dokumentationsstruktur vorbereiten

Erstelle oder übernehme im neuen Projekt:

- docs/projektrules.md
- docs/projectstructure.md
- docs/architecture.md
- docs/pflichtenheft.md
- docs/datenbankmodell.md
- docs/github-setup-checklist.md
- docs/goldstandard-template-plan.md

Falls fachliche Inhalte noch nicht vollständig vorliegen:
- Platzhalter mit klarer Kennzeichnung anlegen
- keine Fachlogik erfinden

---

## 4. Agenten-Regeln vorbereiten

Erstelle oder übernehme:

- .cursor/cursor.rules

Die Regeln müssen sicherstellen:
- Doku ist führend
- keine Fachlogik außerhalb der vorgesehenen Schichten
- TDD-Verpflichtung
- Dokumentationspflicht
- sauberer Git-Workflow
- keine Nebenänderungen in denselben Commit

---

## 5. README vorbereiten

Erstelle eine README mit:

- kurzer Projektbeschreibung
- fachlichem Einstieg
- Strukturüberblick
- Hinweis auf zentrale Dokumente
- technischem Schnellstart (falls schon möglich)

Wenn noch nicht alles bekannt ist:
- klare Platzhalter statt erfundener Details

---

## 6. Pflichtenheft als Startpunkt verwenden

Das Pflichtenheft ist die zentrale Quelle für projektspezifische Inhalte.

Aus dem Pflichtenheft werden abgeleitet:
- Architektur
- Datenmodell
- API-/Use-Case-Struktur
- Domänenbegriffe
- fachliche Regeln

Es ist verboten, ohne Pflichtenheft oder fachliche Vorgaben zentrale Business-Logik zu erfinden.

---

## 7. Technische Initialisierung

Richte die Projektbasis so ein, dass später sauber ergänzt werden kann:

- Backend-Grundstruktur
- Frontend-Grundstruktur
- CI-Grundstruktur
- Dokumentationsgrundlage
- GitHub-Workflow

Falls der konkrete Stack noch nicht feststeht:
- nur neutrale Struktur anlegen
- keine unnötigen Framework-Entscheidungen erzwingen

---

## 8. Git-Workflow

Für die Initialisierung gilt:

- neuer Branch
- klar abgegrenzter Commit
- Pull Request gegen `main`
- Merge bevorzugt per Squash

---

## 9. Qualitätsregeln

Es gilt:

- keine Änderungen außerhalb des Initial-Scopes
- keine unaufgeforderten Features
- keine erfundenen Geschäftsregeln
- keine Vermischung von Struktur, Fachlogik und Refactoring
- keine Build-Artefakte committen

---

## 10. Ergebnis

Nach Ausführung dieses Prompts soll ein neues Projekt vorliegen mit:

- sauberer Grundstruktur
- GitHub-Governance
- Dokumentationsgrundlage
- Agenten-Regeln
- vorbereiteter Entwicklungsumgebung
- klarer Trennung zwischen generischem Standard und projektspezifischem Inhalt

---

## Hinweis

Dieses Dokument ist kein projektspezifisches Pflichtenheft, sondern ein wiederverwendbarer Startprompt für neue Projekte auf Basis des Goldstandards.
