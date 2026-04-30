"""
BehaveDrift Dashboard — Observation Submission
Submit behavioural observations with rich signal forms.
"""

import streamlit as st

st.set_page_config(page_title="Observations | BehaveDrift", page_icon="📝", layout="wide")

import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api_client import api_get, api_post, require_auth
from utils.charts import COLOURS

# ── Auth Guard ───────────────────────────────────────────────
require_auth()

# ── Header ───────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="margin-bottom: 4px;">📝 Submit Observation</h1>
    <p style="color: #94a3b8; margin-top: 0;">
        Record behavioural signals and receive real-time drift evaluation
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ── Load Residents ───────────────────────────────────────────
with st.spinner("Loading residents..."):
    res_data = api_get("/v1/residents", params={"page_size": 100})

if not res_data or not res_data.get("residents"):
    st.info("No residents registered yet. Go to the Residents page to register one.")
    st.stop()

residents = res_data["residents"]
resident_options = {
    f"{r['internal_reference']} ({r['resident_id'][:12]}…)": r["resident_id"]
    for r in residents
}

# ── Resident Selector ───────────────────────────────────────
selected_label = st.selectbox("Select Resident", list(resident_options.keys()))
selected_resident_id = resident_options[selected_label]

# Show resident info
selected_res = next(
    (r for r in residents if r["resident_id"] == selected_resident_id), {}
)
st.markdown(
    f"""
    <div style="background: #1e293b; border-radius: 10px; padding: 12px 16px;
                margin-bottom: 20px; display: flex; gap: 24px; align-items: center;">
        <span style="color: #94a3b8;">Risk: <b style="color:#e2e8f0;">{selected_res.get('risk_profile', '—').title()}</b></span>
        <span style="color: #94a3b8;">Baseline: <b style="color:#e2e8f0;">{selected_res.get('baseline_status', '—').title()}</b></span>
        <span style="color: #94a3b8;">Observations: <b style="color:#e2e8f0;">{selected_res.get('total_observations', 0)}</b></span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 🔬 Behavioural Signals")
st.caption("Complete at least one signal section below. The more signals, the better the drift analysis.")

# ── Signal Forms ─────────────────────────────────────────────

signals = {}

# -- Mood --
with st.expander("😊 Mood", expanded=True):
    enable_mood = st.checkbox("Record mood", value=True, key="enable_mood")
    if enable_mood:
        mood_labels = {1: "😢 Very Low", 2: "😕 Low", 3: "😐 Neutral", 4: "🙂 Good", 5: "😄 Very Good"}
        mood_val = st.slider(
            "Mood Score",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            help="1 = Very Low, 5 = Very Good",
        )
        st.caption(f"Selected: {mood_labels[mood_val]}")
        mood_notes = st.text_input("Mood notes (optional)", max_chars=300, key="mood_notes")
        signals["mood"] = {"value": mood_val, "scale": "1-5"}
        if mood_notes:
            signals["mood"]["notes"] = mood_notes

# -- Appetite --
with st.expander("🍽️ Appetite"):
    enable_appetite = st.checkbox("Record appetite", value=False, key="enable_appetite")
    if enable_appetite:
        app_val = st.selectbox(
            "Appetite Level", ["excellent", "good", "fair", "poor", "refused"]
        )
        app_meal = st.selectbox(
            "Meal (optional)", [None, "breakfast", "lunch", "dinner", "snack"],
            format_func=lambda x: "—" if x is None else x.title(),
        )
        fluid_ml = st.number_input("Fluid Intake (ml)", min_value=0, value=0, step=50)
        signals["appetite"] = {"value": app_val}
        if app_meal:
            signals["appetite"]["meal"] = app_meal
        if fluid_ml > 0:
            signals["appetite"]["fluid_intake_ml"] = fluid_ml

# -- Sleep Quality --
with st.expander("🌙 Sleep Quality"):
    enable_sleep = st.checkbox("Record sleep", value=False, key="enable_sleep")
    if enable_sleep:
        sleep_val = st.selectbox(
            "Sleep Quality",
            ["good", "fair", "disturbed", "very_disturbed", "unknown"],
            format_func=lambda x: x.replace("_", " ").title(),
        )
        night_wake = st.number_input("Night Wakings", min_value=0, value=0, step=1)
        hours_slept = st.slider("Hours Slept", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        signals["sleep_quality"] = {"value": sleep_val}
        if night_wake > 0:
            signals["sleep_quality"]["night_wakings"] = night_wake
        signals["sleep_quality"]["hours_slept"] = hours_slept

# -- Social Engagement --
with st.expander("🤝 Social Engagement"):
    enable_social = st.checkbox("Record social engagement", value=False, key="enable_social")
    if enable_social:
        social_val = st.selectbox(
            "Engagement Level",
            ["engaged", "moderate", "withdrawn", "isolated"],
            format_func=lambda x: x.title(),
        )
        activity = st.checkbox("Participated in activity?", key="social_activity")
        activity_name = None
        if activity:
            activity_name = st.text_input("Activity name", key="activity_name_input")
        signals["social_engagement"] = {
            "value": social_val,
            "activity_participated": activity,
        }
        if activity_name:
            signals["social_engagement"]["activity_name"] = activity_name

# -- Pain Indicators --
with st.expander("💊 Pain Indicators"):
    enable_pain = st.checkbox("Record pain indicators", value=False, key="enable_pain")
    if enable_pain:
        st.caption("Select all observed pain indicators:")
        p1, p2, p3 = st.columns(3)
        with p1:
            grimacing = st.checkbox("Facial Grimacing")
            guarding = st.checkbox("Guarding")
        with p2:
            vocalisation = st.checkbox("Vocalisation")
            restlessness = st.checkbox("Restlessness")
        with p3:
            verbal = st.checkbox("Verbal Report")
        painad = st.slider("PAINAD Score", min_value=0, max_value=10, value=0)
        signals["pain_indicators"] = {
            "facial_grimacing": grimacing,
            "guarding": guarding,
            "vocalisation": vocalisation,
            "restlessness": restlessness,
            "verbal_report": verbal,
        }
        if painad > 0:
            signals["pain_indicators"]["painad_score"] = painad

# -- Mobility --
with st.expander("🚶 Mobility"):
    enable_mobility = st.checkbox("Record mobility", value=False, key="enable_mobility")
    if enable_mobility:
        mob_val = st.selectbox(
            "Mobility Level",
            ["independent", "supervised", "assisted", "dependent", "bedbound"],
            format_func=lambda x: x.title(),
        )
        mob_compare = st.selectbox(
            "Compared to Baseline",
            [None, "better_than_usual", "same_as_usual", "worse_than_usual", "unknown"],
            format_func=lambda x: "—" if x is None else x.replace("_", " ").title(),
        )
        signals["mobility"] = {"value": mob_val}
        if mob_compare:
            signals["mobility"]["baseline_comparison"] = mob_compare

# -- Agitation --
with st.expander("⚡ Agitation"):
    enable_agitation = st.checkbox("Record agitation", value=False, key="enable_agitation")
    if enable_agitation:
        agi_val = st.selectbox(
            "Agitation Level",
            ["calm", "mild", "moderate", "severe"],
            format_func=lambda x: x.title(),
        )
        agi_type = st.selectbox(
            "Type (optional)",
            [None, "physical", "verbal", "wandering", "sundowning", "other"],
            format_func=lambda x: "—" if x is None else x.title(),
        )
        signals["agitation"] = {"value": agi_val}
        if agi_type:
            signals["agitation"]["type"] = agi_type

st.divider()

# ── Context ──────────────────────────────────────────────────
st.markdown("### 📋 Observation Context")
ctx_col1, ctx_col2 = st.columns(2)
with ctx_col1:
    location = st.text_input("Location", placeholder="e.g. Day Room, Bedroom")
    observer_id = st.text_input("Observer ID", placeholder="e.g. staff_nurse_01")
with ctx_col2:
    visitor = st.checkbox("Visitor present?")
    med_admin = st.checkbox("Medication administered?")
    med_notes = st.text_input("Medication notes", max_chars=200) if med_admin else None

context = {}
if location:
    context["location"] = location
if visitor:
    context["visitor_present"] = True
if med_admin:
    context["medication_administered"] = True
    if med_notes:
        context["medication_notes"] = med_notes

st.divider()

# ── Submit ───────────────────────────────────────────────────
signal_count = len(signals)
st.markdown(f"**Signals recorded:** {signal_count}")

if signal_count == 0:
    st.warning("Enable at least one signal section above.")

if st.button(
    "🚀 Submit Observation",
    use_container_width=True,
    type="primary",
    disabled=signal_count == 0,
):
    payload = {
        "resident_id": selected_resident_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "signals": signals,
    }
    if observer_id:
        payload["observer_id"] = observer_id
    if context:
        payload["context"] = context

    with st.spinner("Processing observation..."):
        result = api_post("/v1/observations", payload)

    if result:
        st.success("✅ Observation submitted and processed!")
        st.markdown("---")

        # Display drift evaluation
        drift = result.get("drift_evaluation", {})
        triggered = drift.get("triggered", False)
        score = drift.get("drift_score", 0)
        flagged = drift.get("signals_flagged", [])
        alert = drift.get("alert_generated")

        # Drift score colour
        if score < 0.3:
            score_colour = COLOURS["stable"]
        elif score < 0.6:
            score_colour = COLOURS["watch_t1"]
        elif score < 0.8:
            score_colour = COLOURS["concern_t2"]
        else:
            score_colour = COLOURS["alert_t3"]

        st.markdown(
            f"""
            <div style="background: #1e293b; border-radius: 12px; padding: 24px;
                        border: 1px solid {'#ef4444' if triggered else '#22c55e'}33;">
                <h3 style="color: {'#ef4444' if triggered else '#22c55e'}; margin-top: 0;">
                    {'🚨 Drift Detected!' if triggered else '✅ No Drift Detected'}
                </h3>
                <div style="display: flex; gap: 32px; margin-top: 12px;">
                    <div>
                        <span style="color: #94a3b8; font-size: 0.85rem;">Drift Score</span><br>
                        <span style="font-size: 2rem; font-weight: 700; color: {score_colour};">
                            {score:.3f}
                        </span>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.85rem;">Baseline Status</span><br>
                        <span style="font-size: 1.2rem; color: #e2e8f0;">
                            {drift.get('baseline_status', '—').title()}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if flagged:
            st.markdown(
                "**Flagged Signals:** " + ", ".join(
                    f"`{s}`" for s in flagged
                )
            )

        if alert:
            st.error(
                f"🚨 Alert Generated: **{alert.get('tier_label', alert.get('tier'))}** "
                f"(ID: `{alert.get('alert_id', '—')}`)"
            )

        if drift.get("message"):
            st.info(f"💬 {drift['message']}")

        st.markdown(f"**Observation ID:** `{result.get('observation_id', '—')}`")
