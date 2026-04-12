# Datenbankmodell – Lager-App für Stangenmaterial

<!-- markdownlint-disable MD024 -->

---

## 1. Ziel des Datenmodells

Dieses Dokument beschreibt das relationale Datenmodell der Lager-App.

Es definiert:

- die zentralen Entitäten
- deren Beziehungen
- die fachliche Bedeutung der Daten
- welche Daten führend sind
- welche Daten nur app-intern sind
- welche Regeln in der Datenbank und welche in der Domäne liegen

Dieses Dokument ergänzt:

- docs/pflichtenheft.md
- docs/architecture.md
- docs/projektrules.md

---

## 2. Grundprinzipien

### 2.1 ERP-Führungsprinzip

- Das ERP ist die führende Quelle für:
  - Materialstammdaten
  - Bestände
  - reale Aufträge

- Die App speichert:
  - abgeleitete Daten
  - Reservierungen
  - Konfiguration
  - Statusinformationen

---

### 2.2 Trennung Domain vs. Persistenz

- Datenbankmodelle sind technische Repräsentationen
- Domänenlogik wird **nicht** in der Datenbank implementiert
- ORM-Modelle sind keine Domain-Modelle

---

### 2.3 PostgreSQL als Zielsystem

- relationale Datenbank
- Nutzung von:
  - Foreign Keys
  - Constraints
  - Indizes
  - JSONB für flexible Konfiguration

---

### 2.4 Migrationen

- Schemaänderungen erfolgen ausschließlich über Migrationen
- keine direkten Änderungen an Tabellenstrukturen

---

## 3. Überblick der Kernentitäten

Das System besteht aus folgenden Hauptbereichen:

### Benutzer & Zugriff

- roles
- users

### Material & Bestand

- material_types
- rest_stock_accounts

### Produktion / Aufträge

- app_orders
- order_status_history

### Maschinen

- cutting_machines

### ERP-Konfiguration

- erp_profiles
- erp_auth_configs
- erp_function_endpoints
- erp_field_mappings

### ERP-Transfer-Vorbereitung

- erp_transfer_requests

### Protokollierung

- audit_logs
- photos
- comments

---

## 4. Tabellenbeschreibung

---

## 4.1 roles

Beschreibt Benutzerrollen im System.

### Zweck

- Steuerung von Zugriff und Berechtigungen

### Wichtige Felder

- code (z. B. admin, lager, leitung)
- name
- description

---

## 4.2 users

Speichert Benutzerkonten.

### Zweck

- Authentifizierung
- Zuordnung von Aktionen

### Wichtige Felder

- username
- password_hash
- role_id
- erp_user_reference

---

## 4.3 material_types

Zentrale fachliche Entität.

### Zweck

- Repräsentiert einen Materialtyp (z. B. 40x40 Stahlprofil)

### Wichtige Regeln

- eindeutig über article_number
- enthält keine führende Bestandslogik

### Wichtige Felder

- article_number
- name
- profile
- min_rest_length_mm
- erp_stock_m (nur synchronisiert)
- rest_stock_m (aggregiert)

---

## 4.4 rest_stock_accounts

Aggregiertes Reststückkonto pro Materialtyp.

### Zweck

- Verwaltung aller Reststücke eines Materials

### Regeln

- genau ein Eintrag pro Materialtyp
- Reststücke werden zusammengefasst

### Wichtige Felder

- material_type_id (unique)
- rest_stock_id
- total_rest_stock_m

---

## 4.5 cutting_machines

Speichert verfügbare Sägen.

### Zweck

- Definition der Schnittbreite (Kerf)

### Wichtige Felder

- name
- kerf_mm

---

## 4.6 app_orders

Zentrale operative Tabelle.

### Zweck

- Speichert alle Aufträge innerhalb der App

### Wichtige Regeln

- enthält berechnete Werte (Snapshots)
- beeinflusst Reservierung und Priorisierung

### Wichtige Felder

- material_type_id
- quantity
- part_length_mm
- kerf_mm_snapshot

- calculated_total_demand_m
- demand_from_full_stock_m
- demand_from_rest_stock_m
- shortage_m

- traffic_light
- status
- priority_order

- erp_order_number
- reserved_at
- linked_at

---

## 4.7 order_status_history

Speichert Statusänderungen.

### Zweck

- Nachvollziehbarkeit
- Audit

### Wichtige Felder

- app_order_id
- old_status
- new_status
- changed_by_user_id

---

## 4.8 erp_profiles

Beschreibt ein ERP-System.

### Zweck

- Konfiguration unterschiedlicher ERP-Anbindungen

### Wichtige Felder

- name
- erp_type
- connection_type
- base_url

---

## 4.9 erp_auth_configs

Speichert Authentifizierungsdaten.

### Zweck

- Zugriff auf ERP absichern

### Wichtige Felder

- auth_type
- client_id
- username
- token_url

---

## 4.10 erp_function_endpoints

Definiert fachliche ERP-Funktionen.

### Zweck

- Abbildung von Funktionsklassen auf API-Endpunkte

### Beispiele

- material.search
- material.get
- material.stock.get

### Wichtige Felder

- functional_key
- http_method
- path_template

---

## 4.11 erp_field_mappings

Mapping zwischen ERP und App.

### Zweck

- flexible Datenzuordnung

### Wichtige Felder

- app_field
- erp_field
- direction

---

## 4.12 audit_logs

Allgemeine Protokollierung.

### Zweck

- Nachvollziehbarkeit von Aktionen

### Wichtige Felder

- action
- entity_type
- entity_id
- user_id
- occurred_at
- comment
- payload_json

---

## 4.13 inventory_counts

Inventurzaehlungen fuer Vor-Ort-Bestandserfassung.

### Zweck

- erfassten Ist-Bestand dokumentieren
- Referenzbestand und Abweichung nachvollziehbar speichern

### Wichtige Felder

- material_article_number
- counted_stock_mm
- reference_stock_mm
- difference_mm
- difference_type
- status
- counted_by_user_id
- created_at

---

## 4.14 stock_corrections

Korrekturvorgaenge auf Basis von Inventurabweichungen.

### Zweck

- Korrekturwunsch protokollieren
- Bestaetigung oder Storno nachvollziehbar speichern

### Wichtige Felder

- inventory_count_id
- material_article_number
- correction_mm
- status
- requested_by_user_id
- confirmed_by_user_id
- canceled_by_user_id
- created_at
- confirmed_at
- canceled_at

---

## 4.15 erp_transfer_requests

Kontrollierte Uebergabevorbereitung fuer spaetere ERP-Write-Schritte.

### Zweck

- Write-relevante Uebergaben als App-interne Requests nachvollziehbar speichern
- Status- und Benutzerhistorie fuer kontrollierte Freigabe dokumentieren

### Wichtige Felder

- order_id
- material_article_number
- status (`draft`, `ready`, `approved`, `sent`, `failed`)
- requested_by_user_id
- ready_by_user_id
- approved_by_user_id
- sent_by_user_id
- failed_by_user_id
- created_at
- ready_at
- approved_at
- sent_at
- failed_at
- failure_reason

---

## 4.16 photos

Dokumentiert Fotoanhaenge fuer Material-, Inventur- und Korrekturkontexte.

### Zweck

- visuelle Nachvollziehbarkeit von Materialzustaenden und Inventurvorgaengen
- Trennung von Dateispeicher (file_key) und Metadaten in der Datenbank

### Wichtige Felder

- entity_type (z. B. `material`, `inventory_count`, `stock_correction`)
- entity_id (fachliche Ziel-ID als String)
- file_key (Storage-Referenz)
- original_filename
- uploaded_by_user_id
- uploaded_at
- comment

---

## 4.17 comments

Einfaches, entitaetsgebundenes Kommentarmodell fuer interne Abstimmung.

### Zweck

- kurze, nachvollziehbare Hinweise direkt am fachlichen Objekt
- Kommunikation ohne Chat-/Thread-Komplexitaet

### Wichtige Felder

- entity_type (z. B. `material`, `order`, `inventory_count`, `stock_correction`, `erp_transfer`)
- entity_id (fachliche Ziel-ID als String)
- text
- created_by_user_id
- created_at

---

## 5. Beziehungen

### Überblick

- roles 1:n users
- material_types 1:n app_orders
- material_types 1:1 rest_stock_accounts
- cutting_machines 1:n app_orders
- users 1:n app_orders
- app_orders 1:n order_status_history
- erp_profiles 1:n erp_function_endpoints
- erp_function_endpoints 1:n erp_field_mappings
- users 1:n inventory_counts
- inventory_counts 1:n stock_corrections
- users 1:n stock_corrections (requested/confirmed/canceled)
- users 1:n erp_transfer_requests (requested/ready/approved/sent/failed)
- users 1:n photos
- users 1:n comments

---

## 6. Fachliche Regeln im Datenmodell

### In der Datenbank

- Eindeutigkeit (article_number)
- Foreign Keys
- Basis-Constraints
- Statuswerte eingeschränkt

---

### In der Domäne

- Verfügbarkeitsberechnung
- Ampellogik
- Priorisierung
- Reservierungslogik
- Reststückverwendung

---

## 7. Indizes

Wichtige Indizes:

- material_types.article_number
- app_orders.material_type_id
- app_orders.status
- app_orders.priority_order
- audit_logs.entity_type

---

## 8. Persistenzprinzipien

- Datenbank ist keine Business-Logik-Schicht
- sie speichert Zustand, trifft aber keine Entscheidungen
- Fachlogik liegt ausschließlich in Domain/Application

---

## 9. Erweiterbarkeit

Das Modell ist vorbereitet für:

- mehrere ERP-Systeme
- zusätzliche Lagerprozesse
- Inventur
- Barcode-Scanning
- Benachrichtigungen
- Audit-Erweiterungen

---

## Authentifizierung, Rollen und Verbindungs-Kontext

### 1. Trennung von Identität und Rolle

- Benutzeridentität (Authentifizierung) ist konzeptionell von der Rollen-Zuordnung getrennt.
- Ein Benutzer kann authentifiziert sein, ohne eine App-Rolle zu haben.
- Rollen werden unabhängig von der Authentifizierungsquelle verwaltet.

### 2. ERP-Benutzer vs. App-Benutzer

- ERP-Benutzer (z. B. aus Simulator oder späteren Sage-Systemen) sind externe Identitäten.
- App-Benutzer sind interne Entitäten für Rollen, Berechtigungen und operative Zuordnung.
- Eine Zuordnung zwischen ERP-Benutzer und App-Benutzer kann über Referenzfelder erfolgen.
- Die Konzepte dürfen nicht vermischt werden.
- Es besteht keine direkte Abhängigkeit der Domäne von ERP-spezifischen Benutzerstrukturen.

### 3. Rollenmodell im Datenbankkontext

- Rollen (Lager, Leitung, Admin) sind Bestandteil der App-Daten.
- Rollen steuern Zugriff und verfügbare Funktionen.
- Die Zuordnung Benutzer -> Rolle muss im Datenmodell eindeutig abbildbar sein.

### 4. Verbindungs-Kontext

- Die gewählte Verbindung (ERP-Profil) ist primär ein Laufzeitkontext.
- Dieser Kontext wird in der Regel nicht dauerhaft als Session-Zustand in der Datenbank gespeichert.
- Verbindungen selbst werden über bestehende ERP-Konfigurationstabellen modelliert.
- Unnötige Persistenz von Sessions oder Verbindungen ist zu vermeiden.

### 5. Simulator-Benutzer

- Simulator-Benutzer sind Teil der ERP-Simulation.
- Sie müssen nicht zwingend als vollwertige App-Benutzer gespeichert werden.
- Eine Zuordnung zur App erfolgt nur bei Bedarf über Referenzen.

### 6. Erweiterungsfähigkeit

Das konzeptionelle Modell unterstützt zukünftige Erweiterungen für:

- mehrere ERP-Systeme
- unterschiedliche Authentifizierungsquellen
- Erweiterung des Rollenmodells

---

## 10. Zusammenfassung

Das Datenmodell stellt sicher:

- klare Trennung zwischen ERP und App
- stabile Grundlage für Fachlogik
- Erweiterbarkeit für zukünftige Funktionen
- saubere Integration in DDD und hexagonale Architektur

---

## 11. Technisches Datenmodell (DDL-Referenz)

Dieser Abschnitt beschreibt das konkrete Datenbankschema auf PostgreSQL-Ebene.

Die folgenden Definitionen dienen als Referenz für:

- SQLAlchemy-Modelle
- Migrationen
- Datenbankstruktur
- technische Validierung

---

## 11.1 roles

| Feld        | Typ                | Beschreibung    |
| ----------- | ------------------ | --------------- |
| id          | BIGSERIAL PK       | Primärschlüssel |
| code        | VARCHAR(50) UNIQUE | Rollen-Code     |
| name        | VARCHAR(100)       | Anzeigename     |
| description | TEXT               | Beschreibung    |

---

## 11.2 users

| Feld               | Typ                 | Beschreibung |
| ------------------ | ------------------- | ------------ |
| id                 | BIGSERIAL PK        | Benutzer-ID  |
| username           | VARCHAR(100) UNIQUE | Login        |
| password_hash      | TEXT                | Passwort     |
| display_name       | VARCHAR(150)        | Name         |
| email              | VARCHAR(255)        | E-Mail       |
| role_id            | FK → roles.id       | Rolle        |
| is_active          | BOOLEAN             | Aktiv        |
| erp_user_reference | VARCHAR(100)        | ERP-User     |
| created_at         | TIMESTAMP           | erstellt     |
| updated_at         | TIMESTAMP           | geändert     |

---

## 11.3 material_types

| Feld                  | Typ                 | Beschreibung  |
| --------------------- | ------------------- | ------------- |
| id                    | BIGSERIAL PK        | ID            |
| article_number        | VARCHAR(100) UNIQUE | Artikelnummer |
| erp_material_id       | VARCHAR(100)        | ERP-ID        |
| name                  | VARCHAR(255)        | Name          |
| profile               | VARCHAR(100)        | Profil        |
| unit                  | VARCHAR(20)         | Einheit       |
| min_rest_length_mm    | INTEGER             | Mindestlänge  |
| erp_stock_m           | NUMERIC(14,3)       | ERP-Bestand   |
| rest_stock_m          | NUMERIC(14,3)       | Restbestand   |
| main_storage_location | VARCHAR(100)        | Lagerplatz    |
| rest_storage_location | VARCHAR(100)        | Restlager     |
| is_active             | BOOLEAN             | Aktiv         |
| last_sync_at          | TIMESTAMP           | Sync          |
| created_at            | TIMESTAMP           | erstellt      |
| updated_at            | TIMESTAMP           | geändert      |

---

## 11.4 rest_stock_accounts

| Feld               | Typ                 | Beschreibung |
| ------------------ | ------------------- | ------------ |
| id                 | BIGSERIAL PK        | ID           |
| material_type_id   | FK UNIQUE           | Material     |
| rest_stock_id      | VARCHAR(100) UNIQUE | Rest-ID      |
| total_rest_stock_m | NUMERIC(14,3)       | Menge        |
| storage_location   | VARCHAR(100)        | Lager        |
| updated_at         | TIMESTAMP           | geändert     |

---

## 11.5 cutting_machines

| Feld         | Typ          | Beschreibung  |
| ------------ | ------------ | ------------- |
| id           | BIGSERIAL PK | ID            |
| machine_code | VARCHAR(50)  | Code          |
| name         | VARCHAR(150) | Name          |
| kerf_mm      | NUMERIC(8,3) | Schnittbreite |
| is_active    | BOOLEAN      | Aktiv         |

---

## 11.6 app_orders

| Feld                      | Typ          | Beschreibung   |
| ------------------------- | ------------ | -------------- |
| id                        | BIGSERIAL PK | ID             |
| material_type_id          | FK           | Material       |
| created_by_user_id        | FK           | User           |
| quantity                  | INTEGER      | Stück          |
| part_length_mm            | INTEGER      | Länge          |
| cutting_machine_id        | FK           | Säge           |
| kerf_mm_snapshot          | NUMERIC      | Snapshot       |
| include_rest_stock        | BOOLEAN      | Rest verwenden |
| calculated_total_demand_m | NUMERIC      | Bedarf         |
| demand_from_full_stock_m  | NUMERIC      | Vollmaterial   |
| demand_from_rest_stock_m  | NUMERIC      | Rest           |
| shortage_m                | NUMERIC      | Fehlmenge      |
| traffic_light             | VARCHAR(20)  | Status         |
| status                    | VARCHAR(30)  | Workflow       |
| priority_order            | INTEGER      | Reihenfolge    |
| erp_order_number          | VARCHAR(100) | ERP            |
| reserved_at               | TIMESTAMP    | reserviert     |
| linked_at                 | TIMESTAMP    | verknüpft      |

---

## 11.7 order_status_history

| Feld               | Typ          | Beschreibung |
| ------------------ | ------------ | ------------ |
| id                 | BIGSERIAL PK | ID           |
| app_order_id       | FK           | Auftrag      |
| old_status         | VARCHAR(30)  | alt          |
| new_status         | VARCHAR(30)  | neu          |
| changed_by_user_id | FK           | User         |
| changed_at         | TIMESTAMP    | Zeit         |

---

## 11.8 erp_profiles

| Feld            | Typ          | Beschreibung |
| --------------- | ------------ | ------------ |
| id              | BIGSERIAL PK | ID           |
| name            | VARCHAR(150) | Name         |
| erp_type        | VARCHAR(50)  | Typ          |
| connection_type | VARCHAR(50)  | Verbindung   |
| base_url        | TEXT         | URL          |
| tenant_code     | VARCHAR(100) | Mandant      |

---

## 11.9 erp_function_endpoints

| Feld                  | Typ          | Beschreibung |
| --------------------- | ------------ | ------------ |
| id                    | BIGSERIAL PK | ID           |
| erp_profile_id        | FK           | Profil       |
| functional_key        | VARCHAR(100) | Funktion     |
| http_method           | VARCHAR(10)  | Methode      |
| path_template         | TEXT         | URL          |
| query_template_json   | JSONB        | Query        |
| request_template_json | JSONB        | Body         |

---

## 11.10 erp_field_mappings

| Feld        | Typ          | Beschreibung |
| ----------- | ------------ | ------------ |
| id          | BIGSERIAL PK | ID           |
| endpoint_id | FK           | Endpoint     |
| app_field   | VARCHAR(100) | App          |
| erp_field   | VARCHAR(255) | ERP          |
| direction   | VARCHAR(20)  | Richtung     |

---

## 11.14 audit_logs

| Feld        | Typ          | Beschreibung                     |
| ----------- | ------------ | -------------------------------- |
| id          | BIGSERIAL PK | ID                               |
| entity_type | VARCHAR(100) | fachlicher Bereich               |
| entity_id   | VARCHAR(120) | betroffene Entität               |
| action      | VARCHAR(100) | Aktion (z. B. created, approved) |
| user_id     | BIGINT       | auslösender Benutzer             |
| occurred_at | TIMESTAMP    | Zeitpunkt der Aktion             |
| comment     | TEXT         | optionaler Hinweis/Grund         |
| payload_json| JSONB        | optionaler Snapshot              |

---

## 11.11 inventory_counts

| Feld                    | Typ          | Beschreibung          |
| ----------------------- | ------------ | --------------------- |
| id                      | BIGSERIAL PK | ID                    |
| material_article_number | VARCHAR(100) | Material              |
| counted_stock_mm        | INTEGER      | Istbestand (mm)       |
| reference_stock_mm      | INTEGER      | Referenzbestand (mm)  |
| difference_mm           | INTEGER      | Abweichung (mm)       |
| difference_type         | VARCHAR(20)  | surplus/deficit/equal |
| status                  | VARCHAR(30)  | Prozessstatus         |
| counted_by_user_id      | FK           | Benutzer              |
| comment                 | TEXT         | Kommentar             |
| created_at              | TIMESTAMP    | Erfassung             |

---

## 11.12 stock_corrections

| Feld                    | Typ          | Beschreibung |
| ----------------------- | ------------ | ------------ |
| id                      | BIGSERIAL PK | ID           |
| inventory_count_id      | FK           | Inventur     |
| material_article_number | VARCHAR(100) | Material     |
| correction_mm           | INTEGER      | Korrektur    |
| status                  | VARCHAR(30)  | Status       |
| requested_by_user_id    | FK           | angefragt von   |
| confirmed_by_user_id    | FK           | bestaetigt von  |
| canceled_by_user_id     | FK           | storniert von   |
| comment                 | TEXT         | Kommentar    |
| created_at              | TIMESTAMP    | erstellt     |
| confirmed_at            | TIMESTAMP    | bestaetigt   |
| canceled_at             | TIMESTAMP    | storniert    |

---

## 11.13 erp_transfer_requests

| Feld                    | Typ          | Beschreibung              |
| ----------------------- | ------------ | ------------------------- |
| id                      | BIGSERIAL PK | ID                        |
| order_id                | VARCHAR(100) | Auftragsreferenz          |
| material_article_number | VARCHAR(100) | Materialreferenz          |
| status                  | VARCHAR(30)  | draft/ready/approved/sent/failed |
| payload_json            | JSONB        | Transfer-Payload (optional) |
| requested_by_user_id    | FK           | angelegt von              |
| ready_by_user_id        | FK           | als ready markiert von    |
| approved_by_user_id     | FK           | freigegeben von           |
| sent_by_user_id         | FK           | send ausgefuehrt von      |
| failed_by_user_id       | FK           | als failed markiert von   |
| failure_reason          | TEXT         | Fehlerhinweis             |
| created_at              | TIMESTAMP    | erstellt                  |
| ready_at                | TIMESTAMP    | ready gesetzt             |
| approved_at             | TIMESTAMP    | freigegeben               |
| sent_at                 | TIMESTAMP    | send ausgefuehrt          |
| failed_at               | TIMESTAMP    | failed gesetzt            |

---

## 11.15 photos

| Feld                | Typ          | Beschreibung                                 |
| ------------------- | ------------ | -------------------------------------------- |
| id                  | BIGSERIAL PK | ID                                           |
| entity_type         | VARCHAR(100) | Kontexttyp (material/inventory_count/stock_correction) |
| entity_id           | VARCHAR(120) | Kontext-ID                                   |
| file_key            | VARCHAR(512) | Referenz auf lokal gespeicherte Datei        |
| original_filename   | VARCHAR(255) | Urspruenglicher Dateiname                    |
| content_type        | VARCHAR(255) | MIME-Typ (optional)                          |
| uploaded_by_user_id | FK           | hochgeladen von                              |
| uploaded_at         | TIMESTAMP    | Uploadzeitpunkt                              |
| comment             | TEXT         | optionaler Kommentar                         |

---

## 11.16 comments

| Feld               | Typ          | Beschreibung                                |
| ------------------ | ------------ | ------------------------------------------- |
| id                 | BIGSERIAL PK | ID                                          |
| entity_type        | VARCHAR(100) | Kontexttyp (material/order/inventory/...)  |
| entity_id          | VARCHAR(120) | Kontext-ID                                  |
| text               | TEXT         | Kommentartext                               |
| created_by_user_id | FK           | erstellt von                                |
| created_at         | TIMESTAMP    | Erstellzeitpunkt                            |

---

## 12. Wichtige technische Regeln

- keine Fachlogik in der Datenbank
- keine automatische Berechnung im SQL
- alle Berechnungen erfolgen im Backend
- Constraints dienen nur zur Sicherung, nicht zur Logik

---

## 13. Hinweise für Implementierung

Dieses Modell ist Grundlage für:

- SQLAlchemy Models
- Alembic Migrationen
- Backend-Repositories

Änderungen am Modell müssen immer synchron erfolgen mit:

- Datenbank
- Dokumentation
- ORM
