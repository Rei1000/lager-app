# Pflichtenheft – Lager-App für Stangenmaterial

---

## 📄 Deckblatt

**Projektname:** Lager-App für Stangenmaterial  
**Version:** 1.0  
**Datum:** 2026  
**Erstellt von:** Reiner

### Projektbeschreibung

Entwicklung einer webbasierten Anwendung zur Unterstützung von Lagerpersonal
bei der Verwaltung, Disposition und Planung von Stangenmaterial unter
Integration eines ERP-Systems (z. B. Sage 100).

---

## 📑 Inhaltsverzeichnis

1. Ziel des Projekts
2. Systemübersicht
3. Fachliche Grundlagen
4. Funktionale Anforderungen
5. ERP-Integration
6. Technische Architektur
7. Backend-API
8. Datenmodell
9. Ablauf- und Sequenzlogik
10. Nichtfunktionale Anforderungen
11. Teststrategie
12. Erweiterbarkeit
13. Glossar
14. Zusammenfassung

---

## 1. Ziel des Projekts

Ziel ist die Entwicklung einer webbasierten Anwendung zur Unterstützung von
Lagerpersonal beim Umgang mit Stangenmaterial.

Die Anwendung soll:

- Materialbestände transparent darstellen
- Materialverfügbarkeit berechnen
- Aufträge disponieren und priorisieren
- Reservierungen ermöglichen
- Reststücke berücksichtigen
- ERP-Daten integrieren
- eine konfigurierbare ERP-Anbindung bereitstellen

### Grundsatz

Die Anwendung ist eine **dispositive Planungsschicht**.

Das ERP-System bleibt das **führende System** für:

- Bestände
- Materialstammdaten
- Aufträge

---

## 2. Systemübersicht

### Komponenten

[ Frontend (Browser) ]
↓
[ Backend (API + Logik) ]
↓
[ ERP-Integrationsschicht ]
↓
[ ERP-System ]
Zusätzlich:
[ Datenbank ]
[ Admin-Oberfläche ]

---

## 3. Fachliche Grundlagen

### 3.1 Materialmodell

Material wird als **Materialtyp** geführt.

#### Attribute

- Artikelnummer (zentraler Schlüssel)
- Bezeichnung
- Profil (z. B. 40x40)
- Einheit (Meter)
- Mindestrestlänge
- ERP-Bestand (Vollmaterial)
- Reststückbestand (aggregiert)

---

### 3.2 Bestandslogik

Verfügbarer Bestand =
ERP-Bestand
• offene ERP-Aufträge
• App-Reservierungen

• optional Reststückbestand

#### Wichtige Regeln

- ERP-Bestand wird durch die App nicht direkt verändert
- Reservierungen sind ausschließlich app-intern
- reale Bestandsveränderung erfolgt nur im ERP

---

### 3.3 Reststücklogik

- Reststücke entstehen unterhalb der Mindestlänge
- werden pro Materialtyp aggregiert
- optional nutzbar
- keine automatische Optimierung im MVP

#### Wichtige Regel (Reststücklogik)

Die Nutzung von Reststücken erfolgt bewusst durch den Benutzer.

---

### 3.4 Sägebreite

## Gesamtbedarf = Stückzahl × (Abschnittslänge + Sägebreite)

### 3.5 Ampellogik

| Status | Bedeutung                     |
| ------ | ----------------------------- |
| Grün   | vollständig erfüllbar         |
| Gelb   | nur mit Reststücken erfüllbar |
| Rot    | nicht erfüllbar               |

---

### 3.6 Reservierung

- erfolgt ausschließlich in der App
- blockiert verfügbaren Bestand
- keine direkte ERP-Buchung im MVP
- spätere Verknüpfung mit ERP-Auftrag

---

### 3.7 Priorisierung

- Aufträge werden sortiert
- Reihenfolge beeinflusst Materialverfügbarkeit
- jede Änderung löst Neuberechnung aus

#### Wichtige Regel

- Priorisierung erfolgt materialbezogen
- Berechnung erfolgt sequenziell entlang der Reihenfolge

---

### 3.8 Statusmodell

Entwurf → geprüft → reserviert → verknüpft → bestätigt → abgeschlossen
↓
storniert

---

## 4. Funktionale Anforderungen

### 4.1 Login

- Benutzername / Passwort
- Rollen:
  - Lager
  - Leitung
  - Admin

---

### 4.2 Dashboard

#### Anzeige (Dashboard)

- offene Aufträge
- Status
- Priorität
- Ampelfarbe

#### Funktionen (Dashboard)

- Auftrag öffnen
- Priorität ändern (Drag & Drop)
- neuen Auftrag anlegen

---

### 4.3 Auftragserstellung

#### Ablauf

1. Material suchen (Artikelnummer / Name)
2. Material auswählen
3. Eingabe:
   - Stückzahl
   - Länge
   - Säge
4. Option: Reststücke berücksichtigen
5. Live-Berechnung
6. Ergebnisanzeige
7. Reservierung

---

### 4.4 Auftragsdetail

#### Anzeige (Auftragsdetail)

- Bedarf
- Restanteile
- Status
- ERP-Verknüpfung

#### Aktionen

- ERP-Auftrag verknüpfen
- Reservierung stornieren

---

### 4.5 ERP-Verknüpfung

- manuelle Verknüpfung über Auftragsnummer
- Statusänderung

Optional:

- Reststückübertragung ins ERP

---

### 4.6 Admin-Oberfläche

#### Funktionen (Admin)

- ERP-Profile verwalten
- Endpunkte konfigurieren
- Feldmapping definieren
- Sägen verwalten
- Materialparameter pflegen
- Benutzer verwalten

---

### 4.7 Login- und Verbindungsmodell

#### 1. Startbildschirm

Die Anwendung startet immer mit einem zentralen Login-Screen.

Dieser enthält:

- Auswahl der Verbindung (ERP-Kontext)
- Eingabefelder für Benutzername und Passwort
- Auswahl des Login-Modus (ERP-Benutzer oder Admin)
- optionalen QR-Code für den mobilen Einstieg

Der Login-Screen ist der zentrale Einstiegspunkt in die Anwendung.

#### 2. Verbindungswahl

Vor dem Login muss der Benutzer eine Verbindung auswählen.

Beispiele:

- Sage Simulator
- Sage Connect
- Middleware

Die gewählte Verbindung bestimmt:

- gegen welches System authentifiziert wird
- in welchem ERP-Kontext gearbeitet wird
- welche Datenquellen und Funktionen verwendet werden

Die zuletzt verwendete Verbindung kann lokal gespeichert werden, muss aber jederzeit änderbar sein.

#### 3. Login-Arten

Es gibt zwei klar getrennte Login-Arten:

ERP-Benutzer-Login:

- Anmeldung mit den Zugangsdaten des gewählten ERP-Systems
- beim Simulator mit Simulator-Benutzern
- bei realer Integration später mit ERP-Zugangsdaten
- nach erfolgreichem Login wird der Benutzer intern einer App-Rolle zugeordnet

Admin-Login:

- Anmeldung gegen die Anwendung selbst
- unabhängig vom ERP-System
- Zugriff auf Admin-Oberfläche und Systemkonfiguration
- vollständiger Zugriff auf alle Funktionen

Diese beiden Login-Arten dürfen fachlich nicht vermischt werden.

#### 4. Rollenmodell

Nach der Authentifizierung wird jedem Benutzer eine App-Rolle zugeordnet.

Vorgesehene Rollen:

- Lager
- Leitung
- Admin

Die Rolle bestimmt:

- sichtbare Bereiche der Anwendung
- verfügbare Funktionen
- erlaubte Aktionen

Ein ERP-Benutzer ohne zugewiesene Rolle:

- darf sich anmelden
- erhält jedoch keinen Zugriff auf operative Funktionen
- bekommt eine klare Meldung, dass eine Rollen-Zuweisung fehlt

#### 5. Sicht- und Funktionssteuerung

Die Rolle steuert:

- Navigation
- Seitenzugriff
- erlaubte Aktionen

Die Authentifizierung selbst enthält keine fachliche Logik zur Freigabe von Funktionen.

#### 6. QR-Code für mobilen Einstieg

Der Login-Screen enthält einen QR-Code.

Zweck:

- schnelles Öffnen der mobilen Anwendung auf einem Smartphone

Der QR-Code:

- ersetzt nicht den Login
- überträgt keine Session
- dient nur als Einstiegshilfe

Der Benutzer muss sich auf dem mobilen Gerät regulär anmelden.

#### 7. Session-Kontext

Nach erfolgreichem Login enthält die Session:

- Benutzeridentität
- zugewiesene Rolle
- Login-Modus (ERP oder Admin)
- gewählte Verbindung (ERP-Profil)

Dieser Kontext wird für alle weiteren Aktionen verwendet.

#### 8. Fehlerfälle

Das System muss folgende Fälle klar behandeln:

- Verbindung nicht erreichbar
- ungültige Zugangsdaten
- erfolgreiche Authentifizierung ohne Rollen-Zuweisung
- unzureichende Berechtigung für eine Aktion
- nicht konfigurierte Verbindung

Alle Fehler müssen verständlich und eindeutig kommuniziert werden.

#### 9. Simulator-Verhalten

Für den Sage-Simulator gilt:

- eigene Benutzerkonten
- simulierte Benutzer-IDs und Rollen
- Materialien, Bestände und Aufträge als Testdaten
- Verhalten analog zu einem realen ERP-System

Der Simulator wird fachlich wie eine echte Verbindung behandelt.

---

## 5. ERP-Integration

### Prinzip

ERP bleibt führend für:

- Bestände
- Aufträge
- Materialstammdaten

---

### Funktionsklassen

- material.search
- material.get
- material.stock.get
- erp_orders.list_by_material
- erp_order.get
- stock.adjust

---

### Konfiguration

- Endpunkte konfigurierbar
- Mapping konfigurierbar
- Authentifizierung konfigurierbar

---

### Erweiterung

- Import von API-Dokumentationen
- automatische Endpunktvorschläge

---

## 6. Technische Architektur

### Frontend

- Next.js
- TypeScript
- shadcn/ui
- Tailwind CSS
- responsive

---

### Backend

- Python
- FastAPI

---

### Architekturprinzipien

#### Domain-Driven Design

- Domäne
- Anwendung
- Infrastruktur

#### Hexagonale Architektur

[ API ]
↓
[ Application Layer ]
↓
[ Domain ]
↑
[ Ports ]
↑
[ Adapter ]

---

### Containerisierung

- frontend
- backend
- database

---

### Wichtige Regel (Containerisierung)

Die Anwendung kommuniziert ausschließlich über das Backend mit dem ERP.  
Direkte Frontend-ERP-Kommunikation ist ausgeschlossen.

---

## 7. Backend-API

Bereitstellung einer REST-API für:

- Authentifizierung
- Material
- Aufträge
- ERP-Verknüpfung
- Admin-Funktionen

---

## 8. Datenmodell

### Material

- id
- article_number
- name
- profile
- unit
- min_rest_length
- erp_stock
- rest_stock
- last_sync_at

---

### Auftrag

- id
- material_id
- quantity
- part_length
- kerf
- total_demand
- rest_usage
- status
- priority
- erp_order_number
- reserved_at

---

### ERP-Profil

- id
- name
- connection_type
- base_url

---

### Endpoint

- functional_key
- method
- path
- mapping

---

## 9. Ablauf- und Sequenzlogik

### Auftrag erstellen

User → Frontend → Backend → ERP

1. Material suchen
2. Daten laden
3. Eingabe
4. Berechnung (inkl. Priorität und Reststücken)
5. Reservierung speichern

---

### Priorisierung

User → Backend

1. Reihenfolge ändern
2. Neuberechnung
3. Status aktualisieren

---

### ERP-Verknüpfung

User → Backend → ERP

1. Auftrag auswählen
2. ERP-Nummer setzen
3. Validierung
4. Status ändern

---

## 10. Nichtfunktionale Anforderungen

### Sicherheit

- HTTPS
- Rollenmodell
- sichere Speicherung

---

### Performance

- schnelle Reaktionszeiten
- Echtzeitberechnung

---

### Verfügbarkeit

- ≥ 99 %
- ERP-Ausfälle dürfen App nicht blockieren

---

### Offline-Fähigkeit

- eingeschränkt nutzbar
- Synchronisation bei Verbindung

---

### Logging

- vollständige Nachvollziehbarkeit

---

## 11. Teststrategie

### TDD

- Domain-Logik testgetrieben

---

### Testarten

- Unit-Tests
- Integrations-Tests
- API-Tests
- End-to-End-Tests

---

## 12. Erweiterbarkeit

Geplant:

- weitere ERP-Systeme
- Barcode/QR-Scanning
- Push-Benachrichtigungen
- Inventur
- Chat
- Foto-Upload
- PWA

---

## 13. Glossar

- **Artikelnummer:** eindeutige Identifikation eines Materials
- **Reststück:** Material unterhalb Mindestlänge
- **Reservierung:** temporäre Blockierung in der App
- **ERP:** führendes System für Bestände und Aufträge

---

## 14. Zusammenfassung

Das System ist:

- modular
- erweiterbar
- ERP-unabhängig
- fachlich sauber
- skalierbar
