"""Configurable ERP adapter implementing ERP ports."""

from __future__ import annotations

from typing import Any

from adapters.erp.base_client import DynamicErpBaseClient
from adapters.erp.mapper import apply_mappings, apply_reverse_mappings
from ports.erp_configuration_port import ErpConfigurationPort
from ports.erp_material_port import ErpMaterialPort
from ports.erp_order_link_port import ErpOrderLinkPort
from ports.erp_order_port import ErpOrderPort
from ports.erp_write_port import ErpWritePort

APP_TO_ERP = "app_to_erp"
ERP_TO_APP = "erp_to_app"


class DynamicErpGatewayAdapter(ErpMaterialPort, ErpOrderPort, ErpOrderLinkPort, ErpWritePort):
    def __init__(
        self,
        *,
        profile_name: str,
        configuration_port: ErpConfigurationPort,
        base_client: DynamicErpBaseClient,
    ) -> None:
        self._profile_name = profile_name
        self._configuration_port = configuration_port
        self._base_client = base_client

    def search_materials(self, criteria: dict[str, Any]) -> list[dict[str, Any]]:
        return self._execute_list_function("material.search", query=criteria)

    def get_material(self, material_reference: str) -> dict[str, Any]:
        return self._execute_one_function(
            "material.get",
            query={"material_reference": material_reference},
        )

    def get_material_stock(self, material_reference: str) -> dict[str, Any]:
        return self._execute_one_function(
            "material.stock.get",
            query={"material_reference": material_reference},
        )

    def list_orders_by_material(self, material_reference: str) -> list[dict[str, Any]]:
        return self._execute_list_function(
            "erp_orders.list_by_material",
            query={"material_reference": material_reference},
        )

    def validate_order_reference(self, order_reference: str) -> bool:
        payload = self._execute_one_function(
            "erp_order.get",
            query={"order_reference": order_reference},
        )
        return bool(payload)

    def exists_order_reference(self, erp_order_number: str) -> bool:
        return self.validate_order_reference(erp_order_number)

    def send_transfer(
        self,
        *,
        transfer_payload: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        payload = self._execute_with_mapping(
            function_key="erp_transfer.send",
            body=transfer_payload,
            context=context,
        )
        if isinstance(payload, dict):
            return payload
        if payload is None:
            return None
        raise ValueError("ERP-Antwort ungueltig")

    def _execute_list_function(
        self,
        function_key: str,
        *,
        query: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        payload = self._execute_with_mapping(function_key=function_key, query=query)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            if "items" in payload and isinstance(payload["items"], list):
                return [item for item in payload["items"] if isinstance(item, dict)]
            return [payload]
        return []

    def _execute_one_function(
        self,
        function_key: str,
        *,
        query: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = self._execute_with_mapping(function_key=function_key, query=query)
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, list) and payload and isinstance(payload[0], dict):
            return payload[0]
        return {}

    def _execute_with_mapping(
        self,
        *,
        function_key: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Any:
        profile = self._configuration_port.get_profile(self._profile_name)
        endpoint = self._configuration_port.get_endpoint(profile.profile_id, function_key)

        outgoing_mappings = self._configuration_port.list_field_mappings(endpoint.endpoint_id, APP_TO_ERP)
        outgoing_query = apply_mappings(query or {}, outgoing_mappings) if query else None
        outgoing_body = apply_mappings(body or {}, outgoing_mappings) if body else None

        raw = self._base_client.execute(
            function_key=function_key,
            query=outgoing_query,
            body=outgoing_body,
            path_params={k: str(v) for k, v in (context or {}).items()},
        )

        incoming_mappings = self._configuration_port.list_field_mappings(endpoint.endpoint_id, ERP_TO_APP)
        if not incoming_mappings:
            return raw
        if isinstance(raw, list):
            return [apply_reverse_mappings(item, incoming_mappings) for item in raw if isinstance(item, dict)]
        if isinstance(raw, dict):
            return apply_reverse_mappings(raw, incoming_mappings)
        return raw
