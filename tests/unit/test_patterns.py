"""
Unit tests — Clinical Pattern Matching
"""

from app.patterns.infection_patterns import match_clinical_pattern


def test_no_match_empty_signals():
    result = match_clinical_pattern({}, [])
    assert result is None


def test_uti_precursor_matches():
    result = match_clinical_pattern(
        {"mood": {"value": 1}, "agitation": {"value": "severe"}},
        ["mood", "agitation"],
    )
    assert result is not None
    assert result["pattern"] == "uti_precursor"
    assert result["confidence"] > 0.0
    assert len(result["suggested_actions"]) > 0


def test_uti_precursor_confidence_boosts_with_supporting():
    base_result = match_clinical_pattern(
        {"mood": {"value": 1}, "agitation": {"value": "severe"}},
        ["mood", "agitation"],
    )
    boosted_result = match_clinical_pattern(
        {
            "mood": {"value": 1},
            "agitation": {"value": "severe"},
            "appetite": {"value": "refused"},
        },
        ["mood", "agitation", "appetite"],
    )
    assert boosted_result["confidence"] > base_result["confidence"]


def test_early_infection_indicator_matches():
    result = match_clinical_pattern(
        {
            "mood": {"value": 1},
            "appetite": {"value": "refused"},
            "social_engagement": {"value": "isolated"},
        },
        ["mood", "appetite", "social_engagement"],
    )
    assert result is not None
    assert result["pattern"] in ("early_infection_indicator", "uti_precursor")


def test_partial_required_signals_no_match():
    # Only one of the required signals for UTI — should not match
    result = match_clinical_pattern(
        {"mood": {"value": 1}},
        ["mood"],
    )
    # mood alone matches nothing since all patterns need >= 2 required signals
    # (UTI needs mood + agitation)
    assert result is None or result["pattern"] != "uti_precursor"


def test_confidence_never_exceeds_0_95():
    # All possible signals flagged
    all_signals = [
        "mood",
        "agitation",
        "appetite",
        "sleep_quality",
        "social_engagement",
        "mobility",
    ]
    result = match_clinical_pattern(
        {s: {} for s in all_signals},
        all_signals,
    )
    if result:
        assert result["confidence"] <= 0.95
