"""Dynamic base ERP client using configuration tables."""

from __future__ import annotations

from typing import Any

from adapters.erp.http_client import HttpClientPort
from ports.erp_configuration_port import ErpConfigurationPort


class DynamicErpBaseClient:
    def __init__(
        self,
        *,
        profile_name: str,
        configuration_port: ErpConfigurationPort,
        http_client: HttpClientPort,
    ) -> None:
        self._profile_name = profile_name
        self._configuration_port = configuration_port
        self._http_client = http_client

    def execute(
        self,
        *,
        function_key: str,
        path_params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Any:
        profile = self._configuration_port.get_profile(self._profile_name)
        endpoint = self._configuration_port.get_endpoint(profile.profile_id, function_key)
        url = self._build_url(profile.base_url, endpoint.path_template, path_params)

        return self._http_client.request(
            method=endpoint.http_method,
            url=url,
            query=query,
            body=body,
        )

    @staticmethod
    def _build_url(base_url: str, path_template: str, path_params: dict[str, str] | None) -> str:
        path = path_template
        if path_params:
            path = path_template.format(**path_params)
        return f"{base_url.rstrip('/')}/{path.lstrip('/')}"
