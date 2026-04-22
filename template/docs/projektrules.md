# Projektrichtlinien (Template)

Dieses Dokument ist ein **Platzhalter** für projektspezifische Regeln. Es beschreibt **keine** konkrete Fachdomäne und enthält **keine** ERP- oder Branchenlogik.

---

## 1. Ziel des Dokuments

Hier werden die verbindlichen Grundsätze für dieses Projekt festgehalten, sobald sie fachlich und technisch definiert sind.

---

## 2. Ziel des Projekts (festzulegen)

- **Produktvision:** … *(projektspezifisch festzulegen)*
- **Hauptnutzen für Anwender:** … *(projektspezifisch festzulegen)*
- **Abgrenzung:** Was das System **nicht** leisten soll … *(projektspezifisch festzulegen)*

---

## 3. Systemgrenzen

- **Einzugsbereich:** Welche Organisationseinheiten / Prozesse sind abgedeckt? … *(festzulegen)*
- **Schnittstellen:** Welche externen Systeme gibt es? … *(festzulegen)*
- **Nicht-Ziele:** Welche Themen sind explizit außerhalb des Scopes? … *(festzulegen)*

---

## 4. Verantwortlichkeiten

| Rolle / Bereich | Verantwortung (Kurz) |
|-----------------|----------------------|
| Fachlich / Product Owner | … *(festzulegen)* |
| Architektur / Tech Lead | … *(festzulegen)* |
| Entwicklung | … *(festzulegen)* |
| Betrieb / Infrastruktur | … *(festzulegen)* |

---

## 5. Datenhoheit

- **Das führende System für Stammdaten X ist:** … *(projektspezifisch festzulegen)*
- **Das führende System für transaktionale Daten Y ist:** … *(projektspezifisch festzulegen)*
- **Was die Anwendung selbst führt / ableitet:** … *(festzulegen)*
- **Synchronisations- oder Replikationsregeln:** … *(festzulegen)*

---

## 6. Priorisierungslogik (generisch)

- **Objekte, die priorisiert werden können:** z. B. Aufträge, Tickets, Vorgänge … *(Begriffe projektspezifisch definieren)*
- **Kriterien:** Welche Faktoren beeinflussen die Reihenfolge? … *(festzulegen)*
- **Nebenbedingungen:** z. B. Fairness, Deadlines, Abhängigkeiten … *(festzulegen)*
- **Konfliktlösung:** Was passiert bei widersprüchlichen Prioritäten? … *(festzulegen)*

---

## 7. Validierungsprinzipien

- Eingaben werden gegen **definierte Regeln** geprüft (Regeln im Pflichtenheft / Fachkonzept dokumentieren).
- **Fehlerbehandlung:** Nutzer verständlich informieren, technische Details loggen … *(Detail festzulegen)*
- **Keine stillen Korrekturen** ohne Rückmeldung, sofern nicht ausdrücklich gewünscht … *(festzulegen)*

---

## 8. Ergänzung

Dieses Template ist bewusst knapp gehalten. Ergänzen Sie:

- verbindliche Architekturregeln (siehe `architecture.md`),
- Projektstruktur (siehe `projectstructure.md`),
- fachliche Anforderungen (siehe `pflichtenheft.md`),
- Datenmodell (siehe `datenbankmodell.md`).
