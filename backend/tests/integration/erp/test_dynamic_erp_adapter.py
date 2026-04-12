from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from adapters.erp.base_client import DynamicErpBaseClient
from adapters.erp.gateway import DynamicErpGatewayAdapter
from adapters.erp.http_client import HttpClientPort
from adapters.erp.mapper import apply_mappings, apply_reverse_mappings
from ports.erp_configuration_port import (
    ErpConfigurationPort,
    ErpEndpointConfig,
    ErpFieldMappingConfig,
    ErpProfileConfig,
)


@dataclass
class FakeConfigurationPort(ErpConfigurationPort):
    profile: ErpProfileConfig
    endpoints: dict[str, ErpEndpointConfig]
    mappings: dict[tuple[str, str], list[ErpFieldMappingConfig]] = field(default_factory=dict)

    def get_profile(self, profile_name: str) -> ErpProfileConfig:
        if profile_name != self.profile.name:
            raise ValueError(f"Profil nicht gefunden: {profile_name}")
        return self.profile

    def get_endpoint(self, profile_id: str, function_key: str) -> ErpEndpointConfig:
        endpoint = self.endpoints.get(function_key)
        if endpoint is None or endpoint.profile_id != profile_id:
            raise ValueError(f"Endpoint nicht gefunden: {function_key}")
        return endpoint

    def list_field_mappings(self, endpoint_id: str, direction: str) -> list[ErpFieldMappingConfig]:
        return self.mappings.get((endpoint_id, direction), [])


@dataclass
class FakeHttpClient(HttpClientPort):
    payload_by_url: dict[str, Any]
    calls: list[dict[str, Any]] = field(default_factory=list)

    def request(
        self,
        *,
        method: str,
        url: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "query": query,
                "body": body,
                "headers": headers,
            }
        )
        return self.payload_by_url[url]


def _build_adapter() -> tuple[DynamicErpGatewayAdapter, FakeHttpClient]:
    profile = ErpProfileConfig(profile_id="p1", name="default", base_url="https://erp.example")
    endpoints = {
        "material.search": ErpEndpointConfig(
            endpoint_id="e-search",
            profile_id="p1",
            function_key="material.search",
            http_method="GET",
            path_template="/materials/search",
        ),
        "material.get": ErpEndpointConfig(
            endpoint_id="e-material",
            profile_id="p1",
            function_key="material.get",
            http_method="GET",
            path_template="/materials/get",
        ),
        "material.stock.get": ErpEndpointConfig(
            endpoint_id="e-stock",
            profile_id="p1",
            function_key="material.stock.get",
            http_method="GET",
            path_template="/materials/stock",
        ),
        "erp_orders.list_by_material": ErpEndpointConfig(
            endpoint_id="e-orders",
            profile_id="p1",
            function_key="erp_orders.list_by_material",
            http_method="GET",
            path_template="/orders/by-material",
        ),
        "erp_order.get": ErpEndpointConfig(
            endpoint_id="e-order-get",
            profile_id="p1",
            function_key="erp_order.get",
            http_method="GET",
            path_template="/orders/get",
        ),
        "erp_transfer.send": ErpEndpointConfig(
            endpoint_id="e-transfer-send",
            profile_id="p1",
            function_key="erp_transfer.send",
            http_method="POST",
            path_template="/transfers/{transfer_id}/send",
        ),
    }
    mappings = {
        ("e-search", "app_to_erp"): [
            ErpFieldMappingConfig(
                endpoint_id="e-search",
                app_field="query",
                erp_field="q",
                direction="app_to_erp",
            )
        ],
        ("e-search", "erp_to_app"): [
            ErpFieldMappingConfig(
                endpoint_id="e-search",
                app_field="material_id",
                erp_field="id",
                direction="erp_to_app",
            )
        ],
        ("e-transfer-send", "app_to_erp"): [
            ErpFieldMappingConfig(
                endpoint_id="e-transfer-send",
                app_field="order_id",
                erp_field="order_ref",
                direction="app_to_erp",
            ),
            ErpFieldMappingConfig(
                endpoint_id="e-transfer-send",
                app_field="material_article_number",
                erp_field="material_ref",
                direction="app_to_erp",
            ),
        ],
        ("e-transfer-send", "erp_to_app"): [
            ErpFieldMappingConfig(
                endpoint_id="e-transfer-send",
                app_field="erp_transfer_reference",
                erp_field="transfer_ref",
                direction="erp_to_app",
            )
        ],
    }
    config = FakeConfigurationPort(profile=profile, endpoints=endpoints, mappings=mappings)
    http = FakeHttpClient(
        payload_by_url={
            "https://erp.example/materials/search": [{"id": "M-1", "name": "Steel A"}],
            "https://erp.example/materials/get": {"id": "M-1", "name": "Steel A"},
            "https://erp.example/materials/stock": {"id": "M-1", "stock_m": 120.0},
            "https://erp.example/orders/by-material": [{"order_ref": "ERP-42"}],
            "https://erp.example/orders/get": {"order_ref": "ERP-42"},
            "https://erp.example/transfers/7/send": {"transfer_ref": "TR-7", "state": "accepted"},
        }
    )
    base_client = DynamicErpBaseClient(
        profile_name="default",
        configuration_port=config,
        http_client=http,
    )
    adapter = DynamicErpGatewayAdapter(
        profile_name="default",
        configuration_port=config,
        base_client=base_client,
    )
    return adapter, http


def test_dynamic_endpoint_call_and_query_mapping() -> None:
    adapter, http = _build_adapter()

    payload = adapter.search_materials({"query": "steel"})

    assert payload == [{"material_id": "M-1", "name": "Steel A"}]
    assert http.calls[0]["url"] == "https://erp.example/materials/search"
    assert http.calls[0]["query"] == {"q": "steel"}


def test_order_reference_validation_uses_dynamic_endpoint() -> None:
    adapter, http = _build_adapter()

    valid = adapter.validate_order_reference("ERP-42")

    assert valid is True
    assert any(call["url"] == "https://erp.example/orders/get" for call in http.calls)


def test_missing_endpoint_configuration_raises_value_error() -> None:
    profile = ErpProfileConfig(profile_id="p1", name="default", base_url="https://erp.example")
    config = FakeConfigurationPort(profile=profile, endpoints={})
    http = FakeHttpClient(payload_by_url={})
    base_client = DynamicErpBaseClient(
        profile_name="default",
        configuration_port=config,
        http_client=http,
    )
    adapter = DynamicErpGatewayAdapter(
        profile_name="default",
        configuration_port=config,
        base_client=base_client,
    )

    with pytest.raises(ValueError):
        adapter.search_materials({"query": "steel"})


def test_transfer_send_uses_configured_write_endpoint_and_mapping() -> None:
    adapter, http = _build_adapter()

    response = adapter.send_transfer(
        transfer_payload={
            "order_id": "ORD-7",
            "material_article_number": "ART-7",
            "payload": {"amount_mm": 900},
        },
        context={"transfer_id": 7},
    )

    assert response == {"erp_transfer_reference": "TR-7", "state": "accepted"}
    assert http.calls[-1]["method"] == "POST"
    assert http.calls[-1]["url"] == "https://erp.example/transfers/7/send"
    assert http.calls[-1]["body"] == {
        "order_ref": "ORD-7",
        "material_ref": "ART-7",
        "payload": {"amount_mm": 900},
    }


def test_transfer_send_rejects_unexpected_erp_response_shape() -> None:
    adapter, http = _build_adapter()
    http.payload_by_url["https://erp.example/transfers/7/send"] = ["unexpected"]

    with pytest.raises(ValueError):
        adapter.send_transfer(
            transfer_payload={"order_id": "ORD-7"},
            context={"transfer_id": 7},
        )


def test_mapping_helpers_apply_forward_and_reverse_mapping() -> None:
    mappings = [
        ErpFieldMappingConfig(
            endpoint_id="e1",
            app_field="order_reference",
            erp_field="order_ref",
            direction="app_to_erp",
        )
    ]
    forward = apply_mappings({"order_reference": "ERP-42"}, mappings)
    reverse = apply_reverse_mappings({"order_ref": "ERP-42"}, mappings)

    assert forward["order_ref"] == "ERP-42"
    assert reverse["order_reference"] == "ERP-42"
