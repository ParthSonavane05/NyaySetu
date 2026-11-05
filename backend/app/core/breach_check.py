"""Breached password checker interface and mock implementation."""

from __future__ import annotations

import abc
from typing import ClassVar


class BreachedPasswordChecker(abc.ABC):
    @abc.abstractmethod
    async def is_breached(self, password: str) -> bool:
        pass


class MockBreachedPasswordChecker(BreachedPasswordChecker):
    """Local offline check against common banned/breached passwords."""

    COMMON_BREACHED: ClassVar[set[str]] = {
        "password12345",
        "admin12345678",
        "qwertyuiop12",
        "lawfirm2026!",
        "nyaysetu12345",
    }

    async def is_breached(self, password: str) -> bool:
        return password.lower() in self.COMMON_BREACHED
