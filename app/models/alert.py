"""Alert ORM model — drift alert with tier, explanation, and audit trail."""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, JSON, Boolean, Text, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_resident_dismissed", "resident_id", "dismissed"),
        Index("ix_alerts_tenant_tier", "tenant_id", "tier"),
    )

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: f"alr_{uuid.uuid4().hex[:8]}"
    )
    resident_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("residents.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    # Tier classification
    tier: Mapped[str] = mapped_column(String(4), nullable=False)     # T1 | T2 | T3 | T4
    tier_label: Mapped[str] = mapped_column(String(20), nullable=False)

    # Scores
    drift_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Full explanation payload (natural language + signal breakdown)
    explanation: Mapped[dict] = mapped_column(JSON, nullable=False)
    historical_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Audit fields
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dismissed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    dismiss_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)

    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship
    resident: Mapped["Resident"] = relationship("Resident", back_populates="alerts")  # noqa: F821

    @property
    def metadata_dict(self) -> dict:
        return {
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "action_taken": self.action_taken,
            "dismissed": self.dismissed,
        }

    def __repr__(self) -> str:
        return f"<Alert id={self.id} tier={self.tier} resident={self.resident_id}>"
