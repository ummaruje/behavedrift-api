"""
Clinical pattern matching library.

Maps combinations of flagged signals to known clinical patterns
(e.g. UTI precursor, respiratory infection, psychological decline).

IMPORTANT: These patterns are decision-support heuristics, NOT diagnoses.
All pattern matches must include a confidence score and suggested actions.
The API never outputs a diagnosis — only a pattern correlation.
"""

from __future__ import annotations
from typing import Any


# ---- Pattern definitions ----
# Each pattern specifies:
#   - required_signals: all of these must be flagged
#   - supporting_signals: adds to confidence if also flagged
#   - confidence_base: base confidence when required signals match
#   - suggested_actions: plain-language care actions

_PATTERNS = [
    {
        "pattern": "uti_precursor",
        "required_signals": {"mood", "agitation"},
        "supporting_signals": {"appetite", "social_engagement"},
        "confidence_base": 0.55,
        "suggested_actions": [
            "Check fluid intake over the past 48 hours",
            "Observe for UTI indicators (colour/odour changes, discomfort)",
            "Consider requesting urine dipstick test",
            "Notify responsible clinical lead",
        ],
    },
    {
        "pattern": "early_infection_indicator",
        "required_signals": {"mood", "appetite", "social_engagement"},
        "supporting_signals": {"agitation", "sleep_quality", "mobility"},
        "confidence_base": 0.63,
        "suggested_actions": [
            "Take baseline temperature and blood pressure",
            "Review recent medication changes",
            "Check for any signs of localised infection",
            "Escalate to GP or clinical lead if pattern persists > 24 hours",
        ],
    },
    {
        "pattern": "respiratory_precursor",
        "required_signals": {"mobility", "sleep_quality"},
        "supporting_signals": {"appetite", "agitation"},
        "confidence_base": 0.45,
        "suggested_actions": [
            "Monitor oxygen saturation if equipment available",
            "Observe respiratory rate during rest",
            "Ensure adequate room ventilation",
            "Notify nursing team",
        ],
    },
    {
        "pattern": "psychological_decline",
        "required_signals": {"mood", "social_engagement"},
        "supporting_signals": {"sleep_quality", "appetite"},
        "confidence_base": 0.50,
        "suggested_actions": [
            "Review recent life events or changes in care home environment",
            "Consider referral to the mental health team",
            "Increase meaningful social activities",
            "Review medication for psychological side effects",
        ],
    },
    {
        "pattern": "positive_improvement",
        "required_signals": set(),  # handled separately
        "supporting_signals": set(),
        "confidence_base": 0.0,
        "suggested_actions": [],
    },
]


def match_clinical_pattern(
    signals: dict[str, Any],
    flagged_signal_names: list[str],
) -> dict | None:
    """
    Attempt to match flagged signals to a clinical pattern.

    Returns the best matching pattern dict, or None if no match.
    Always includes a confidence score and suggested actions.
    """
    flagged_set = set(flagged_signal_names)
    best_match = None
    best_confidence = 0.0

    for pattern_def in _PATTERNS:
        required = pattern_def["required_signals"]
        supporting = pattern_def["supporting_signals"]

        if not required:
            continue

        # Only match if ALL required signals are flagged
        if not required.issubset(flagged_set):  # type: ignore[attr-defined]
            continue

        # Confidence boost for supporting signals
        supporting_matches = len(supporting.intersection(flagged_set))  # type: ignore[attr-defined]
        confidence_boost = supporting_matches * 0.05
        confidence = min(pattern_def["confidence_base"] + confidence_boost, 0.95)  # type: ignore[operator]

        if confidence > best_confidence:
            best_confidence = confidence
            best_match = {
                "pattern": pattern_def["pattern"],
                "confidence": round(confidence, 4),
                "suggested_actions": pattern_def["suggested_actions"],
            }

    return best_match
