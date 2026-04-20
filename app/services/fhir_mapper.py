"""
FHIR Mapper Service
Maps FHIR R4 resources to BehaveDrift internal models and vice versa.
"""

from __future__ import annotations


from dateutil.parser import isoparse  # type: ignore[import-untyped]
from app.exceptions import ValidationError

# SNOMED CT → BehaveDrift signal mapping
_SNOMED_SIGNAL_MAP = {
    "285854004": "mood",  # Emotion
    "363787002": "appetite",  # Appetite (observable entity)
    "258158006": "sleep_quality",  # Sleep quality
    "228553004": "social_engagement",  # Social engagement
    "22253000": "pain_indicators",  # Pain
    "282097004": "mobility",  # Mobility and transfer
    "24199005": "agitation",  # Agitation
}


def parse_fhir_observation(fhir_resource: dict) -> tuple[str, str, dict]:
    """
    Parses a FHIR R4 Observation resource into (resident_id, observed_at, signals_dict).
    Raises ValidationError if the resource is invalid or missing required fields.
    """
    if fhir_resource.get("resourceType") != "Observation":
        raise ValidationError("resourceType must be 'Observation'.")

    # Extract resident_id from subject reference
    subject = fhir_resource.get("subject", {})
    resident_id = subject.get("reference", "").replace("Patient/", "")
    if not resident_id:
        raise ValidationError(
            "subject.reference is required (e.g. 'Patient/res_7f3a9c21')."
        )

    # Extract observed_at
    effective = fhir_resource.get("effectiveDateTime") or fhir_resource.get("effective")
    if not effective:
        raise ValidationError("effectiveDateTime or effective is required.")

    try:
        observed_at = isoparse(effective) if isinstance(effective, str) else effective
    except (ValueError, TypeError):
        raise ValidationError(f"Could not parse effective date: {effective}")

    # Map SNOMED code to signal
    code_obj = fhir_resource.get("code", {})
    codings = code_obj.get("coding", [])
    signal_name = None
    for coding in codings:
        snomed_code = coding.get("code", "")
        if snomed_code in _SNOMED_SIGNAL_MAP:
            signal_name = _SNOMED_SIGNAL_MAP[snomed_code]
            break

    if not signal_name:
        coded_values = [c.get("code", "?") for c in codings]
        raise ValidationError(
            f"No mapped SNOMED code found. Codes: {coded_values}. "
            f"Supported: {list(_SNOMED_SIGNAL_MAP.keys())}"
        )

    # Extract value
    value = None
    if "valueQuantity" in fhir_resource:
        value = fhir_resource["valueQuantity"].get("value")
    elif "valueString" in fhir_resource:
        value = fhir_resource["valueString"]
    elif "valueInteger" in fhir_resource:
        value = fhir_resource["valueInteger"]
    elif "valueCodeableConcept" in fhir_resource:
        cc = fhir_resource["valueCodeableConcept"]
        value = cc.get("text") or (cc.get("coding", [{}])[0].get("display"))

    if value is None:
        raise ValidationError(
            "No value found in FHIR Observation (valueQuantity, valueString, etc.)."
        )

    signals_dict = {signal_name: {"value": value}}

    return resident_id, observed_at, signals_dict
