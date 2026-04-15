# Auftragsarchitektur – App vs. ERP (Simulator)

Dieses Dokument ist **verbindlich** für die fachliche und technische Trennung von App-Aufträgen und ERP-Aufträgen sowie für die Verfügbarkeitslogik. Es ergänzt `docs/architecture.md`, `docs/datenbankmodell.md` und `docs/projektrules.md`.

---

## 1. Unterschied App-Auftrag vs. ERP-Auftrag

| | **App-Auftrag** | **ERP-Auftrag** (Simulator / echtes ERP) |
|---|------------------|------------------------------------------|
| **Zweck** | Disposition, Priorisierung, Reservierung, Workflow in der Lager-App | Führende betriebliche Auftrags-/Bestandswahrheit im ERP |
| **Schreiben** | Die App **persistiert** App-Aufträge in PostgreSQL (`app_orders`). | ERP-Aufträge werden **nicht** in der App-DB als „ERP-Spiegel“ angelegt; sie kommen **read-only** aus dem ERP bzw. Sage-Simulator. |
| **Identität** | `order_id`: API-Schlüssel = `external_order_id` (vom Client bei Anlage) **oder** numerische `id` der Zeile `app_orders`, wenn keine externe ID gesetzt ist (z. B. Seed). | `order_no` / ERP-Referenz (z. B. `SAGE-ORD-2026-001`); führt das ERP. |
| **Verknüpfung** | Optional: `erp_order_number` am App-Auftrag verweist auf eine **bestehende** ERP-Referenz (nach erfolgreicher Prüfung / Übernahme). | Existenzprüfung z. B. über Simulator `get_order` / ERP-API. |

---

## 2. Datenquellen (DB vs. Simulator)

| Daten | Quelle | Bemerkung |
|-------|--------|-----------|
| App-Aufträge (vollständiger Datensatz) | **PostgreSQL** `app_orders` | Einzige Schreib-/Lesewahrheit für App-Workflow. |
| ERP-/Simulator-Aufträge (offene Aufträge, Pipeline) | **Sage-Simulator** (`sage_simulator_data`, Endpunkte unter `/simulator/sage/...`) | Read-only; keine eigene ERP-Tabelle in der App-DB. |
| Materialstamm / Suche für App | **PostgreSQL** `material_types` | In der Pilotphase aus dem gleichen Katalog wie der Simulator geseedet; fachlich bleibt ERP/Simulator führend für den **fachlichen** Bestand in der Zielarchitektur. |
| Verfügbarkeit (Preview, Planung) | **Kombination**: Simulator-Bestand/Pipeline **plus** App-Aufträge ohne Doppelzählung (siehe Abschnitt 5). | Implementierung: `AppAwareMaterialPlanAvailabilityAdapter` + `SageSimulatorMaterialPlanAvailabilityAdapter`. |
| Dispositions-Snapshot (Ampel, Priorität) | `DatabaseStockSnapshotAdapter`: Materialzeile aus DB + Simulator-Pipeline + App-only-Bedarf | `StockSnapshot` für `evaluate_orders_sequentially`. |

---

## 3. Lebenszyklus eines App-Auftrags

1. **Anlage** über Use Case `CreateOrderUseCase`: neuer `AppOrder` mit `created_by_user_id` (aus authentifiziertem Benutzer), Persistenz in `app_orders` (`external_order_id` = vom Client gelieferte `order_id`).
2. **Statusübergänge** nach Domain-Regeln (`ALLOWED_STATUS_TRANSITIONS`), z. B. `draft` → `checked` → `reserved` → `linked` → …
3. **ERP-Verknüpfung**: `erp_order_number` setzen, wenn eine **gültige** ERP-Referenz existiert (`SimulatorErpOrderLinkAdapter` prüft gegen Simulator-Daten).
4. **Abschluss/Storno**: Status `done` / `canceled` – aus offenen App-Aufträgen für Verfügbarkeit ausgeschlossen.

---

## 4. Rolle von `erp_order_number`

- Verknüpft einen App-Auftrag mit einer **ERP-Auftragsreferenz**, sobald diese fachlich bekannt und validiert ist.
- **Keine Doppelzählung in der Pipeline:** Wenn `erp_order_number` **gleich** der Referenz eines bereits in der ERP-/Simulator-Pipeline geführten Auftrags ist, fließt der Bedarf dieses App-Auftrags **nicht** erneut in `app_only`-Anteile ein (siehe `domain/material_pipeline.py`).

---

## 5. Verfügbarkeitsberechnung (inkl. Formel)

### 5.1 ERP-Simulator (Basis)

Aus `get_material_availability(material_reference)` (Simulator):

- `stock_m` = ERP-Lager (Simulator)
- `in_pipeline_m` = Summe `required_m` der **offenen Simulator-Aufträge** für dieses Material
- `available_m_sim` = `stock_m - in_pipeline_m`

Die Menge `in_pipeline_m` bildet die **ERP-offenen Aufträge** ab.

### 5.2 App-only-Zusatz (ohne Doppelzählung)

Für alle App-Aufträge **dieselben Materials** gelten:

- Geschlossen: `status ∈ { done, canceled }` → kein Beitrag.
- Wenn `erp_order_number` gesetzt ist **und** diese Referenz in der Menge der **Simulator-Open-Order-Referenzen** für dieses Material vorkommt → **kein** zusätzlicher Bedarf (bereits in `in_pipeline_m` enthalten).
- Andernfalls: Brutto-Bedarf in mm = `AppOrder.total_demand_mm` (inkl. Kerf nach Domain-Formel).

\[
\text{app\_additional\_m} = \frac{1}{1000} \sum \text{app\_only\_demand\_mm}
\]

### 5.3 Kombinierte Planungs-Verfügbarkeit (Preview-API)

\[
\text{in\_pipeline\_combined} = \text{in\_pipeline\_m} + \text{app\_additional\_m}
\]

\[
\text{available\_combined} = \text{stock\_m} - \text{in\_pipeline\_combined}
\]

(Rundung wie im Adapter, typischerweise drei Nachkommastellen.)

### 5.4 Dispositions-Snapshot (`StockSnapshot`)

`DatabaseStockSnapshotAdapter` liefert:

- `erp_stock_mm` = `stock_m · 1000` (aus Simulator, sofern Material im Simulator bekannt; sonst Fallback aus `material_types`).
- `open_erp_orders_mm` = `in_pipeline_m · 1000` (nur ERP/Simulator).
- `app_reservations_mm` = Summe der **app-only**-Bedarf in mm (gleiche Ausschlusslogik wie oben).
- `rest_stock_mm` = `rest_stock_m · 1000` aus `material_types`.

Die Domain-Funktion `evaluate_orders_sequentially` rechnet mit:

\[
\text{remaining\_without\_rest} = \text{erp\_stock\_mm} - \text{open\_erp\_orders\_mm} - \text{app\_reservations\_mm}
\]

Damit sind ERP-Pipeline und App-only getrennt parametrisiert, aber **gemeinsam** von der gleichen physischen Lagergröße abgezogen.

---

## 6. Regeln: speichern, lesen, Führung

| Was | Wo speichern | Wo lesen | Führend |
|-----|--------------|----------|---------|
| App-Auftrag (Workflow, Priorität, Reservierung) | PostgreSQL `app_orders` | `OrderRepositoryPort` / REST `/orders` | **App** für Dispositionsdaten |
| ERP-offene Aufträge, ERP-Bestand (Demo) | Sage-Simulator (statisch/HTTP) | `MaterialPlanAvailabilityPort`, Simulator-Endpunkte | **ERP/Simulator** für ERP-Sicht |
| Materialstamm (Pilot) | PostgreSQL `material_types` (+ Abgleich mit Simulator-Katalog) | `MaterialLookupPort` | **ERP** fachlich; DB = App-Spiegel |
| Gültigkeit ERP-Auftragsnummer | — | `ErpOrderLinkPort` (`SimulatorErpOrderLinkAdapter`) | **ERP/Simulator** |

---

## 7. Verweise im Code

- Repository: `adapters/persistence/order_repository.py`
- Verfügbarkeit Preview: `adapters/erp/app_aware_material_plan_availability_adapter.py`, `adapters/erp/material_plan_availability_sage_simulator_adapter.py`
- Stock-Snapshot: `adapters/persistence/database_stock_snapshot_adapter.py`
- Reine Domänenlogik Zählung: `domain/material_pipeline.py`
- Dependency Injection: `adapters/api/dependencies/use_cases.py`
