from app.models.audit import AuditLog
from app.models.gdpr import GDPRDeletionLog

def test_audit_log_instantiation():
    """Verify AuditLog model can be instantiated."""
    log = AuditLog(
        tenant_id="ten_123",
        action="resident.create",
        resource="resident",
        resource_id="res_456",
        status="success",
        context={"ip": "127.0.0.1"}
    )
    assert log.tenant_id == "ten_123"
    assert log.action == "resident.create"
    assert log.status == "success"

def test_gdpr_deletion_log_instantiation():
    """Verify GDPRDeletionLog model can be instantiated."""
    log = GDPRDeletionLog(
        tenant_id="ten_123",
        resident_id="res_456",
        certificate_id="cert_789",
        deleted_by="user_abc",
        evidence_hash="sha256:abc123"
    )
    assert log.tenant_id == "ten_123"
    assert log.resident_id == "res_456"
    assert log.certificate_id == "cert_789"
