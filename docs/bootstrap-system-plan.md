# Bootstrap System Plan (Goldstandard Level 3)

## 1. Ziel

Ziel ist es, ein System zu definieren, mit dem neue Projekte reproduzierbar, schnell und konsistent auf Basis des Goldstandards erstellt werden können.

Der Fokus liegt auf:
- Wiederverwendbarkeit
- Konsistenz
- Automatisierbarkeit
- klarer Trennung zwischen generischem Standard und projektspezifischem Inhalt

---

## 2. Ausgangspunkt

Vorhandene Bausteine:

- GitHub-Governance (CI, Rulesets, PR-Workflow)
- GitHub Setup Checklist
- Goldstandard Template Plan
- Master Start Prompt

Diese bilden die Grundlage für das Bootstrap-System.

---

## 3. Varianten zur Projekterstellung

### Variante A – Template Repository

Ein Repository wird als Template verwendet.

Vorteile:
- sofortige Struktur
- CI und .github direkt vorhanden

Nachteile:
- GitHub Rulesets müssen manuell gesetzt werden

---

### Variante B – Master Prompt (Agent-basiert)

Ein Agent erstellt das Projekt auf Basis des Master Start Prompts.

Vorteile:
- flexibel
- kann auf Pflichtenheft reagieren
- hohe Anpassbarkeit

Nachteile:
- erfordert korrekte Prompt-Ausführung

---

### Variante C – Kombination (empfohlen)

- Template Repository für Struktur
- Master Prompt für projektspezifische Inhalte
- GitHub Setup Checklist für Governance

---

## 4. Empfohlener Zielworkflow

1. Neues Repository erstellen (Template oder leer)
2. Struktur übernehmen (Template)
3. GitHub Setup Checklist durchführen
4. Master Start Prompt ausführen
5. Pflichtenheft integrieren
6. Architektur ableiten
7. Feature-basierte Entwicklung starten

---

## 5. Trennung der Verantwortlichkeiten

### Generisch (immer gleich)

- .github Struktur
- CI Workflow
- PR-Regeln
- Dokumentationsstruktur
- Agenten-Regeln
- Git-Workflow

### Projektspezifisch

- Fachlogik
- Datenmodell
- API
- UI
- Integrationen
- Use Cases

---

## 6. Rolle der Agenten

Agenten werden eingesetzt für:

- Strukturaufbau
- Dokumentation
- Codegenerierung
- Refactoring
- Validierung

Agenten dürfen NICHT:

- eigenständig Fachlogik erfinden
- bestehende Architektur überschreiben
- mehrere Themen gleichzeitig verändern

---

## 7. GitHub-Governance im Bootstrap

Nach Erstellung eines neuen Projekts:

- Rulesets setzen
- Status Checks aktivieren
- PR-Zwang aktivieren
- Merge-Strategie definieren

Langfristig:
- Automatisierung via GitHub CLI oder API

---

## 8. Zukunft (Automatisierung)

Mögliche nächste Schritte:

- Template Repository erstellen
- CLI-Tool entwickeln (z. B. „create-project“)
- GitHub API Integration für automatische Rulesets
- Prompt-Bibliothek für verschiedene Projekttypen

---

## 9. Ergebnis

Ein skalierbares System zur Projekterstellung mit:

- klarer Struktur
- reproduzierbarem Setup
- konsistenten Regeln
- effizientem Agenteneinsatz

---

## 6. Abschlussprüfung

- Es existiert genau eine neue Datei:
  docs/bootstrap-system-plan.md
- Keine bestehenden Dateien wurden verändert
- Arbeitsverzeichnis ist sauber

---

## Verboten

- keine Änderungen an anderen Dateien
- kein Commit von Build-Artefakten
- keine weiteren Dokumente erstellen
