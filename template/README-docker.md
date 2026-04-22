# Docker Setup (Template)

Dieses Template enthält eine generische Docker-Basis für lokale Entwicklung.

## Ziel

- reproduzierbare Entwicklungsumgebung
- konsistenter lokaler Start
- Basis für spätere projektspezifische Container-Anpassung

## Enthalten

- `docker-compose.yml`
- `infra/docker/backend.Dockerfile`
- PostgreSQL als lokaler Standard-Datenbankdienst
- generischer Backend-Container

## Hinweise

- Die Docker-Dateien sind bewusst generisch
- Sie müssen für das konkrete Projekt angepasst werden
- Es wird keine projektspezifische Fachlogik oder App-Startlogik vorausgesetzt

## Start

```bash
docker compose up --build
```
