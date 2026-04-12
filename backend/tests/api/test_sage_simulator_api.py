from __future__ import annotations

from fastapi.testclient import TestClient

from adapters.api.app import app


def test_sage_simulator_material_search_and_material_detail() -> None:
    client = TestClient(app)

    search_response = client.get("/simulator/sage/materials/search", params={"q": "ALU"})
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert len(search_payload) >= 2
    assert any(item["material_no"] == "ALU-R20-2000" for item in search_payload)

    detail_response = client.get(
        "/simulator/sage/materials/get",
        params={"material_no": "ALU-R20-2000"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["description"] == "Aluminium Rundrohr 20x2"


def test_sage_simulator_stock_and_order_validation_payloads() -> None:
    client = TestClient(app)

    stock_response = client.get(
        "/simulator/sage/materials/stock",
        params={"material_no": "STA-FL50-5000"},
    )
    assert stock_response.status_code == 200
    assert stock_response.json()["stock_m"] > 0

    order_response = client.get(
        "/simulator/sage/orders/get",
        params={"order_no": "SAGE-ORD-2026-002"},
    )
    assert order_response.status_code == 200
    assert order_response.json()["order_no"] == "SAGE-ORD-2026-002"


def test_sage_simulator_transfer_send_returns_reference() -> None:
    client = TestClient(app)

    response = client.post(
        "/simulator/sage/transfers/7/send",
        json={
            "order_ref": "SAGE-ORD-2026-002",
            "material_ref": "STA-FL50-5000",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["transfer_ref"] == "SIM-TR-00007"
    assert payload["status"] == "accepted"
