"""Observation ORM model — a single care observation data point."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, JSON, Float, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.resident import Resident


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (
        # Key query pattern: all observations for a resident in date range
        Index("ix_observations_resident_observed_at", "resident_id", "observed_at"),
    )

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: f"obs_{uuid.uuid4().hex[:8]}"
    )
    resident_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("residents.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    observer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Raw signals as submitted — JSON blob
    signals: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Optional context (location, medication, visitor)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Drift evaluation result at time of ingestion
    drift_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    drift_triggered: Mapped[bool | None] = mapped_column(nullable=True)
    signals_flagged: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Relationships
    resident: Mapped[Resident] = relationship("Resident", back_populates="observations")

    def __repr__(self) -> str:
        return f"<Observation id={self.id} resident={self.resident_id} at={self.observed_at}>"
