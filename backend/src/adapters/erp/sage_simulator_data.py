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


SIMULATOR_USERS: tuple[SimulatorUserSeed, ...] = (
    SimulatorUserSeed(
        username="sage_admin",
        password="SageAdmin123!",
        role_code="admin",
        display_name="Sage Simulator Admin",
        email="sage_admin@example.local",
        erp_user_reference="sage_admin",
    ),
    SimulatorUserSeed(
        username="sage_leitung",
        password="SageLeitung123!",
        role_code="leitung",
        display_name="Sage Simulator Leitung",
        email="sage_leitung@example.local",
        erp_user_reference="sage_leitung",
    ),
    SimulatorUserSeed(
        username="sage_lager",
        password="SageLager123!",
        role_code="lager",
        display_name="Sage Simulator Lager",
        email="sage_lager@example.local",
        erp_user_reference="sage_lager",
    ),
)


SIMULATOR_MATERIALS: tuple[SimulatorMaterialSeed, ...] = (
    SimulatorMaterialSeed("ALU-R20-2000", "Aluminium Rundrohr 20x2", "R20", "round", "20x2", "m", Decimal("142.500"), Decimal("6.200")),
    SimulatorMaterialSeed("ALU-Q30-3000", "Aluminium Vierkantprofil 30x30x2", "Q30", "square", "30x30x2", "m", Decimal("96.000"), Decimal("5.400")),
    SimulatorMaterialSeed("STA-FL50-5000", "Stahl Flachprofil 50x8", "FL50", "flat", "50x8", "m", Decimal("73.250"), Decimal("3.100")),
    SimulatorMaterialSeed("STA-R40-4000", "Stahl Rundrohr 40x3", "R40", "round", "40x3", "m", Decimal("81.700"), Decimal("2.500")),
    SimulatorMaterialSeed("INO-Q25-2500", "Edelstahl Vierkantprofil 25x25x2", "Q25", "square", "25x25x2", "m", Decimal("54.400"), Decimal("1.800")),
    SimulatorMaterialSeed("PVC-U30-3000", "PVC U-Profil 30x20x30", "U30", "u-profile", "30x20x30", "m", Decimal("210.000"), Decimal("9.300")),
    SimulatorMaterialSeed("KUP-R15-1500", "Kupferrohr 15x1", "R15", "round", "15x1", "m", Decimal("61.900"), Decimal("2.200")),
    SimulatorMaterialSeed("MES-R12-1200", "Messingrohr 12x1", "R12", "round", "12x1", "m", Decimal("37.500"), Decimal("1.100")),
    SimulatorMaterialSeed("ALU-T40-4000", "Aluminium T-Profil 40x40x4", "T40", "t-profile", "40x40x4", "m", Decimal("88.000"), Decimal("4.000")),
    SimulatorMaterialSeed("STA-L35-3500", "Stahl Winkelprofil 35x35x5", "L35", "angle", "35x35x5", "m", Decimal("69.800"), Decimal("2.900")),
)


SIMULATOR_OPEN_ORDERS: tuple[SimulatorOrderSeed, ...] = (
    SimulatorOrderSeed("SAGE-ORD-2026-001", "ALU-R20-2000", "Meyer Metallbau", 24, 850, "2026-04-18", "open"),
    SimulatorOrderSeed("SAGE-ORD-2026-002", "STA-FL50-5000", "Krause Industrietechnik", 12, 1400, "2026-04-20", "open"),
    SimulatorOrderSeed("SAGE-ORD-2026-003", "PVC-U30-3000", "Innenausbau Nord", 40, 620, "2026-04-24", "open"),
    SimulatorOrderSeed("SAGE-ORD-2026-004", "ALU-T40-4000", "Fassadenbau Richter", 16, 1750, "2026-04-27", "released"),
    SimulatorOrderSeed("SAGE-ORD-2026-005", "STA-L35-3500", "Anlagenbau Schubert", 20, 980, "2026-05-02", "open"),
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
                "unit": material.unit,
            }
    return None


def get_material_stock(material_reference: str) -> dict[str, Any] | None:
    normalized = material_reference.strip()
    for material in SIMULATOR_MATERIALS:
        if material.article_number == normalized:
            return {
                "material_no": material.article_number,
                "stock_m": float(material.stock_m),
                "rest_stock_m": float(material.rest_stock_m),
                "stock_as_of": date.today().isoformat(),
            }
    return None


def list_orders_by_material(material_reference: str) -> list[dict[str, Any]]:
    normalized = material_reference.strip()
    result: list[dict[str, Any]] = []
    for order in SIMULATOR_OPEN_ORDERS:
        if order.material_reference != normalized:
            continue
        result.append(
            {
                "order_no": order.order_reference,
                "material_no": order.material_reference,
                "customer_name": order.customer_name,
                "quantity": order.quantity,
                "part_length_mm": order.part_length_mm,
                "due_date": order.due_date,
                "status": order.status,
            }
        )
    return result


def get_order(order_reference: str) -> dict[str, Any] | None:
    normalized = order_reference.strip()
    for order in SIMULATOR_OPEN_ORDERS:
        if order.order_reference == normalized:
            return {
                "order_no": order.order_reference,
                "material_no": order.material_reference,
                "customer_name": order.customer_name,
                "quantity": order.quantity,
                "part_length_mm": order.part_length_mm,
                "due_date": order.due_date,
                "status": order.status,
            }
    return None


def send_transfer(transfer_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    transfer_ref = f"SIM-TR-{transfer_id.zfill(5)}"
    return {
        "transfer_ref": transfer_ref,
        "status": "accepted",
        "received_order_ref": payload.get("order_ref"),
        "received_material_ref": payload.get("material_ref"),
    }
