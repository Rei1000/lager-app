# Projektstruktur – Lager-App für Stangenmaterial

---

## 1. Überblick

Dieses Dokument beschreibt die verbindliche Projektstruktur der Anwendung.

Dieses Dokument ist verbindlich in Kombination mit:

- docs/projektrules.md
- docs/architecture.md
- docs/pflichtenheft.md
- docs/datenbankmodell.md

Ziel ist:

- klare Trennung der Verantwortlichkeiten
- saubere Umsetzung von DDD und hexagonaler Architektur
- konsistente Struktur für Entwickler und Agenten
- Vermeidung von chaotischem Wachstum

---

## 2. Gesamtstruktur

Das Projekt ist in folgende Hauptbereiche unterteilt:

- docs
- .cursor
- backend
- frontend
- infra

---

## 3. Verzeichnisstruktur

project-root/

docs/
pflichtenheft.md
datenbankmodell.md
projektrules.md
architecture.md
projectstructure.md
prompts/

.cursor/
cursor.rules

backend/
src/
domain/
application/
ports/
adapters/
api/
persistence/
erp/
auth/
config/

    tests/
      unit/
      application/
      integration/
      api/

    alembic/

frontend/
src/
app/
features/
components/
lib/

    tests/

infra/
docker/
db/

---

## 4. Backend-Struktur

### 4.1 domain/

Enthält:

- Entities
- Value Objects
- Domain Services
- fachliche Regeln

Darf NICHT enthalten:

- Datenbankzugriffe
- API-Code
- ERP-Zugriffe
- Framework-Abhängigkeiten

---

### 4.2 application/

Enthält:

- Use Cases
- Orchestrierung von Fachlogik

Beispiele:

- create_order
- reserve_order
- reprioritize_orders

---

### 4.3 ports/

Enthält:

- Schnittstellen (Interfaces) nach außen

Beispiele:

- Repository Interfaces
- ERP Gateway
- Auth Schnittstellen

Keine Implementierung.

---

### 4.4 adapters/

Implementiert Ports.

Unterteilung:

- api → FastAPI (Controller, Router)
- persistence → Datenbankzugriff (SQLAlchemy)
- erp → ERP-Integration
- auth → Authentifizierung

Regel:

- Adapter enthalten nur technische Logik
- keine führende Fachlogik

---

### 4.5 config/

Enthält:

- Konfiguration
- Settings
- Environment-Handling

---

## 5. Teststruktur

### unit/

- Domain Tests
- reine Fachlogik
- keine Infrastruktur

---

### application/

- Use Case Tests
- Ports werden gemockt

---

### integration/

- Adapter Tests
- Datenbanktests
- ERP-Adapter Tests

---

### api/

- Endpoint Tests
- Request/Response Validierung

---

## 6. Frontend-Struktur

frontend/src/

app/
features/
components/
lib/

---

### 6.1 app/

- Routing
- Seitenstruktur
- z. B. `app/orders/page.tsx` – Tabs (Neuer Auftrag / Aufträge), bei Query `traffic_light` Umschalten auf die Listenansicht (reine UI-Anbindung an die URL)

---

### 6.2 features/

Fachlich gruppierte Module:

- orders
- materials
- dashboard
- admin

**orders** (Auftragsübersicht, Planung, Bearbeitung):

- Listen- und Filter-UI: u. a. `orders-open-overview.tsx` – Zusammenführung geladener App- und Simulator-Daten; **Filter** (Ampel per URL, Kunde, Fälligkeit, Status, Volltext, Materialstruktur) arbeiten auf **DTO-Feldern** aus der API, ohne Dispositions-Neuberechnung (`matchesListingFilters` und Hilfsfunktionen).
- Mobile: z. B. `mobile-material-reorder-sheet.tsx` – gestützte Reihenfolgeänderung; Reihung nur konsistent, wenn keine Filter-Teilmenge die vollständige Material-Sequenz verdeckt (siehe Architektur-/Order-Doku).

**dashboard**:

- Übersicht offener Aufträge und Ampel-Zähler aus dem Backend; **Navigation** per Link zu `/orders?traffic_light=…` auf gefilterte Auftragsliste (`dashboard-overview.tsx`).

---

### 6.3 components/

- UI-Komponenten
- wiederverwendbar
- keine Fachlogik

**shared** (z. B. `components/shared/`):

- `traffic-light-indicator.tsx` – **Darstellung** von `traffic_light`-Werten aus der API (Farben, ggf. kompakte Labels auf schmalen Viewports), **keine** Berechnung der Ampel.

---

### 6.4 lib/

- API-Client
- Konfiguration
- Hilfsfunktionen (ohne Fachlogik)

---

## 7. Infra-Struktur

### docker/

- Dockerfiles
- docker-compose
- Container-Konfiguration

---

### db/

- Datenbankskripte
- Seeds
- Hilfsdateien

---

## 8. Dokumentation

docs/ enthält:

- pflichtenheft.md → fachliche Anforderungen
- architecture.md → Systemarchitektur
- datenbankmodell.md → Datenstruktur
- order-architecture.md → App vs. ERP, Verfügbarkeit, Disposition, UI-Kontrakt
- projektrules.md → Umsetzungsregeln
- projectstructure.md → Projektstruktur

---

## 9. Grundregeln

- keine Vermischung von Schichten
- keine parallelen Strukturen
- klare Verantwortlichkeiten
- Fachlogik nur in Domain und Application
- Adapter enthalten nur technische Implementierung
- Frontend enthält keine Geschäftslogik

---

## 10. Ziel der Struktur

Diese Struktur stellt sicher:

- hohe Wartbarkeit
- klare Erweiterbarkeit
- konsistente Umsetzung durch Agenten
- saubere Trennung von Fachlogik und Technik
