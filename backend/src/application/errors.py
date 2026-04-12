"""Lightweight application error types for API mapping."""

from __future__ import annotations


class NotFoundError(ValueError):
    """Raised when an expected resource does not exist."""


class AuthenticationError(ValueError):
    """Raised when authentication fails."""


class AuthorizationError(ValueError):
    """Raised when authenticated user has insufficient permissions."""
