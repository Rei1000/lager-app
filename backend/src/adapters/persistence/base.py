"""SQLAlchemy declarative base for infrastructure models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Infrastructure ORM base class."""
