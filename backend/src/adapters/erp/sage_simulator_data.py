"""Static, realistic test dataset for Sage simulator flows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class SimulatorUserSeed:
    username: str
    password: str
    role_code: str
    display_name: str
    email: str
    erp_user_reference: str


@dataclass(frozen=True)
class SimulatorMaterialSeed:
    article_number: str
    name: str
    category_code: str
    category_name: str
    material_code: str
    material_name: str
    dimension_code: str
    dimension_mm: int
    profile: str
    shape: str
    size_mm: str
    unit: str
    stock_m: Decimal
    rest_stock_m: Decimal


@dataclass(frozen=True)
class SimulatorOrderSeed:
    order_reference: str
    material_reference: str
    customer_name: str
    quantity: int
    part_length_mm: int
    due_date: str
    status: str
    priority: str


SIMULATOR_USERS: tuple[SimulatorUserSeed, ...] = (
    SimulatorUserSeed(
        username="sage_admin",
        password="SageAdmin123!",
        role_code="admin",
        display_name="Sage Simulator Admin",
        email="sage_admin@example.local",
        erp_user_reference="ERP-SAGE-USER-ADMIN-001",
    ),
    SimulatorUserSeed(
        username="sage_leitung",
        password="SageLeitung123!",
        role_code="leitung",
        display_name="Sage Simulator Leitung",
        email="sage_leitung@example.local",
        erp_user_reference="ERP-SAGE-USER-LEITUNG-001",
    ),
    SimulatorUserSeed(
        username="sage_lager",
        password="SageLager123!",
        role_code="lager",
        display_name="Sage Simulator Lager",
        email="sage_lager@example.local",
        erp_user_reference="ERP-SAGE-USER-LAGER-001",
    ),
)


CATEGORY_NAMES: dict[str, str] = {
    "100": "Stangenmaterial",
    "200": "Vollmaterial",
    "300": "Flachmaterial / Blech",
    "400": "Profilmaterial",
    "410": "Rundprofile",
    "420": "Rechteckprofile",
    "430": "Winkelprofile",
    "440": "Sonderprofile",
}

MATERIAL_NAMES: dict[str, str] = {
    "FE": "Stahl",
    "AL": "Aluminium",
    "CU": "Kupfer",
    "VA": "Edelstahl",
    "MS": "Messing",
}

DIMENSION_MM_BY_CODE: dict[str, int] = {
    "010": 10,
    "012": 12,
    "025": 25,
    "050": 50,
    "100": 100,
}

SHAPE_BY_CATEGORY: dict[str, str] = {
    "100": "rod",
    "200": "solid",
    "300": "flat",
    "400": "profile",
    "410": "round-profile",
    "420": "rectangular-profile",
    "430": "angle-profile",
    "440": "special-profile",
}

DESCRIPTION_PREFIX_BY_CATEGORY: dict[str, str] = {
    "410": "Rundprofil",
    "420": "Rechteckprofil",
    "430": "Winkelprofil",
    "440": "Sonderprofil",
}

ARTICLE_CATALOG: tuple[tuple[str, str, str], ...] = (
    ("100-FE-010", "185.0", "12.5"),
    ("100-FE-025", "142.0", "10.0"),
    ("100-AL-012", "168.5", "11.4"),
    ("100-AL-050", "97.0", "7.2"),
    ("100-CU-010", "88.0", "6.1"),
    ("100-VA-025", "73.5", "4.8"),
    ("100-MS-012", "64.0", "4.2"),
    ("200-FE-050", "120.0", "8.6"),
    ("200-FE-100", "82.0", "5.1"),
    ("200-AL-025", "111.5", "7.0"),
    ("200-VA-050", "69.0", "3.9"),
    ("200-CU-012", "54.5", "3.1"),
    ("200-MS-010", "49.0", "2.8"),
    ("300-FE-012", "133.0", "9.2"),
    ("300-AL-010", "118.0", "8.4"),
    ("300-VA-025", "77.5", "5.0"),
    ("300-CU-050", "46.0", "2.5"),
    ("300-MS-012", "59.0", "3.4"),
    ("400-FE-025", "101.0", "6.8"),
    ("400-AL-050", "84.0", "5.7"),
    ("400-VA-100", "38.5", "2.0"),
    ("400-CU-010", "57.5", "3.3"),
    ("410-FE-010", "149.0", "10.5"),
    ("410-AL-025", "112.0", "7.1"),
    ("420-VA-012", "93.0", "6.2"),
    ("420-FE-050", "71.0", "4.4"),
    ("430-FE-025", "86.0", "5.5"),
    ("430-AL-012", "98.0", "6.0"),
    ("440-VA-050", "41.0", "2.3"),
    ("440-MS-010", "52.0", "3.0"),
)


def _build_material_seed(article_number: str, stock_m: str, rest_stock_m: str) -> SimulatorMaterialSeed:
    category_code, material_code, dimension_code = article_number.split("-")
    category_name = CATEGORY_NAMES[category_code]
    material_name = MATERIAL_NAMES[material_code]
    dimension_mm = DIMENSION_MM_BY_CODE[dimension_code]
    description_prefix = DESCRIPTION_PREFIX_BY_CATEGORY.get(category_code, category_name)
    description = f"{description_prefix} {material_name} {dimension_mm} mm"
    return SimulatorMaterialSeed(
        article_number=article_number,
        name=description,
        category_code=category_code,
        category_name=category_name,
        material_code=material_code,
        material_name=material_name,
        dimension_code=dimension_code,
        dimension_mm=dimension_mm,
        profile=f"{category_code}-{material_code}",
        shape=SHAPE_BY_CATEGORY[category_code],
        size_mm=str(dimension_mm),
        unit="m",
        stock_m=Decimal(stock_m),
        rest_stock_m=Decimal(rest_stock_m),
    )


SIMULATOR_MATERIALS: tuple[SimulatorMaterialSeed, ...] = tuple(
    _build_material_seed(article_number, stock_m, rest_stock_m)
    for article_number, stock_m, rest_stock_m in ARTICLE_CATALOG
)


SIMULATOR_OPEN_ORDERS: tuple[SimulatorOrderSeed, ...] = (
    SimulatorOrderSeed("SAGE-ORD-2026-001", "420-VA-012", "Meyer Metallbau", 24, 850, "2026-04-18", "open", "high"),
    SimulatorOrderSeed("SAGE-ORD-2026-002", "420-VA-012", "Krause Industrietechnik", 12, 1400, "2026-04-20", "in_pipeline", "normal"),
    SimulatorOrderSeed("SAGE-ORD-2026-003", "100-FE-025", "Innenausbau Nord", 40, 620, "2026-04-24", "open", "high"),
    SimulatorOrderSeed("SAGE-ORD-2026-004", "300-AL-010", "Fassadenbau Richter", 16, 1750, "2026-04-27", "not_finished", "normal"),
    SimulatorOrderSeed("SAGE-ORD-2026-005", "430-AL-012", "Anlagenbau Schubert", 20, 980, "2026-05-02", "open", "normal"),
)


def list_materials(search_query: str | None = None) -> list[dict[str, Any]]:
    normalized = (search_query or "").strip().lower()
    result: list[dict[str, Any]] = []
    for material in SIMULATOR_MATERIALS:
        searchable = f"{material.article_number} {material.name} {material.profile} {material.shape}".lower()
        if normalized and normalized not in searchable:
            continue
        result.append(
            {
                "material_no": material.article_number,
                "description": material.name,
                "profile": material.profile,
                "shape": material.shape,
                "size_mm": material.size_mm,
                "material_group_code": material.category_code,
                "material_group": material.category_name,
                "material_code": material.material_code,
                "material": material.material_name,
                "dimension_code": material.dimension_code,
                "dimension_mm": material.dimension_mm,
                "unit": material.unit,
            }
        )
    return result


def get_material(material_reference: str) -> dict[str, Any] | None:
    normalized = material_reference.strip()
    for material in SIMULATOR_MATERIALS:
        if material.article_number == normalized:
            return {
                "material_no": material.article_number,
                "description": material.name,
                "profile": material.profile,
                "shape": material.shape,
                "size_mm": material.size_mm,
                "material_group_code": material.category_code,
                "material_group": material.category_name,
                "material_code": material.material_code,
                "material": material.material_name,
                "dimension_code": material.dimension_code,
                "dimension_mm": material.dimension_mm,
                "unit": material.unit,
                "stock_m": float(material.stock_m),
            }
    return None


def get_material_stock(material_reference: str) -> dict[str, Any] | None:
    normalized = material_reference.strip()
    for material in SIMULATOR_MATERIALS:
        if material.article_number == normalized:
            return {
                "material_no": material.article_number,
                "description": material.name,
                "stock_m": float(material.stock_m),
                "rest_stock_m": float(material.rest_stock_m),
                "stock_as_of": date.today().isoformat(),
            }
    return None


def list_orders_by_material(material_reference: str) -> list[dict[str, Any]]:
    return list_open_orders(material_reference=material_reference)


def get_order(order_reference: str) -> dict[str, Any] | None:
    normalized = order_reference.strip()
    for order in SIMULATOR_OPEN_ORDERS:
        if order.order_reference == normalized:
            return _order_to_payload(order)
    return None


def list_open_orders(material_reference: str | None = None) -> list[dict[str, Any]]:
    normalized_material = material_reference.strip() if material_reference else None
    result: list[dict[str, Any]] = []
    for order in SIMULATOR_OPEN_ORDERS:
        if normalized_material and order.material_reference != normalized_material:
            continue
        result.append(_order_to_payload(order))
    return result


def get_material_availability(material_reference: str) -> dict[str, Any] | None:
    material_payload = get_material(material_reference)
    stock_payload = get_material_stock(material_reference)
    if material_payload is None or stock_payload is None:
        return None
    open_orders = list_open_orders(material_reference=material_reference)
    in_pipeline_m = round(sum(float(order["required_m"]) for order in open_orders), 3)
    stock_m = float(stock_payload["stock_m"])
    available_m = round(stock_m - in_pipeline_m, 3)
    return {
        "material_no": material_payload["material_no"],
        "description": material_payload["description"],
        "stock_m": stock_m,
        "in_pipeline_m": in_pipeline_m,
        "available_m": available_m,
        "open_orders": open_orders,
    }


def _order_to_payload(order: SimulatorOrderSeed) -> dict[str, Any]:
    required_m = round((order.quantity * order.part_length_mm) / 1000, 3)
    material = get_material(order.material_reference) or {"description": "-"}
    return {
        "order_no": order.order_reference,
        "material_no": order.material_reference,
        "material_description": material["description"],
        "customer_name": order.customer_name,
        "quantity": order.quantity,
        "part_length_mm": order.part_length_mm,
        "required_m": required_m,
        "due_date": order.due_date,
        "status": order.status,
        "priority": order.priority,
    }


def send_transfer(transfer_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    transfer_ref = f"SIM-TR-{transfer_id.zfill(5)}"
    return {
        "transfer_ref": transfer_ref,
        "status": "accepted",
        "received_order_ref": payload.get("order_ref"),
        "received_material_ref": payload.get("material_ref"),
    }
