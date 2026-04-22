# Goldstandard Template Plan

## 1. Ziel des Goldstandards

Dieses Projekt dient als Referenz für einen wiederverwendbaren Entwicklungsstandard.

Ziel ist es:
- neue Projekte schnell aufzusetzen
- konsistente Struktur und Qualität sicherzustellen
- Agenten effizient einsetzen zu können
- Governance (CI, PR, Regeln) automatisch zu etablieren

---

## 2. Wiederverwendbare Bausteine (Template)

Diese Komponenten sollen in jedes neue Projekt übernommen werden:

### Repository-Struktur
- .github/
- .cursor/
- docs/
- backend/
- frontend/

### GitHub Governance
- CODEOWNERS
- PR Template
- Issue Templates
- CI Workflow
- Branch Protection Regeln (manuell oder automatisiert)

### Entwicklungsregeln
- PR-Zwang
- Branch pro Feature
- Squash Merge
- CI muss grün sein

### Dokumentationsstruktur
- docs/ als zentrale Wissensbasis

---

## 3. Projektspezifische Bausteine

Diese Inhalte sind NICHT Teil des Templates:

- Fachlogik (z. B. Lager, ERP, Disposition)
- Datenmodelle
- API-Strukturen
- Business-Regeln
- UI-Logik
- externe Integrationen (z. B. Sage)

Diese werden pro Projekt neu definiert.

---

## 4. Ableitung aus dem Pflichtenheft

Ein neues Projekt entsteht aus:

Input:
- Pflichtenheft
- Zielgruppe
- Use Cases
- Fachdomäne

Daraus werden generiert:
- Architektur (docs/architecture.md)
- Datenmodell (docs/datenbankmodell.md)
- Feature-Struktur
- API-Design

---

## 5. Zielstruktur eines neuen Projekts

Ein neues Projekt sollte initial enthalten:

- GitHub Setup (CI + PR Regeln)
- Dokumentationsstruktur
- leere Backend-/Frontend-Struktur
- vorbereitete .cursor Regeln
- Platzhalter für Architektur-Dokumente

---

## 6. Standard-Startprozess für neue Projekte

1. Template Repository verwenden
2. GitHub Setup durchführen (Checkliste)
3. Pflichtenheft einpflegen
4. Agent zur Architektur-Erstellung verwenden
5. Feature-basierte Entwicklung starten

---

## 7. Rolle von Agenten

Agenten werden eingesetzt für:

- Strukturaufbau
- Dokumentation
- Refactoring
- Codegenerierung
- Validierung gegen Regeln

Nicht für:
- unkontrollierte Änderungen
- Überschreiben bestehender Architektur

---

## 8. Nächste Schritte

- Erstellung eines Template-Repositories
- Automatisierung der GitHub Rulesets
- Erstellung eines Master-Startprompts
- Integration von Setup-Skripten (optional)

---

## Ergebnis

Dieses Dokument definiert die Grundlage für ein skalierbares, wiederverwendbares Projektsystem auf Basis dieses Goldstandards.
