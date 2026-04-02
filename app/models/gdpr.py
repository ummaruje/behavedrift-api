from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.database import Base
import ulid


class GDPRDeletionLog(Base):
    """
    Records of resident data erasure requests and execution.
    Acts as the source for 'deletion certificates' as per GDPR requirements.
    """

    __tablename__ = "gdpr_deletion_logs"

    id = Column(
        String, primary_key=True, default=lambda: f"gdl_{ulid.new().str.lower()}"
    )
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)

    resident_id = Column(
        String, nullable=False, index=True
    )  # ID of the now-deleted resident
    certificate_id = Column(String, unique=True, nullable=False, index=True)

    deleted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_by = Column(String, nullable=False)  # User ID who initiated the erasure

    # Hash of the proof of deletion (e.g. combined hash of deleted records)
    evidence_hash = Column(String, nullable=True)

    def __repr__(self):
        return f"<GDPRDeletionLog(resident_id={self.resident_id}, certificate={self.certificate_id})>"
