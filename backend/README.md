# Backend Basis

Python/FastAPI-Projektbasis ohne implementierte Fachlogik.

## Schichten

- `src/domain/`: Fachlicher Kern (Entities, Value Objects, Domain Services).
- `src/application/`: Use-Case-Orchestrierung.
- `src/ports/`: Schnittstellen (Inbound/Outbound Ports).
- `src/adapters/`: Technische Adapter (API, Persistence, ERP, Auth).
- `src/config/`: Konfiguration und Bootstrap-Grundlagen.

## Tests

- `tests/unit/`: Isolierte Unit-Tests.
- `tests/application/`: Application-Service-Tests.
- `tests/integration/`: Integrationsnahe Tests.
- `tests/api/`: API-Vertragstests.
