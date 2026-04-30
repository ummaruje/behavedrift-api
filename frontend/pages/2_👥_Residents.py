"""
BehaveDrift Dashboard — Resident Management
Register, list, view details, and delete residents.
"""

import streamlit as st

st.set_page_config(page_title="Residents | BehaveDrift", page_icon="👥", layout="wide")

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api_client import api_get, api_post, api_delete, api_put, require_auth

# ── Auth Guard ───────────────────────────────────────────────
require_auth()

# ── Header ───────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="margin-bottom: 4px;">👥 Resident Management</h1>
    <p style="color: #94a3b8; margin-top: 0;">
        Register new residents, view profiles, and manage baseline data
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ── Register New Resident ────────────────────────────────────
with st.expander("➕ Register New Resident", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        ref = st.text_input(
            "Internal Reference *",
            placeholder="e.g. Ward-A-Rm12",
            help="A unique identifier for the resident within your facility",
        )
        dob = st.date_input(
            "Date of Birth",
            value=None,
            min_value=date(1920, 1, 1),
            max_value=date.today(),
        )
        notes = st.text_area(
            "Notes",
            placeholder="Optional clinical notes...",
            max_chars=500,
        )

    with col2:
        risk_profile = st.selectbox("Risk Profile", ["low", "medium", "high"], index=1)
        window_days = st.slider(
            "Baseline Window (days)", min_value=14, max_value=90, value=28
        )
        diagnosis_input = st.text_input(
            "Diagnosis Codes",
            placeholder="e.g. G30.1, F00.1 (comma-separated)",
            help="ICD-10 codes, comma-separated",
        )

    if st.button("📋 Register Resident", use_container_width=True, type="primary"):
        if not ref:
            st.warning("Internal Reference is required.")
        else:
            payload = {
                "internal_reference": ref,
                "risk_profile": risk_profile,
                "baseline_window_days": window_days,
                "diagnosis_codes": [
                    c.strip() for c in diagnosis_input.split(",") if c.strip()
                ],
            }
            if dob:
                payload["date_of_birth"] = dob.isoformat()
            if notes:
                payload["notes"] = notes

            with st.spinner("Registering..."):
                result = api_post("/v1/residents", payload)
            if result:
                st.success(
                    f"✅ Resident registered! ID: `{result.get('resident_id')}`"
                )

st.divider()

# ── Resident List ────────────────────────────────────────────
st.markdown("### 📋 All Residents")

# Filters
f1, f2, f3 = st.columns([1, 1, 2])
with f1:
    filter_status = st.selectbox(
        "Baseline Status",
        [None, "initialising", "learning", "established"],
        format_func=lambda x: "All" if x is None else x.title(),
    )
with f2:
    filter_risk = st.selectbox(
        "Risk Profile",
        [None, "low", "medium", "high"],
        format_func=lambda x: "All" if x is None else x.title(),
    )
with f3:
    page = st.number_input("Page", min_value=1, value=1, step=1)

# Fetch
params = {"page": page, "page_size": 20}
if filter_status:
    params["baseline_status"] = filter_status
if filter_risk:
    params["risk_profile"] = filter_risk

with st.spinner("Loading residents..."):
    data = api_get("/v1/residents", params=params)

if not data or not data.get("residents"):
    st.info("No residents found. Register your first resident above.")
    st.stop()

residents = data["residents"]
meta = data.get("meta", {})

# Display pagination info
st.caption(
    f"Showing {len(residents)} of {meta.get('total', '?')} residents • "
    f"Page {meta.get('page', 1)}"
)

# Display residents as styled cards
for res in residents:
    rid = res.get("resident_id", "—")
    ref_name = res.get("internal_reference", "—")
    baseline = res.get("baseline_status", "—")
    risk = res.get("risk_profile", "—")
    total_obs = res.get("total_observations", 0)
    created = res.get("created_at", "—")
    last_obs = res.get("last_observation_at", "—") or "Never"

    # Baseline status colour
    status_colours = {
        "initialising": "#eab308",
        "learning": "#06b6d4",
        "established": "#22c55e",
    }
    status_colour = status_colours.get(baseline, "#94a3b8")

    with st.container():
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid rgba(6,182,212,0.15);
                        border-radius: 12px; padding: 18px 20px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0;">
                            {ref_name}
                        </span>
                        <span style="color: #64748b; font-size: 0.8rem; margin-left: 10px;">
                            {rid[:20]}…
                        </span>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <span style="background:{status_colour}22;color:{status_colour};
                                     padding:4px 12px;border-radius:20px;font-size:0.8rem;
                                     font-weight:600;border:1px solid {status_colour}44;">
                            {baseline.title()}
                        </span>
                        <span style="color:#94a3b8;font-size:0.85rem;">
                            Risk: <b>{risk.title()}</b>
                        </span>
                    </div>
                </div>
                <div style="color: #64748b; font-size: 0.85rem; margin-top: 8px;
                            display: flex; gap: 24px;">
                    <span>📊 {total_obs} observations</span>
                    <span>📅 Last: {str(last_obs)[:10] if last_obs != "Never" else "Never"}</span>
                    <span>🕐 Created: {str(created)[:10]}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Expandable detail panel
    with st.expander(f"🔍 Details: {ref_name}", expanded=False):
        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:
            st.markdown("**Resident ID:**")
            st.code(rid, language="text")
            st.markdown(f"**Diagnosis Codes:** {', '.join(res.get('diagnosis_codes', [])) or 'None'}")
            st.markdown(
                f"**Baseline Window:** {res.get('baseline_window_days', 28)} days"
            )
            st.markdown(f"**Min Observations Required:** {res.get('min_observations_required', '—')}")

        with detail_col2:
            # Fetch baseline
            baseline_data = api_get(f"/v1/residents/{rid}/baseline")
            if baseline_data:
                st.markdown("**Baseline Summary:**")
                st.json(baseline_data.get("signals", {}))
            else:
                st.info("No baseline data yet.")

        # Actions row
        act_col1, act_col2, act_col3 = st.columns(3)

        with act_col1:
            if st.button("🔄 Reset Baseline", key=f"reset_{rid}"):
                reason = "clinical_review"
                result = api_put(
                    f"/v1/residents/{rid}/baseline/reset",
                    {"reason": reason},
                )
                if result:
                    st.success("Baseline reset!")
                    st.rerun()

        with act_col3:
            if st.button("🗑️ Delete Resident", key=f"del_{rid}", type="secondary"):
                st.session_state[f"confirm_del_{rid}"] = True

            if st.session_state.get(f"confirm_del_{rid}"):
                st.warning("⚠️ This will permanently delete the resident and all their data!")
                if st.button("✅ Confirm Delete", key=f"confirm_{rid}"):
                    result = api_delete(f"/v1/residents/{rid}")
                    if result:
                        st.success(f"Deleted. Certificate: {result.get('certificate_id', '—')}")
                        st.session_state.pop(f"confirm_del_{rid}", None)
                        st.rerun()

# Pagination
if meta.get("has_next"):
    st.caption("➡️ Use the page input above to view more residents.")
