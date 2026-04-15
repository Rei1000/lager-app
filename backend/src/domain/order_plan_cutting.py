"""Pure cutting-plan demand calculations for order planning (Stangen, Trennschnitte).

Fachliche Ein-Quelle-der-Wahrheit für linearen Materialbedarf inkl. Kerf zwischen Schnitten:
Netto = Stückzahl × Teillänge, Verschnitt = (Stückzahl − 1) × Kerf, Brutto = Netto + Verschnitt.

Verwendung: Planungsvorschau (`PreviewOrderPlanUseCase`), `AppOrder.total_demand_mm`, Seeds.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CuttingPlanDemandMm:
    """Meter-linear demand split into net material and kerf waste between cuts."""

    net_mm: int
    kerf_waste_mm: int
    gross_mm: int


def calculate_cutting_plan_demand_mm(
    quantity: int, part_length_mm: int, kerf_mm: float
) -> CuttingPlanDemandMm:
    if quantity <= 0:
        raise ValueError("quantity muss groesser als 0 sein")
    if part_length_mm <= 0:
        raise ValueError("part_length_mm muss groesser als 0 sein")
    if kerf_mm < 0:
        raise ValueError("kerf_mm darf nicht negativ sein")
    net_mm = quantity * part_length_mm
    kerf_waste_raw = max(0, quantity - 1) * kerf_mm
    kerf_waste_mm = int(round(kerf_waste_raw))
    gross_mm = net_mm + kerf_waste_mm
    return CuttingPlanDemandMm(net_mm=net_mm, kerf_waste_mm=kerf_waste_mm, gross_mm=gross_mm)


def is_cutting_plan_feasible(*, gross_m: float, available_m: float) -> bool:
    """True if planned gross demand does not exceed ERP/simulator-reported available meters."""
    return gross_m <= available_m + 1e-9
