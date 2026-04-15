from __future__ import annotations

from fastapi.testclient import TestClient

from adapters.api.app import app


def test_sage_simulator_material_search_and_material_detail() -> None:
    client = TestClient(app)

    search_response = client.get("/simulator/sage/materials/search", params={"q": "100-FE"})
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert len(search_payload) >= 2
    assert any(item["material_no"] == "100-FE-010" for item in search_payload)
    assert all(item["material_group_code"] == "100" for item in search_payload)

    detail_response = client.get(
        "/simulator/sage/materials/get",
        params={"material_no": "420-VA-012"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["description"] == "Rechteckprofil Edelstahl 12 mm"
    assert detail_response.json()["material_group_code"] == "420"
    assert detail_response.json()["material_code"] == "VA"
    assert detail_response.json()["dimension_mm"] == 12


def test_sage_simulator_stock_and_order_validation_payloads() -> None:
    client = TestClient(app)

    stock_response = client.get(
        "/simulator/sage/materials/stock",
        params={"material_no": "430-FE-025"},
    )
    assert stock_response.status_code == 200
    assert stock_response.json()["stock_m"] > 0
    assert stock_response.json()["description"] == "Winkelprofil Stahl 25 mm"

    order_response = client.get(
        "/simulator/sage/orders/get",
        params={"order_no": "SAGE-ORD-2026-002"},
    )
    assert order_response.status_code == 200
    assert order_response.json()["order_no"] == "SAGE-ORD-2026-002"
    assert order_response.json()["material_no"] == "420-VA-012"


def test_sage_simulator_open_orders_and_availability_payloads() -> None:
    client = TestClient(app)

    open_orders_response = client.get("/simulator/sage/orders/open")
    assert open_orders_response.status_code == 200
    open_orders = open_orders_response.json()
    assert len(open_orders) == 5
    assert all(item["required_m"] > 0 for item in open_orders)

    by_material_response = client.get(
        "/simulator/sage/orders/by-material",
        params={"material_no": "420-VA-012"},
    )
    assert by_material_response.status_code == 200
    assert len(by_material_response.json()) == 2

    availability_response = client.get(
        "/simulator/sage/materials/availability",
        params={"material_no": "420-VA-012"},
    )
    assert availability_response.status_code == 200
    payload = availability_response.json()
    assert payload["stock_m"] == 93.0
    assert payload["in_pipeline_m"] == 37.2
    assert payload["available_m"] == 55.8


def test_sage_simulator_transfer_send_returns_reference() -> None:
    client = TestClient(app)

    response = client.post(
        "/simulator/sage/transfers/7/send",
        json={
            "order_ref": "SAGE-ORD-2026-002",
            "material_ref": "300-AL-010",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["transfer_ref"] == "SIM-TR-00007"
    assert payload["status"] == "accepted"
