"""Use cases for material lookup and scan-driven search."""

from __future__ import annotations

from application.dtos import SearchMaterialsCommand
from ports.material_lookup_port import MaterialLookupPort, MaterialLookupRecord


class SearchMaterialsUseCase:
    def __init__(self, material_lookup_port: MaterialLookupPort) -> None:
        self._material_lookup_port = material_lookup_port

    def execute(self, command: SearchMaterialsCommand) -> list[MaterialLookupRecord]:
        query = command.query.strip()
        if not query:
            raise ValueError("query darf nicht leer sein")
        return self._material_lookup_port.search_materials(query)


class GetMaterialByArticleNumberUseCase:
    def __init__(self, material_lookup_port: MaterialLookupPort) -> None:
        self._material_lookup_port = material_lookup_port

    def execute(self, article_number: str) -> MaterialLookupRecord:
        normalized = article_number.strip()
        if not normalized:
            raise ValueError("article_number darf nicht leer sein")
        return self._material_lookup_port.get_by_article_number(normalized)
