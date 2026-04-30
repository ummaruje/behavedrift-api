"""
BehaveDrift Dashboard — Population Overview
Displays risk distribution, key metrics, and active alerts.
"""

import streamlit as st

st.set_page_config(page_title="Dashboard | BehaveDrift", page_icon="🏠", layout="wide")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api_client import api_get, require_auth
from utils.charts import build_risk_donut, tier_badge, COLOURS

# ── Auth Guard ───────────────────────────────────────────────
require_auth()

# ── Header ───────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="margin-bottom: 4px;">🏠 Population Dashboard</h1>
    <p style="color: #94a3b8; margin-top: 0;">
        Real-time overview of all residents and active alerts
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ── Fetch Data ───────────────────────────────────────────────
with st.spinner("Loading population data..."):
    pop_data = api_get("/v1/analytics/population")
    alerts_data = api_get("/v1/alerts", params={"page_size": 10})

if not pop_data:
    st.info("No data available yet. Start by registering residents and submitting observations.")
    st.stop()

risk = pop_data.get("risk_distribution", {})
total = pop_data.get("total_residents", 0)
active_alerts_list = pop_data.get("active_alerts", [])

# ── Key Metrics ──────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Total Residents", total)
with m2:
    st.metric("Active Alerts", len(active_alerts_list))
with m3:
    critical = risk.get("critical_t4", 0) + risk.get("alert_t3", 0)
    st.metric("⚠️ High Risk", critical)
with m4:
    st.metric("✅ Stable", risk.get("stable", 0))

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts + Alerts ──────────────────────────────────────────
chart_col, alerts_col = st.columns([1, 1])

with chart_col:
    fig = build_risk_donut(risk)
    st.plotly_chart(fig, use_container_width=True)

    # Trending signals
    trending = pop_data.get("trending_signals", [])
    if trending:
        st.markdown("#### 📈 Trending Signals")
        for i, signal in enumerate(trending, 1):
            st.markdown(
                f'<span style="color:{COLOURS["primary"]};font-weight:600;">'
                f"{i}.</span> {signal.replace('_', ' ').title()}",
                unsafe_allow_html=True,
            )

with alerts_col:
    st.markdown("#### 🚨 Recent Alerts")

    if alerts_data and alerts_data.get("alerts"):
        for alert in alerts_data["alerts"][:8]:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border-left: 4px solid
                        {COLOURS.get(f'{"alert_t3" if alert.get("tier") in ("T3","T4") else "watch_t1"}', COLOURS["muted"])};
                        border-radius: 8px; padding: 14px 16px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; color: #e2e8f0;">
                                {alert.get('resident_id', '—')[:16]}…
                            </span>
                            {tier_badge(alert.get('tier', '—'))}
                        </div>
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 6px;">
                            Drift: {alert.get('drift_score', 0):.3f} •
                            Confidence: {alert.get('confidence_score', 0):.1%}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.markdown(
            """
            <div style="text-align: center; padding: 40px; color: #94a3b8;">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">🎉</div>
                <p>No active alerts — all residents are stable.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
