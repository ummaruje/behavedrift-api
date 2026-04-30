"""
BehaveDrift Dashboard — Main Entry Point
Streamlit multi-page app with sidebar authentication.
"""

import streamlit as st

# ── Page config (must be first Streamlit command) ────────────

st.set_page_config(
    page_title="BehaveDrift Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* ── Global tweaks ─────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Metric cards ──────────────────────────────────── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(6, 182, 212, 0.2);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
    }

    /* ── Sidebar styling ───────────────────────────────── */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(6, 182, 212, 0.15);
    }
    section[data-testid="stSidebar"] .stMarkdown h1 {
        font-size: 1.3rem;
        background: linear-gradient(135deg, #06b6d4, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ── Buttons ────────────────────────────────────────── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
    }

    /* ── Expander ───────────────────────────────────────── */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #06b6d4;
    }

    /* ── Divider ────────────────────────────────────────── */
    hr {
        border-color: rgba(6, 182, 212, 0.15) !important;
    }

    /* ── Success/Warning/Error boxes ───────────────────── */
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Sidebar ──────────────────────────────────────────────────

from api_client import check_health, register_tenant, get_token  # noqa: E402
from utils.charts import status_dot  # noqa: E402

with st.sidebar:
    st.markdown("# 🧠 BehaveDrift")
    st.caption("Behavioural Drift Detection for Dementia Care")
    st.divider()

    # ── API Connection ───────────────────────────────────
    st.markdown("### ⚡ API Connection")
    api_url = st.text_input(
        "API Base URL",
        value=st.session_state.get("api_base_url", "https://behavedrift-api.onrender.com"),
        key="api_url_input",
    )
    st.session_state["api_base_url"] = api_url

    if st.button("🔄 Check Connection", use_container_width=True):
        with st.spinner("Connecting..."):
            health = check_health()
        if health and health.get("status") == "healthy":
            st.session_state["api_connected"] = True
            st.success(f"✅ API v{health.get('version', '?')} — DB: {health.get('database')}")
        else:
            st.session_state["api_connected"] = False
            st.error("❌ API unreachable or unhealthy")

    connected = st.session_state.get("api_connected", False)
    st.markdown(status_dot(connected), unsafe_allow_html=True)

    st.divider()

    # ── Auth Status ──────────────────────────────────────
    if st.session_state.get("access_token"):
        st.markdown("### 🟢 Authenticated")
        st.caption(f"Tenant: `{st.session_state.get('tenant_id', '—')}`")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ["access_token", "tenant_id", "client_id_saved"]:
                st.session_state.pop(key, None)
            st.rerun()
    else:
        # ── Register Tenant ──────────────────────────────
        with st.expander("📋 Register New Tenant", expanded=False):
            st.caption("Create a new organisation account")
            org_name = st.text_input("Organisation Name", key="reg_org")
            email = st.text_input("Contact Email", key="reg_email")
            plan = st.selectbox("Plan", ["self_hosted", "starter", "enterprise"], key="reg_plan")

            if st.button("Register", use_container_width=True, key="reg_btn"):
                if org_name and email:
                    with st.spinner("Registering..."):
                        result = register_tenant(org_name, email, plan)
                    if result:
                        st.success("✅ Tenant registered!")
                        st.warning(
                            "⚠️ **Save these credentials NOW — they won't be shown again!**"
                        )
                        st.code(
                            f"Client ID:     {result['client_id']}\n"
                            f"Client Secret: {result['client_secret']}\n"
                            f"API Key:       {result['api_key']}",
                            language="text",
                        )
                else:
                    st.warning("Please fill in all fields.")

        # ── Login ────────────────────────────────────────
        with st.expander("🔐 Login", expanded=True):
            st.caption("Authenticate with your client credentials")
            client_id = st.text_input("Client ID", key="login_client_id")
            client_secret = st.text_input(
                "Client Secret", type="password", key="login_client_secret"
            )

            if st.button("🔑 Get Token", use_container_width=True, key="login_btn"):
                if client_id and client_secret:
                    with st.spinner("Authenticating..."):
                        result = get_token(client_id, client_secret)
                    if result:
                        st.session_state["access_token"] = result["access_token"]
                        st.session_state["client_id_saved"] = client_id
                        # Extract tenant_id from client_id (format: ten_XXXX_client)
                        tid = client_id.replace("_client", "")
                        st.session_state["tenant_id"] = tid
                        st.success(f"✅ Authenticated! Token expires in {result['expires_in']}s")
                        st.rerun()
                else:
                    st.warning("Please enter both Client ID and Client Secret.")

    st.divider()
    st.caption("Built with ❤️ for dementia care")


# ── Main Landing Page ────────────────────────────────────────

st.markdown(
    """
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="font-size: 2.8rem; font-weight: 700;
                   background: linear-gradient(135deg, #06b6d4, #8b5cf6);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   margin-bottom: 8px;">
            BehaveDrift Dashboard
        </h1>
        <p style="color: #94a3b8; font-size: 1.15rem; max-width: 600px; margin: 0 auto 40px;">
            AI-powered behavioural pattern drift detection for dementia residents.
            Monitor, analyse, and act on early signs of cognitive decline.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Feature cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 1px solid rgba(6,182,212,0.2); border-radius: 16px;
                    padding: 28px; text-align: center; min-height: 200px;">
            <div style="font-size: 2.5rem; margin-bottom: 12px;">📋</div>
            <h3 style="color: #06b6d4; margin-bottom: 8px;">Residents</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Register and manage residents with personalised baseline profiles and risk assessment.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 1px solid rgba(139,92,246,0.2); border-radius: 16px;
                    padding: 28px; text-align: center; min-height: 200px;">
            <div style="font-size: 2.5rem; margin-bottom: 12px;">🧠</div>
            <h3 style="color: #8b5cf6; margin-bottom: 8px;">Drift Detection</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Submit observations and get real-time drift evaluation with AI-powered pattern analysis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 1px solid rgba(34,197,94,0.2); border-radius: 16px;
                    padding: 28px; text-align: center; min-height: 200px;">
            <div style="font-size: 2.5rem; margin-bottom: 12px;">📊</div>
            <h3 style="color: #22c55e; margin-bottom: 8px;">Analytics</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Population-level insights, drift trends, and exportable reports for clinical review.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.info("👈 **Get started** by connecting to the API and authenticating in the sidebar.")
else:
    st.success("✅ You're authenticated! Use the pages in the sidebar to explore the dashboard.")
