from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import adapters.api.app as app_module


class _DummyConnection:
    def __enter__(self) -> "_DummyConnection":
        return self

    def __exit__(self, _exc_type: object, _exc: object, _tb: object) -> None:
        return None

    def execute(self, _query: object) -> None:
        return None


class _DummyEngine:
    def connect(self) -> _DummyConnection:
        return _DummyConnection()


def test_system_status_reports_ok(monkeypatch) -> None:
    monkeypatch.setattr(app_module, "get_engine", lambda: _DummyEngine())
    monkeypatch.setattr(Path, "exists", lambda _self: True)

    class _ConfiguredRepo:
        def get_profile(self, _name: str) -> object:
            return {"name": "default"}

    monkeypatch.setattr(app_module, "SqlAlchemyErpConfigurationRepository", lambda: _ConfiguredRepo())

    client = TestClient(app_module.app)
    response = client.get("/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["checks"]["database"] == "ok"
    assert payload["checks"]["storage"] == "ok"
    assert payload["checks"]["erp_profile"] == "configured"


def test_system_status_reports_degraded(monkeypatch) -> None:
    class _FailingEngine:
        def connect(self) -> _DummyConnection:
            raise RuntimeError("db down")

    monkeypatch.setattr(app_module, "get_engine", lambda: _FailingEngine())
    monkeypatch.setattr(Path, "exists", lambda _self: False)

    class _MissingRepo:
        def get_profile(self, _name: str) -> object:
            raise ValueError("missing profile")

    monkeypatch.setattr(app_module, "SqlAlchemyErpConfigurationRepository", lambda: _MissingRepo())

    client = TestClient(app_module.app)
    response = client.get("/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["checks"]["database"] == "error"
    assert payload["checks"]["storage"] == "missing"
    assert payload["checks"]["erp_profile"] == "not_configured"
