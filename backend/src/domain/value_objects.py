"""Domain value objects."""

from __future__ import annotations

from enum import Enum


class TrafficLight(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
