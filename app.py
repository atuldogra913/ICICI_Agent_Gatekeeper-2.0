"""
AGENT GATEKEEPER: An AI Agent Permission and Risk Management System for ICICI Bank
Professional Banking Dashboard UI for MBA Academic Project Presentation.
"""

import sys
import os

# Auto-runner guard: If user runs `python app.py` directly instead of `streamlit run app.py`,
# automatically launch Streamlit web server so the website opens without errors!
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    if get_script_run_ctx() is None:
        import webbrowser
        from streamlit.web import cli as stcli
        # Open browser automatically after 1 second
        import threading
        def open_browser():
            import time
            time.sleep(1.5)
            webbrowser.open_new_tab("http://localhost:8501")
        threading.Thread(target=open_browser, daemon=True).start()
        
        sys.argv = ["streamlit", "run", __file__, "--server.port=8501"]
        sys.exit(stcli.main())
except Exception as e:
    pass

import streamlit as st
import pandas as pd
from datetime import datetime

from config import (
    STUDENT_NAME,
    ENROLMENT_NUMBER,
    PROJECT_TITLE,
    PROJECT_SUBTITLE,
    BANK_NAME,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_NAVY,
    ACTIONS,
    ACTION_VIEW_BALANCE,
    ACTION_PAY_BILL,
    ACTION_TRANSFER_MONEY,
    DECISION_ALLOW,
    DECISION_ASK_CUSTOMER,
    DECISION_BLOCK,
    STATUS_ACTIVE,
    STATUS_REVOKED
)

import storage
import decision_engine

# -------------------------------------------------------------
# Streamlit Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title=f"{PROJECT_TITLE} | {BANK_NAME}",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# High-End Corporate Banking CSS Styling
# -------------------------------------------------------------
NAVY_PRIMARY = "#0A2540"       # Deep Executive Navy
NAVY_SECONDARY = "#002D62"     # ICICI Corporate Navy
ACCENT_ORANGE = "#F58220"      # ICICI Brand Orange
ACCENT_CRIMSON = "#B3282D"     # ICICI Burgundy / Red
BG_CARD = "#FFFFFF"            # Clean Card White
TEXT_DARK = "#0F172A"          # Slate 900
TEXT_MUTED = "#64748B"         # Slate 500
BORDER_LIGHT = "#E2E8F0"       # Slate 200

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {TEXT_DARK};
    }}

    /* Global page padding */
    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1300px;
    }}

    /* Top ICICI Corporate Header Banner */
    .icici-top-banner {{
        background: linear-gradient(135deg, {NAVY_PRIMARY} 0%, {NAVY_SECONDARY} 65%, #0B3C78 100%);
        border-bottom: 4px solid {ACCENT_ORANGE};
        border-radius: 12px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(10, 37, 64, 0.2), 0 8px 10px -6px rgba(10, 37, 64, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }}
    .banner-brand-section {{
        display: flex;
        align-items: center;
        gap: 18px;
    }}
    .bank-logo-badge {{
        background: white;
        color: {ACCENT_CRIMSON};
        font-weight: 800;
        font-size: 22px;
        padding: 10px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        letter-spacing: -0.5px;
    }}
    .banner-title-text {{
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.2;
    }}
    .banner-sub-text {{
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
        font-weight: 400;
    }}
    .banner-author-badge {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(8px);
        padding: 12px 20px;
        border-radius: 10px;
        text-align: right;
        min-width: 220px;
    }}
    .banner-author-badge .sub {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: {ACCENT_ORANGE};
        font-weight: 700;
    }}
    .banner-author-badge .name {{
        font-size: 15px;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 2px;
    }}
    .banner-author-badge .enrol {{
        font-size: 12px;
        color: #CBD5E1;
        font-family: monospace;
        margin-top: 2px;
    }}

    /* Executive KPI Cards */
    .metric-card {{
        background: {BG_CARD};
        border-radius: 12px;
        border: 1px solid {BORDER_LIGHT};
        padding: 20px 22px;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
        position: relative;
        overflow: hidden;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08);
    }}
    .metric-card-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}
    .metric-label {{
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {TEXT_MUTED};
    }}
    .metric-icon {{
        font-size: 18px;
        width: 34px;
        height: 34px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .metric-value {{
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: {TEXT_DARK};
        line-height: 1.1;
    }}
    .metric-footer {{
        font-size: 12px;
        color: {TEXT_MUTED};
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 5px;
    }}

    /* Card Top Accent Bars */
    .accent-bar-navy {{ border-top: 4px solid {NAVY_SECONDARY}; }}
    .accent-bar-green {{ border-top: 4px solid #059669; }}
    .accent-bar-amber {{ border-top: 4px solid #D97706; }}
    .accent-bar-red {{ border-top: 4px solid #DC2626; }}
    .accent-bar-orange {{ border-top: 4px solid {ACCENT_ORANGE}; }}

    /* Section Subheadings */
    .section-title {{
        font-size: 16px;
        font-weight: 700;
        color: {NAVY_PRIMARY};
        letter-spacing: -0.01em;
        margin: 20px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* Form Container Card */
    .content-box {{
        background: {BG_CARD};
        border: 1px solid {BORDER_LIGHT};
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }}

    /* Verdict Display Cards */
    .verdict-box {{
        border-radius: 12px;
        padding: 24px;
        margin-top: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }}
    .verdict-allow {{
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 2px solid #16A34A;
        color: #14532D;
    }}
    .verdict-ask {{
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border: 2px solid #D97706;
        color: #78350F;
    }}
    .verdict-block {{
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 2px solid #DC2626;
        color: #7F1D1D;
    }}

    .verdict-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}
    .verdict-title {{
        font-size: 19px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.01em;
    }}
    .verdict-badge {{
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .badge-allow {{ background: #16A34A; color: white; }}
    .badge-ask {{ background: #D97706; color: white; }}
    .badge-block {{ background: #DC2626; color: white; }}

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {{
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }}

    /* Status Pill Badges */
    .status-pill-active {{
        background: #DCFCE7;
        color: #15803D;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
    }}
    .status-pill-revoked {{
        background: #FEE2E2;
        color: #B91C1C;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Ensure database directory and sample data exist
storage.ensure_data_directory()

# -------------------------------------------------------------
# Sidebar: Navigation & Student Profile
# -------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding: 10px 0 16px 0; text-align: center;">
            <div style="font-size: 30px; margin-bottom: 4px;">🏦</div>
            <div style="font-weight: 800; color: {NAVY_PRIMARY}; font-size: 19px; letter-spacing: -0.5px;">ICICI BANK</div>
            <div style="font-size: 11px; font-weight: 600; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 1px;">AI Risk & Governance Office</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()

    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px;'>Control Center</p>", unsafe_allow_html=True)
    menu = st.radio(
        "Navigation",
        [
            "📊 Executive Dashboard",
            "⚡ Request Evaluation",
            "📝 Agent Registration",
            "🛡️ Agent Revocation",
            "📜 Audit Log",
            "📚 Governance Rules (R1-R8)"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px;'>🎓 Academic Project Profile</p>", unsafe_allow_html=True)

    # Ensure any cached old placeholder or old default is cleared to user's actual enrolment number
    if st.session_state.get("enrolment_no") in [None, "", "MBA-2024-ICICI-001", "[INSERT YOUR ACTUAL ENROLMENT NUMBER]"]:
        st.session_state["enrolment_no"] = "PGD202563436"

    enrolment_val = st.text_input(
        "Enrolment Number",
        value=st.session_state.get("enrolment_no", "PGD202563436"),
        help="Official MBA Candidate Enrolment ID"
    )
    if enrolment_val and enrolment_val != "MBA-2024-ICICI-001":
        st.session_state["enrolment_no"] = enrolment_val
    else:
        st.session_state["enrolment_no"] = "PGD202563436"

    candidate_val = st.text_input(
        "Candidate Name",
        value=st.session_state.get("student_name", STUDENT_NAME)
    )
    st.session_state["student_name"] = candidate_val

    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; font-size: 12px; color: #334155; margin-top: 12px;">
            <div style="font-weight: 700; color: {NAVY_PRIMARY};">MBA Capstone Project</div>
            <div style="color: #64748B; margin-top: 2px;">Banking & Financial Technology</div>
            <hr style="border: 0; border-top: 1px solid #F1F5F9; margin: 8px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 11px;">
                <span style="color: #64748B;">Decision Engine:</span>
                <span style="font-weight: 700; color: #16A34A;">Online (R1-R8)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------------
# Top Banner: ICICI Bank Branding & Enrolment Display
# -------------------------------------------------------------
current_enrolment = st.session_state.get("enrolment_no", "PGD202563436")
if current_enrolment in ["MBA-2024-ICICI-001", "[INSERT YOUR ACTUAL ENROLMENT NUMBER]"]:
    current_enrolment = "PGD202563436"

current_candidate = st.session_state.get("student_name", STUDENT_NAME)

st.markdown(
    f"""
    <div class="icici-top-banner">
        <div class="banner-brand-section">
            <div class="bank-logo-badge">ICICI</div>
            <div>
                <h1 class="banner-title-text">{PROJECT_TITLE}</h1>
                <div class="banner-sub-text">{PROJECT_SUBTITLE}</div>
            </div>
        </div>
        <div class="banner-author-badge">
            <div class="sub">MBA Presentation Profile</div>
            <div class="name">{current_candidate}</div>
            <div class="enrol">Enrolment: {current_enrolment}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================
# PAGE 1: MAIN DASHBOARD
# =============================================================
if menu == "📊 Executive Dashboard":
    metrics = storage.get_dashboard_metrics()

    # Section 1: Agent Fleet Metrics
    st.markdown('<div class="section-title"><span>🤖</span> AI Agent Fleet Registry Summary</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(
            f"""
            <div class="metric-card accent-bar-navy">
                <div class="metric-card-top">
                    <span class="metric-label">Total Registered Agents</span>
                    <span class="metric-icon" style="background: #EFF6FF; color: {NAVY_SECONDARY};">📋</span>
                </div>
                <div class="metric-value">{metrics['total_agents']}</div>
                <div class="metric-footer">Total authorized & cataloged agents</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card accent-bar-green">
                <div class="metric-card-top">
                    <span class="metric-label">Active Agents</span>
                    <span class="metric-icon" style="background: #F0FDF4; color: #16A34A;">✅</span>
                </div>
                <div class="metric-value" style="color: #16A34A;">{metrics['active_agents']}</div>
                <div class="metric-footer">Eligible for transaction evaluation</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card accent-bar-red">
                <div class="metric-card-top">
                    <span class="metric-label">Revoked Agents</span>
                    <span class="metric-icon" style="background: #FEF2F2; color: #DC2626;">🛑</span>
                </div>
                <div class="metric-value" style="color: #DC2626;">{metrics['revoked_agents']}</div>
                <div class="metric-footer">Barred permanently under Rule R1</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Section 2: Request Decision Statistics
    st.markdown('<div class="section-title"><span>🛡️</span> Request Evaluation Telemetry & Statistics</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)

    total_req = metrics['total_requests']
    allow_pct = round((metrics['allowed_requests'] / total_req * 100), 1) if total_req > 0 else 0
    pending_pct = round((metrics['pending_requests'] / total_req * 100), 1) if total_req > 0 else 0
    block_pct = round((metrics['blocked_requests'] / total_req * 100), 1) if total_req > 0 else 0

    with r1:
        st.markdown(
            f"""
            <div class="metric-card accent-bar-navy">
                <div class="metric-card-top">
                    <span class="metric-label">Total Requests</span>
                    <span class="metric-icon" style="background: #F1F5F9; color: #334155;">⚡</span>
                </div>
                <div class="metric-value">{total_req}</div>
                <div class="metric-footer">Audited under Rule R8</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with r2:
        st.markdown(
            f"""
            <div class="metric-card accent-bar-green">
                <div class="metric-card-top">
                    <span class="metric-label">ALLOW</span>
                    <span class="metric-icon" style="background: #DCFCE7; color: #15803D;">✓</span>
                </div>
                <div class="metric-value" style="color: #15803D;">{metrics['allowed_requests']}</div>
                <div class="metric-footer">{allow_pct}% of total requests</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with r3:
        st.markdown(
            f"""
            <div class="metric-card accent-bar-amber">
                <div class="metric-card-top">
                    <span class="metric-label">ASK CUSTOMER</span>
                    <span class="metric-icon" style="background: #FEF3C7; color: #D97706;">?</span>
                </div>
                <div class="metric-value" style="color: #D97706;">{metrics['pending_requests']}</div>
                <div class="metric-footer">{pending_pct}% step-up approval required</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with r4:
        st.markdown(
            f"""
            <div class="metric-card accent-bar-red">
                <div class="metric-card-top">
                    <span class="metric-label">BLOCK</span>
                    <span class="metric-icon" style="background: #FEE2E2; color: #DC2626;">✕</span>
                </div>
                <div class="metric-value" style="color: #DC2626;">{metrics['blocked_requests']}</div>
                <div class="metric-footer">{block_pct}% prohibited requests</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Section 3: Visual Analytics & Recent Activity Table
    ch_col, tbl_col = st.columns([1, 1], gap="medium")

    with ch_col:
        st.markdown('<div class="section-title"><span>📈</span> Decision Distribution (Telemetry)</div>', unsafe_allow_html=True)
        chart_df = pd.DataFrame({
            "Verdict": ["ALLOW", "ASK CUSTOMER", "BLOCK"],
            "Count": [metrics['allowed_requests'], metrics['pending_requests'], metrics['blocked_requests']]
        })
        st.bar_chart(chart_df.set_index("Verdict"), color="#002D62", height=280)

    with tbl_col:
        st.markdown('<div class="section-title"><span>⏱️</span> Recent Audit Ledger (Rule R8)</div>', unsafe_allow_html=True)
        recent_logs = storage.load_audit_log()
        if recent_logs:
            df_display = pd.DataFrame(recent_logs).head(5)
            st.dataframe(
                df_display[["timestamp", "customer_name", "action", "amount", "decision", "rule_number"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No audit logs recorded yet.")

# =============================================================
# PAGE 2: REQUEST EVALUATION
# =============================================================
elif menu == "⚡ Request Evaluation":
    st.markdown('<div class="section-title"><span>⚡</span> Agent Request Evaluation Console</div>', unsafe_allow_html=True)
    st.caption("Receive and evaluate transaction requests dispatched by personal AI agents against Banking Rules R1 to R8.")

    agents = storage.load_agents()
    agent_options = [a["agent_name"] for a in agents]

    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown("##### 📥 Inbound Transaction Parameters")
        with st.form("eval_form"):
            input_mode = st.radio(
                "Agent Origin Mode:",
                ["Registered Agent (From Bank Registry)", "Simulate Unregistered / Unknown Agent (Test R2)"],
                horizontal=True
            )

            if input_mode == "Registered Agent (From Bank Registry)" and agent_options:
                chosen_agent = st.selectbox("AI Agent Name", agent_options)
                agent_obj = next((a for a in agents if a["agent_name"] == chosen_agent), None)
                customer_name = st.text_input(
                    "Customer Name",
                    value=agent_obj["customer_name"] if agent_obj else "",
                    help="Name of account holder"
                )
                if agent_obj:
                    perms = agent_obj.get("permissions", {})
                    st.caption(
                        f"🔒 **Customer-Granted Permissions:** "
                        f"View Balance: {'✅' if perms.get('view_balance') else '❌'} | "
                        f"Pay Bills: {'✅' if perms.get('pay_bills') else '❌'} | "
                        f"Transfer Money: {'✅' if perms.get('transfer_money') else '❌'}"
                    )
            else:
                customer_name = st.text_input("Customer Name", placeholder="e.g., Rajesh Khanna")
                chosen_agent = st.text_input("AI Agent Name", placeholder="e.g., Unofficial Web Bot")

            action = st.selectbox(
                "Requested Action",
                ACTIONS + ["Invalid Action Demo (e.g. Crypto Trade)"],
                index=0
            )

            if action == ACTION_VIEW_BALANCE:
                st.info("ℹ️ Action 'View Balance' is read-only (Amount = ₹0.00).")
                amount = 0.0
            else:
                amount = st.number_input(
                    "Transaction Amount (₹ INR)",
                    min_value=-5000.0,
                    max_value=10000000.0,
                    value=3500.0,
                    step=500.0,
                    format="%.2f",
                    help="Tip: Enter negative to test R3, <= ₹5,000 to test R5, or > ₹5,000 to test R6."
                )

            submit_eval = st.form_submit_button("🛡️ Evaluate Request Through Gatekeeper", type="primary", use_container_width=True)

    with col_out:
        st.markdown("##### 📋 Gatekeeper Decision & Rationale")
        if submit_eval:
            agent_record = storage.get_agent_by_name(chosen_agent)
            result = decision_engine.evaluate_request(
                customer_name=customer_name,
                agent_name=chosen_agent,
                action=action,
                amount=amount,
                agent_record=agent_record
            )

            # R8: Permanently record in Audit Log
            storage.log_request(
                customer_name=customer_name,
                agent_name=chosen_agent,
                action=action,
                amount=amount,
                decision=result.decision,
                rule_number=result.rule_number,
                reason=result.reason
            )

            # Render styled verdict card
            if result.decision == DECISION_ALLOW:
                st.markdown(
                    f"""
                    <div class="verdict-box verdict-allow">
                        <div class="verdict-header">
                            <span class="verdict-title">✅ PERMISSION GRANTED: ALLOW</span>
                            <span class="verdict-badge badge-allow">Rule {result.rule_number}</span>
                        </div>
                        <p style="margin: 0; font-size: 15px; line-height: 1.5; font-weight: 500;">{result.reason}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif result.decision == DECISION_ASK_CUSTOMER:
                st.markdown(
                    f"""
                    <div class="verdict-box verdict-ask">
                        <div class="verdict-header">
                            <span class="verdict-title">⚠️ STEP-UP AUTH: ASK CUSTOMER</span>
                            <span class="verdict-badge badge-ask">Rule {result.rule_number}</span>
                        </div>
                        <p style="margin: 0; font-size: 15px; line-height: 1.5; font-weight: 500;">{result.reason}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:  # BLOCK
                st.markdown(
                    f"""
                    <div class="verdict-box verdict-block">
                        <div class="verdict-header">
                            <span class="verdict-title">🛑 REQUEST PROHIBITED: BLOCK</span>
                            <span class="verdict-badge badge-block">Rule {result.rule_number}</span>
                        </div>
                        <p style="margin: 0; font-size: 15px; line-height: 1.5; font-weight: 500;">{result.reason}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; margin-top: 14px; font-size: 13px;">
                    <div style="font-weight: 700; color: {NAVY_PRIMARY}; margin-bottom: 6px;">Evaluation Audit Trail (Rule R8):</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; color: #475569;">
                        <div><b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                        <div><b>Decision:</b> {result.decision}</div>
                        <div><b>Customer:</b> {customer_name}</div>
                        <div><b>Rule Code:</b> {result.rule_number}</div>
                        <div><b>Agent:</b> {chosen_agent}</div>
                        <div><b>Amount:</b> ₹{amount:,.2f}</div>
                    </div>
                    <div style="margin-top: 8px; font-size: 11px; color: #16A34A; font-weight: 600;">✓ Permanently written to CSV and JSON audit storage.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("👈 Enter transaction parameters on the left and click 'Evaluate Request Through Gatekeeper' to trigger rule evaluation.")

# =============================================================
# PAGE 3: AGENT REGISTRATION
# =============================================================
elif menu == "📝 Agent Registration":
    st.markdown('<div class="section-title"><span>📝</span> Customer AI Agent Registration</div>', unsafe_allow_html=True)
    st.caption("Enroll a customer's personal AI agent into ICICI Bank's trusted identity registry and assign granular permissions.")

    reg_col1, reg_col2 = st.columns([1, 1], gap="large")

    with reg_col1:
        st.markdown("##### 📋 Agent Enrollment Form")
        with st.form("agent_reg_form"):
            c_name = st.text_input("Customer Full Name", placeholder="e.g., Vikram Malhotra")
            a_name = st.text_input("AI Agent Name", placeholder="e.g., Vikram FinBot")
            reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.text_input("Registration Timestamp", value=reg_time, disabled=True)
            st.text_input("Initial Operational Status", value=STATUS_ACTIVE, disabled=True)

            st.markdown("###### 🔐 Customer-Granted Permissions:")
            p_view = st.checkbox("Grant 'View Balance' Permission (Required for R4)", value=True)
            p_pay = st.checkbox("Grant 'Pay Bills' Permission (Required for R5)", value=True, help="If unchecked, bill payments will be BLOCKED under Rule R5")
            p_transfer = st.checkbox("Grant 'Transfer Money' Permission (Subject to R7)", value=True)

            reg_submit = st.form_submit_button("✅ Register AI Agent", type="primary", use_container_width=True)

            if reg_submit:
                if not c_name.strip() or not a_name.strip():
                    st.error("❌ Both Customer Name and Agent Name are required.")
                else:
                    existing = storage.get_agent_by_name(a_name)
                    if existing:
                        st.warning(f"⚠️ An agent named '{a_name}' is already registered (ID: {existing['agent_id']}).")
                    else:
                        created = storage.save_agent(
                            customer_name=c_name,
                            agent_name=a_name,
                            can_view_balance=p_view,
                            can_pay_bills=p_pay,
                            can_transfer_money=p_transfer
                        )
                        st.success(f"🎉 Agent successfully enrolled with ID: **{created['agent_id']}**")

    with reg_col2:
        st.markdown("##### 🗃️ Current Registered Fleet & Status")
        agents_list = storage.load_agents()
        if agents_list:
            rows = []
            for a in agents_list:
                p = a.get("permissions", {})
                rows.append({
                    "Agent ID": a.get("agent_id"),
                    "Customer": a.get("customer_name"),
                    "Agent Name": a.get("agent_name"),
                    "Status": a.get("status"),
                    "Registered On": a.get("registration_date"),
                    "Revoked On": a.get("revoked_at") if a.get("revoked_at") else "—",
                    "Bill Pay Perm": "Yes" if p.get("pay_bills") else "No"
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No agents registered yet.")

# =============================================================
# PAGE 4: AGENT REVOCATION
# =============================================================
elif menu == "🛡️ Agent Revocation":
    st.markdown('<div class="section-title"><span>🛡️</span> Administrative Agent Revocation Console</div>', unsafe_allow_html=True)
    st.caption("Terminate an AI agent's operational permissions permanently. Under Rule R1, revoked agents are blocked from all future requests.")

    agents = storage.load_agents()
    active_agents = [a for a in agents if a["status"] == STATUS_ACTIVE]

    rev_col1, rev_col2 = st.columns([1, 1], gap="large")

    with rev_col1:
        st.markdown("##### 🚨 Revoke Active Agent")
        if active_agents:
            with st.form("revoke_form"):
                agent_dict = {f"{a['agent_id']} — {a['agent_name']} (Customer: {a['customer_name']})": a['agent_id'] for a in active_agents}
                selected_label = st.selectbox("Select Active Agent to Revoke", list(agent_dict.keys()), help="Every active agent is listed here with immediate revocation capability")
                reason = st.text_area(
                    "Revocation Audit Reason",
                    value="Administrative security review: Suspicious frequency detected by risk team"
                )

                st.warning("⚠️ Warning: Revocation is irreversible. Under Rule R1, all subsequent requests from this agent will be permanently BLOCKED.")
                revoke_submit = st.form_submit_button("🛑 Permanently Revoke Agent", type="primary", use_container_width=True)

                if revoke_submit:
                    target_id = agent_dict[selected_label]
                    success = storage.revoke_agent(target_id, reason)
                    if success:
                        st.success(f"✅ Agent {target_id} has been permanently REVOKED and logged to the security audit trail.")
                        st.rerun()
                    else:
                        st.error("Revocation failed. Please try again.")
        else:
            st.info("No active agents available for revocation (all registered agents are currently revoked).")

    with rev_col2:
        st.markdown("##### 📜 Revoked Agents Registry (Rule R1 Target)")
        revoked_agents = [a for a in agents if a["status"] == STATUS_REVOKED]
        if revoked_agents:
            df_revoked = pd.DataFrame(revoked_agents)
            st.dataframe(
                df_revoked[["agent_id", "customer_name", "agent_name", "status", "revoked_at", "revocation_reason"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("No agents are currently revoked.")

    # Full Fleet Status Table showing all agents, status, and revocation timestamps
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>📋</span> Comprehensive Agent Fleet Status & Revocation Audit</div>', unsafe_allow_html=True)
    if agents:
        fleet_data = []
        for a in agents:
            fleet_data.append({
                "Agent ID": a.get("agent_id"),
                "Customer Name": a.get("customer_name"),
                "Agent Name": a.get("agent_name"),
                "Current Status": a.get("status"),
                "Registration Timestamp": a.get("registration_date"),
                "Revocation Timestamp": a.get("revoked_at") if a.get("revoked_at") else "—",
                "Revocation Reason": a.get("revocation_reason") if a.get("revocation_reason") else "—"
            })
        st.dataframe(pd.DataFrame(fleet_data), use_container_width=True, hide_index=True)

# =============================================================
# PAGE 5: AUDIT LOG
# =============================================================
elif menu == "📜 Audit Log":
    st.markdown('<div class="section-title"><span>📜</span> Compliance & Security Audit Ledger (Rule R8)</div>', unsafe_allow_html=True)
    st.caption("Permanent, tamper-evident audit record of every request, agent registration, revocation, and gatekeeper decision. Data persists permanently across application sessions.")

    logs = storage.load_audit_log()

    if logs:
        df_logs = pd.DataFrame(logs)

        # Quick summary metrics for audit events
        tot_ev = len(df_logs)
        allow_ev = sum(1 for e in logs if e.get("decision") in [DECISION_ALLOW, "REGISTERED"])
        ask_ev = sum(1 for e in logs if e.get("decision") == DECISION_ASK_CUSTOMER)
        block_ev = sum(1 for e in logs if e.get("decision") in [DECISION_BLOCK, "REVOKED"])

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Events Audited", tot_ev)
        with m2:
            st.metric("Allowed / Registered", allow_ev)
        with m3:
            st.metric("Step-Up (Ask Customer)", ask_ev)
        with m4:
            st.metric("Blocked / Revoked", block_ev)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Comprehensive Filters
        f1, f2, f3 = st.columns(3)
        with f1:
            filter_decision = st.multiselect("Filter by Decision", [DECISION_ALLOW, DECISION_ASK_CUSTOMER, DECISION_BLOCK], default=[])
        with f2:
            available_actions = sorted(list(set(df_logs["action"].dropna().unique())))
            filter_action = st.multiselect("Filter by Requested Action", available_actions, default=[])
        with f3:
            search_text = st.text_input("Search Customer / Agent / Keyword", "")

        filtered = df_logs.copy()
        if filter_decision:
            filtered = filtered[filtered["decision"].isin(filter_decision)]
        if filter_action:
            filtered = filtered[filtered["action"].isin(filter_action)]
        if search_text:
            q = search_text.lower()
            filtered = filtered[
                filtered["customer_name"].str.lower().str.contains(q) |
                filtered["agent_name"].str.lower().str.contains(q) |
                filtered["explanation"].str.lower().str.contains(q)
            ]

        # Format readable display dataframe with the 8 required columns
        display_df = filtered.copy()
        display_df["formatted_amount"] = display_df["amount"].apply(lambda x: f"₹{x:,.2f}" if float(x) > 0 else "—")

        # Map to user-friendly column names
        readable_table = display_df[[
            "timestamp",
            "customer_name",
            "agent_name",
            "action",
            "formatted_amount",
            "decision",
            "rule_number",
            "explanation"
        ]].rename(columns={
            "timestamp": "Date & Time",
            "customer_name": "Customer Name",
            "agent_name": "Agent Name",
            "action": "Requested Action",
            "formatted_amount": "Transaction Amount",
            "decision": "Decision",
            "rule_number": "Rule #",
            "explanation": "Explanation"
        })

        st.dataframe(
            readable_table,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Displaying **{len(readable_table)}** of **{len(df_logs)}** audit events. Records are permanently stored in `data/audit_log.csv` and `data/audit_log.json`.")

        # Download buttons
        d1, d2 = st.columns(2)
        with d1:
            csv_bytes = filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Audit Log (CSV)",
                data=csv_bytes,
                file_name=f"ICICI_Gatekeeper_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with d2:
            json_bytes = filtered.to_json(orient="records", indent=4)
            st.download_button(
                "📥 Export Audit Log (JSON)",
                data=json_bytes,
                file_name=f"ICICI_Gatekeeper_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("The security audit log is currently empty.")

# =============================================================
# PAGE 6: GOVERNANCE RULES MATRIX (R1-R8)
# =============================================================
elif menu == "📚 Governance Rules (R1-R8)":
    st.markdown('<div class="section-title"><span>📚</span> Banking Risk Rules Matrix (R1 through R8)</div>', unsafe_allow_html=True)
    st.caption("Official specification of the 8 business rules implemented in the ICICI Agent Gatekeeper decision engine.")

    rules_table = [
        {
            "Rule Code": "R1",
            "Rule Name": "Revocation Check",
            "Condition / Trigger": "Agent status is REVOKED (checked first)",
            "Decision": "BLOCK",
            "Banking Rationale": "Revocation is irreversible. Prevents compromised agents from performing any transaction."
        },
        {
            "Rule Code": "R2",
            "Rule Name": "Registration & Ownership",
            "Condition / Trigger": "Agent unregistered OR customer ownership mismatch",
            "Decision": "BLOCK",
            "Banking Rationale": "Guarantees untrusted agents and cross-customer impersonations are rejected immediately."
        },
        {
            "Rule Code": "R3",
            "Rule Name": "Action & Amount Validity",
            "Condition / Trigger": "Invalid action name OR negative / zero transaction amount",
            "Decision": "BLOCK",
            "Banking Rationale": "Rejects malformed commands and negative balances before reaching core banking systems."
        },
        {
            "Rule Code": "R4",
            "Rule Name": "View Balance",
            "Condition / Trigger": "Active agent requests 'View Balance'",
            "Decision": "ALLOW",
            "Banking Rationale": "Zero-risk read-only query that does not mutate account funds or move balances."
        },
        {
            "Rule Code": "R5",
            "Rule Name": "Autonomous Bill Payment",
            "Condition / Trigger": "Agent has bill-payment permission AND amount <= ₹5,000",
            "Decision": "ALLOW",
            "Banking Rationale": "Frictionless automated convenience for recurring utility payments within a safe threshold."
        },
        {
            "Rule Code": "R6",
            "Rule Name": "High-Value Bill Payment",
            "Condition / Trigger": "Bill payment requested above ₹5,000",
            "Decision": "ASK CUSTOMER",
            "Banking Rationale": "Exceeds autonomous micro-threshold. Dispatches prompt to customer for explicit confirmation."
        },
        {
            "Rule Code": "R7",
            "Rule Name": "Transfer Money (All Amounts)",
            "Condition / Trigger": "Every 'Transfer Money' request, regardless of amount",
            "Decision": "ASK CUSTOMER",
            "Banking Rationale": "Direct funds transfer to external parties carries high risk and always mandates human-in-the-loop authorization."
        },
        {
            "Rule Code": "R8",
            "Rule Name": "Audit Logging",
            "Condition / Trigger": "Every evaluated request and decision",
            "Decision": "PERMANENTLY LOGGED",
            "Banking Rationale": "Logs timestamp, customer, agent, action, amount, decision, reason, and rule number in CSV and JSON."
        }
    ]

    st.table(pd.DataFrame(rules_table))

    st.markdown(
        """
        ---
        ##### 💡 MBA Project Defense Summary:
        - **3-Tier Decision Taxonomy:** `ALLOW` (Frictionless low risk), `ASK CUSTOMER` (Human-in-the-loop 2FA), and `BLOCK` (Security firewall).
        - **Regulatory Alignment:** Adheres to RBI guidelines for algorithmic delegation and multi-factor authentication in retail banking.
        - **Audit Immutability:** Fully conforms to forensic compliance requirements with persistent CSV/JSON ledgers.
        """
    )
