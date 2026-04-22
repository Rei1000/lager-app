# Datenbankmodell – Leitlinien (Template)

Dieses Dokument beschreibt **generische** Regeln für den Umgang mit persistierten Daten. Es enthält **keine** konkreten Tabellen, Spalten oder Beispieldaten.

---

## 1. Entities und Value Objects

- **Entity:** Objekt mit identitätsstiftendem Merkmal (technisch oft Primärschlüssel); Lebenszyklus über die Zeit hinweg nachverfolgbar.
- **Value Object:** Unveränderlicher Wert ohne eigene Identität außerhalb des Aggregats; Gleichheit über Wert, nicht über technische IDs.
- **Aggregat:** Konsistenzgrenze; Änderungen erfolgen über eine klar definierte Wurzel (*Aggregate Root*).

---

## 2. Beziehungen

- Beziehungen sollen der **fachlichen** Modellierung folgen, nicht der reinen UI-Bequemlichkeit.
- **Kardinalitäten** explizit dokumentieren (1:1, 1:n, n:m) und benennen.
- **Referenzielle Integrität:** Wo im System welche Garantien gelten (DB-Constraints vs. Anwendungslogik) projektspezifisch festlegen.

---

## 3. Namensregeln

- Einheitliche Konvention für **Tabellen** und **Spalten** (z. B. `snake_case` in der DB, konsistente Präfixe für technische Spalten).
- Fachbegriffe aus der Ubiquitous Language bevorzugen; Abkürzungen nur, wenn sie dokumentiert sind.
- **Migrationen** benennen: beschreibend, zeitlich oder fortlaufend – Teamkonvention festlegen.

---

## 4. Migrationen

- Schemaänderungen erfolgen **versioniert** und nachvollziehbar (z. B. Migrationswerkzeug des Stacks).
- **Keine** stillen Änderungen auf Produktionssystemen ohne Freigabeprozess.
- Rollback-Strategie für riskante Änderungen definieren (projektspezifisch).

---

## 5. Trennung Domain vs. ORM / Persistenz

- Das **Domänenmodell** beschreibt Regeln und Invarianten; es ist nicht identisch mit der Tabellenstruktur.
- **Persistenzmodelle** (ORM-Entities, Row-DTOs) sind Adapter-Sichten: Mapping zwischen Speicher und Domain explizit halten.
- Vermeiden, dass ORM-Annotationen oder DB-Details die **Fachschicht** durchziehen.

---

## 6. Qualität und Konsistenz

- Transaktionsgrenzen klar definieren (wo beginnt/endet eine konsistente Änderung?).
- Indizes und Performance: nach Zugriffsmustern aus Use Cases ableiten, nicht raten.
- Testdaten: getrennt von Produktion; keine echten personenbezogenen Daten in Repositories.

---

## 7. Nächster Schritt im Projekt

Sobald die Domäne steht:

- konkretes **logisches** Datenmodell ableiten,
- physisches Schema dokumentieren,
- Migrationen und Zugriffspfade mit der Architektur abstimmen.
