"""
Unit tests — Drift Engine
Tests the core scoring algorithm without any DB interaction.
"""

from app.services.drift_engine import evaluate_drift, _classify_tier, _signal_to_numeric


# ---- _signal_to_numeric ----


def test_mood_to_numeric():
    assert _signal_to_numeric("mood", {"value": 3}) == 3.0


def test_appetite_excellent():
    assert _signal_to_numeric("appetite", {"value": "excellent"}) == 5.0


def test_appetite_refused():
    assert _signal_to_numeric("appetite", {"value": "refused"}) == 1.0


def test_sleep_good():
    assert _signal_to_numeric("sleep_quality", {"value": "good"}) == 4.0


def test_sleep_unknown_returns_none():
    assert _signal_to_numeric("sleep_quality", {"value": "unknown"}) is None


def test_pain_score_all_false():
    data = {
        "facial_grimacing": False,
        "guarding": False,
        "vocalisation": False,
        "restlessness": False,
        "verbal_report": False,
    }
    assert _signal_to_numeric("pain_indicators", data) == 0.0


def test_pain_score_partial():
    data = {
        "facial_grimacing": True,
        "guarding": False,
        "vocalisation": True,
        "restlessness": False,
        "verbal_report": False,
    }
    assert _signal_to_numeric("pain_indicators", data) == 2.0


def test_mobility_bedbound():
    assert _signal_to_numeric("mobility", {"value": "bedbound"}) == 1.0


def test_agitation_severe():
    assert _signal_to_numeric("agitation", {"value": "severe"}) == 4.0


# ---- _classify_tier ----

THRESHOLDS = {"T1": 0.40, "T2": 0.60, "T3": 0.75, "T4": 0.90}


def test_classify_below_t1():
    tier, label = _classify_tier(0.30, THRESHOLDS)
    assert tier is None
    assert label is None


def test_classify_t1():
    tier, label = _classify_tier(0.45, THRESHOLDS)
    assert tier == "T1"
    assert label == "Watch"


def test_classify_t2():
    tier, label = _classify_tier(0.65, THRESHOLDS)
    assert tier == "T2"
    assert label == "Concern"


def test_classify_t3():
    tier, label = _classify_tier(0.80, THRESHOLDS)
    assert tier == "T3"
    assert label == "Alert"


def test_classify_t4():
    tier, label = _classify_tier(0.95, THRESHOLDS)
    assert tier == "T4"
    assert label == "Critical"


# ---- evaluate_drift — no baseline ----


def test_evaluate_drift_no_baseline_returns_zero():
    signals = {"mood": {"value": 1}, "appetite": {"value": "refused"}}
    result = evaluate_drift(signals, baseline_data={})
    assert result.drift_score == 0.0
    assert result.triggered is False
    assert result.tier is None
    assert "initialising" in (result.message or "")


# ---- evaluate_drift — with baseline ----

BASELINE_WITH_MOOD = {
    "signals": {
        "mood": {"mean": 4.0, "std_dev": 0.3, "sample_count": 30},
        "appetite": {"mean": 4.5, "std_dev": 0.5, "sample_count": 28},
    }
}


def test_evaluate_drift_stable_no_trigger():
    signals = {"mood": {"value": 4}, "appetite": {"value": "good"}}
    result = evaluate_drift(signals, baseline_data=BASELINE_WITH_MOOD)
    assert result.drift_score < 0.40
    assert result.triggered is False


def test_evaluate_drift_large_deviation_triggers():
    # mood=1 against baseline mean=4.0 std=0.3 → z=(3/0.3)=10 → flagged
    signals = {"mood": {"value": 1}, "appetite": {"value": "refused"}}
    result = evaluate_drift(signals, baseline_data=BASELINE_WITH_MOOD)
    assert result.triggered is True
    assert result.drift_score > 0.40
    assert "mood" in result.signals_flagged


def test_evaluate_drift_high_risk_profile_increases_score():
    signals = {"mood": {"value": 2}, "appetite": {"value": "fair"}}
    normal = evaluate_drift(
        signals, baseline_data=BASELINE_WITH_MOOD, risk_profile="medium"
    )
    high = evaluate_drift(
        signals, baseline_data=BASELINE_WITH_MOOD, risk_profile="high"
    )
    assert high.drift_score >= normal.drift_score


def test_evaluate_drift_low_risk_profile_decreases_score():
    signals = {"mood": {"value": 2}, "appetite": {"value": "fair"}}
    normal = evaluate_drift(
        signals, baseline_data=BASELINE_WITH_MOOD, risk_profile="medium"
    )
    low = evaluate_drift(signals, baseline_data=BASELINE_WITH_MOOD, risk_profile="low")
    assert low.drift_score <= normal.drift_score


def test_evaluate_drift_unknown_signal_skipped_gracefully():
    signals = {"mood": {"value": 3}}
    # Baseline has only mood — should score fine
    result = evaluate_drift(signals, baseline_data=BASELINE_WITH_MOOD)
    assert result.drift_score >= 0.0


def test_evaluate_drift_score_never_exceeds_1():
    # Extreme deviation
    signals = {
        "mood": {"value": 1},
        "appetite": {"value": "refused"},
        "agitation": {"value": "severe"},
    }
    big_baseline = {
        "signals": {
            "mood": {"mean": 5.0, "std_dev": 0.01},
            "appetite": {"mean": 5.0, "std_dev": 0.01},
            "agitation": {"mean": 1.0, "std_dev": 0.01},
        }
    }
    result = evaluate_drift(signals, baseline_data=big_baseline, risk_profile="high")
    assert result.drift_score <= 1.0
