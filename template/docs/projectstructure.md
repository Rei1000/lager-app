# Projektstruktur (Template)

Dieses Dokument beschreibt eine **generische** Verzeichnis- und Modulstruktur. Konkrete Fachpakete oder branchenspezifische Ordner sind **nicht** vorgegeben.

---

## 1. Leitidee

- **Domain und Anwendungslogik** liegen im Backend, klar nach Schichten getrennt.
- **Darstellung und Interaktion** liegen im Frontend, ohne Business-Regeln zu duplizieren.
- **Konfiguration und Infrastruktur** sind vom Kern getrennt.

---

## 2. Backend (Beispielstruktur)

```
backend/
  domain/          # Fachmodell, Regeln, Value Objects, Entities (ohne Framework)
  application/   # Use Cases, Orchestrierung, Ports nutzend
  ports/         # Schnittstellen / Contracts nach außen (Persistenz, Messaging, …)
  adapters/      # Technische Implementierungen der Ports (DB, HTTP-Clients, …)
  config/        # Umgebung, Einstellungen, Zusammenstellung der Abhängigkeiten
```

| Ordner | Rolle |
|--------|--------|
| `domain/` | Reine Fachlogik; keine Datenbank-, HTTP- oder Framework-Details. |
| `application/` | Abläufe und Anwendungsfälle; koordiniert Domain und Ports. |
| `ports/` | Abstraktionen für alles Technische; richten den Fluss nach außen. |
| `adapters/` | Konkrete Technik (ORM, REST, Dateien, Queues, …). |
| `config/` | Verdrahtung, Umgebungsprofile, Start der Anwendung. |

---

## 3. Frontend (Beispielstruktur)

```
frontend/
  app/           # Routing, Seiten, Layout (frameworkspezifisch anpassen)
  features/      # Feature-orientierte Module (UI + lokaler State)
  components/    # Wiederverwendbare UI-Bausteine
  lib/           # Hilfen: API-Client, Formatierung, reine Utilities ohne Fachlogik
```

| Ordner | Rolle |
|--------|--------|
| `app/` | Einstieg, Navigation, ggf. Meta-Layout; möglichst dünn halten. |
| `features/` | Ein Feature pro Bereich; kapselt Screens und zugehörige UI-Logik. |
| `components/` | Wiederverwendbare, fachlich neutrale Bausteine. |
| `lib/` | Technische Hilfen; **keine** Domänenregeln duplizieren. |

---

## 4. Weitere übliche Bereiche (optional, projektspezifisch)

- `infra/` – Container, Deployment, IaC (falls genutzt)
- `scripts/` – Wartungs- und Entwicklungsskripte
- `docs/` – zentrale Dokumentation (dieses Repository)

Pfade und Namen können an den gewählten Stack angepasst werden; die **Trennung der Verantwortlichkeiten** soll erhalten bleiben.
