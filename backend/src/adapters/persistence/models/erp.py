"""ERP configuration infrastructure ORM models."""

from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.base import Base


class ErpProfileModel(Base):
    __tablename__ = "erp_profiles"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    erp_type: Mapped[str | None] = mapped_column(String(50))
    connection_type: Mapped[str | None] = mapped_column(String(50))
    base_url: Mapped[str | None] = mapped_column(Text())
    tenant_code: Mapped[str | None] = mapped_column(String(100))

    function_endpoints: Mapped[list["ErpFunctionEndpointModel"]] = relationship(
        back_populates="erp_profile"
    )


class ErpAuthConfigModel(Base):
    __tablename__ = "erp_auth_configs"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    auth_type: Mapped[str | None] = mapped_column(String(50))
    client_id: Mapped[str | None] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(100))
    token_url: Mapped[str | None] = mapped_column(Text())


class ErpFunctionEndpointModel(Base):
    __tablename__ = "erp_function_endpoints"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    erp_profile_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("erp_profiles.id"),
        nullable=False,
    )
    functional_key: Mapped[str] = mapped_column(String(100), nullable=False)
    http_method: Mapped[str] = mapped_column(String(10), nullable=False)
    path_template: Mapped[str] = mapped_column(Text(), nullable=False)
    query_template_json: Mapped[dict | None] = mapped_column(JSONB())
    request_template_json: Mapped[dict | None] = mapped_column(JSONB())

    erp_profile: Mapped[ErpProfileModel] = relationship(back_populates="function_endpoints")
    field_mappings: Mapped[list["ErpFieldMappingModel"]] = relationship(back_populates="endpoint")


class ErpFieldMappingModel(Base):
    __tablename__ = "erp_field_mappings"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    endpoint_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("erp_function_endpoints.id"),
        nullable=False,
    )
    app_field: Mapped[str] = mapped_column(String(100), nullable=False)
    erp_field: Mapped[str] = mapped_column(String(255), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)

    endpoint: Mapped[ErpFunctionEndpointModel] = relationship(back_populates="field_mappings")
