# Projektrichtlinien – Lager-App für Stangenmaterial

---

## 1. Ziel dieses Dokuments

Dieses Dokument definiert die verbindlichen Regeln für:

- Architektur
- Implementierung
- Code-Struktur
- Tests
- Dokumentation
- Zusammenarbeit (inkl. Agentenverhalten)
  Zusätzlich sind folgende Dokumente verbindlich:

- docs/pflichtenheft.md
- docs/architecture.md
- docs/datenbankmodell.md
- docs/projectstructure.md

Dieses Dokument ist die **zentrale Referenz für alle Umsetzungen**.

---

## 2. Grundprinzipien

Dieses Projekt folgt strikt:

- Domain-Driven Design (DDD)
- hexagonaler Architektur
- testgetriebener Entwicklung (TDD)
- API-first Backend
- klarer Trennung von Frontend, Backend und ERP

Diese Prinzipien sind **nicht verhandelbar**.

---

## 3. Fachliche Grundregeln

### 3.1 ERP-Führungsprinzip

Das ERP ist führend für:

- Bestände
- Materialstammdaten
- reale Aufträge

Die App darf:

- keine Bestände direkt im ERP verändern
- keine parallele Lagerführung aufbauen

---

### 3.2 Reservierung

- Reservierungen existieren nur in der App
- sie blockieren verfügbaren Bestand
- sie sind nicht gleichbedeutend mit ERP-Buchungen

---

### 3.3 Priorisierung

- Priorisierung erfolgt materialbezogen
- Reihenfolge beeinflusst Verfügbarkeit
- Berechnung erfolgt sequenziell

#### Verbindliche Regel zur Repriorisierung (vollständige Datenmenge)

- Eine Repriorisierung (Änderung der Auftragsreihenfolge je Material) darf **ausschließlich** auf der **vollständigen** Menge der offenen App-Aufträge dieses Materials erfolgen.
- An das Backend ist in jedem Fall die **gesamte** Auftrags-ID-Liste des betroffenen Materials in der neuen Reihenfolge zu übergeben. Unvollständige Listen sind **nicht zulässig** und werden abgelehnt.
- **Teilmengen** (z. B. gefilterte, gesuchte oder anderweitig eingeschränkte Listen im Frontend) dürfen **niemals** eine fachliche Neuberechnung, Persistenz oder Repriorisierung auslösen.
- Sobald ein Filter, eine Suche oder ein anderer Mechanismus Aufträge ausblendet, ist die Reordering-Funktion in der Oberfläche **zu sperren** (vgl. Abschnitt 5 Frontend-Regeln).
- Diese Regel ist **nicht interpretierbar**: Fachliche Dispositionslogik und Reihenfolgewirkung werden ausschließlich auf vollständigen Datenmengen berechnet.

---

### 3.4 Reststücklogik

- Reststücke werden aggregiert pro Materialtyp geführt
- Nutzung erfolgt bewusst durch den Benutzer
- keine automatische Optimierung im MVP

---

### 3.5 Ampellogik

- Grün: vollständig erfüllbar
- Gelb: nur mit Reststücken erfüllbar
- Rot: nicht erfüllbar

Die Berechnung erfolgt ausschließlich im Backend.

---

## 4. Backend-Architekturregeln

### 4.1 Schichtenmodell

Das Backend besteht aus:

- Domain
- Application
- Ports
- Adapter
- API

---

### 4.2 Domain

Die Domain:

- enthält Fachlogik
- kennt keine Infrastruktur
- kennt keine Frameworks
- enthält keine SQLAlchemy-Modelle

Verboten:

- Datenbankzugriffe
- API-Aufrufe
- ERP-Zugriffe

---

### 4.3 Application Layer

- implementiert Use Cases
- orchestriert Domain-Logik
- greift über Ports auf externe Systeme zu

---

### 4.3.1 Aufteilung von Use-Case-Modulen

Use-Case-Dateien dürfen in frühen Phasen mehrere zusammengehörige Use Cases enthalten (z. B. `admin_configuration_use_cases.py`).

Sobald ein Bereich wächst oder unübersichtlich wird, ist eine Aufteilung in fachlich klar getrennte Dateien vorzunehmen.

Ziel:

- gute Lesbarkeit
- klare Verantwortlichkeiten
- keine "God-Use-Case-Dateien"

---

### 4.3.2 Erweiterung fuer Inventur-Use-Cases

Fuer das Inventurmodul gilt analog:

Dateien wie `inventory_use_cases.py` duerfen in fruehen Phasen mehrere zusammengehoerige Use Cases buendeln.

Sobald der Umfang waechst, ist eine Aufteilung in fachlich getrennte Dateien vorzunehmen (z. B. Counts, Corrections, Vergleichslogik).

---

### 4.3.3 Spaeterer Ausbauhinweis fuer Scan-/Lookup-Use-Cases

`material_lookup_use_cases.py` darf im aktuellen Stand mehrere zusammengehoerige Use Cases buendeln.

Wenn das Modul waechst, ist eine fachliche Aufteilung vorzunehmen.

Der `/scan`-Flow kann spaeter enger mit Materialdetail oder Auftragsanlage verbunden werden.

Eine echte Scanner-/Kamera-Integration erfolgt erst, wenn der scanbasierte Lookup-Flow stabil und sinnvoll genutzt wird.

---

### 4.3.4 Strukturhinweis fuer ERP-Read-Use-Cases

`erp_read_use_cases.py` ist im aktuellen Stand in Ordnung.

Solange der Umfang ueberschaubar bleibt, duerfen mehrere zusammengehoerige ERP-Read-Use-Cases in einer Datei gebuendelt sein.

Wenn der Bereich waechst, ist eine fachliche Aufteilung vorzunehmen (z. B. Material Read, Stock Read, Order Validation).

Die Regel ist ein Strukturhinweis fuer spaetere Refactorings und kein sofortiger Aenderungsauftrag.

---

### 4.3.5 Strukturhinweis fuer ERP-Transfer-Use-Cases

`erp_transfer_use_cases.py` ist im aktuellen Stand in Ordnung.

Solange der Umfang ueberschaubar bleibt, duerfen mehrere zusammengehoerige Use Cases in einer Datei gebuendelt sein.

Wenn der Bereich waechst, ist eine fachliche Aufteilung vorzunehmen (z. B. Creation/Listing, Status Transitions, Send/Fail Handling).

Die Regel ist ein Strukturhinweis fuer spaetere Refactorings und kein sofortiger Aenderungsauftrag.

---

### 4.4 Ports

- definieren Schnittstellen
- enthalten keine Implementierung

---

### 4.5 Adapter

- implementieren Ports
- enthalten technische Logik
- keine führende Fachlogik

---

### 4.6 API Layer

- nur Request/Response Handling
- keine Fachlogik

---

## 5. Frontend-Regeln

- Frontend ist rein darstellend
- keine Fachlogik im Frontend
- keine ERP-Logik im Frontend

Frontend darf:

- Daten anzeigen
- Eingaben erfassen
- Backend aufrufen

Frontend darf nicht:

- Verfügbarkeit berechnen
- Priorisierung berechnen
- Reservierungen simulieren
- Ampelstatus oder disponible Mengen **neu** berechnen (Anzeige und **Filter auf bereits vom Backend gelieferten Feldern** sind erlaubt)

**Erlaubt im UI:** Teilmengenfilter (z. B. nach `traffic_light`, Kunde, Fälligkeit) auf Basis der geladenen Auftragsdaten – **ohne** eigene Dispositionslogik.

**Reihenfolge ändern (Repriorisierung):** Nur wenn für ein Material die sichtbare App-Auftragsliste **der vollständigen** Sequenz entspricht; bei aktiven Filtern, die Aufträge ausblenden, ist die Reihung in der Oberfläche zu sperren (Backend verlangt die vollständige ID-Liste je Material).

---

## 6. Datenbankregeln

- PostgreSQL ist die Zieldatenbank
- alle Änderungen erfolgen über Migrationen

---

### 6.1 Persistenzregeln

- ORM-Modelle sind keine Domain-Modelle
- Domain kennt keine Datenbank
- keine Fachlogik in SQL

---

### 6.2 Datenverantwortung

- ERP-Daten werden synchronisiert, nicht ersetzt
- App speichert:
  - Reservierungen
  - Status
  - Konfiguration

---

## 7. ERP-Integrationsregeln

- keine direkte ERP-Kommunikation außerhalb von Adaptern
- alle ERP-Zugriffe über Ports

---

### 7.1 Konfigurationsprinzip

ERP-Integration basiert auf:

- ERP-Profilen
- Endpunkten
- Feldmapping
- Auth-Konfiguration

---

### 7.2 Verbot

- keine hartcodierten ERP-Endpunkte im Code
- keine ERP-Logik in Domain oder Application

---

### 7.3 Mapping-Konsistenz

Die Mapping-Richtungen sind systemweit konsistent zu verwenden:

- `app_to_erp` nur für App → ERP
- `erp_to_app` nur für ERP → App
- gilt identisch für `erp_field_mappings`, ERP-Adapter und Admin-Oberfläche
- keine alternativen Bezeichner für dieselbe Richtung

---

### 7.4 Login-, Verbindungs- und Rollenregeln

#### 7.4.1 Trennung der Login-Arten (verbindlich)

- ERP-Benutzer-Login und Admin-Login sind strikt getrennt umzusetzen.
- Diese Authentifizierungsarten dürfen technisch und fachlich nicht vermischt werden.
- Admin-Authentifizierung erfolgt gegen die Anwendung.
- ERP-Benutzer-Authentifizierung erfolgt gegen die gewählte Verbindung.

#### 7.4.2 Verbindungswahl als führender Kontext (verbindlich)

- Die gewählte Verbindung ist ein verpflichtender Teil des Login-Kontexts.
- Alle ERP-bezogenen Operationen müssen diesen Verbindungskontext berücksichtigen.
- Hardcodierung von ERP-Zugängen oder festen Verbindungen ist verboten.

#### 7.4.3 Rollenmodell nach der Authentifizierung (verbindlich)

- Authentifizierung und Rollenzuordnung sind getrennte Schritte.
- Ein erfolgreich authentifizierter ERP-Benutzer darf ohne zugewiesene App-Rolle keine operativen Funktionen nutzen.
- Rollensteuerung bleibt zentral und darf nicht verteilt implementiert werden.

#### 7.4.4 Zentrale Rollenprüfung (verbindlich)

- Rollen- und Rechteprüfungen erfolgen zentral (z. B. über API-Dependencies oder äquivalente zentrale Mechanismen).
- Copy-Paste-Rollenprüfungen in Routern oder Komponenten sind verboten.
- Rollenlogik in der Domain ist verboten.

#### 7.4.5 Simulator-Regel (verbindlich)

- Der Sage-Simulator ist architektonisch wie eine normale ERP-Verbindung zu behandeln.
- Sonderlogik in Domain oder Application ist verboten.
- Simulator-spezifische Unterschiede dürfen nur in vorgesehenen Adaptern oder Konfigurationen liegen.

#### 7.4.6 QR-Code-Regel (verbindlich)

- Der QR-Code auf dem Login-Screen dient ausschließlich als Einstiegshilfe für die mobile Nutzung.
- Der QR-Code ersetzt keine Authentifizierung.
- Session-Übertragung oder Auth-Umgehung über den QR-Code ist verboten.

#### 7.4.7 Fehlerbehandlung (verbindlich)

- Login-Fehler, Verbindungsfehler, Rollenfehler und Konfigurationsfehler müssen sauber unterschieden werden.
- Netzwerk-/CORS-/Verbindungsfehler dürfen nicht mit Authentifizierungsfehlern vermischt werden.
- Fehlermeldungen müssen fachlich und technisch eindeutig zuordenbar bleiben.

---

## 8. Testregeln (TDD)

### 8.1 Grundsatz

Jede Fachlogik wird testgetrieben entwickelt.

---

### 8.2 Ablauf

1. Test schreiben
2. Test schlägt fehl
3. Implementierung
4. Test besteht
5. Refactoring

---

### 8.3 Testarten

- Domain: Unit-Tests
- Application: Use Case Tests
- Adapter: Integrationstests
- API: Endpoint Tests

---

## 9. Dokumentationsregeln

Dokumentation ist verpflichtend.
### README-Regel

Die README.md ist als lebende Projektübersicht zu pflegen.

Sie muss insbesondere aktualisiert werden bei:
- neuen Modulen
- neuen zentralen Komponenten
- Änderungen an Start- oder Betriebsanweisungen
- Änderungen an Ports, Services oder Infrastruktur
- neuen technischen Abhängigkeiten
- neuen Entwicklungs- oder Testschritten

Die README.md ersetzt keine Fachdokumentation, sondern ergänzt diese als zentrale Einstiegshilfe und Projektübersicht.

---

### 9.1 Pflichtprüfung

Bei jeder Änderung prüfen:

- Fachlogik → pflichtenheft.md
- Datenmodell → datenbankmodell.md
- Architektur → architecture.md

---

### 9.2 Regeln

- keine stillen Architekturänderungen
- zentrale Logik muss dokumentiert werden

---

### 9.3 Fortschrittsdokumentation im Implementierungsplan

Nach Abschluss einer Phase ist `docs/implementationplan.md` knapp und konsistent zu aktualisieren:

- nur klare Statuskennzeichnung (z. B. `✅`)
- keine ausführlichen Fließtexte im Plan
- keine inhaltlichen Planänderungen ohne Begründung

---

## 10. Coding-Standards

### Backend

- keine Fachlogik in API
- keine Fachlogik in ORM
- keine Utility-Klassen für Kernlogik

---

### Frontend

- keine Geschäftslogik
- klare Struktur nach Features

---

### Allgemein

- keine Magic Strings
- keine toten Codepfade
- klare Benennung nach Fachsprache

---

## 11. Git-Regeln

### Branching

- keine Arbeit auf main
- Feature-Branches verwenden

---

### Commit-Format

- feat:
- fix:
- refactor:
- test:
- docs:

---

### Regeln

- kleine Commits
- keine Mischänderungen

---

## 12. Migrationsregeln

- jede DB-Änderung benötigt Migration
- Migrationen müssen reproduzierbar sein

---

## 13. Refactoring-Regeln

- darf Fachlogik nicht verändern
- Tests müssen bestehen bleiben

---

## 14. Verhalten des Agenten

Vor jeder Umsetzung:

1. relevante Dokumente lesen:
   - projektrules.md
   - architecture.md
   - projectstructure.md
   - pflichtenheft.md
   - datenbankmodell.md
2. Aufgabe einordnen
3. Architektur prüfen
4. Struktur prüfen (richtiger Ordner!)
5. Tests definieren
6. implementieren

---

## 15. Verbotene Patterns

- God Services
- direkte ERP-Zugriffe aus Domain
- doppelte Fachlogik in mehreren Schichten
- Vermischung von Domain und Infrastruktur

---

## 16. Definition of Done

Eine Aufgabe ist abgeschlossen, wenn:

- Architektur eingehalten wurde
- Tests vorhanden sind
- Dokumentation aktualisiert wurde
- keine verbotenen Abkürzungen verwendet wurden
- Fachbegriffe korrekt verwendet wurden
- README.md wurde geprüft und bei Bedarf aktualisiert
