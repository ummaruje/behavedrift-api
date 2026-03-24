"""Resident ORM model — one row per care home resident."""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, JSON, Float, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Resident(Base):
    __tablename__ = "residents"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: f"res_{uuid.uuid4().hex[:8]}"
    )
    tenant_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    internal_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    # Unique within a tenant — not globally
    __table_args__ = (
        __import__("sqlalchemy").UniqueConstraint("tenant_id", "internal_reference"),
    )

    # Clinical (no PII — only age-band metadata)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    diagnosis_codes: Mapped[list] = mapped_column(JSON, default=list)
    risk_profile: Mapped[str] = mapped_column(String(20), default="medium")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Baseline config
    baseline_window_days: Mapped[int] = mapped_column(Integer, default=28)
    baseline_status: Mapped[str] = mapped_column(String(30), default="initialising")
    # Serialised baseline statistics — updated periodically by baseline service
    baseline_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    baseline_last_calculated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    baseline_reset_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    baseline_reset_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)

    total_observations: Mapped[int] = mapped_column(Integer, default=0)
    last_observation_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="residents")  # noqa: F821
    observations: Mapped[list["Observation"]] = relationship(  # noqa: F821
        "Observation", back_populates="resident", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(  # noqa: F821
        "Alert", back_populates="resident", cascade="all, delete-orphan"
    )

    @property
    def min_observations_required(self) -> int:
        from app.config import get_settings
        return get_settings().baseline_min_observations

    def __repr__(self) -> str:
        return f"<Resident id={self.id} ref={self.internal_reference!r}>"
