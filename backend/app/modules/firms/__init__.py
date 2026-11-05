"""Firms module exports."""

from __future__ import annotations

from app.modules.firms.router import router
from app.modules.firms.service import FirmService

__all__ = ["FirmService", "router"]
