"""
BehaveDrift Dashboard — Data Export
Download observation and alert data as CSV.
"""

import streamlit as st

st.set_page_config(page_title="Export | BehaveDrift", page_icon="📥", layout="wide")

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api_client import api_get, api_get_raw, require_auth

# ── Auth Guard ───────────────────────────────────────────────
require_auth()

# ── Header ───────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="margin-bottom: 4px;">📥 Data Export</h1>
    <p style="color: #94a3b8; margin-top: 0;">
        Download observation and alert data as CSV for clinical review and reporting
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ── Export Configuration ─────────────────────────────────────
st.markdown("### ⚙️ Export Settings")

col1, col2 = st.columns(2)

with col1:
    export_format = st.selectbox(
        "Format",
        ["csv"],
        format_func=lambda x: x.upper(),
        help="CSV is currently supported. PDF and FHIR Bundle are planned.",
    )

    include_alerts = st.checkbox("Include Alerts", value=True)
    include_observations = st.checkbox("Include Observations", value=False)

with col2:
    # Date range
    today = date.today()
    start_date = st.date_input(
        "Start Date",
        value=today - timedelta(days=30),
        key="export_start",
    )
    end_date = st.date_input("End Date", value=today, key="export_end")

# Optional: filter by resident
st.markdown("#### 🔍 Filter by Resident (optional)")
filter_resident = st.text_input(
    "Resident ID",
    placeholder="Leave empty to export all residents",
    help="Paste a specific resident ID to filter, or leave blank for all",
)

st.divider()

# ── Validation ───────────────────────────────────────────────
if not include_alerts and not include_observations:
    st.warning("Please select at least one data type to export (Alerts or Observations).")

if start_date and end_date and start_date > end_date:
    st.error("Start date must be before end date.")

# ── Export Preview ───────────────────────────────────────────
st.markdown("### 📋 Export Summary")

summary_items = []
summary_items.append(f"**Format:** {export_format.upper()}")
summary_items.append(f"**Date Range:** {start_date} → {end_date}")
if include_alerts:
    summary_items.append("**Include:** ✅ Alerts")
if include_observations:
    summary_items.append("**Include:** ✅ Observations")
if filter_resident:
    summary_items.append(f"**Resident Filter:** `{filter_resident}`")
else:
    summary_items.append("**Resident Filter:** All residents")

for item in summary_items:
    st.markdown(item)

st.markdown("<br>", unsafe_allow_html=True)

# ── Download ─────────────────────────────────────────────────
if st.button(
    "📥 Generate & Download Export",
    use_container_width=True,
    type="primary",
    disabled=(not include_alerts and not include_observations),
):
    params = {
        "format": export_format,
        "include_alerts": str(include_alerts).lower(),
        "include_observations": str(include_observations).lower(),
    }
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    if filter_resident:
        params["resident_id"] = filter_resident

    with st.spinner("Generating export..."):
        csv_bytes = api_get_raw("/v1/analytics/export", params=params)

    if csv_bytes:
        st.success("✅ Export generated successfully!")

        # Show preview
        csv_text = csv_bytes.decode("utf-8")
        lines = csv_text.strip().split("\n")

        with st.expander(f"👀 Preview ({len(lines)} rows)", expanded=True):
            st.code(csv_text[:3000], language="csv")
            if len(csv_text) > 3000:
                st.caption("... (truncated preview)")

        # Download button
        st.download_button(
            label="⬇️ Download CSV File",
            data=csv_bytes,
            file_name=f"behavedrift_export_{start_date}_{end_date}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.error("Export failed. Please check your filters and try again.")

st.divider()
st.caption(
    "📌 Exports contain de-identified data using internal references only. "
    "No personally identifiable information (PII) is included in standard exports."
)
