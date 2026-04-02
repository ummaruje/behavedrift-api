from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from app.database import Base
import ulid

class AuditLog(Base):
    """
    Immutable audit trail for all significant API actions and system events.
    Required for regulatory compliance (CQC, GDPR).
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: f"aud_{ulid.new().str.lower()}")
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    
    action = Column(String, nullable=False, index=True) # e.g. "observation.create", "resident.erase"
    resource = Column(String, nullable=False, index=True) # e.g. "resident", "observation"
    resource_id = Column(String, nullable=True, index=True)
    
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    status = Column(String, nullable=False) # "success", "failure"
    
    # Contextual data: Request ID, IP address, user agent, or sanitized request payload
    context = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource})>"
