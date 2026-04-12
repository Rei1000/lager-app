"""Database engine and session setup for persistence adapters."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings

SessionLocal = sessionmaker(autoflush=False, autocommit=False, class_=Session)


def get_engine() -> Engine:
    """Build SQLAlchemy engine from environment settings."""
    return create_engine(
        settings.sqlalchemy_database_url,
        echo=settings.db_echo,
        pool_pre_ping=True,
    )


def get_session() -> Session:
    """Return a new SQLAlchemy session."""
    return SessionLocal(bind=get_engine())
