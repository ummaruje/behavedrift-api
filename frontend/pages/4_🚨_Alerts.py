"""
BehaveDrift Dashboard — Alert Management
View, filter, acknowledge, and dismiss drift alerts.
"""

import streamlit as st

st.set_page_config(page_title="Alerts | BehaveDrift", page_icon="🚨", layout="wide")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api_client import api_get, api_post, api_delete, require_auth
from utils.charts import tier_badge, TIER_COLOURS, COLOURS

# ── Auth Guard ───────────────────────────────────────────────
require_auth()

# ── Header ───────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="margin-bottom: 4px;">🚨 Alert Centre</h1>
    <p style="color: #94a3b8; margin-top: 0;">
        Monitor drift alerts, acknowledge clinical actions, and dismiss resolved issues
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ── Filters ──────────────────────────────────────────────────
f1, f2, f3 = st.columns([1, 1, 2])
with f1:
    tier_filter = st.selectbox(
        "Tier",
        [None, "T1", "T2", "T3", "T4"],
        format_func=lambda x: "All Tiers" if x is None else f"{x} — {{'T1':'Watch','T2':'Concern','T3':'Alert','T4':'Critical'}.get(x, x)}",
    )
with f2:
    ack_filter = st.selectbox(
        "Acknowledged",
        [None, False, True],
        format_func=lambda x: "All" if x is None else ("Yes" if x else "No"),
    )
with f3:
    page = st.number_input("Page", min_value=1, value=1, step=1, key="alert_page")

# ── Fetch Alerts ─────────────────────────────────────────────
params = {"page": page, "page_size": 15}
if tier_filter:
    params["tier"] = tier_filter
if ack_filter is not None:
    params["acknowledged"] = str(ack_filter).lower()

with st.spinner("Loading alerts..."):
    data = api_get("/v1/alerts", params=params)

if not data or not data.get("alerts"):
    st.markdown(
        """
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 3rem; margin-bottom: 16px;">🎉</div>
            <h3 style="color: #22c55e;">All Clear</h3>
            <p style="color: #94a3b8;">No active alerts at this time. All residents are stable.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

alerts = data["alerts"]
meta = data.get("meta", {})

st.caption(
    f"Showing {len(alerts)} of {meta.get('total', '?')} alerts • Page {meta.get('page', 1)}"
)

# ── Alert Cards ──────────────────────────────────────────────
for alert in alerts:
    aid = alert.get("alert_id", "—")
    tier = alert.get("tier", "—")
    tier_label = alert.get("tier_label", "—")
    rid = alert.get("resident_id", "—")
    drift_score = alert.get("drift_score", 0)
    confidence = alert.get("confidence_score", 0)
    generated = alert.get("generated_at", "—")
    explanation = alert.get("explanation", {})
    border_colour = TIER_COLOURS.get(tier, COLOURS["muted"])

    st.markdown(
        f"""
        <div style="background: #1e293b; border-left: 5px solid {border_colour};
                    border-radius: 10px; padding: 18px 20px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;
                        flex-wrap: wrap; gap: 10px;">
                <div>
                    {tier_badge(tier)}
                    <span style="color: #64748b; font-size: 0.8rem; margin-left: 12px;">
                        {str(generated)[:19]}
                    </span>
                </div>
                <div style="display: flex; gap: 20px; color: #94a3b8; font-size: 0.9rem;">
                    <span>Drift: <b style="color:#e2e8f0;">{drift_score:.3f}</b></span>
                    <span>Confidence: <b style="color:#e2e8f0;">{confidence:.1%}</b></span>
                </div>
            </div>
            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 10px;">
                Resident: <code style="color:#06b6d4;">{rid[:20]}…</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(f"🔍 Details & Actions — {aid[:16]}…", expanded=False):
        # Explanation
        if explanation:
            summary = explanation.get("summary", "")
            if summary:
                st.markdown(f"**Summary:** {summary}")

            exp_signals = explanation.get("signals", [])
            if exp_signals:
                st.markdown("**Flagged Signals:**")
                for sig in exp_signals:
                    sig_name = sig.get("signal", "?")
                    z_score = sig.get("z_score", "—")
                    current = sig.get("current_value", "—")
                    baseline_mean = sig.get("baseline_mean", "—")
                    st.markdown(
                        f"- **{sig_name}**: current=`{current}`, "
                        f"baseline_mean=`{baseline_mean}`, z-score=`{z_score}`"
                    )

            clinical = explanation.get("clinical_correlation")
            if clinical:
                st.info(f"🧬 Clinical Correlation: {clinical}")

        st.markdown(f"**Alert ID:** `{aid}`")

        # ── Actions ──────────────────────────────────────
        act1, act2 = st.columns(2)

        with act1:
            st.markdown("##### ✅ Acknowledge")
            action_taken = st.text_input(
                "Action taken",
                placeholder="e.g. Reviewed with GP, medication adjusted",
                key=f"ack_action_{aid}",
            )
            actioned_by = st.text_input(
                "Actioned by", placeholder="e.g. Nurse Sarah", key=f"ack_by_{aid}"
            )
            if st.button("Acknowledge Alert", key=f"ack_btn_{aid}", type="primary"):
                if action_taken:
                    payload = {"action_taken": action_taken}
                    if actioned_by:
                        payload["actioned_by"] = actioned_by
                    result = api_post(f"/v1/alerts/{aid}/acknowledge", payload)
                    if result:
                        st.success("✅ Alert acknowledged!")
                        st.rerun()
                else:
                    st.warning("Please describe the action taken.")

        with act2:
            st.markdown("##### 🗑️ Dismiss")
            dismiss_reason = st.text_input(
                "Reason for dismissal",
                placeholder="e.g. False positive — resident was on holiday",
                key=f"dismiss_reason_{aid}",
            )
            dismissed_by = st.text_input(
                "Dismissed by", placeholder="e.g. Dr. Smith", key=f"dismiss_by_{aid}"
            )
            if st.button("Dismiss Alert", key=f"dismiss_btn_{aid}", type="secondary"):
                if dismiss_reason:
                    payload = {"reason": dismiss_reason}
                    if dismissed_by:
                        payload["dismissed_by"] = dismissed_by
                    result = api_delete(f"/v1/alerts/{aid}", json_data=payload)
                    if result:
                        st.success("🗑️ Alert dismissed.")
                        st.rerun()
                else:
                    st.warning("Please provide a reason for dismissal.")

# Pagination
if meta.get("has_next"):
    st.caption("➡️ Use the page input above to see more alerts.")
