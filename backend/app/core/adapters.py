"""Notification and communication adapters (Email, SMS) and audit stub."""

from __future__ import annotations

import abc
from typing import Any

import structlog

logger = structlog.get_logger("app.adapters")


class EmailSender(abc.ABC):
    @abc.abstractmethod
    async def send_email(self, *, to: str, subject: str, body: str) -> None:
        pass


class ConsoleEmailSender(EmailSender):
    async def send_email(self, *, to: str, subject: str, body: str) -> None:
        logger.info("send_email", to=to, subject=subject, body=body)


class SMSSender(abc.ABC):
    @abc.abstractmethod
    async def send_sms(self, *, to: str, message: str) -> None:
        pass


class ConsoleSMSSender(SMSSender):
    async def send_sms(self, *, to: str, message: str) -> None:
        logger.info("send_sms", to=to, message=message)


class AuditServiceStub:
    """Stub audit recorder until Module M2 (P05) is built."""

    @staticmethod
    async def record(
        *,
        firm_id: Any,
        actor_id: Any,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: Any,
        matter_id: Any = None,
        ip: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        logger.info(
            "audit_stub_record",
            firm_id=str(firm_id) if firm_id else None,
            actor_id=str(actor_id) if actor_id else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
        )


_email_sender: EmailSender = ConsoleEmailSender()
_sms_sender: SMSSender = ConsoleSMSSender()


def get_email_sender() -> EmailSender:
    return _email_sender


def get_sms_sender() -> SMSSender:
    return _sms_sender
