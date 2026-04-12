"""API error mapping helpers."""

from __future__ import annotations

from fastapi import HTTPException, status

from application.errors import AuthenticationError, AuthorizationError, NotFoundError


def map_value_error(exc: ValueError) -> HTTPException:
    message = str(exc)
    if isinstance(exc, AuthenticationError):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
    if isinstance(exc, AuthorizationError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    if "nicht gefunden" in message.lower():
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
