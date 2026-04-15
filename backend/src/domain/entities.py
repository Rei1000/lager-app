"""Domain entities for phase 2 core rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.order_plan_cutting import calculate_cutting_plan_demand_mm
from domain.value_objects import TrafficLight

ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"checked"},
    "checked": {"reserved", "canceled"},
    "reserved": {"linked", "canceled"},
    "linked": {"confirmed", "canceled"},
    "confirmed": {"done", "canceled"},
    "done": set(),
    "canceled": set(),
}

ALLOWED_INVENTORY_DIFFERENCE_TYPES = {"surplus", "deficit", "equal"}
ALLOWED_STOCK_CORRECTION_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "requested": {"confirmed", "canceled"},
    "confirmed": set(),
    "canceled": set(),
}
ALLOWED_ERP_TRANSFER_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"ready", "failed"},
    "ready": {"approved", "failed"},
    "approved": {"sent", "failed"},
    "sent": set(),
    "failed": {"ready"},
}
ALLOWED_PHOTO_ENTITY_TYPES = {
    "material",
    "inventory_count",
    "stock_correction",
}
ALLOWED_COMMENT_ENTITY_TYPES = {
    "material",
    "order",
    "inventory_count",
    "stock_correction",
    "erp_transfer",
}


@dataclass
class MaterialType:
    article_number: str
    name: str
    min_rest_length_mm: int

    def __post_init__(self) -> None:
        if not self.article_number.strip():
            raise ValueError("article_number darf nicht leer sein")
        if not self.name.strip():
            raise ValueError("name darf nicht leer sein")
        if self.min_rest_length_mm < 0:
            raise ValueError("min_rest_length_mm darf nicht negativ sein")


@dataclass
class RestStockAccount:
    material_article_number: str
    total_rest_stock_mm: int

    def __post_init__(self) -> None:
        if not self.material_article_number.strip():
            raise ValueError("material_article_number darf nicht leer sein")
        if self.total_rest_stock_mm < 0:
            raise ValueError("total_rest_stock_mm darf nicht negativ sein")


@dataclass
class AppOrder:
    material_article_number: str
    quantity: int
    part_length_mm: int
    kerf_mm: int
    include_rest_stock: bool
    order_id: str | None = None
    status: str = "draft"
    priority_order: int | None = None
    traffic_light: TrafficLight | None = None
    erp_order_number: str | None = None
    """Erstellender Benutzer (nur fuer Persistenz beim Anlegen; aus DB bei Lesen)."""
    created_by_user_id: int | None = None

    def __post_init__(self) -> None:
        if not self.material_article_number.strip():
            raise ValueError("material_article_number darf nicht leer sein")
        if self.quantity <= 0:
            raise ValueError("quantity muss groesser als 0 sein")
        if self.part_length_mm <= 0:
            raise ValueError("part_length_mm muss groesser als 0 sein")
        if self.kerf_mm < 0:
            raise ValueError("kerf_mm darf nicht negativ sein")
        if self.priority_order is not None and self.priority_order <= 0:
            raise ValueError("priority_order muss groesser als 0 sein")
        if self.status not in ALLOWED_STATUS_TRANSITIONS:
            raise ValueError(f"Unbekannter Status: {self.status}")

    @property
    def total_demand_mm(self) -> int:
        """Bruttolinearbedarf mm: Netto (Stück × Länge) + Verschnitt ((Stück−1) × Kerf)."""
        return calculate_cutting_plan_demand_mm(
            self.quantity, self.part_length_mm, float(self.kerf_mm)
        ).gross_mm

    def transition_to(self, new_status: str) -> None:
        allowed = ALLOWED_STATUS_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(f"Statuswechsel nicht erlaubt: {self.status} -> {new_status}")
        self.status = new_status


@dataclass
class InventoryCount:
    material_article_number: str
    counted_stock_mm: int
    reference_stock_mm: int
    counted_by_user_id: int
    comment: str | None = None

    def __post_init__(self) -> None:
        if not self.material_article_number.strip():
            raise ValueError("material_article_number darf nicht leer sein")
        if self.counted_stock_mm < 0:
            raise ValueError("counted_stock_mm darf nicht negativ sein")
        if self.reference_stock_mm < 0:
            raise ValueError("reference_stock_mm darf nicht negativ sein")
        if self.counted_by_user_id <= 0:
            raise ValueError("counted_by_user_id muss groesser als 0 sein")

    @property
    def difference_mm(self) -> int:
        return self.counted_stock_mm - self.reference_stock_mm

    @property
    def difference_type(self) -> str:
        if self.difference_mm > 0:
            return "surplus"
        if self.difference_mm < 0:
            return "deficit"
        return "equal"


@dataclass
class InventoryDifference:
    material_article_number: str
    counted_stock_mm: int
    reference_stock_mm: int

    def __post_init__(self) -> None:
        if not self.material_article_number.strip():
            raise ValueError("material_article_number darf nicht leer sein")
        if self.counted_stock_mm < 0:
            raise ValueError("counted_stock_mm darf nicht negativ sein")
        if self.reference_stock_mm < 0:
            raise ValueError("reference_stock_mm darf nicht negativ sein")

    @property
    def difference_mm(self) -> int:
        return self.counted_stock_mm - self.reference_stock_mm

    @property
    def difference_type(self) -> str:
        if self.difference_mm > 0:
            return "surplus"
        if self.difference_mm < 0:
            return "deficit"
        return "equal"


@dataclass
class StockCorrectionRequest:
    inventory_count_id: int
    material_article_number: str
    correction_mm: int
    requested_by_user_id: int
    comment: str | None = None
    status: str = "requested"

    def __post_init__(self) -> None:
        if self.inventory_count_id <= 0:
            raise ValueError("inventory_count_id muss groesser als 0 sein")
        if not self.material_article_number.strip():
            raise ValueError("material_article_number darf nicht leer sein")
        if self.correction_mm == 0:
            raise ValueError("correction_mm darf nicht 0 sein")
        if self.requested_by_user_id <= 0:
            raise ValueError("requested_by_user_id muss groesser als 0 sein")
        if self.status not in ALLOWED_STOCK_CORRECTION_STATUS_TRANSITIONS:
            raise ValueError(f"Unbekannter Korrekturstatus: {self.status}")

    def transition_to(self, new_status: str) -> None:
        allowed = ALLOWED_STOCK_CORRECTION_STATUS_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(f"Korrekturstatus nicht erlaubt: {self.status} -> {new_status}")
        self.status = new_status


@dataclass
class ErpTransferRequest:
    order_id: str
    material_article_number: str
    requested_by_user_id: int
    payload: dict[str, object] | None = None
    status: str = "draft"
    failure_reason: str | None = None
    created_at: datetime | None = None
    ready_at: datetime | None = None
    approved_at: datetime | None = None
    sent_at: datetime | None = None
    failed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.order_id.strip():
            raise ValueError("order_id darf nicht leer sein")
        if not self.material_article_number.strip():
            raise ValueError("material_article_number darf nicht leer sein")
        if self.requested_by_user_id <= 0:
            raise ValueError("requested_by_user_id muss groesser als 0 sein")
        if self.status not in ALLOWED_ERP_TRANSFER_STATUS_TRANSITIONS:
            raise ValueError(f"Unbekannter ERP-Transferstatus: {self.status}")

    def transition_to(self, new_status: str) -> None:
        allowed = ALLOWED_ERP_TRANSFER_STATUS_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(f"ERP-Transferstatus nicht erlaubt: {self.status} -> {new_status}")
        self.status = new_status


@dataclass
class PhotoAttachment:
    entity_type: str
    entity_id: str
    uploaded_by_user_id: int
    comment: str | None = None

    def __post_init__(self) -> None:
        if self.entity_type not in ALLOWED_PHOTO_ENTITY_TYPES:
            raise ValueError(f"Unbekannter Foto-Kontext: {self.entity_type}")
        if not self.entity_id.strip():
            raise ValueError("entity_id darf nicht leer sein")
        if self.uploaded_by_user_id <= 0:
            raise ValueError("uploaded_by_user_id muss groesser als 0 sein")


@dataclass
class Comment:
    entity_type: str
    entity_id: str
    text: str
    created_by_user_id: int

    def __post_init__(self) -> None:
        if self.entity_type not in ALLOWED_COMMENT_ENTITY_TYPES:
            raise ValueError(f"Unbekannter Kommentar-Kontext: {self.entity_type}")
        if not self.entity_id.strip():
            raise ValueError("entity_id darf nicht leer sein")
        if not self.text.strip():
            raise ValueError("comment text darf nicht leer sein")
        if self.created_by_user_id <= 0:
            raise ValueError("created_by_user_id muss groesser als 0 sein")
