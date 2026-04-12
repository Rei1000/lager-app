"""SQLAlchemy adapter for admin configuration port."""

from __future__ import annotations

from decimal import Decimal
from typing import Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from adapters.auth.password_hasher import Pbkdf2PasswordHasher
from adapters.persistence.db import get_session
from adapters.persistence.models.access import UserModel
from adapters.persistence.models.erp import (
    ErpFieldMappingModel,
    ErpFunctionEndpointModel,
    ErpProfileModel,
)
from ports.password_hasher_port import PasswordHasherPort
from adapters.persistence.models.material import CuttingMachineModel
from application.errors import NotFoundError
from ports.admin_configuration_port import (
    AdminConfigurationPort,
    CuttingMachineRecord,
    ErpEndpointRecord,
    ErpFieldMappingRecord,
    ErpProfileRecord,
    UserRecord,
)


class SqlAlchemyAdminConfigurationRepository(AdminConfigurationPort):
    def __init__(
        self,
        session_factory: Callable[[], Session] = get_session,
        password_hasher: PasswordHasherPort | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._password_hasher = password_hasher or Pbkdf2PasswordHasher()

    def list_erp_profiles(self) -> list[ErpProfileRecord]:
        with self._session_factory() as session:
            profiles = session.query(ErpProfileModel).order_by(ErpProfileModel.id.asc()).all()
            return [self._to_erp_profile_record(profile) for profile in profiles]

    def get_erp_profile(self, profile_id: int) -> ErpProfileRecord:
        with self._session_factory() as session:
            profile = session.get(ErpProfileModel, profile_id)
            if profile is None:
                raise NotFoundError(f"ERP-Profil nicht gefunden: {profile_id}")
            return self._to_erp_profile_record(profile)

    def create_erp_profile(
        self,
        *,
        name: str,
        erp_type: str | None,
        connection_type: str | None,
        base_url: str | None,
        tenant_code: str | None,
    ) -> ErpProfileRecord:
        with self._session_factory() as session:
            model = ErpProfileModel(
                name=name,
                erp_type=erp_type,
                connection_type=connection_type,
                base_url=base_url,
                tenant_code=tenant_code,
            )
            session.add(model)
            self._commit_or_raise(session, "ERP-Profil konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_erp_profile_record(model)

    def update_erp_profile(
        self,
        *,
        profile_id: int,
        name: str,
        erp_type: str | None,
        connection_type: str | None,
        base_url: str | None,
        tenant_code: str | None,
    ) -> ErpProfileRecord:
        with self._session_factory() as session:
            model = session.get(ErpProfileModel, profile_id)
            if model is None:
                raise NotFoundError(f"ERP-Profil nicht gefunden: {profile_id}")
            model.name = name
            model.erp_type = erp_type
            model.connection_type = connection_type
            model.base_url = base_url
            model.tenant_code = tenant_code
            self._commit_or_raise(session, "ERP-Profil konnte nicht aktualisiert werden")
            session.refresh(model)
            return self._to_erp_profile_record(model)

    def list_endpoints(self) -> list[ErpEndpointRecord]:
        with self._session_factory() as session:
            endpoints = (
                session.query(ErpFunctionEndpointModel)
                .order_by(ErpFunctionEndpointModel.id.asc())
                .all()
            )
            return [self._to_endpoint_record(endpoint) for endpoint in endpoints]

    def create_endpoint(
        self,
        *,
        erp_profile_id: int,
        functional_key: str,
        http_method: str,
        path_template: str,
    ) -> ErpEndpointRecord:
        with self._session_factory() as session:
            model = ErpFunctionEndpointModel(
                erp_profile_id=erp_profile_id,
                functional_key=functional_key,
                http_method=http_method,
                path_template=path_template,
            )
            session.add(model)
            self._commit_or_raise(session, "Endpoint konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_endpoint_record(model)

    def list_mappings(self) -> list[ErpFieldMappingRecord]:
        with self._session_factory() as session:
            mappings = session.query(ErpFieldMappingModel).order_by(ErpFieldMappingModel.id.asc()).all()
            return [self._to_mapping_record(mapping) for mapping in mappings]

    def create_mapping(
        self,
        *,
        endpoint_id: int,
        app_field: str,
        erp_field: str,
        direction: str,
    ) -> ErpFieldMappingRecord:
        with self._session_factory() as session:
            model = ErpFieldMappingModel(
                endpoint_id=endpoint_id,
                app_field=app_field,
                erp_field=erp_field,
                direction=direction,
            )
            session.add(model)
            self._commit_or_raise(session, "Feldmapping konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_mapping_record(model)

    def list_cutting_machines(self) -> list[CuttingMachineRecord]:
        with self._session_factory() as session:
            machines = session.query(CuttingMachineModel).order_by(CuttingMachineModel.id.asc()).all()
            return [self._to_cutting_machine_record(machine) for machine in machines]

    def create_cutting_machine(
        self,
        *,
        machine_code: str | None,
        name: str,
        kerf_mm: float | None,
        is_active: bool,
    ) -> CuttingMachineRecord:
        with self._session_factory() as session:
            model = CuttingMachineModel(
                machine_code=machine_code,
                name=name,
                kerf_mm=Decimal(str(kerf_mm)) if kerf_mm is not None else None,
                is_active=is_active,
            )
            session.add(model)
            self._commit_or_raise(session, "Saege konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_cutting_machine_record(model)

    def list_users(self) -> list[UserRecord]:
        with self._session_factory() as session:
            users = session.query(UserModel).order_by(UserModel.id.asc()).all()
            return [self._to_user_record(user) for user in users]

    def create_user(
        self,
        *,
        username: str,
        password: str,
        role_id: int,
        display_name: str | None,
        email: str | None,
        is_active: bool,
        erp_user_reference: str | None,
    ) -> UserRecord:
        with self._session_factory() as session:
            model = UserModel(
                username=username,
                password_hash=self._password_hasher.hash_password(password),
                role_id=role_id,
                display_name=display_name,
                email=email,
                is_active=is_active,
                erp_user_reference=erp_user_reference,
            )
            session.add(model)
            self._commit_or_raise(session, "Benutzer konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_user_record(model)

    @staticmethod
    def _commit_or_raise(session: Session, message: str) -> None:
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValueError(message) from exc

    @staticmethod
    def _to_erp_profile_record(model: ErpProfileModel) -> ErpProfileRecord:
        return ErpProfileRecord(
            id=model.id,
            name=model.name,
            erp_type=model.erp_type,
            connection_type=model.connection_type,
            base_url=model.base_url,
            tenant_code=model.tenant_code,
        )

    @staticmethod
    def _to_endpoint_record(model: ErpFunctionEndpointModel) -> ErpEndpointRecord:
        return ErpEndpointRecord(
            id=model.id,
            erp_profile_id=model.erp_profile_id,
            functional_key=model.functional_key,
            http_method=model.http_method,
            path_template=model.path_template,
        )

    @staticmethod
    def _to_mapping_record(model: ErpFieldMappingModel) -> ErpFieldMappingRecord:
        return ErpFieldMappingRecord(
            id=model.id,
            endpoint_id=model.endpoint_id,
            app_field=model.app_field,
            erp_field=model.erp_field,
            direction=model.direction,
        )

    @staticmethod
    def _to_cutting_machine_record(model: CuttingMachineModel) -> CuttingMachineRecord:
        kerf_mm = float(model.kerf_mm) if model.kerf_mm is not None else None
        return CuttingMachineRecord(
            id=model.id,
            machine_code=model.machine_code,
            name=model.name,
            kerf_mm=kerf_mm,
            is_active=model.is_active,
        )

    @staticmethod
    def _to_user_record(model: UserModel) -> UserRecord:
        return UserRecord(
            id=model.id,
            username=model.username,
            display_name=model.display_name,
            email=model.email,
            role_id=model.role_id,
            is_active=model.is_active,
            erp_user_reference=model.erp_user_reference,
        )
