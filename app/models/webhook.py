"""Webhook ORM model — registered endpoint for event delivery."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, Boolean, JSON, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant


class Webhook(Base):
    __tablename__ = "webhooks"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: f"wh_{uuid.uuid4().hex[:8]}"
    )
    tenant_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    events: Mapped[list] = mapped_column(JSON, nullable=False)  # list of event strings
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    min_tier: Mapped[str] = mapped_column(String(4), default="T1")

    # HMAC signing secret — needs to be accessible in plaintext for signature generation
    signing_secret: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="webhooks")

    def __repr__(self) -> str:
        return f"<Webhook id={self.id} url={self.url!r}>"
