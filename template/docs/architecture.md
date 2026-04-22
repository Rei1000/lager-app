# Architektur (Template)

Dieses Dokument erklärt die **architektonischen Grundprinzipien** für Projekte, die auf diesem Template aufsetzen. Es enthält **keine** konkreten Geschäftsbeispiele und keine produktspezifischen Abläufe.

---

## 1. Domain-Driven Design (DDD)

- Das **Fachmodell** steht im Mittelpunkt: Begriffe, Regeln und Grenzen der Domäne prägen die Softwarestruktur.
- **Ubiquitous Language:** Dieselben Begriffe in Dokumentation, Code und Gesprächen verwenden (Begriffe projektspezifisch definieren).
- **Bounded Contexts:** Wo nötig, klar abgegrenzte Kontexte mit expliziten Schnittstellen (grenzen projektspezifisch festlegen).

---

## 2. Hexagonale Architektur (Ports & Adapter)

- Der **Kern** (Domain + Application) ist von technischen Details entkoppelt.
- **Ports** definieren, was der Kern von außen braucht (z. B. Persistenz, Zeit, Benachrichtigung).
- **Adapter** implementieren diese Ports mit konkreter Technik (Datenbank, HTTP, Dateisystem, …).
- Austausch von Infrastruktur soll möglich sein, **ohne** die Fachlogik zu ändern.

---

## 3. Schichtenmodell

| Schicht | Verantwortung |
|---------|----------------|
| **Domain** | Regeln, Invarianten, Domänenmodelle; keine Abhängigkeit nach außen. |
| **Application** | Use Cases, Transaktionsgrenzen, Orchestrierung; nutzt Domain und Ports. |
| **Ports** | Verträge / Interfaces zwischen Kern und Technik. |
| **Adapter** | Implementierung der Ports; technische Details. |
| **API** | HTTP-/RPC-Schicht; Mapping Request/Response, **keine** Fachlogik. |
| **Frontend** | Darstellung, Eingabe, Navigation; kommuniziert mit der API. |

Abhängigkeiten sollen **nach innen** zeigen: API und Adapter hängen vom definierten Kern-Kontrakt ab, nicht umgekehrt.

---

## 4. Datenfluss (vereinfacht)

1. **Anfrage** erreicht die API (z. B. HTTP).
2. Die API übergibt an einen **Application-Use-Case** (Validierung auf Transportebene, dann fachliche Orchestrierung).
3. Der Use Case arbeitet mit der **Domain** und ruft bei Bedarf **Ports** auf.
4. **Adapter** erfüllen die Ports (z. B. Lesen/Schreiben persistenter Daten).
5. Die Antwort wandert zurück durch Application und API zum Client / Frontend.

---

## 5. Trennungen (verbindlich)

- **Domain** kennt weder Datenbank noch Web-Framework.
- **Application** enthält keine UI- und keine HTTP-Details.
- **API** mappt Protokolle und Statuscodes, **ohne** Geschäftsregeln zu „verstecken“.
- **Frontend** zeigt Zustände und löst Aktionen aus, **ohne** serverseitige Regeln zu duplizieren.

---

## 6. Ergänzung im Projekt

Nach Festlegung der Domäne:

- konkrete Kontexte und Module benennen,
- Schnittstellen und Datenflüsse verfeinern,
- Nicht-funktionale Anforderungen (Sicherheit, Performance, Verfügbarkeit) ergänzen,

und die Ergebnisse in diesem Dokument oder in verlinkten Detaildokumenten festhalten.
