# Umsetzungsplan – Lager-App für Stangenmaterial

---

## 1. Ziel dieses Dokuments

Dieses Dokument definiert die **verbindliche Reihenfolge der Umsetzung**.

Es dient dazu:

- den Agenten zu steuern
- eine saubere, schrittweise Entwicklung sicherzustellen
- Chaos durch zu große Aufgaben zu vermeiden
- Abhängigkeiten korrekt zu berücksichtigen

---

## 2. Grundregeln

- Es darf immer nur **eine Phase gleichzeitig** umgesetzt werden
- Eine Phase muss vollständig abgeschlossen sein, bevor die nächste beginnt
- Es dürfen **keine Inhalte aus späteren Phasen vorgezogen werden**
- Jede Umsetzung erfolgt **TDD-getrieben**
- Architektur- und Projektregeln sind jederzeit einzuhalten

---

## 3. Phasenübersicht

0. Projektbasis (Bootstrap) ✅  
1. Persistenz & Infrastruktur ✅  
2. Domain-Kern ✅  
3. Application Layer (Use Cases) ✅  
4. API Layer ✅  
5. Frontend Basis ✅  
6. ERP-Integrationsbasis ✅  
7. Admin-Oberfläche ✅  
8. Erweiterungen ✅  

---

## 4. Phase 0 – Projektbasis (Bootstrap)

### Ziel

Technische Grundlage schaffen, ohne Fachlogik.

---

### Inhalte

- FastAPI-Projektstruktur initialisieren
- Docker Setup erstellen
- docker-compose konfigurieren
- PostgreSQL anbinden
- pyproject.toml vervollständigen
- pytest einrichten
- grundlegende Projektstruktur prüfen
- Healthcheck Endpoint erstellen

---

### Verboten

- keine Fachlogik
- keine Domain-Objekte
- keine ERP-Logik
- keine Geschäftsregeln

---

### Ergebnis

- Backend startet
- Datenbank erreichbar
- Tests laufen
- Docker funktioniert

---

## 5. Phase 1 – Persistenz & Infrastruktur

### Ziel

Technische Datenbasis vorbereiten.

---

### Inhalte

- SQLAlchemy Base erstellen
- DB Session Management
- Alembic initialisieren
- erste Migration erstellen
- ORM-Modelle implementieren (gemäß Datenmodell)
- Repository-Strukturen vorbereiten (nur Interfaces + einfache Implementierung)

---

### Verboten

- keine Fachlogik in Repositories
- keine Berechnungslogik
- keine Domain-Regeln

---

### Ergebnis

- Tabellenstruktur vorhanden
- Migration funktioniert
- Datenzugriff technisch möglich

---

## 6. Phase 2 – Domain-Kern

### Ziel

Fachlogik isoliert implementieren.

---

### Inhalte

- MaterialType
- AppOrder
- RestStockAccount
- TrafficLight (Value Object)

#### Fachlogik:

- Verfügbarkeitsberechnung
- Bedarfsberechnung (inkl. Sägebreite)
- Ampellogik
- Reststücklogik
- Priorisierungslogik
- Statusübergänge

---

### Regeln

- keine Infrastrukturabhängigkeiten
- reine Domain-Logik
- vollständig testgetrieben

---

### Ergebnis

- Domain vollständig testbar
- keine DB-Abhängigkeit
- keine API-Abhängigkeit

---

## 7. Phase 3 – Application Layer (Use Cases)

### Ziel

Fachliche Abläufe orchestrieren.

---

### Inhalte

- CreateOrderUseCase
- RecalculateOrdersUseCase
- ReserveOrderUseCase
- ReprioritizeOrdersUseCase
- LinkErpOrderUseCase

---

### Regeln

- Nutzung von Ports
- keine DB-Details
- keine ERP-Details

---

### Ergebnis

- Use Cases funktionieren isoliert
- Domain wird korrekt genutzt

---

## 8. Phase 4 – API Layer

### Ziel

Backend nach außen zugänglich machen.

---

### Inhalte

- FastAPI Router
- Request/Response Schemas
- Validation
- Fehlerbehandlung

---

### Verboten

- keine Fachlogik
- keine direkten DB-Zugriffe

---

### Ergebnis

- API-Endpunkte funktionieren
- Use Cases werden korrekt aufgerufen

---

## 9. Phase 5 – Frontend Basis

### Ziel

Grundlegende Benutzeroberfläche.

---

### Inhalte

- Next.js Setup
- Login UI
- Dashboard-Grundstruktur
- Materialsuche UI
- Auftragsliste UI
- Auftragserstellung UI

---

### Regeln

- keine Fachlogik im Frontend
- nur API-Nutzung

---

### Ergebnis

- erste End-to-End Nutzung möglich

---

## 10. Phase 6 – ERP-Integrationsbasis

### Ziel

ERP-Anbindung vorbereiten.

---

### Inhalte

- ERP-Profile
- ERP-Ports definieren
- ERP-Adapter (Stub + erste Implementierung)
- Endpunkt-Konfiguration
- Feldmapping

---

### Verboten

- keine ERP-Logik in Domain
- keine hartcodierten Endpunkte

---

### Ergebnis

- ERP-Struktur vorbereitet
- Erweiterbar für Sage 100

---

## 11. Phase 7 – Admin-Oberfläche

### Ziel

Konfigurierbarkeit sicherstellen.

---

### Inhalte

- ERP-Profile UI
- Endpunktverwaltung
- Mapping UI
- Benutzerverwaltung
- Sägenverwaltung

---

### Ergebnis

- System konfigurierbar

---

## 12. Phase 8 – Erweiterungen

### Ziel

Zusatzfunktionen implementieren.

---

### Inhalte

- Reststückübertragung ins ERP
- Inventur
- Barcode/QR-Scanning ✅
- Push-Benachrichtigungen
- Chat ✅
- Foto-Upload ✅
- PWA ✅
- ERP-Read-Daten in bestehenden Arbeitsoberflächen sichtbar machen (Scan, Orders, Dashboard) als reiner Read-/Darstellungsschritt ✅
- kontrollierten ERP-Write-Vorbereitungsflow aufbauen (Transfer-Requests, Statusfluss, simuliertes Senden ohne echte ERP-Schreiboperation) ✅
- feinere zentrale Rollen- und Rechtepruefung fuer sensible API-Aktionen (Admin/Leitung/Lager) ✅
- ERP-Write-Freigabestufe ergaenzen (ready -> approved -> send als erster optional echter Write) mit klarer Rollenfreigabe und Auditdaten ✅
- Audit- und Protokollierungsschicht fuer sensible Aktionen im Application Layer ausbauen ✅
- Pilot-/Produktionsreife erhoehen (idempotenter Demo-Seed, vereinfachter Docker-Start inkl. Auto-Migration, Empty States, klarere Fehleranzeigen, README-Betriebsanleitung) ✅
- Pilotvorbereitung und Abnahmeszenarien dokumentieren (Nutzungsszenarien, Checklisten, Pilot-Notizen, README-Verweis) ✅
- Login-, Verbindungs- und Rollenmodell erweitern (zentraler Login-Screen mit Verbindungswahl, klare Trennung ERP-Login/Admin-Login, Rollenzuordnung nach Authentifizierung, QR-Code nur als mobiler Einstieg; keine Vermischung der Auth-Arten, keine QR-basierte Authentifizierung, keine neue Domain-Fachlogik, keine Hardcodierung von ERP-Verbindungen; Umsetzungsbereiche: Frontend Login-Screen, Backend Auth-/Session-Kontext, zentrale Rollenpruefung, Simulator als normale Verbindung; dokumentengetriebene Umsetzung vor ad-hoc Login-Implementierung)

---

## 13. Arbeitsweise mit dem Agenten

Jeder Prompt muss:

- sich auf **eine Phase oder einen Schritt** beziehen
- klare Grenzen enthalten
- Verbote enthalten (was NICHT gemacht werden darf)

---

## 14. Definition of Done pro Phase

Eine Phase ist abgeschlossen, wenn:

- alle definierten Inhalte umgesetzt sind
- keine Inhalte aus späteren Phasen enthalten sind
- Tests vorhanden und erfolgreich sind
- Architektur eingehalten wurde
- Dokumentation geprüft wurde

---

## 15. Wichtigste Regel

👉 Der Agent darf niemals versuchen, mehrere Phasen gleichzeitig umzusetzen.