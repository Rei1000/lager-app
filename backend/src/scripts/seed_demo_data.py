"""Seed idempotent demo data for pilot/test startup."""

from __future__ import annotations

import os
from decimal import Decimal

from adapters.auth.password_hasher import Pbkdf2PasswordHasher
from adapters.persistence.db import get_session
from adapters.persistence.models.access import RoleModel, UserModel
from adapters.persistence.models.erp import ErpFieldMappingModel, ErpFunctionEndpointModel, ErpProfileModel
from adapters.persistence.models.material import MaterialTypeModel
from adapters.persistence.models.orders import AppOrderModel
from adapters.erp.sage_simulator_data import (
    SIMULATOR_MATERIALS,
    SIMULATOR_OPEN_ORDERS,
    SIMULATOR_USERS,
)


def _get_or_create_role(*, code: str, name: str, description: str) -> RoleModel:
    with get_session() as session:
        existing = session.query(RoleModel).filter(RoleModel.code == code).one_or_none()
        if existing is not None:
            return existing
        role = RoleModel(code=code, name=name, description=description)
        session.add(role)
        session.commit()
        session.refresh(role)
        return role


def _get_or_create_user(
    *,
    username: str,
    plain_password: str,
    role_id: int,
    display_name: str,
    email: str,
    erp_user_reference: str | None = None,
) -> UserModel:
    hasher = Pbkdf2PasswordHasher()
    with get_session() as session:
        existing = session.query(UserModel).filter(UserModel.username == username).one_or_none()
        if existing is not None:
            if erp_user_reference and not existing.erp_user_reference:
                existing.erp_user_reference = erp_user_reference
                session.commit()
                session.refresh(existing)
            return existing
        user = UserModel(
            username=username,
            password_hash=hasher.hash_password(plain_password),
            role_id=role_id,
            display_name=display_name,
            email=email,
            is_active=True,
            erp_user_reference=erp_user_reference,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def _get_or_create_material(
    *,
    article_number: str,
    name: str,
    profile: str,
    erp_stock_m: Decimal,
    rest_stock_m: Decimal,
) -> MaterialTypeModel:
    with get_session() as session:
        existing = (
            session.query(MaterialTypeModel)
            .filter(MaterialTypeModel.article_number == article_number)
            .one_or_none()
        )
        if existing is not None:
            return existing
        material = MaterialTypeModel(
            article_number=article_number,
            name=name,
            profile=profile,
            unit="m",
            min_rest_length_mm=500,
            erp_stock_m=erp_stock_m,
            rest_stock_m=rest_stock_m,
            is_active=True,
        )
        session.add(material)
        session.commit()
        session.refresh(material)
        return material


def _get_or_create_order(
    *,
    material_type_id: int,
    created_by_user_id: int,
    quantity: int,
    part_length_mm: int,
    include_rest_stock: bool,
    status: str,
    priority_order: int,
    erp_order_number: str | None,
) -> AppOrderModel:
    with get_session() as session:
        existing = (
            session.query(AppOrderModel)
            .filter(
                AppOrderModel.material_type_id == material_type_id,
                AppOrderModel.priority_order == priority_order,
            )
            .one_or_none()
        )
        if existing is not None:
            return existing
        order = AppOrderModel(
            material_type_id=material_type_id,
            created_by_user_id=created_by_user_id,
            quantity=quantity,
            part_length_mm=part_length_mm,
            kerf_mm_snapshot=Decimal("3.0"),
            include_rest_stock=include_rest_stock,
            calculated_total_demand_m=Decimal(quantity * part_length_mm) / Decimal("1000"),
            demand_from_full_stock_m=Decimal(quantity * part_length_mm) / Decimal("1000"),
            demand_from_rest_stock_m=Decimal("0"),
            shortage_m=Decimal("0"),
            traffic_light="green",
            status=status,
            priority_order=priority_order,
            erp_order_number=erp_order_number,
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        return order


def _get_or_create_erp_profile() -> ErpProfileModel:
    simulator_base_url = os.getenv("SAGE_SIMULATOR_BASE_URL", "http://localhost:8000/simulator/sage")
    with get_session() as session:
        existing = session.query(ErpProfileModel).filter(ErpProfileModel.name == "default").one_or_none()
        if existing is not None:
            needs_update = False
            if existing.erp_type != "sage-simulator":
                existing.erp_type = "sage-simulator"
                needs_update = True
            if existing.connection_type != "rest":
                existing.connection_type = "rest"
                needs_update = True
            if existing.base_url != simulator_base_url:
                existing.base_url = simulator_base_url
                needs_update = True
            if needs_update:
                session.commit()
                session.refresh(existing)
            return existing
        profile = ErpProfileModel(
            name="default",
            erp_type="sage-simulator",
            connection_type="rest",
            base_url=simulator_base_url,
            tenant_code="demo",
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile


def _get_or_create_endpoint(
    *,
    erp_profile_id: int,
    functional_key: str,
    http_method: str,
    path_template: str,
) -> ErpFunctionEndpointModel:
    with get_session() as session:
        existing = (
            session.query(ErpFunctionEndpointModel)
            .filter(
                ErpFunctionEndpointModel.erp_profile_id == erp_profile_id,
                ErpFunctionEndpointModel.functional_key == functional_key,
            )
            .one_or_none()
        )
        if existing is not None:
            return existing
        endpoint = ErpFunctionEndpointModel(
            erp_profile_id=erp_profile_id,
            functional_key=functional_key,
            http_method=http_method,
            path_template=path_template,
        )
        session.add(endpoint)
        session.commit()
        session.refresh(endpoint)
        return endpoint


def _get_or_create_mapping(
    *,
    endpoint_id: int,
    app_field: str,
    erp_field: str,
    direction: str,
) -> ErpFieldMappingModel:
    with get_session() as session:
        existing = (
            session.query(ErpFieldMappingModel)
            .filter(
                ErpFieldMappingModel.endpoint_id == endpoint_id,
                ErpFieldMappingModel.app_field == app_field,
                ErpFieldMappingModel.erp_field == erp_field,
                ErpFieldMappingModel.direction == direction,
            )
            .one_or_none()
        )
        if existing is not None:
            return existing
        mapping = ErpFieldMappingModel(
            endpoint_id=endpoint_id,
            app_field=app_field,
            erp_field=erp_field,
            direction=direction,
        )
        session.add(mapping)
        session.commit()
        session.refresh(mapping)
        return mapping


def _seed_simulator_endpoints_and_mappings(profile: ErpProfileModel) -> None:
    endpoint_specs = [
        ("material.search", "GET", "/materials/search"),
        ("material.get", "GET", "/materials/get"),
        ("material.stock.get", "GET", "/materials/stock"),
        ("erp_orders.list_by_material", "GET", "/orders/by-material"),
        ("erp_order.get", "GET", "/orders/get"),
        ("erp_transfer.send", "POST", "/transfers/{transfer_id}/send"),
    ]
    endpoint_by_key: dict[str, ErpFunctionEndpointModel] = {}
    for function_key, method, path_template in endpoint_specs:
        endpoint_by_key[function_key] = _get_or_create_endpoint(
            erp_profile_id=profile.id,
            functional_key=function_key,
            http_method=method,
            path_template=path_template,
        )

    mapping_specs = [
        ("material.search", "query", "q", "app_to_erp"),
        ("material.search", "material_reference", "material_no", "erp_to_app"),
        ("material.search", "name", "description", "erp_to_app"),
        ("material.get", "material_reference", "material_no", "app_to_erp"),
        ("material.get", "material_reference", "material_no", "erp_to_app"),
        ("material.get", "name", "description", "erp_to_app"),
        ("material.stock.get", "material_reference", "material_no", "app_to_erp"),
        ("material.stock.get", "material_reference", "material_no", "erp_to_app"),
        ("erp_orders.list_by_material", "material_reference", "material_no", "app_to_erp"),
        ("erp_orders.list_by_material", "erp_order_number", "order_no", "erp_to_app"),
        ("erp_order.get", "order_reference", "order_no", "app_to_erp"),
        ("erp_order.get", "order_reference", "order_no", "erp_to_app"),
        ("erp_transfer.send", "order_id", "order_ref", "app_to_erp"),
        ("erp_transfer.send", "material_article_number", "material_ref", "app_to_erp"),
        ("erp_transfer.send", "erp_transfer_reference", "transfer_ref", "erp_to_app"),
    ]
    for function_key, app_field, erp_field, direction in mapping_specs:
        _get_or_create_mapping(
            endpoint_id=endpoint_by_key[function_key].id,
            app_field=app_field,
            erp_field=erp_field,
            direction=direction,
        )


def seed_demo_data() -> None:
    admin_role = _get_or_create_role(
        code="admin",
        name="Admin",
        description="Systemverwaltung",
    )
    leitung_role = _get_or_create_role(
        code="leitung",
        name="Leitung",
        description="Freigaben und Steuerung",
    )
    lager_role = _get_or_create_role(
        code="lager",
        name="Lager",
        description="Operative Lagerbearbeitung",
    )

    admin_user = _get_or_create_user(
        username="admin",
        plain_password="Admin123!",
        role_id=admin_role.id,
        display_name="Pilot Admin",
        email="admin@example.local",
    )
    _get_or_create_user(
        username="leitung1",
        plain_password="Leitung123!",
        role_id=leitung_role.id,
        display_name="Leitung Demo",
        email="leitung@example.local",
    )
    _get_or_create_user(
        username="lager1",
        plain_password="Lager123!",
        role_id=lager_role.id,
        display_name="Lager Demo",
        email="lager@example.local",
    )

    role_by_code = {
        "admin": admin_role,
        "leitung": leitung_role,
        "lager": lager_role,
    }
    simulator_users: dict[str, UserModel] = {}
    for user_seed in SIMULATOR_USERS:
        simulator_users[user_seed.username] = _get_or_create_user(
            username=user_seed.username,
            plain_password=user_seed.password,
            role_id=role_by_code[user_seed.role_code].id,
            display_name=user_seed.display_name,
            email=user_seed.email,
            erp_user_reference=user_seed.erp_user_reference,
        )

    material_id_by_article_number: dict[str, int] = {}
    for material_seed in SIMULATOR_MATERIALS:
        material = _get_or_create_material(
            article_number=material_seed.article_number,
            name=material_seed.name,
            profile=material_seed.profile,
            erp_stock_m=material_seed.stock_m,
            rest_stock_m=material_seed.rest_stock_m,
        )
        material_id_by_article_number[material_seed.article_number] = material.id

    for index, order_seed in enumerate(SIMULATOR_OPEN_ORDERS, start=1):
        _get_or_create_order(
            material_type_id=material_id_by_article_number[order_seed.material_reference],
            created_by_user_id=simulator_users["sage_leitung"].id,
            quantity=order_seed.quantity,
            part_length_mm=order_seed.part_length_mm,
            include_rest_stock=True,
            status="checked",
            priority_order=index,
            erp_order_number=order_seed.order_reference,
        )

    _get_or_create_order(
        material_type_id=material_id_by_article_number["ALU-Q30-3000"],
        created_by_user_id=admin_user.id,
        quantity=1,
        part_length_mm=1800,
        include_rest_stock=True,
        status="reserved",
        priority_order=len(SIMULATOR_OPEN_ORDERS) + 1,
        erp_order_number=None,
    )

    profile = _get_or_create_erp_profile()
    _seed_simulator_endpoints_and_mappings(profile)


if __name__ == "__main__":
    seed_demo_data()
    print("Demo-Seed abgeschlossen (idempotent).")
