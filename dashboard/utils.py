"""
Shared UI, Data utilities, and AI Copilot sidebar for the Streamlit Civic Analytics Dashboard.
"""

import sys
from pathlib import Path

# Add project root to sys.path dynamically for Streamlit Cloud
FILE_DIR = Path(__file__).resolve().parent
ROOT_DIR = FILE_DIR.parent
for p in [ROOT_DIR, FILE_DIR]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st
import pandas as pd
from sqlalchemy import text
from src.core.config import FEATURE_CSV_PATH
from src.core.db import get_engine
from src.analytics.ai_copilot import CivicAICopilot

CUSTOM_CSS = """
<style>
    /* Metric Card Styling */
    .metric-box {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px 20px;
        color: #f8fafc;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #cbd5e1;
        margin-top: 4px;
    }
    /* AI Box Styling */
    .ai-copilot-box {
        background: linear-gradient(135deg, #0f172a, #1e1b4b);
        border: 1px solid #6366f1;
        border-radius: 8px;
        padding: 12px 14px;
        color: #e0e7ff;
        margin-bottom: 12px;
        font-size: 0.85rem;
    }
</style>
"""


@st.cache_data
def load_data() -> pd.DataFrame:
    """Loads and caches the feature-engineered civic dataset."""
    df = pd.read_csv(FEATURE_CSV_PATH)
    df["Complaint_Date"] = pd.to_datetime(df["Complaint_Date"])
    df["Resolution_Date"] = pd.to_datetime(df["Resolution_Date"])
    return df


def apply_custom_css():
    """Injects custom CSS styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, subtitle: str = ""):
    """Renders a styled KPI box."""
    html = f"""
    <div class="metric-box">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_ai_copilot_sidebar(current_page: str = "Executive Overview"):
    """
    Renders an embedded, persistent AI Assistant in the sidebar of every page.
    Explains charts, answers questions in English/Hinglish, and gives placement tips.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Civic AI Copilot (App Guide)")
    st.sidebar.caption("Ask anything about this page, graphs, metrics, or ML models:")

    # Quick One-Click Action Buttons
    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        if st.button("📖 Explain Page", key=f"btn_exp_{current_page}", use_container_width=True):
            st.session_state[f"ai_reply_{current_page}"] = CivicAICopilot.get_page_explanation(current_page)
    with col_b:
        if st.button("💼 Interview Tips", key=f"btn_int_{current_page}", use_container_width=True):
            st.session_state[f"ai_reply_{current_page}"] = CivicAICopilot.answer_query("interview placement bolna pitch", current_page)

    # Interactive Query Input Box
    user_q = st.sidebar.text_input(
        "Ask AI Assistant (Hinglish/English):",
        placeholder="e.g. Is graph ka kya matlab hai?",
        key=f"ai_query_{current_page}",
    )

    if user_q:
        answer = CivicAICopilot.answer_query(user_q, current_page)
        st.session_state[f"ai_reply_{current_page}"] = answer

    # Display Answer if available
    reply_key = f"ai_reply_{current_page}"
    if reply_key in st.session_state and st.session_state[reply_key]:
        with st.sidebar.expander("💡 AI Explanation & Insights", expanded=True):
            st.markdown(st.session_state[reply_key])
            if st.button("✖️ Clear", key=f"clear_{current_page}"):
                st.session_state[reply_key] = ""
                st.rerun()


def get_filtered_data(df: pd.DataFrame) -> pd.DataFrame:
    """Renders sidebar global filters and returns filtered dataframe."""
    st.sidebar.header("🔍 Global Filters")

    # District filter
    districts = ["All"] + sorted(df["District"].dropna().unique().tolist())
    sel_district = st.sidebar.selectbox("District", districts)

    # Department filter
    departments = ["All"] + sorted(df["Department"].dropna().unique().tolist())
    sel_dept = st.sidebar.selectbox("Department", departments)

    # Priority filter
    priorities = ["All"] + sorted(df["Priority"].dropna().unique().tolist())
    sel_priority = st.sidebar.selectbox("Priority", priorities)

    # Status filter
    statuses = ["All"] + sorted(df["Status"].dropna().unique().tolist())
    sel_status = st.sidebar.selectbox("Status", statuses)

    filtered_df = df.copy()
    if sel_district != "All":
        filtered_df = filtered_df[filtered_df["District"] == sel_district]
    if sel_dept != "All":
        filtered_df = filtered_df[filtered_df["Department"] == sel_dept]
    if sel_priority != "All":
        filtered_df = filtered_df[filtered_df["Priority"] == sel_priority]
    if sel_status != "All":
        filtered_df = filtered_df[filtered_df["Status"] == sel_status]

    st.sidebar.markdown(f"**Filtered Tickets:** `{len(filtered_df):,}` / `{len(df):,}`")
    return filtered_df
