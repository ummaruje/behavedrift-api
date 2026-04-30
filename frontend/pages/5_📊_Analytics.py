"""
BehaveDrift Dashboard — Analytics & Trends
Drift trends, population correlations, and visual insights.
"""

import streamlit as st

st.set_page_config(page_title="Analytics | BehaveDrift", page_icon="📊", layout="wide")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api_client import api_get, require_auth
from utils.charts import build_drift_timeline, COLOURS

# ── Auth Guard ───────────────────────────────────────────────
require_auth()

# ── Header ───────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="margin-bottom: 4px;">📊 Analytics & Trends</h1>
    <p style="color: #94a3b8; margin-top: 0;">
        Longitudinal drift analysis and population-level insights
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ── Tabs ─────────────────────────────────────────────────────
tab_trends, tab_correlations = st.tabs(["📈 Drift Trends", "🔗 Correlations"])

# ── Tab 1: Drift Trends ─────────────────────────────────────
with tab_trends:
    st.markdown("### 📈 Resident Drift Trend")
    st.caption("Select a resident and time period to visualise their drift score over time.")

    # Load residents
    with st.spinner("Loading residents..."):
        res_data = api_get("/v1/residents", params={"page_size": 100})

    if not res_data or not res_data.get("residents"):
        st.info("No residents available. Register residents first.")
    else:
        residents = res_data["residents"]
        resident_options = {
            f"{r['internal_reference']} ({r['resident_id'][:12]}…)": r["resident_id"]
            for r in residents
        }

        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            selected_label = st.selectbox(
                "Select Resident", list(resident_options.keys()), key="trend_resident"
            )
            selected_id = resident_options[selected_label]
        with t_col2:
            days = st.slider("Time Period (days)", min_value=7, max_value=365, value=30)

        # Fetch trend data
        with st.spinner("Loading trend data..."):
            trend_data = api_get(
                f"/v1/analytics/trends/{selected_id}", params={"days": days}
            )

        if trend_data and trend_data.get("data_points"):
            data_points = trend_data["data_points"]

            # Summary metrics
            scores = [
                dp["drift_score"]
                for dp in data_points
                if dp.get("drift_score") is not None
            ]

            if scores:
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    st.metric("Data Points", len(data_points))
                with s2:
                    st.metric("Avg Drift", f"{sum(scores)/len(scores):.4f}")
                with s3:
                    st.metric("Max Drift", f"{max(scores):.4f}")
                with s4:
                    alert_days = sum(
                        1 for dp in data_points if dp.get("alert_tier")
                    )
                    st.metric("Alert Days", alert_days)

            st.markdown("<br>", unsafe_allow_html=True)

            # Chart
            fig = build_drift_timeline(data_points)
            st.plotly_chart(fig, use_container_width=True)

            # Data table
            with st.expander("📋 Raw Data", expanded=False):
                import pandas as pd

                df = pd.DataFrame(data_points)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "date": "Date",
                        "drift_score": st.column_config.NumberColumn(
                            "Drift Score", format="%.4f"
                        ),
                        "alert_tier": "Alert Tier",
                        "signals": "Signals",
                    },
                )
        else:
            st.markdown(
                """
                <div style="text-align: center; padding: 50px; color: #94a3b8;">
                    <div style="font-size: 2.5rem; margin-bottom: 12px;">📭</div>
                    <p>No observation data in this period. Submit observations to see trends.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ── Tab 2: Correlations ─────────────────────────────────────
with tab_correlations:
    st.markdown("### 🔗 Correlation Analysis")
    st.caption("Identifies patterns between staff, environment, and behavioural outcomes.")

    corr_days = st.slider(
        "Analysis Period (days)", min_value=7, max_value=365, value=30, key="corr_days"
    )

    with st.spinner("Running correlation analysis..."):
        corr_data = api_get("/v1/analytics/correlations", params={"days": corr_days})

    if corr_data and corr_data.get("strongest_correlations"):
        correlations = corr_data["strongest_correlations"]

        for corr in correlations:
            coeff = corr.get("correlation_coefficient", 0)

            # Colour based on strength
            if coeff >= 0.7:
                bar_colour = COLOURS["stable"]
                strength = "Strong"
            elif coeff >= 0.4:
                bar_colour = COLOURS["watch_t1"]
                strength = "Moderate"
            else:
                bar_colour = COLOURS["muted"]
                strength = "Weak"

            st.markdown(
                f"""
                <div style="background: #1e293b; border-radius: 12px; padding: 20px;
                            margin-bottom: 14px; border: 1px solid rgba(6,182,212,0.12);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="color: #e2e8f0; margin: 0;">
                            {corr.get('factor', '—').replace('_', ' ').title()}
                        </h4>
                        <span style="background:{bar_colour}22;color:{bar_colour};
                                     padding:4px 14px;border-radius:20px;font-size:0.85rem;
                                     font-weight:600;border:1px solid {bar_colour}44;">
                            {strength} ({coeff:.2f})
                        </span>
                    </div>
                    <p style="color: #94a3b8; margin-top: 10px; margin-bottom: 0;">
                        {corr.get('finding', '—')}
                    </p>
                    <div style="margin-top: 12px; background: #0f172a; border-radius: 6px;
                                height: 8px; overflow: hidden;">
                        <div style="width: {coeff * 100:.0f}%; height: 100%;
                                    background: linear-gradient(90deg, {bar_colour}, {bar_colour}88);
                                    border-radius: 6px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No correlation data available. More observations are needed for meaningful analysis.")
