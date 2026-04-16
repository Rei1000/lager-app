Lager-App für Stangenmaterial

Dieses Repository enthält die technische Grundlage für eine webbasierte Lager- und Dispositionsanwendung für Stangenmaterial.

Die Anwendung folgt strikt:
	•	Domain-Driven Design (DDD)
	•	hexagonaler Architektur
	•	testgetriebener Entwicklung (TDD)

⸻

🧭 Projektziel

Ziel ist die Entwicklung einer Anwendung zur:
	•	Disposition von Stangenmaterial
	•	Berechnung von Materialverfügbarkeit
	•	Verwaltung von Reservierungen
	•	Priorisierung von Aufträgen
	•	Integration mit einem ERP-System (z. B. Sage 100)

👉 Wichtiger Grundsatz:
Das ERP bleibt das führende System für Bestände und Aufträge.
Die App dient als Planungs- und Dispositionsschicht.

⸻

📁 Projektstruktur
	•	docs/ → Fachliche und technische Dokumentation
	•	.cursor/ → Regeln für den Agenten (Cursor)
	•	backend/ → Python/FastAPI (DDD + Hexagonal)
	•	frontend/ → Next.js (UI, ohne Business-Logik)
	•	infra/ → Docker & Infrastruktur

Detaillierte Struktur:
→ siehe docs/projectstructure.md

⸻

🚀 Schnellstart (Docker)

Voraussetzungen
	•	Docker Desktop installiert und gestartet

⸻

Start

docker compose up –build

**Schneller lokaler Neustart (empfohlen für die Entwicklung)**  
Das Skript `scripts/start-app.sh` startet Docker und das Frontend; **standardmäßig ohne Image-Rebuild** (kein erneutes `pip install` im Dockerfile):

```bash
./scripts/start-app.sh localhost
```

**Backend-Image bewusst neu bauen** (z. B. nach Änderung von `backend/pyproject.toml` oder Dockerfile):

```bash
./scripts/start-app.sh localhost --rebuild
# oder: ./scripts/start-app.sh localhost --build
```

Weitere Modi: `lan`, `tailscale` — dieselben Optionen `--rebuild` / `--build` und optional `--with-testserver` gelten analog.

⸻

Hinweis zum Startverhalten:
	•	Beim Backend-Start werden Migrationen automatisch ausgeführt.
	•	Demo-Seed-Daten werden idempotent angelegt (kein Überschreiben vorhandener Daten).
	•	Storage-Verzeichnis für Fotos wird automatisch erstellt.
	•	Optionaler Statuscheck: http://localhost:8001/system/status

⸻

Zugriff
	•	Backend: http://localhost:8001
	•	Healthcheck: http://localhost:8001/health
	•	Systemstatus: http://localhost:8001/system/status

⸻

Stoppen

docker compose down

⸻

🔐 Demo-Login (nur für Test/Pilot)

Wichtig: Die folgenden Standardpasswörter sind nur für lokale Demo-/Pilotumgebungen gedacht und müssen in Produktivumgebungen ersetzt werden.

	•	admin / Admin123! (Rolle: admin)
	•	leitung1 / Leitung123! (Rolle: leitung)
	•	lager1 / Lager123! (Rolle: lager)

⸻

🧪 Demo-Seed-Daten

Beim Start (oder manuell) werden folgende Datensätze idempotent angelegt:
	•	Rollen: admin, leitung, lager
	•	Benutzer: admin, leitung1, lager1
	•	Materialien: ART-DEMO, ART-ALU-20, ART-PIPE-30
	•	Demo-Aufträge (DB-seitig): 2 Beispielaufträge
	•	ERP-Profil: default (Dummy)

Manueller Seed:
	•	docker compose run --rm backend python -m scripts.seed_demo_data

⸻

🔌 Ports (konfliktfreie Defaults)
	•	Backend: 8001 → 8000
	•	Frontend (geplant): 3001 → 3000

Die Ports sind bewusst so gewählt, um Konflikte mit anderen Projekten zu vermeiden.

⸻

🧱 Architekturüberblick

Das Backend ist nach DDD und hexagonaler Architektur aufgebaut:
	•	Domain → Fachlogik
	•	Application → Use Cases
	•	Ports → Schnittstellen
	•	Adapters → technische Implementierungen
	•	API → FastAPI

👉 Details: docs/architecture.md

⸻

📊 Aktueller Entwicklungsstand

Kompaktstatus:
	•	Phase 0–8 abgeschlossen ✅
	•	Phase 9 (ERP-Read in Arbeitsoberflächen) umgesetzt ✅
	•	Backend (Domain, Use Cases, API) funktionsfähig ✅
	•	Frontend inkl. Admin- und Inventur-Oberfläche an Backend-API angebunden ✅
	•	Aktueller Fokus: Stabilisierung und weitere Erweiterungen

Vorhandene Kernfunktionen über API/UI:
	•	Auftrag anlegen
	•	Auftrag reservieren
	•	Aufträge repriorisieren
	•	ERP-Link setzen
	•	Aufträge neu berechnen (recalculate)
	•	ERP-Read-Daten in Scan-/Lookup sichtbar (Material + Bestand, klar gekennzeichnet)
	•	ERP-Read-Daten im Orders-Detail sichtbar (Bestands-Read + Referenzvalidierung)
	•	Dashboard mit ERP-Read-Hinweisen fuer offene Auftraege (Bestand/Referenzstatus)
	•	Praktischer Barcode-/QR-Scanner im `/scan`-Flow mit Browserkamera und manuellem Fallback
	•	Kontrollierter ERP-Transfer-Flow mit expliziter Freigabe (draft/ready/approved/sent/failed, send als erster optional echter ERP-Write)
	•	Feinere zentrale Rollenpruefung fuer sensible Aktionen (Admin, Leitung, Lager)
	•	Zentrale Audit-Protokollierung fuer sensible Aktionen (ERP-Transfer, Inventur, kritische Auftragsaktionen)
	•	Foto-Upload zur Zustandsdokumentation fuer Material, Inventurzaehlungen und Korrekturen (lokaler Storage + Metadaten)
	•	Einfache Kommentar-/Kommunikationsfunktion an Material, Auftrag, Inventur, Korrektur und ERP-Transfer
	•	Mobile-First UI-Feinschliff und installierbare PWA-Basis (Manifest + minimaler Service Worker)

Architektur weiterhin strikt:
	•	DDD + hexagonale Architektur

⸻

Phase 0 – Projektbasis ✅
	•	FastAPI Grundsetup
	•	Docker Setup
	•	PostgreSQL Integration vorbereitet
	•	pytest eingerichtet
	•	Healthcheck Endpoint (/health)
	•	zentraler Entry Point (main.py)

Phase 1 – Persistenz & Infrastruktur ✅
	•	SQLAlchemy Basis (Base, Engine, Session)
	•	ORM-Modelle im Persistence-Adapter
	•	Alembic initialisiert (inkl. Initialmigration)
	•	Infrastrukturtests für Persistenz-Setup

Phase 2 – Domain-Kern ✅
	•	Domain-Entities und Value Objects
	•	fachliche Kernregeln (Bedarf, Verfügbarkeit, Ampel, Priorisierung, Status)
	•	umfangreiche Domain-Unit-Tests

Phase 3 – Application Layer ✅
	•	Use-Case-Struktur mit Ports
	•	Create/Recalculate/Reserve/Reprioritize/Link Use Cases
	•	Application-Tests mit Fakes (ohne Infrastruktur)

Phase 4 – API Layer ✅
	•	FastAPI-Router + Request/Response-Schemas
	•	Endpunkte fuer Order-Operationen auf Use-Case-Basis
	•	API-Tests fuer HTTP-Verhalten (ohne DB-Zugriffe)

Phase 5 – Frontend Basis ✅
	•	Next.js + TypeScript Basis in `frontend/`
	•	Login-, Dashboard- und Orders-Grundseiten
	•	API-Client fuer alle vorhandenen Backend-Endpunkte
	•	erste Frontend-Basistests

Phase 6 – ERP-Integrationsbasis ✅
	•	ERP-Ports fuer Material, Bestand und Auftragsvalidierung
	•	dynamischer ERP-Adapter mit konfigurierbaren Funktionskeys
	•	konfigurationsgetriebene Mapping-Basis (app_to_erp / erp_to_app)
	•	Integrationstests mit Mock-HTTP

Phase 7 – Admin-Oberfläche ✅
	•	Admin-API-Endpunkte fuer ERP-Profile, Endpunkte, Mapping, Saegen und Benutzer
	•	Application-Use-Cases fuer Admin-Konfigurationsoperationen
	•	Frontend-Route `/admin` mit einfachen Listen- und Erfassungsformularen

Phase 8 – Erweiterung Inventur/Korrektur ✅
	•	Domain-Objekte fuer Inventurzaehlung, Abweichung und Korrekturstatus
	•	Use Cases fuer Inventur erfassen, vergleichen und Korrekturprozess
	•	Persistenz + Alembic-Migration fuer `inventory_counts` und `stock_corrections`
	•	API-Endpunkte unter `/inventory/*` und Frontend-Route `/inventory`
	•	Scan-/Lookup-Basis mit Materialsuche ueber `/materials/*` und Frontend-Route `/scan`
	•	Barcode-/QR-Scan-Einstieg in `/scan` (Browserkamera + Fallback auf manuelle Eingabe) mit unveraendertem Backend-Lookup
	•	Auth-Basis mit Login, Access-Token und erster Rollenpruefung (Admin-Schutz)
	•	Vertieftes Dashboard und Orders-Read-Flow (`/dashboard/overview`, `GET /orders`, `GET /orders/{id}`)
	•	Erster realer ERP-Read-Flow (`/erp/materials/*`, `/erp/orders/*/validate`) auf konfigurierter Adapterbasis
	•	Kontrollierter ERP-Transfer-Flow (`/erp/transfers/*`) mit Status-/Auditdaten und optional echtem ERP-Write nur beim Send-Schritt
	•	Foto-Dokumentationsflow (`/photos`) fuer Upload, Kontextzuordnung und Anzeige in Inventur-/Scan-Oberflaechen
	•	Kommentarflow (`/comments`) fuer entitaetsgebundene Notizen ohne Chat-/Realtime-Komplexitaet
	•	PWA-Grundlage (`/manifest.json`, `public/sw.js`, App-Icons) mit serverbasierter Laufzeit ohne Offline-Sync-Logik

⸻

🧪 Tests

Tests werden mit pytest ausgeführt:

pytest

Aktuell:
	•	Domain-, Application- und API-Tests vorhanden

⸻

🌐 Verfügbare API-Endpunkte

Hinweis zur Absicherung:
	•	geschützt (Auth erforderlich): `/orders/*`, `/materials/*`, `/inventory/*`, `/admin/*`
	•	öffentlich: `/health`, `/system/status`, `/auth/login`
	•	sensible Aktionen zusaetzlich rollenbasiert (403 bei fehlender Rolle)

	•	POST /orders
	•	GET /orders
	•	GET /orders/{id}
	•	POST /orders/{id}/reserve
	•	POST /orders/reprioritize
	•	POST /orders/{id}/link-erp
	•	POST /orders/recalculate
	•	POST /auth/login
	•	GET /auth/me
	•	GET/POST /admin/erp-profiles
	•	GET/PUT /admin/erp-profiles/{id}
	•	GET/POST /admin/endpoints
	•	GET/POST /admin/mappings
	•	GET/POST /admin/cutting-machines
	•	GET/POST /admin/users
	•	GET/POST /inventory/counts
	•	POST /inventory/compare
	•	POST /inventory/corrections
	•	POST /inventory/corrections/{id}/confirm
	•	POST /inventory/corrections/{id}/cancel
	•	GET /materials/search
	•	GET /materials/{article_number}
	•	GET /erp/materials/{reference}
	•	GET /erp/materials/{reference}/stock
	•	GET /erp/orders/{reference}/validate
	•	GET /erp/transfers
	•	POST /erp/transfers
	•	POST /erp/transfers/{id}/ready
	•	POST /erp/transfers/{id}/approve
	•	POST /erp/transfers/{id}/send
	•	POST /erp/transfers/{id}/fail
	•	POST /photos
	•	GET /photos?entity_type=&entity_id=
	•	GET /photos/{id}/file
	•	POST /comments
	•	GET /comments?entity_type=&entity_id=
	•	GET /audit-logs
	•	GET /dashboard/overview
	•	GET /health
	•	GET /system/status

⸻

🖥️ Frontend starten (lokal)

Voraussetzungen:
	•	Node.js installiert

Setup:
	•	cd frontend
	•	npm install

Start:
	•	npm run dev

Zugriff:
	•	Frontend: http://localhost:3001

⸻

▶️ App-Starter fuer lokale Entwicklung

Mit einem Befehl werden lokale Dev-Prozesse sauber neu gestartet:

	•	Prozesse auf Port 3001 und 9999 beenden
	•	docker compose down && docker compose up -d --build
	•	`frontend/.next` loeschen
	•	Frontend-Dev-Server neu starten
	•	optional Python-Testserver auf Port 9999 starten
	•	am Ende Status + URLs ausgeben

Aufrufe:

	•	`./scripts/start-app.sh localhost`
	•	`./scripts/start-app.sh lan`
	•	`./scripts/start-app.sh tailscale`
	•	`./scripts/start-app.sh localhost --with-testserver`

Modi:

	•	`localhost`: nur fuer lokale Nutzung auf dem Mac (`localhost:3001` <-> `localhost:8001`)
	•	`lan`: fuer Nutzung im Heimnetz; nutzt automatisch die LAN-IP des Macs (z. B. `192.168.x.x`)
	•	`tailscale`: ermittelt automatisch die Tailscale-IP und startet Frontend mit:
		•	`NEXT_PUBLIC_API_BASE_URL=http://<TS_IP>:8001`
		•	`NEXT_PUBLIC_MOBILE_APP_URL=http://<TS_IP>:3001/login`

⸻

📱 PWA-Installation (Basis)

- Android/Chrome: Seite oeffnen -> Browsermenue -> "App installieren".
- iOS/Safari: Seite oeffnen -> Teilen -> "Zum Home-Bildschirm".
- Die App bleibt serverbasiert; es gibt keine Offline-Synchronisation oder lokale Fachlogik.
	•	Backend-API (Standard): http://localhost:8001

Umgebungsvariable:
	•	`NEXT_PUBLIC_API_BASE_URL` (Default: `http://localhost:8001`)

🗄️ Migrationen im Container

Alembic wird über die in `backend/pyproject.toml` definierten Abhängigkeiten bereitgestellt.

Beispiele:
	•	docker compose run --rm backend alembic --version
	•	docker compose run --rm backend python -m alembic -c backend/alembic.ini heads
	•	docker compose run --rm backend python -m alembic -c backend/alembic.ini upgrade head

⸻

📚 Dokumentation

Die zentrale Projektdokumentation liegt unter:
	•	docs/pflichtenheft.md → Fachliche Anforderungen
	•	docs/architecture.md → Systemarchitektur
	•	docs/datenbankmodell.md → Datenstruktur
	•	docs/projektrules.md → Entwicklungsregeln
	•	docs/projectstructure.md → Projektstruktur
	•	docs/implementationplan.md → Umsetzungsplan
	•	docs/pilot_scenarios.md → Pilot-Abnahmeszenarien aus Nutzersicht

👉 Diese Dokumente sind verbindlich führend

⸻

🤖 Entwicklung mit Agent (Cursor)

Dieses Projekt ist für die Zusammenarbeit mit einem Agenten ausgelegt.

Wichtige Regeln:
	•	Vor jeder Umsetzung müssen die Dokumente gelesen werden
	•	Umsetzung erfolgt strikt phasenweise
	•	Architekturregeln sind verbindlich
	•	keine Fachlogik außerhalb der Domain/Application

👉 Details: .cursor/cursor.rules

⸻

🛠️ Nächste Schritte
	•	weitere Ausbauschritte aus Backlog

⸻

⚠️ Hinweise
	•	Dieses Projekt enthält aktuell bewusst keine Business-Logik
	•	Struktur und Architektur stehen im Vordergrund
	•	Umsetzung erfolgt kontrolliert und schrittweise

⸻

📌 Status

🟢 Projektbasis steht
🟢 Phase 0–8 abgeschlossen
🟢 Pilot-/Produktionsreife (Start, Seed, Empty States, Fehlerhinweise) umgesetzt
🟡 Nächster Fokus: inkrementelle Erweiterungen

⸻

🧭 Wichtigste Seiten (Pilotbetrieb)

	•	`/scan` -> Material per Eingabe/Kamera suchen, ERP-Read sehen, Fotos/Kommentare erfassen
	•	`/orders` -> Aufträge anlegen, reservieren, priorisieren, ERP-Link setzen
	•	`/inventory` -> Inventur zählen, Abweichung prüfen, Korrektur anlegen/bestätigen, Fotos/Kommentare
	•	`/erp-transfers` -> Transfer vorbereiten, freigeben, senden (kontrollierter Write-Flow)

⸻

✅ Typischer Ablauf (kurz)

1. Einloggen (z. B. `leitung1`).
2. In `/scan` Material suchen/scannen und Daten prüfen.
3. In `/orders` Auftrag erstellen und bei Bedarf reservieren.
4. In `/erp-transfers` Transfer anlegen, freigeben und senden.

⸻

🧪 Pilot testen

Für den strukturierten Pilottest mit klaren Abnahmeszenarien:
	•	siehe `docs/pilot_scenarios.md`
	•	siehe `docs/e2e_checkplan.md`
	•	siehe `docs/testzugaenge.md`

⸻

📶 Smartphone-Test im lokalen Netzwerk

Erforderlich fuer QR-/Mobiltest:
- Smartphone und Rechner im gleichen WLAN/LAN
- Frontend ueber LAN-IP erreichbar
- Backend-CORS erlaubt die LAN-Frontend-Origin

Empfohlene LAN-Konfiguration (Beispiel):
- Frontend URL: `http://192.168.178.160:3001/login`
- Backend URL: `http://192.168.178.160:8001`

Frontend-Umgebung (`frontend/.env.local`):
- `NEXT_PUBLIC_API_BASE_URL=http://192.168.178.160:8001`
- `NEXT_PUBLIC_MOBILE_APP_URL=http://192.168.178.160:3001/login`

Backend-Umgebung (docker compose / env):
- `CORS_ALLOW_ORIGINS=http://localhost:3001,http://192.168.178.160:3001`

Hinweis:
- Der QR-Code ist nur Einstiegshilfe und enthaelt keine Session-/Auth-Daten.