"""SQLAlchemy configuration repository for dynamic ERP adapter."""

from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from adapters.persistence.db import get_session
from adapters.persistence.models.erp import (
    ErpFieldMappingModel,
    ErpFunctionEndpointModel,
    ErpProfileModel,
)
from application.errors import NotFoundError
from ports.erp_configuration_port import (
    ErpConfigurationPort,
    ErpEndpointConfig,
    ErpFieldMappingConfig,
    ErpProfileConfig,
)


class SqlAlchemyErpConfigurationRepository(ErpConfigurationPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def get_profile(self, profile_name: str) -> ErpProfileConfig:
        with self._session_factory() as session:
            profile = (
                session.query(ErpProfileModel)
                .filter(ErpProfileModel.name == profile_name)
                .one_or_none()
            )
            if profile is None:
                raise NotFoundError(f"ERP-Profil nicht gefunden: {profile_name}")
            if not profile.base_url:
                raise ValueError(f"ERP-Profil ohne base_url: {profile_name}")
            return ErpProfileConfig(
                profile_id=str(profile.id),
                name=profile.name,
                base_url=profile.base_url,
            )

    def get_endpoint(self, profile_id: str, function_key: str) -> ErpEndpointConfig:
        with self._session_factory() as session:
            endpoint = (
                session.query(ErpFunctionEndpointModel)
                .filter(
                    ErpFunctionEndpointModel.erp_profile_id == int(profile_id),
                    ErpFunctionEndpointModel.functional_key == function_key,
                )
                .one_or_none()
            )
            if endpoint is None:
                raise NotFoundError(f"ERP-Endpoint nicht gefunden: {function_key}")
            return ErpEndpointConfig(
                endpoint_id=str(endpoint.id),
                profile_id=str(endpoint.erp_profile_id),
                function_key=endpoint.functional_key,
                http_method=endpoint.http_method,
                path_template=endpoint.path_template,
            )

    def list_field_mappings(
        self,
        endpoint_id: str,
        direction: str,
    ) -> list[ErpFieldMappingConfig]:
        with self._session_factory() as session:
            mappings = (
                session.query(ErpFieldMappingModel)
                .filter(
                    ErpFieldMappingModel.endpoint_id == int(endpoint_id),
                    ErpFieldMappingModel.direction == direction,
                )
                .all()
            )
            return [
                ErpFieldMappingConfig(
                    endpoint_id=str(mapping.endpoint_id),
                    app_field=mapping.app_field,
                    erp_field=mapping.erp_field,
                    direction=mapping.direction,
                )
                for mapping in mappings
            ]
