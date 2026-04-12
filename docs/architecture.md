# Architektur – Lager-App für Stangenmaterial

---

## 1. Ziel und Zweck der Architektur

Dieses Dokument beschreibt die technische Zielarchitektur der Lager-App für Stangenmaterial.

Es definiert:

- die Hauptkomponenten des Systems
- deren Verantwortlichkeiten
- die Richtung von Abhängigkeiten
- die Trennung von Fachlogik, Infrastruktur und Benutzeroberfläche
- die Struktur des Backends nach DDD und hexagonaler Architektur
- die Rolle von Frontend, Datenbank und ERP-Integration
- die architektonischen Leitplanken für die Umsetzung

Dieses Dokument ergänzt:

- `docs/pflichtenheft.md`
- `docs/datenbankmodell.md`
- `docs/projektrules.md`
- docs/projectstructure.md

---

## 2. Architekturziele

Die Architektur verfolgt folgende Ziele:

1. **Klare Trennung von Fachlogik und Technik**  
   Die fachlichen Regeln des Systems dürfen nicht an Frameworks,
   Datenbanktechnologien oder ERP-Schnittstellen gekoppelt sein.

2. **ERP-unabhängige Integrationsfähigkeit**  
   Das ERP-System bleibt führend, muss aber über eine konfigurierbare
   Integrationsschicht anbindbar sein.

3. **Saubere Erweiterbarkeit**  
   Weitere ERP-Systeme, zusätzliche Prozesse, Scanning, Inventur oder
   Push-Funktionen sollen später ohne grundlegenden Umbau integrierbar sein.

4. **Hohe Testbarkeit**  
   Fachlogik, Use Cases und Integrationen sollen getrennt testbar sein.

5. **Konsistente Umsetzung mit Agentenunterstützung**  
   Die Architektur muss so klar sein, dass ein Agent Aufgaben zuverlässig
   innerhalb der vorgesehenen Schichten umsetzen kann.

---

## 3. Systemkontext

Die Anwendung ist Teil eines Gesamtsystems, in dem das ERP die führende
betriebliche Datenquelle bleibt.

### Kontextübersicht

```text
[ Benutzer im Browser ]
          ↓
[ Frontend (Next.js) ]
          ↓
[ Backend API (FastAPI) ]
          ↓
[ ERP-Integrationsschicht ]
          ↓
[ ERP-System ]
Zusätzlich:
[ PostgreSQL ]
       ↑
[ Backend ]
```

Grundprinzipien des Systemkontexts

- Benutzer arbeiten ausschließlich über das Frontend.
- Das Frontend kommuniziert ausschließlich mit dem Backend.
- Das Backend kommuniziert mit Datenbank und ERP-Integrationsadaptern.
- Direkte Frontend-zu-ERP-Kommunikation ist nicht zulässig.
- Das ERP bleibt führend für offizielle Bestände, Materialstammdaten und Aufträge.

---

## 4. Container- und Komponentensicht

### 4.1 Hauptcontainer

Das System besteht aus folgenden Hauptcontainern:

Frontend

Verantwortlich für:

- Login
- Dashboard
- Materialsuche
- Auftragserstellung
- Priorisierung
- ERP-Verknüpfung
- Admin-Oberfläche

Technologie:

- Next.js
- TypeScript
- shadcn/ui
- Tailwind CSS

Backend

Verantwortlich für:

- Fachlogik
- Use Cases
- REST-API
- Authentifizierung
- ERP-Integrationsorchestrierung
- Persistenzzugriffe

Technologie:

- Python
- FastAPI

Datenbank

Verantwortlich für:

- app-interne Daten
- Konfiguration
- Reservierungen
- Statushistorie
- ERP-Profile und Mappings
- Audit-Logs

Technologie:

- PostgreSQL

ERP

Verantwortlich für:

- Materialstammdaten
- offizielle Bestände
- ERP-Aufträge
- reale betriebliche Buchungen

Beispiel:

- Sage 100

---

## 5. Frontend-Architektur

### 5.1 Grundprinzip

Das Frontend ist eine browserbasierte, responsive Webanwendung.

Es ist für folgende Aufgaben zuständig:

- Anzeige
- Eingabe
- Bedienung
- Workflow-Führung

Es ist nicht zuständig für:

- führende Fachlogik
- Verfügbarkeitsberechnung
- Priorisierungsberechnung
- ERP-Logik
- Reservierungslogik als Quelle der Wahrheit

### 5.2 Frontend-Verantwortlichkeiten

Das Frontend:

- erfasst Benutzeraktionen
- ruft Backend-Endpunkte auf
- zeigt serverseitig berechnete Ergebnisse an
- visualisiert Status und Ampelfarben
- bietet responsive Oberflächen für Lager und Admin

### 5.3 Frontend-Struktur

Empfohlene Struktur:

```text
frontend/
  src/
    app/
    features/
      auth/
      dashboard/
      materials/
      orders/
      admin/
    components/
      ui/
      shared/
    lib/
```

Bedeutung

- app/ enthält Routing und Seitenstruktur
- features/ enthält fachlich gruppierte UI-Bereiche
- components/ui/ enthält generische UI-Komponenten
- components/shared/ enthält wiederverwendbare projektinterne Komponenten
- lib/ enthält Frontend-nahe Hilfen, API-Client, Konfiguration

### 5.4 Frontend-Regeln

- Keine Geschäftslogik im Frontend
- Keine ERP-spezifische Verarbeitung im Frontend
- Keine doppelte Berechnung von Verfügbarkeit
- Das Frontend zeigt nur serverseitig berechnete Zustände
- UI-Komponenten müssen konsistent mit shadcn/ui aufgebaut sein

---

## 6. Backend-Architektur

### 6.1 Grundprinzip

Das Backend ist der zentrale Fachkern des Systems.

Es stellt eine REST-API bereit und enthält:

- die Domäne
- die Use Cases
- Ports
- Adapter
- API-Einstiegspunkte

Das Backend ist nach DDD und hexagonaler Architektur aufgebaut.

### 6.2 Schichtenmodell

```text
[ API Layer ]
      ↓
[ Application Layer ]
      ↓
[ Domain Layer ]
      ↑
[ Ports ]
      ↑
[ Adapters ]
```

Abhängigkeitsregel

Abhängigkeiten zeigen immer nach innen.

Das bedeutet:

- API hängt von Application ab
- Application hängt von Domain und Ports ab
- Adapter hängen von Ports ab
- Domain hängt von nichts Technischem ab

Die Domain darf niemals abhängen von:

- FastAPI
- SQLAlchemy
- PostgreSQL
- ERP-Protokollen
- HTTP
- JSON
- UI

---

## 7. DDD-Schnitt des Backends

### 7.1 Domain Layer

Der Domain Layer enthält die fachlichen Konzepte des Systems.

Beispiele:

- MaterialType
- RestStockAccount
- AppOrder
- ReservationPolicy
- DemandCalculator
- PriorityPlanner
- OrderStatusRules

Domain-Regeln

Die Domain:

- enthält Fachlogik
- kennt die Sprache des Pflichtenhefts
- kennt keine Infrastruktur
- ist unabhängig von Datenbank und Framework

Typische Inhalte

- Entities
- Value Objects
- Domain Services
- fachliche Invarianten
- Statusregeln

### 7.2 Application Layer

Der Application Layer implementiert Use Cases.

Beispiele:

- CreateOrderUseCase
- RecalculateOrdersUseCase
- ReserveOrderUseCase
- ReprioritizeOrdersUseCase
- LinkErpOrderUseCase
- TransferRestStockToErpUseCase

Aufgaben

- Use Cases orchestrieren
- Ports ansprechen
- Domain-Regeln anwenden
- Ergebnisse für API oder Frontend bereitstellen

Der Application Layer enthält:

- keine Datenbankdetails
- keine Framework-spezifische Fachlogik

### 7.3 Ports

Ports definieren Schnittstellen nach außen.

Beispiele:

- MaterialRepositoryPort
- OrderRepositoryPort
- RestStockRepositoryPort
- ErpGatewayPort
- AuthPort
- AuditLogPort

Ports enthalten:

- nur Verträge
- keine Implementierung

### 7.4 Adapter

Adapter implementieren Ports.

Beispiele:

- SQLAlchemyMaterialRepository
- SQLAlchemyOrderRepository
- Sage100RestAdapter
- MiddlewareErpAdapter
- JwtAuthAdapter

Adapter enthalten:

- technische Umsetzung
- keine führende Fachlogik

---

## 8. Hexagonale Architektur konkret im Projekt

### 8.1 Warum hexagonal?

Das Projekt hat mehrere äußere Systeme und technische Einstiegspunkte:

- Frontend / HTTP
- PostgreSQL
- ERP
- Authentifizierung
- später evtl. Scanner, Messaging, Datei-Uploads

Hexagonale Architektur sorgt dafür, dass diese äußeren Systeme austauschbar
bleiben und die Fachlogik nicht dominieren.

### 8.2 Eingangsportale

Primäre Eingänge ins System:

- REST-API
- später optional Admin-Importe oder Hintergrundjobs

### 8.3 Ausgangsports

Wichtige externe Abhängigkeiten:

- Datenbank
- ERP
- Audit-Logging
- Authentifizierung
- spätere Benachrichtigungen

---

## 9. Persistenzarchitektur

### 9.1 Grundprinzip

PostgreSQL ist die relationale Persistenzbasis des Systems.

Persistiert werden:

- Benutzer
- Rollen
- Materialtypen
- Reststückkonten
- App-Aufträge
- Statushistorie
- ERP-Profile
- Auth-Konfigurationen
- Endpunkte
- Feldmappings
- Audit-Logs

### 9.2 ORM-Rolle

Für die technische Persistenz wird SQLAlchemy verwendet.

Wichtige Regel:

- SQLAlchemy-Modelle sind Infrastrukturmodelle
- sie sind nicht die Domänenmodelle

### 9.3 Migrationen

Schemaänderungen erfolgen ausschließlich über Migrationen.

Empfohlen:

- Alembic

### 9.4 Persistenzprinzipien

- keine stillen Schemaänderungen
- jede fachlich relevante Schemaänderung aktualisiert auch docs/datenbankmodell.md
- keine Datenbanklogik, die zentrale Fachlogik ersetzt
- Constraints und Referenzen werden auf DB-Ebene genutzt, fachliche Regeln
  bleiben im Domain/Application Layer

---

## 10. ERP-Integrationsarchitektur

### 10.1 Grundprinzip

Das ERP bleibt führend, wird aber über eine konfigurierbare
Integrationsschicht angebunden.

Die Anwendung spricht niemals direkt und starr gegen eine bestimmte ERP-Implementierung.

### 10.2 ERP-Anbindung erfolgt über Ports und Adapter

Das Backend definiert einen ERP-Port, z. B.:

- ErpGatewayPort

Dieser Port wird je nach ERP-Profil implementiert durch:

- Sage100RestAdapter
- MiddlewareAdapter
- ReadOnlyDbAdapter
- GatewayAdapter

### 10.3 Konfigurationsmodell

Die ERP-Integrationsschicht arbeitet nicht mit hardcodierten Endpunkten,
sondern mit:

- ERP-Profilen
- Auth-Konfigurationen
- fachlichen Funktionsklassen
- technischen Endpunkten
- Feldmappings

### 10.4 Fachliche Funktionsklassen

Beispiele:

- material.search
- material.get
- material.stock.get
- erp_orders.list_by_material
- erp_order.get
- stock.adjust

Diese fachlichen Funktionen werden konfigurierbar auf technische Endpunkte gemappt.

### 10.5 Architekturelle Regel

ERP-spezifische Details dürfen niemals in:

- Domain
- Use Cases
- Frontend

hineinlaufen.

Sie gehören ausschließlich in Adapter und Konfiguration.

---

## 11. Zentrale Datenflüsse

### 11.1 Auftrag anlegen

Benutzer
  → Frontend
  → Backend API
  → Application Use Case
  → Domain-Regeln
  → Repository/ERP-Adapter
  → Ergebnis zurück an Frontend
Ablauf

1. Benutzer wählt Material
2. Frontend lädt Verfügbarkeitsdaten
3. Benutzer gibt Stückzahl, Länge und Säge an
4. Backend berechnet Bedarf
5. Backend bestimmt Ampelstatus
6. Auftrag wird angelegt
7. Auftrag kann anschließend reserviert werden

### 11.2 Priorisierung ändern

Benutzer
  → Frontend
  → Backend API
  → ReprioritizeOrdersUseCase
  → Domain-Regeln / sequenzielle Neubewertung
  → Speicherung
  → Rückgabe aktualisierter Zustände
Fachregel

Die Priorisierung erfolgt materialbezogen.
Aufträge werden in der Reihenfolge verarbeitet und neu bewertet.

### 11.3 Reservierung

Benutzer
  → Frontend
  → Backend API
  → ReserveOrderUseCase
  → Domain-Regeln
  → Speicherung Status "reserved"
Fachregel

Reservierung ist nur app-intern und verändert keine ERP-Bestände direkt.

### 11.4 ERP-Verknüpfung

Benutzer
  → Frontend
  → Backend API
  → LinkErpOrderUseCase
  → ERP-Port / Adapter
  → Statusänderung und Referenzspeicherung

## 12. Testarchitektur

### 12.1 Grundsatz

Die Architektur ist auf Testbarkeit ausgelegt.
Die wichtigste Folge davon ist:

- Fachlogik ist unabhängig von Infrastruktur testbar

### 12.2 Testebenen

Domain Tests

- testen fachliche Regeln isoliert
- ohne Datenbank
- ohne API
- ohne ERP

Application Tests

- testen Use Cases
- mit gemockten Ports
- prüfen Orchestrierung und Geschäftsabläufe

Adapter Integration Tests

- testen DB-Adapter, ERP-Adapter, Auth-Adapter

API Tests

- testen REST-Endpunkte
- prüfen Request/Response-Verhalten

Frontend Tests

- Komponenten-Tests
- E2E-Tests für Hauptworkflows

### 12.3 TDD-Architekturfolge

Die Architektur muss so gestaltet sein, dass neue Fachlogik testgetrieben
entwickelt werden kann, ohne zuerst Infrastruktur aufbauen zu müssen.

---

## 13. Laufzeit- und Deploymentarchitektur

### 13.1 Containerisierung

Die Anwendung wird containerisiert betrieben.

Container:

- frontend
- backend
- database

Optional später:

- reverse proxy
- worker
- monitoring

### 13.2 Docker-Prinzip

Docker ist der primäre Laufzeitweg.
Lokale virtuelle Umgebungen dürfen optional genutzt werden, sind aber nicht der
führende Betriebsweg.

### 13.3 Entwicklung

Für die lokale Entwicklung wird Docker Compose verwendet.

Ziele:

- reproduzierbare Umgebung
- konsistente Services
- einfache Teamnutzung
- stabile Testbasis

---

## 14. Architektonische Leitplanken

### 14.1 Erlaubte Abhängigkeiten

Erlaubt:

- API → Application
- Application → Domain
- Application → Ports
- Adapter → Ports
- Persistence Adapter → SQLAlchemy / PostgreSQL
- ERP Adapter → ERP-spezifische Technik

### 14.2 Verbotene Abhängigkeiten

Nicht erlaubt:

- Domain → SQLAlchemy
- Domain → FastAPI
- Domain → ERP-Technik
- Frontend → ERP direkt
- API → direkte Fachlogik ohne Use Case
- SQLAlchemy-Modelle als Domain-Objekte
- Adapter, die an der Domain vorbei direkt Geschäftsentscheidungen treffen

### 14.3 Weitere Verbote

Nicht zulässig:

- God Services
- generische Utility-Klassen für Kernfachlogik
- doppelte Berechnung derselben Fachregel in verschiedenen Schichten
- versteckte Architekturwechsel ohne Dokumentationsanpassung

## 15. Architektonische Definition of Done

Eine architektursaubere Änderung ist nur dann fertig, wenn:

- sie in der vorgesehenen Schicht implementiert wurde
- keine verbotenen Abhängigkeiten entstanden sind
- passende Tests vorhanden sind
- relevante Dokumentation aktualisiert wurde
- fachliche Sprache konsistent verwendet wird
- keine technische Abkürzung die Domäne beschädigt

## 16. Zusammenfassung

Die Lager-App ist architektonisch als klar getrenntes, testbares und
erweiterbares System aufgebaut.

Die Architektur stellt sicher, dass:

- das ERP führend bleibt
- die App eine saubere Dispositionsschicht bildet
- Fachlogik unabhängig von Technik bleibt
- Adapter austauschbar sind
- die Umsetzung konsistent und agentenfähig bleibt

Die Architektur ist damit auf langfristige Wartbarkeit, saubere
Erweiterbarkeit und kontrollierte Implementierung ausgelegt.

## Authentifizierung und Verbindungsmanagement

### 1. Trennung der Authentifizierungsarten

Die Architektur unterscheidet technisch strikt zwischen zwei
Authentifizierungsarten:

- App-Authentifizierung für Admin-Login
- ERP-Authentifizierung für ERP-Benutzer-Login

Die Authentifizierungsquellen sind getrennt zu behandeln. Eine Vermischung von
Login-Pfaden, Identitätsquellen oder Token-Herkunft ist architektonisch nicht
zulässig.

Für die technische Umsetzung sind getrennte Ports und Adapter vorgesehen bzw.
erweiterbar, damit App-Identity und ERP-Identity unabhängig bleiben.

### 2. Rolle der Application-Schicht

Die Application-Schicht orchestriert Login-Abläufe über dedizierte Use Cases.

Die Use Cases:

- enthalten keine technische Auth-Implementierung
- treffen keine Infrastrukturentscheidungen
- nutzen Ports für:
  - Identity-Zugriff
  - Token-Erzeugung/-Prüfung
  - ERP-Authentifizierung (zukünftige Erweiterung)

Damit bleibt die Fachorchestrierung in der Application-Schicht, während die
technischen Details in Adaptern liegen.

### 3. Session-/Token-Kontext

Nach erfolgreichem Login muss ein einheitlicher Auth-Kontext verfügbar sein mit:

- `user_id`
- `role`
- `login_type` (`admin` oder `erp`)
- `selected_connection` (ERP-Profil)
- `token` und Ablaufzeit (`expiration`)

Dieser Kontext ist die technische Grundlage für alle folgenden Use Cases und
für die API-seitige Zugriffskontrolle.

### 4. Verbindungsabhängige Verarbeitung

Die gewählte Verbindung steuert zur Laufzeit:

- welcher ERP-Adapter verwendet wird
- welche ERP-Konfiguration geladen wird

Die Verbindung ist Teil des Request-Kontexts und wird entlang der
Use-Case-Ausführung berücksichtigt.

Hardcodierte ERP-Zugänge, feste ERP-Endpunkte oder statische
Verbindungsverdrahtungen außerhalb der Konfiguration sind architektonisch
ausgeschlossen.

### 5. Integration in bestehende Ports/Adapter

Das Verbindungsmanagement integriert sich in die bestehende Port- und
Adapterstruktur:

- Nutzung der vorhandenen ERP-Ports als Abstraktionsgrenze
- keine direkte Kopplung der Application-Schicht an konkrete ERP-Systeme
- Simulator-Anbindung als normaler Adapter innerhalb derselben Port-Verträge

Die Austauschbarkeit der Adapter bleibt damit vollständig erhalten.

### 6. Rollen- und Rechteprüfung

Rollen- und Rechteprüfung erfolgt zentral über API-Dependencies und den
Auth-Kontext.

Architekturregeln:

- keine Rollenlogik in der Domain
- keine verteilten Einzelprüfungen als Fachlogik in mehreren Schichten
- konsistente Zugriffskontrolle am API-Eingang mit Übergabe eines validierten
  Request-Users an Use Cases

### 7. Login-Flow (technisch)

ERP-Login:

1. Frontend sendet Login-Daten inkl. gewählter Verbindung.
2. Backend nutzt den passenden Port/Adapter zur ERP-Authentifizierung.
3. Benutzer wird geladen oder angelegt.
4. Rolle wird ermittelt bzw. geprüft.
5. Token mit vollständigem Auth-Kontext wird erstellt.

Admin-Login:

1. Frontend sendet App-Login-Daten.
2. Backend authentifiziert gegen App-Identity.
3. Rolle wird ermittelt.
4. Token wird ohne ERP-Abhängigkeit erstellt.

Beide Flows bleiben technisch getrennt, liefern aber einen einheitlichen
Session-Kontext für nachgelagerte Use Cases.

### 8. Fehlerbehandlung

Die Architektur trennt Fehlerklassen klar:

- Netzwerkfehler (Verbindung/Transport)
- Authentifizierungsfehler (ungültige Zugangsdaten)
- Autorisierungsfehler (fehlende Berechtigung)
- Konfigurationsfehler (nicht konfigurierte Verbindung/Profile)

Die Fehlerklassifikation erfolgt technisch eindeutig, damit API und Frontend
korrekte und verständliche Rückmeldungen bereitstellen können.

### 9. Simulator-Integration

Der Simulator wird architektonisch wie jede andere ERP-Verbindung behandelt:

- Nutzung derselben Ports
- Adapteraustausch ohne Änderung von Domain oder Application
- keine Sonderlogik in Domain oder Use Cases

Damit bleibt der Simulator vollständig austauschbar und unterstützt die
kontrollierte Entwicklung gegen produktionsnahe Schnittstellen.
