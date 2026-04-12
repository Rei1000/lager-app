from __future__ import annotations

from dataclasses import dataclass

import pytest

from application.dtos import SearchMaterialsCommand
from application.use_cases.material_lookup_use_cases import (
    GetMaterialByArticleNumberUseCase,
    SearchMaterialsUseCase,
)
from ports.material_lookup_port import MaterialLookupPort, MaterialLookupRecord


@dataclass
class FakeMaterialLookupPort(MaterialLookupPort):
    materials: list[MaterialLookupRecord]

    def search_materials(self, query: str) -> list[MaterialLookupRecord]:
        lowered = query.lower()
        return [
            material
            for material in self.materials
            if lowered in material.article_number.lower() or lowered in material.name.lower()
        ]

    def get_by_article_number(self, article_number: str) -> MaterialLookupRecord:
        for material in self.materials:
            if material.article_number == article_number:
                return material
        raise ValueError(f"Material nicht gefunden: {article_number}")


def test_search_materials_use_case_returns_matching_materials() -> None:
    port = FakeMaterialLookupPort(
        materials=[
            MaterialLookupRecord(
                article_number="ART-001",
                name="Stahlprofil 40x40",
                profile="40x40",
                erp_stock_m=120.0,
                rest_stock_m=12.0,
            ),
            MaterialLookupRecord(
                article_number="ART-002",
                name="Aluprofil 20x20",
                profile="20x20",
                erp_stock_m=40.0,
                rest_stock_m=3.0,
            ),
        ]
    )
    use_case = SearchMaterialsUseCase(material_lookup_port=port)

    result = use_case.execute(SearchMaterialsCommand(query="stahl"))

    assert len(result) == 1
    assert result[0].article_number == "ART-001"


def test_get_material_by_article_number_use_case_returns_one_material() -> None:
    port = FakeMaterialLookupPort(
        materials=[
            MaterialLookupRecord(
                article_number="ART-001",
                name="Stahlprofil 40x40",
                profile="40x40",
                erp_stock_m=120.0,
                rest_stock_m=12.0,
            )
        ]
    )
    use_case = GetMaterialByArticleNumberUseCase(material_lookup_port=port)

    material = use_case.execute("ART-001")

    assert material.name == "Stahlprofil 40x40"


def test_search_materials_use_case_rejects_empty_query() -> None:
    port = FakeMaterialLookupPort(materials=[])
    use_case = SearchMaterialsUseCase(material_lookup_port=port)

    with pytest.raises(ValueError):
        use_case.execute(SearchMaterialsCommand(query="  "))
