"""Tenant ORM model — one row per care organisation."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.resident import Resident
    from app.models.webhook import Webhook


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: f"ten_{uuid.uuid4().hex[:8]}"
    )
    organisation_name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="self_hosted")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Credentials — stored as hashes, never plaintext
    client_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    client_secret_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    residents: Mapped[list[Resident]] = relationship(
        "Resident", back_populates="tenant", cascade="all, delete-orphan"
    )
    webhooks: Mapped[list[Webhook]] = relationship(
        "Webhook", back_populates="tenant", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Tenant id={self.id} org={self.organisation_name!r}>"
