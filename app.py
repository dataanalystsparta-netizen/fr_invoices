# ==========================================================
# ZOHO ACCOUNTS RECEIVABLE DASHBOARD
# COMPLETE FIXED SCRIPT
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests

from datetime import date
from html import escape as html_escape


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="FastRanking Dashboard",
    page_icon="💰",
    layout="wide"
)


# ==========================================================
# LOGIN / AUTHENTICATION
# ==========================================================

def check_login():

    # ------------------------------------------------------
    # Already logged in
    # ------------------------------------------------------

    if st.session_state.get("authenticated", False):
        return True

    # ------------------------------------------------------
    # Login Page
    # ------------------------------------------------------

    st.markdown(
        """
        <style>

        .stApp {
            background: radial-gradient(circle at top, #eef4ff 0%, #f6f8fb 45%, #eef2f7 100%);
        }

        .login-container {
            max-width: 430px;
            margin: 70px auto 30px auto;
            padding: 34px;
            border: 1px solid #dfe6ef;
            border-radius: 22px;
            background: rgba(255,255,255,0.96);
            box-shadow: 0 22px 60px rgba(15,23,42,0.12);
        }

        .login-title {
            text-align: center;
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 8px;
            color: #0f172a;
        }

        .login-subtitle {
            text-align: center;
            color: #64748b;
            margin-bottom: 26px;
            font-size: 14px;
        }

        .login-brand {
            width: 58px;
            height: 58px;
            margin: 0 auto 16px auto;
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            background: linear-gradient(135deg, #0f172a, #0f766e);
            color: #ffffff;
            box-shadow: 0 12px 28px rgba(15,118,110,0.20);
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-container">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-brand">💰</div>'
        '<div class="login-title">FastRanking</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">FastRanking Payments Dashboard</div>',
        unsafe_allow_html=True
    )

    email = st.text_input(
        "Email",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    login_clicked = st.button(
        "Login",
        type="primary",
        width="stretch"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # Validate Login
    # ------------------------------------------------------

    if login_clicked:

        email = email.strip().lower()

        users = st.secrets.get(
            "users",
            {}
        )

        if (
            email in users
            and password == users[email].get(
                "password",
                ""
            )
        ):

            st.session_state.authenticated = True
            st.session_state.logged_in_email = email

            st.session_state.view = users[email].get(
                "view",
                "financial"
            )

            st.rerun()

        else:

            st.error(
                "Invalid email or password."
            )

    return False


# ==========================================================
# REQUIRE LOGIN
# ==========================================================

if not check_login():
    st.stop()


# ==========================================================
# USER VIEW
# ==========================================================

USER_VIEW = st.session_state.get(
    "view",
    "financial"
)

IS_FINANCIAL = USER_VIEW == "financial"
IS_PERCENTAGE = USER_VIEW == "percentage"

view_label = "Financial View" if IS_FINANCIAL else "Percentage View"
logged_email = html_escape(
    str(st.session_state.get("logged_in_email", "")).strip()
)


# ==========================================================
# LOGOUT
# ==========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark">💰</div>
            <div>
                <div class="sidebar-brand-title">FastRanking</div>
                <div class="sidebar-brand-sub">Payments Dashboard</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="sidebar-user">
            <div class="sidebar-user-label">Signed in as</div>
            <div class="sidebar-user-email">{html_escape(str(st.session_state.get('logged_in_email', '')))}</div>
            <div class="sidebar-view-chip">{html_escape(view_label)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.12em;font-weight:800;margin:0 0 8px 2px;">Navigate</div>
        <div style="font-size:12px;color:#cbd5e1;line-height:1.9;padding:0 2px 14px 2px;">
            Overview<br>Customer Details<br>Payments Received
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🚪 Logout",
        width="stretch"
    ):

        st.session_state.authenticated = False

        st.session_state.pop(
            "logged_in_email",
            None
        )

        st.rerun()


# ==========================================================
# DASHBOARD SHELL / VISUAL SYSTEM
# ==========================================================

st.markdown(
    f"""
    <style>

    :root {{
        --fr-ink: #0f172a;
        --fr-muted: #64748b;
        --fr-border: #e2e8f0;
        --fr-white: #ffffff;
        --fr-teal: #0f766e;
    }}

    .stApp {{
        background: #f6f8fb;
        color: var(--fr-ink);
    }}

    .block-container {{
        max-width: 1540px;
        padding-top: 1.45rem;
        padding-bottom: 4rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }}

    [data-testid="stSidebar"] {{
        background: #0b1220;
        border-right: 1px solid rgba(255,255,255,0.06);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.25rem;
    }}

    [data-testid="stSidebar"] * {{
        color: #e2e8f0;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.06);
        color: #f8fafc;
        font-weight: 700;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        border-color: rgba(255,255,255,0.20);
        background: rgba(255,255,255,0.10);
    }}

    .sidebar-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 2px 18px 2px;
    }}

    .sidebar-brand-mark {{
        width: 42px;
        height: 42px;
        flex: 0 0 42px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 21px;
        background: linear-gradient(135deg, #0f766e, #14b8a6);
        box-shadow: 0 10px 24px rgba(20,184,166,0.20);
    }}

    .sidebar-brand-title {{
        font-size: 16px;
        line-height: 1.1;
        font-weight: 800;
        color: #f8fafc;
    }}

    .sidebar-brand-sub {{
        font-size: 11px;
        color: #94a3b8;
        margin-top: 3px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}

    .sidebar-user {{
        margin: 6px 0 18px 0;
        padding: 13px 14px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.045);
        border-radius: 14px;
    }}

    .sidebar-user-label {{
        font-size: 10px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }}

    .sidebar-user-email {{
        font-size: 12px;
        color: #f8fafc;
        margin-top: 4px;
        word-break: break-word;
    }}

    .sidebar-view-chip {{
        display: inline-flex;
        margin-top: 9px;
        padding: 4px 8px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 800;
        color: #ccfbf1;
        background: rgba(15,118,110,0.28);
        border: 1px solid rgba(20,184,166,0.28);
    }}

    .hero {{
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        padding: 28px 30px 26px 30px;
        margin-bottom: 16px;
        background: linear-gradient(135deg, #0f172a 0%, #172554 55%, #0f766e 100%);
        box-shadow: 0 18px 50px rgba(15,23,42,0.16);
    }}

    .hero::after {{
        content: "";
        position: absolute;
        width: 300px;
        height: 300px;
        right: -90px;
        top: -130px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(45,212,191,0.28) 0%, rgba(45,212,191,0) 70%);
        pointer-events: none;
    }}

    .hero-eyebrow {{
        position: relative;
        z-index: 1;
        color: #99f6e4;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }}

    .hero-title {{
        position: relative;
        z-index: 1;
        color: #ffffff;
        font-size: clamp(28px, 3vw, 40px);
        font-weight: 850;
        letter-spacing: -0.04em;
        line-height: 1.05;
    }}

    .hero-subtitle {{
        position: relative;
        z-index: 1;
        color: #cbd5e1;
        font-size: 14px;
        margin-top: 8px;
        max-width: 760px;
    }}

    .hero-meta {{
        position: relative;
        z-index: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 17px;
    }}

    .hero-chip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 11px;
        font-weight: 750;
        color: #e2e8f0;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        backdrop-filter: blur(8px);
    }}

    .quick-nav {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 0 0 24px 2px;
    }}

    .quick-nav a {{
        display: inline-flex;
        align-items: center;
        text-decoration: none;
        color: #475569;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 999px;
        padding: 7px 11px;
        font-size: 11px;
        font-weight: 750;
        box-shadow: 0 3px 12px rgba(15,23,42,0.04);
    }}

    .quick-nav a:hover {{
        color: #0f766e;
        border-color: #99f6e4;
        background: #f0fdfa;
    }}

    .section-heading {{
        scroll-margin-top: 24px;
        margin-top: 10px;
        margin-bottom: 16px;
    }}

    .section-kicker {{
        color: #0f766e;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}

    .section-title {{
        color: #0f172a;
        font-size: 23px;
        line-height: 1.15;
        font-weight: 820;
        letter-spacing: -0.025em;
    }}

    .section-subtitle {{
        color: #64748b;
        font-size: 12px;
        margin-top: 5px;
        max-width: 860px;
    }}

    .subsection-heading {{
        margin-top: 7px;
        margin-bottom: 11px;
        color: #1e293b;
        font-size: 16px;
        font-weight: 800;
        letter-spacing: -0.015em;
    }}

    .section-rule {{
        height: 1px;
        margin: 25px 0 27px 0;
        background: linear-gradient(90deg, transparent, #dbe3ec 18%, #dbe3ec 82%, transparent);
    }}

    .filter-note {{
        color: #64748b;
        font-size: 11px;
        margin-top: -4px;
        margin-bottom: 9px;
    }}

    .filter-summary {{
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin: 2px 0 18px 0;
    }}

    .filter-pill {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 6px 9px;
        border-radius: 999px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        color: #475569;
        font-size: 10px;
        font-weight: 750;
        box-shadow: 0 2px 8px rgba(15,23,42,0.03);
    }}

    .kpi-grid-label {{
        margin: 2px 0 8px 0;
        color: #94a3b8;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }}

    .kpi-card {{
        position: relative;
        overflow: hidden;
        min-height: 124px;
        padding: 17px 16px 15px 16px;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        background: #ffffff;
        box-shadow: 0 7px 24px rgba(15,23,42,0.055);
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}

    .kpi-card::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #0f766e, #14b8a6);
    }}

    .kpi-title {{
        font-size: 12px;
        color: #64748b;
        margin-bottom: 8px;
        font-weight: 750;
        line-height: 1.2;
    }}

    .kpi-value {{
        font-size: clamp(20px, 2vw, 28px);
        font-weight: 850;
        color: #0f172a;
        letter-spacing: -0.035em;
        line-height: 1.05;
    }}

    .kpi-percentage {{
        font-size: 11px;
        color: #0f766e;
        font-weight: 800;
        margin-top: 7px;
        line-height: 1;
    }}

    .info-card {{
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        background: #ffffff;
        padding: 17px 18px;
        box-shadow: 0 7px 24px rgba(15,23,42,0.045);
        height: 100%;
        box-sizing: border-box;
    }}

    .info-card-label {{
        color: #94a3b8;
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        font-weight: 800;
        margin-bottom: 4px;
    }}

    .info-card-value {{
        color: #1e293b;
        font-size: 12px;
        font-weight: 650;
        line-height: 1.45;
        word-break: break-word;
    }}

    .status-pill {{
        display: inline-flex;
        align-items: center;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 850;
        margin-top: 3px;
    }}

    .status-active {{ background: #dcfce7; color: #166534; }}
    .status-inactive {{ background: #fee2e2; color: #991b1b; }}
    .status-neutral {{ background: #f1f5f9; color: #475569; }}

    .table-caption {{
        display: flex;
        justify-content: space-between;
        gap: 10px;
        flex-wrap: wrap;
        align-items: center;
        margin: 3px 0 9px 1px;
    }}

    .table-caption-title {{
        color: #334155;
        font-size: 12px;
        font-weight: 800;
    }}

    .table-caption-note {{
        color: #94a3b8;
        font-size: 10px;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 18px rgba(15,23,42,0.035);
        background: #ffffff;
    }}

    div[data-testid="stDataFrame"] [role="columnheader"] {{
        background: #f8fafc;
    }}

    [data-testid="stMetric"] {{
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        background: #ffffff;
        padding: 15px 16px;
        box-shadow: 0 6px 18px rgba(15,23,42,0.045);
    }}

    [data-testid="stMetricLabel"] {{
        color: #64748b;
        font-size: 11px;
        font-weight: 750;
    }}

    [data-testid="stMetricValue"] {{
        color: #0f172a;
        font-weight: 850;
    }}

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {{
        border-radius: 11px;
    }}

    .stDateInput label, .stSelectbox label, .stTextInput label {{
        color: #475569 !important;
        font-size: 11px !important;
        font-weight: 750 !important;
    }}

    .stCheckbox label {{
        color: #475569 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
    }}

    .stButton > button {{
        border-radius: 11px;
        font-weight: 750;
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        background: #ffffff;
        box-shadow: 0 5px 18px rgba(15,23,42,0.035);
    }}

    .footer-note {{
        text-align: center;
        color: #94a3b8;
        font-size: 10px;
        padding-top: 18px;
    }}

    @media (max-width: 900px) {{
        .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
        .hero {{ padding: 23px 21px; border-radius: 20px; }}
    }}

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-eyebrow">FastRanking · Accounts Receivable</div>
        <div class="hero-title">Payments &amp; Collections</div>
        <div class="hero-subtitle">
            A focused financial view of invoices, cash collection, outstanding balances,
            customer history and payments received.
        </div>
        <div class="hero-meta">
            <span class="hero-chip">◉ {html_escape(view_label)}</span>
            <span class="hero-chip">◷ Updated {pd.Timestamp.today().strftime('%d %b %Y')}</span>
            <span class="hero-chip">👤 {logged_email or 'Authenticated user'}</span>
        </div>
    </div>

    <div class="quick-nav">
        <a href="#dashboard-overview">01 · Overview</a>
        <a href="#customer-details">02 · Customers</a>
        <a href="#payments-received">03 · Payments</a>
    </div>
    """,
    unsafe_allow_html=True
)


def section_heading(anchor_id, kicker, title, subtitle=""):
    subtitle_html = (
        f'<div class="section-subtitle">{html_escape(subtitle)}</div>'
        if subtitle else ""
    )
    st.markdown(
        f"""
        <div id="{html_escape(anchor_id)}" class="section-heading">
            <div class="section-kicker">{html_escape(kicker)}</div>
            <div class="section-title">{html_escape(title)}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def subsection_heading(title):
    st.markdown(
        f'<div class="subsection-heading">{html_escape(title)}</div>',
        unsafe_allow_html=True
    )


def table_caption(title, note=""):
    note_html = (
        f'<div class="table-caption-note">{html_escape(note)}</div>'
        if note else ""
    )
    st.markdown(
        f"""
        <div class="table-caption">
            <div class="table-caption-title">{html_escape(title)}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# KPI CARD
# ==========================================================

def kpi_card(
    title,
    value,
    percentage=None
):

    if percentage is not None:

        percentage_html = (
            f'<div class="kpi-percentage">'
            f'{percentage:.1f}% collected'
            f'</div>'
        )

    else:

        percentage_html = ""

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{html_escape(str(title))}</div>
            <div class="kpi-value">{html_escape(str(value))}</div>
            {percentage_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# SERVICE CLASSIFICATION
# ==========================================================

def classify_service(
    item_name,
    item_desc
):

    item_name = (
        str(item_name).strip()
        if pd.notna(item_name)
        else ""
    )

    item_desc = (
        str(item_desc).strip()
        if pd.notna(item_desc)
        else ""
    )

    source = (
        item_name
        if item_name
        else item_desc
    )

    source_clean = (
        source
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
        .casefold()
    )

    # ------------------------------------------------------
    # WEB DEVELOPMENT
    # ------------------------------------------------------

    if (
        "web development" in source_clean
        or "landing page development" in source_clean
        or "api integration" in source_clean
        or "crm development" in source_clean
        or "web hosting" in source_clean
        or "website maintenance" in source_clean
        or "website optimisation" in source_clean
        or "website optimization" in source_clean
        or "business card and flyers design" in source_clean
        or "web" in source_clean
        or "amc" in source_clean
    ):

        return "Web Development", ""


    # ------------------------------------------------------
    # GOOGLE + META ADS
    # ------------------------------------------------------

    if (
        "google and meta ads" in source_clean
        or (
            "google" in source_clean
            and "meta" in source_clean
            and "ads" in source_clean
        )
    ):

        return "SEO", "Google + Meta Ads"


    # ------------------------------------------------------
    # META ADS
    # ------------------------------------------------------

    if "meta ads" in source_clean:

        return "SEO", "Meta Ads"


    # ------------------------------------------------------
    # GOOGLE ADS
    # ------------------------------------------------------

    if (
        "google ads" in source_clean
        or "google advertis" in source_clean
        or "ad spent" in source_clean
        or "ad spends" in source_clean
        or "ppc management" in source_clean
        or "management fee" in source_clean
    ):

        return "SEO", "Google Ads"


    # ------------------------------------------------------
    # GBPO
    # ------------------------------------------------------

    if (
        "gbpo" in source_clean
        or "google business profile" in source_clean
    ):

        return "SEO", "GBPO"


    # ------------------------------------------------------
    # GMB
    # ------------------------------------------------------

    if (
        "google my business" in source_clean
        or "(gmb)" in source_clean
        or source_clean == "gmb"
    ):

        return "SEO", "GMB"


    # ------------------------------------------------------
    # SMO
    # ------------------------------------------------------

    if (
        "smo" in source_clean
        or "social media optimization" in source_clean
    ):

        return "SEO", "SMO"


    # ------------------------------------------------------
    # SEO
    # ------------------------------------------------------

    if "seo" in source_clean:

        return "SEO", "SEO"


    # ------------------------------------------------------
    # EMAIL MARKETING
    # ------------------------------------------------------

    if "email marketing" in source_clean:

        return "SEO", "Email Marketing"


    # ------------------------------------------------------
    # OTHER
    # ------------------------------------------------------

    return "Unclassified", ""


# ==========================================================
# FILES
# ==========================================================

INVOICE_FILE = "Invoice_zoho.xlsx"
PAYMENT_FILE = "Customer_Payment_zoho.xlsx"
AR_CURRENT_FILE = "AR_current_zoho.xlsx"
AR_OVERDUE_FILE = "AR_overdue_zoho.xlsx"
CONTACTS_FILE = "Contacts_zoho.xlsx"


# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data
def load_data():

    invoices = pd.read_excel(
        INVOICE_FILE
    )

    payments = pd.read_excel(
        PAYMENT_FILE
    )

    ar_current = pd.read_excel(
        AR_CURRENT_FILE
    )

    ar_overdue = pd.read_excel(
        AR_OVERDUE_FILE
    )


    # ======================================================
    # CLEAN COLUMN NAMES
    # ======================================================

    invoices.columns = (
        invoices.columns
        .astype(str)
        .str.strip()
    )

    payments.columns = (
        payments.columns
        .astype(str)
        .str.strip()
    )

    ar_current.columns = (
        ar_current.columns
        .astype(str)
        .str.strip()
    )

    ar_overdue.columns = (
        ar_overdue.columns
        .astype(str)
        .str.strip()
    )


    # ======================================================
    # SERVICE CLASSIFICATION
    # ======================================================

    if "Item Name" not in invoices.columns:

        invoices["Item Name"] = ""


    if "Item Desc" not in invoices.columns:

        invoices["Item Desc"] = ""


    service_classification = invoices.apply(
        lambda row: classify_service(
            row["Item Name"],
            row["Item Desc"]
        ),
        axis=1,
        result_type="expand"
    )


    service_classification.columns = [
        "Service Type",
        "Service Subcategory"
    ]


    invoices = pd.concat(
        [
            invoices,
            service_classification
        ],
        axis=1
    )


    # ======================================================
    # INVOICE DATE COLUMNS
    # ======================================================

    invoice_dates = [
        "Invoice Date",
        "Due Date",
        "Last Payment Date",
        "Expected Payment Date"
    ]


    for col in invoice_dates:

        if col in invoices.columns:

            invoices[col] = pd.to_datetime(
                invoices[col],
                dayfirst=True,
                errors="coerce"
            )


    # ======================================================
    # PAYMENT DATE
    # ======================================================

    if "Date" in payments.columns:

        payments["Date"] = pd.to_datetime(
            payments["Date"],
            dayfirst=True,
            errors="coerce"
        )


    # ======================================================
    # PAYMENT INVOICE DATE
    # ======================================================

    if "Invoice Date" in payments.columns:

        payments["Invoice Date"] = pd.to_datetime(
            payments["Invoice Date"],
            dayfirst=True,
            errors="coerce"
        )


    # ======================================================
    # PAYMENT APPLIED DATE
    # ======================================================

    if "Invoice Payment Applied Date" in payments.columns:

        payments["Invoice Payment Applied Date"] = pd.to_datetime(
            payments["Invoice Payment Applied Date"],
            dayfirst=True,
            errors="coerce"
        )


    # ======================================================
    # AR DATES
    # ======================================================

    for df in [
        ar_current,
        ar_overdue
    ]:

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"],
                dayfirst=True,
                errors="coerce"
            )


        if "due_date" in df.columns:

            df["due_date"] = pd.to_datetime(
                df["due_date"],
                dayfirst=True,
                errors="coerce"
            )


    # ======================================================
    # INVOICE NUMERIC
    # ======================================================

    for col in [
        "Total",
        "Balance",
        "SubTotal"
    ]:

        if col in invoices.columns:

            invoices[col] = pd.to_numeric(
                invoices[col],
                errors="coerce"
            ).fillna(0)


    # ======================================================
    # PAYMENT NUMERIC
    # ======================================================

    for col in [
        "Amount",
        "Amount Applied to Invoice"
    ]:

        if col in payments.columns:

            payments[col] = pd.to_numeric(
                payments[col],
                errors="coerce"
            ).fillna(0)


    # ======================================================
    # AR NUMERIC
    # ======================================================

    for df in [
        ar_current,
        ar_overdue
    ]:

        for col in [
            "balance",
            "amount"
        ]:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).fillna(0)


    # ======================================================
    # REMOVE DRAFT / VOID
    # ======================================================

    invoices = invoices[
        ~invoices["Invoice Status"].isin(
            [
                "Draft",
                "Void"
            ]
        )
    ].copy()


    # ======================================================
    # MONTH
    # ======================================================

    invoices["Month"] = (
        invoices["Invoice Date"]
        .dt.to_period("M")
        .astype(str)
    )


    # ======================================================
    # DEDUPLICATE INVOICES
    # ======================================================

    invoices = (
        invoices
        .sort_values(
            "Invoice Date"
        )
        .drop_duplicates(
            subset="Invoice Number",
            keep="first"
        )
        .reset_index(
            drop=True
        )
    )


    # ======================================================
    # CUSTOMER FIRST INVOICE
    # ======================================================

    customer_first_invoice = (
        invoices
        .groupby(
            "Customer Name"
        )["Invoice Date"]
        .min()
    )


    invoices[
        "First Customer Invoice Date"
    ] = (
        invoices[
            "Customer Name"
        ]
        .map(
            customer_first_invoice
        )
    )


    # ======================================================
    # INVOICE TYPE
    # ======================================================

    invoices["Invoice Type"] = np.where(
        invoices["Invoice Date"]
        ==
        invoices["First Customer Invoice Date"],
        "New Customer",
        "Recurring Customer"
    )


    # ======================================================
    # ENTITY ID CHECK
    # ======================================================

    if "entity_id" in invoices.columns:

        print(
            "entity_id found in Invoice file."
        )

        print(
            f"Unique entity_id values: "
            f"{invoices['entity_id'].nunique():,}"
        )

        print(
            f"Duplicate entity_id values: "
            f"{invoices['entity_id'].duplicated().sum():,}"
        )

    else:

        print(
            "entity_id NOT found in Invoice file."
        )


    # ======================================================
    # PAYMENT SUMMARY
    # ======================================================

    payment_summary = (
        payments
        .groupby(
            "Invoice Number",
            as_index=False
        )
        .agg(
            Paid=(
                "Amount Applied to Invoice",
                "sum"
            )
        )
    )


    invoices = invoices.merge(
        payment_summary,
        on="Invoice Number",
        how="left"
    )


    invoices["Paid"] = (
        invoices["Paid"]
        .fillna(0)
    )


    # ======================================================
    # CALCULATED OUTSTANDING
    # ======================================================

    invoices["Calculated Outstanding"] = (
        invoices["Total"]
        -
        invoices["Paid"]
    ).clip(
        lower=0
    )


    invoices["Outstanding"] = (
        invoices["Calculated Outstanding"]
    )


    # ======================================================
    # CUSTOMER TYPE
    # ======================================================

    customer_first_invoice = (
        invoices
        .groupby(
            "Customer Name"
        )["Invoice Date"]
        .min()
    )


    invoices[
        "First Customer Invoice Date"
    ] = (
        invoices[
            "Customer Name"
        ].map(
            customer_first_invoice
        )
    )


    invoices["Customer Type"] = np.where(
        invoices["Invoice Date"]
        ==
        invoices["First Customer Invoice Date"],
        "New Customer",
        "Recurring Customer"
    )


    # ======================================================
    # ZOHO BALANCE RECONCILIATION
    # ======================================================

    invoices["Balance Difference"] = (
        invoices["Calculated Outstanding"]
        -
        invoices["Balance"]
    )


    invoices["Balance Reconciles"] = (
        invoices["Balance Difference"]
        .abs()
        <= 0.01
    )


    # ======================================================
    # RE-CALCULATE OUTSTANDING
    # ======================================================

    invoices["Calculated Outstanding"] = (
        invoices["Total"]
        -
        invoices["Paid"]
    ).clip(
        lower=0
    )


    # ======================================================
    # RECONCILIATION CHECK
    # ======================================================

    invoice_total_check = (
        invoices["Total"].sum()
    )

    invoice_paid_check = (
        invoices["Paid"].sum()
    )

    invoice_outstanding_check = (
        invoices[
            "Calculated Outstanding"
        ].sum()
    )

    reconciliation_difference = (
        invoice_total_check
        -
        invoice_paid_check
        -
        invoice_outstanding_check
    )


    print(
        f"Invoice Total       : "
        f"£{invoice_total_check:,.2f}"
    )

    print(
        f"Payments Applied    : "
        f"£{invoice_paid_check:,.2f}"
    )

    print(
        f"Calculated Pending  : "
        f"£{invoice_outstanding_check:,.2f}"
    )

    print(
        f"Reconciliation Diff : "
        f"£{reconciliation_difference:,.2f}"
    )


    # ======================================================
    # RECONCILIATION ISSUES
    # ======================================================

    reconciliation_issues = invoices[
        invoices[
            "Balance Difference"
        ].abs()
        > 0.01
    ].copy()


    print("=" * 70)
    print(
        "INVOICE / PAYMENT / BALANCE RECONCILIATION"
    )
    print("=" * 70)


    print(
        f"Unique invoices     : "
        f"{invoices['Invoice Number'].nunique():,}"
    )


    print(
        f"Invoice Total       : "
        f"£{invoices['Total'].sum():,.2f}"
    )


    print(
        f"Payments Matched    : "
        f"£{invoices['Paid'].sum():,.2f}"
    )


    print(
        f"Calculated Pending  : "
        f"£{invoices['Calculated Outstanding'].sum():,.2f}"
    )


    print(
        f"Zoho Invoice Balance: "
        f"£{invoices['Balance'].sum():,.2f}"
    )


    print(
        f"Balance Difference  : "
        f"£{invoices['Balance Difference'].sum():,.2f}"
    )


    print(
        f"Mismatch invoices   : "
        f"{len(reconciliation_issues):,}"
    )


    print("=" * 70)


    # ======================================================
    # AR REFERENCE
    # ======================================================

    ar_current["AR Source"] = "Future Due"
    ar_overdue["AR Source"] = "Overdue"


    ar_reference = pd.concat(
        [
            ar_current,
            ar_overdue
        ],
        ignore_index=True
    )


    # ======================================================
    # AR INVOICE NUMBER
    # ======================================================

    if "invoice_number" in ar_reference.columns:

        ar_reference["Invoice Number"] = (
            ar_reference["invoice_number"]
            .astype(str)
            .str.strip()
        )

    elif "Invoice Number" not in ar_reference.columns:

        ar_reference["Invoice Number"] = ""


    # ======================================================
    # AR BALANCE
    # ======================================================

    if "balance" in ar_reference.columns:

        ar_reference["AR Balance"] = (
            pd.to_numeric(
                ar_reference["balance"],
                errors="coerce"
            )
            .fillna(0)
        )

    else:

        ar_reference["AR Balance"] = 0


    # ======================================================
    # DEDUP AR
    # ======================================================

    ar_reference = (
        ar_reference
        .drop_duplicates(
            subset="Invoice Number",
            keep="first"
        )
        .reset_index(
            drop=True
        )
    )


    # ======================================================
    # MATCH AR
    # ======================================================

    invoice_reference = invoices[
        [
            "Invoice Number",
            "Outstanding",
            "Due Date"
        ]
    ].copy()


    invoice_reference["Invoice Number"] = (
        invoice_reference[
            "Invoice Number"
        ]
        .astype(str)
        .str.strip()
    )


    invoice_reference = (
        invoice_reference
        .rename(
            columns={
                "Outstanding":
                    "Invoice Outstanding"
            }
        )
    )


    ar_reconciliation = (
        ar_reference
        .merge(
            invoice_reference,
            on="Invoice Number",
            how="outer",
            indicator=True
        )
    )


    ar_reconciliation[
        "Invoice Outstanding"
    ] = (
        ar_reconciliation[
            "Invoice Outstanding"
        ]
        .fillna(0)
    )


    ar_reconciliation[
        "AR Balance"
    ] = (
        ar_reconciliation[
            "AR Balance"
        ]
        .fillna(0)
    )


    ar_reconciliation[
        "Difference"
    ] = (
        ar_reconciliation[
            "Invoice Outstanding"
        ]
        -
        ar_reconciliation[
            "AR Balance"
        ]
    )


    # ======================================================
    # AR MISMATCHES
    # ======================================================

    ar_mismatches = ar_reconciliation[
        (
            ar_reconciliation[
                "Difference"
            ].abs()
            > 0.01
        )
        |
        (
            ar_reconciliation[
                "_merge"
            ]
            != "both"
        )
    ].copy()


    print(
        f"AR reconciliation mismatches: "
        f"{len(ar_mismatches):,}"
    )


    if not ar_mismatches.empty:

        print(
            ar_mismatches[
                [
                    "Invoice Number",
                    "Invoice Outstanding",
                    "AR Balance",
                    "Difference",
                    "_merge"
                ]
            ].to_string(
                index=False
            )
        )


    # ======================================================
    # CUSTOMER SUMMARY
    # ======================================================

    customer_summary = (
        invoices
        .groupby(
            "Customer Name",
            as_index=False
        )
        .agg(
            Total_Invoiced=(
                "Total",
                "sum"
            ),
            Outstanding=(
                "Calculated Outstanding",
                "sum"
            ),
            Invoice_Count=(
                "Invoice Number",
                "nunique"
            )
        )
    )


    # ======================================================
    # MONTHLY SUMMARY
    # ======================================================

    monthly_summary = (
        invoices
        .groupby(
            "Month",
            as_index=False
        )
        .agg(
            Customers=(
                "Customer Name",
                "nunique"
            ),
            Invoices=(
                "Invoice Number",
                "nunique"
            ),
            Total_Invoiced=(
                "Total",
                "sum"
            ),
            Outstanding=(
                "Calculated Outstanding",
                "sum"
            )
        )
        .sort_values(
            "Month"
        )
    )


    # ======================================================
    # GLOBAL KPIs
    # ======================================================

    total_customers = (
        invoices[
            "Customer Name"
        ].nunique()
    )


    total_invoiced = (
        invoices["Total"].sum()
    )


    total_pending = (
        invoices["Outstanding"].sum()
    )


    # ======================================================
    # CONTACTS
    # ======================================================

    contacts = pd.read_excel(
        CONTACTS_FILE
    )


    contacts.columns = (
        contacts.columns
        .astype(str)
        .str.strip()
    )


    return (
        invoices,
        payments,
        ar_current,
        ar_overdue,
        ar_reconciliation,
        ar_mismatches,
        customer_summary,
        monthly_summary,
        total_customers,
        total_invoiced,
        total_pending,
        contacts
    )


# ==========================================================
# LOAD DATA
# ==========================================================

(
    invoices,
    payments,
    ar_current,
    ar_overdue,
    ar_reconciliation,
    ar_mismatches,
    customer_summary,
    monthly_summary,
    TOTAL_CUSTOMERS,
    TOTAL_INVOICED,
    TOTAL_PENDING,
    contacts
) = load_data()


# ==========================================================
# PART 2
# MAIN DASHBOARD FILTERS
# ==========================================================

section_heading(
    "dashboard-overview",
    "01 · Dashboard Overview",
    "Invoice Performance",
    "Filter the invoice population, then review collection, outstanding balances and monthly performance."
)


with st.container(border=True):
    st.markdown('<div class="kpi-grid-label">Reporting filters</div>', unsafe_allow_html=True)
    st.markdown('<div class="filter-note">Choose the reporting period and population used across the overview below.</div>', unsafe_allow_html=True)
    f1, f2, f3, f4, f5 = st.columns(5)


    # ==========================================================
    # FIXED DATE RANGE
    # ==========================================================

    min_date = date(
        2021,
        1,
        1
    )

    max_date = date(
        2027,
        12,
        31
    )


    current_year = (
        pd.Timestamp.today().year
    )


    default_start = date(
        current_year,
        1,
        1
    )


    default_end = date(
        current_year,
        12,
        31
    )


    with f1:

        start_date = st.date_input(
            "Start Date",
            value=default_start,
            min_value=min_date,
            max_value=max_date
        )


    with f2:

        end_date = st.date_input(
            "End Date",
            value=default_end,
            min_value=min_date,
            max_value=max_date
        )


    # ==========================================================
    # SERVICE FILTER
    # ==========================================================

    with f3:

        service_options = [
            "All Services",
            "SEO",
            "Web Development",
            "Unclassified"
        ]


        selected_service = st.selectbox(
            "Service Type",
            service_options
        )


    # ==========================================================
    # INVOICE TYPE FILTER
    # ==========================================================

    with f4:

        invoice_type_options = [
            "All Invoices",
            "New Customer",
            "Recurring Customer"
        ]


        selected_invoice_type = st.selectbox(
            "Invoice Type",
            invoice_type_options,
            key="main_invoice_type"
        )


    # ==========================================================
    # CUSTOMER STATUS FILTER
    # ==========================================================

    with f5:

        customer_status_options = [
            "All Customers",
            "Active",
            "Inactive"
        ]


        selected_customer_status = st.selectbox(
            "Customer Status",
            customer_status_options,
            key="main_customer_status"
        )



# ==========================================================
# APPLY FILTERS
# ==========================================================

display_df = invoices[
    (
        invoices["Invoice Date"]
        >= pd.Timestamp(start_date)
    )
    &
    (
        invoices["Invoice Date"]
        <= pd.Timestamp(end_date)
    )
].copy()


if selected_service != "All Services":

    display_df = display_df[
        display_df[
            "Service Type"
        ]
        ==
        selected_service
    ].copy()


if selected_invoice_type != "All Invoices":

    display_df = display_df[
        display_df[
            "Invoice Type"
        ]
        ==
        selected_invoice_type
    ].copy()


if selected_customer_status != "All Customers":

    selected_status_customers = set(
        contacts[
            contacts["Status"]
            .astype(str)
            .str.strip()
            .str.title()
            ==
            selected_customer_status
        ]["Display Name"]
        .astype(str)
        .str.strip()
    )


    display_df = display_df[
        display_df[
            "Customer Name"
        ]
        .astype(str)
        .str.strip()
        .isin(
            selected_status_customers
        )
    ].copy()


st.markdown(
    f"""
    <div class="filter-summary">
        <span class="filter-pill">📅 {html_escape(str(start_date))} → {html_escape(str(end_date))}</span>
        <span class="filter-pill">🧩 {html_escape(selected_service)}</span>
        <span class="filter-pill">🧾 {html_escape(selected_invoice_type)}</span>
        <span class="filter-pill">👥 {html_escape(selected_customer_status)}</span>
        <span class="filter-pill">↳ {len(display_df):,} invoice rows</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# MAIN KPIs
# ==========================================================

total_customers = (
    display_df[
        "Customer Name"
    ].nunique()
)


total_invoices = (
    display_df[
        "Invoice Number"
    ].nunique()
)


total_invoiced = (
    display_df[
        "Total"
    ].sum()
)


total_paid = (
    display_df[
        "Paid"
    ].sum()
)


# ==========================================================
# COLLECTION RATE
# ==========================================================

collection_rate = (
    total_paid
    /
    total_invoiced
    *
    100
    if total_invoiced > 0
    else 0
)


st.markdown('<div class="kpi-grid-label">Current filtered position</div>', unsafe_allow_html=True)


# ==========================================================
# AR
# ==========================================================

today = (
    pd.Timestamp.today()
    .normalize()
)


overdue_df = display_df[
    (
        display_df[
            "Outstanding"
        ]
        > 0
    )
    &
    (
        display_df[
            "Due Date"
        ]
        <= today
    )
].copy()


overdue_due = (
    overdue_df[
        "Outstanding"
    ].sum()
)


future_df = display_df[
    (
        display_df[
            "Outstanding"
        ]
        > 0
    )
    &
    (
        display_df[
            "Due Date"
        ]
        > today
    )
].copy()


future_due = (
    future_df[
        "Outstanding"
    ].sum()
)


total_pending = (
    overdue_due
    +
    future_due
)


invoice_balance = (
    display_df[
        "Outstanding"
    ].sum()
)


calculated_pending = (
    overdue_due
    +
    future_due
)


difference = (
    invoice_balance
    -
    calculated_pending
)


overdue_total = overdue_due


# ==========================================================
# UNCLASSIFIED
# ==========================================================

if selected_service == "Unclassified":

    subsection_heading("Unclassified Invoices")


    st.dataframe(
        display_df[
            [
                "Invoice Number",
                "Customer Name",
                "Item Name",
                "Item Desc",
                "Total"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# KPI PERCENTAGES
# ==========================================================

paid_percentage = (
    total_paid
    /
    total_invoiced
    *
    100
    if total_invoiced > 0
    else 0
)


pending_percentage = (
    total_pending
    /
    total_invoiced
    *
    100
    if total_invoiced > 0
    else 0
)


future_percentage = (
    future_due
    /
    total_invoiced
    *
    100
    if total_invoiced > 0
    else 0
)


overdue_percentage = (
    overdue_due
    /
    total_invoiced
    *
    100
    if total_invoiced > 0
    else 0
)


# ==========================================================
# KPI CARDS
# ==========================================================

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)


if IS_FINANCIAL:

    with c1:

        kpi_card(
            "👥 Customers",
            f"{total_customers:,}"
        )


    with c2:

        kpi_card(
            "📄 Invoices",
            f"{total_invoices:,}"
        )


    with c3:

        kpi_card(
            "💷 Invoiced",
            f"£{total_invoiced:,.2f}"
        )


    with c4:

        kpi_card(
            "✅ Paid",
            f"£{total_paid:,.2f}",
            paid_percentage
        )


    with c5:

        kpi_card(
            "⏳ Pending",
            f"£{total_pending:,.2f}",
            pending_percentage
        )


    with c6:

        kpi_card(
            "📅 Future Due",
            f"£{future_due:,.2f}",
            future_percentage
        )


    with c7:

        kpi_card(
            "🔴 Overdue",
            f"£{overdue_due:,.2f}",
            overdue_percentage
        )


else:

    outstanding_percentage = (
        total_pending
        /
        total_invoiced
        *
        100
        if total_invoiced > 0
        else 0
    )


    with c1:

        kpi_card(
            "👥 Customers",
            f"{total_customers:,}"
        )


    with c2:

        kpi_card(
            "📄 Invoices",
            f"{total_invoices:,}"
        )


    with c3:

        kpi_card(
            "✅ Paid",
            f"{paid_percentage:.1f}%"
        )


    with c4:

        kpi_card(
            "⏳ Outstanding",
            f"{outstanding_percentage:.1f}%"
        )


    with c5:

        kpi_card(
            "⏳ Pending",
            f"{outstanding_percentage:.1f}%"
        )


    with c6:

        kpi_card(
            "📅 Future Due",
            f"{future_percentage:.1f}%"
        )


    with c7:

        kpi_card(
            "🔴 Overdue",
            f"{overdue_percentage:.1f}%"
        )


# ==========================================================
# AR RECONCILIATION
# ==========================================================

filtered_invoice_numbers = set(
    display_df[
        "Invoice Number"
    ]
    .astype(str)
    .str.strip()
)


filtered_ar_mismatches = ar_mismatches[
    ar_mismatches[
        "Invoice Number"
    ]
    .astype(str)
    .str.strip()
    .isin(
        filtered_invoice_numbers
    )
].copy()


with st.expander(
    "🔧 Reconciliation",
    expanded=False
):

    st.write(
        f"AR mismatches in current filtered data: "
        f"{len(filtered_ar_mismatches):,}"
    )


    if not filtered_ar_mismatches.empty:

        diagnostic_columns = [
            "Invoice Number",
            "Invoice Outstanding",
            "AR Balance",
            "Difference",
            "_merge"
        ]


        diagnostic_columns = [
            col
            for col in diagnostic_columns
            if col in filtered_ar_mismatches.columns
        ]


        st.dataframe(
            filtered_ar_mismatches[
                diagnostic_columns
            ].sort_values(
                "Difference",
                key=lambda x: x.abs(),
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )


    else:

        st.success(
            "✅ Invoice/Payment data reconciles with AR files."
        )


# ==========================================================
# MONTHLY INVOICE SUMMARY
# ==========================================================

subsection_heading("Monthly Invoice Summary")


monthly_invoice_summary = (
    display_df
    .groupby(
        "Month",
        as_index=False
    )
    .agg(
        Customers=(
            "Customer Name",
            "nunique"
        ),

        Invoices=(
            "Invoice Number",
            "nunique"
        ),

        Total_Invoiced=(
            "Total",
            "sum"
        ),

        Outstanding=(
            "Calculated Outstanding",
            "sum"
        )
    )
    .sort_values(
        "Month"
    )
    .reset_index(
        drop=True
    )
)


# ==========================================================
# PAYMENT MONTH ANALYSIS
# ==========================================================

filtered_invoice_numbers = set(
    display_df[
        "Invoice Number"
    ]
    .astype(str)
    .str.strip()
)


monthly_payments = payments[
    payments[
        "Invoice Number"
    ]
    .astype(str)
    .str.strip()
    .isin(
        filtered_invoice_numbers
    )
].copy()


# ==========================================================
# ORIGINAL INVOICE DATE LOOKUP
# ==========================================================

invoice_dates_lookup = invoices[
    [
        "Invoice Number",
        "Invoice Date"
    ]
].copy()


invoice_dates_lookup["Invoice Number"] = (
    invoice_dates_lookup[
        "Invoice Number"
    ]
    .astype(str)
    .str.strip()
)


invoice_dates_lookup = (
    invoice_dates_lookup
    .rename(
        columns={
            "Invoice Date":
                "Original Invoice Date"
        }
    )
)


monthly_payments["Invoice Number"] = (
    monthly_payments[
        "Invoice Number"
    ]
    .astype(str)
    .str.strip()
)


monthly_payments = (
    monthly_payments
    .merge(
        invoice_dates_lookup,
        on="Invoice Number",
        how="left"
    )
)


# ==========================================================
# PAYMENT MONTH
# ==========================================================

monthly_payments["Payment Month"] = (
    monthly_payments[
        "Date"
    ]
    .dt.to_period("M")
    .astype(str)
)


# ==========================================================
# ORIGINAL INVOICE MONTH
# ==========================================================

monthly_payments["Invoice Month"] = (
    monthly_payments[
        "Original Invoice Date"
    ]
    .dt.to_period("M")
    .astype(str)
)


# ==========================================================
# PAYMENT TYPE
# ==========================================================

monthly_payments["Payment Type"] = np.where(
    monthly_payments[
        "Payment Month"
    ]
    ==
    monthly_payments[
        "Invoice Month"
    ],
    "Current Invoice",
    "Older Invoice"
)


# ==========================================================
# MONTHLY PAYMENT TOTALS
# ==========================================================

monthly_payment_summary = (
    monthly_payments
    .groupby(
        [
            "Payment Month",
            "Payment Type"
        ],
        as_index=False
    )
    .agg(
        Payment_Amount=(
            "Amount Applied to Invoice",
            "sum"
        )
    )
)


monthly_payment_summary = (
    monthly_payment_summary
    .pivot(
        index="Payment Month",
        columns="Payment Type",
        values="Payment_Amount"
    )
    .fillna(0)
    .reset_index()
)


if "Current Invoice" not in (
    monthly_payment_summary.columns
):

    monthly_payment_summary[
        "Current Invoice"
    ] = 0


if "Older Invoice" not in (
    monthly_payment_summary.columns
):

    monthly_payment_summary[
        "Older Invoice"
    ] = 0


monthly_payment_summary = (
    monthly_payment_summary
    .rename(
        columns={
            "Payment Month":
                "Month",

            "Current Invoice":
                "Paid_Current_Month",

            "Older Invoice":
                "Paid_Older_Invoices"
        }
    )
)


monthly_payment_summary[
    "Total_Paid"
] = (
    monthly_payment_summary[
        "Paid_Current_Month"
    ]
    +
    monthly_payment_summary[
        "Paid_Older_Invoices"
    ]
)


# ==========================================================
# COMBINE MONTHLY DATA
# ==========================================================

monthly_display = (
    monthly_invoice_summary
    .merge(
        monthly_payment_summary[
            [
                "Month",
                "Paid_Current_Month",
                "Paid_Older_Invoices",
                "Total_Paid"
            ]
        ],
        on="Month",
        how="outer"
    )
)


for col in [
    "Paid_Current_Month",
    "Paid_Older_Invoices",
    "Total_Paid"
]:

    monthly_display[col] = (
        monthly_display[col]
        .fillna(0)
    )


for col in [
    "Customers",
    "Invoices",
    "Total_Invoiced",
    "Outstanding"
]:

    monthly_display[col] = (
        monthly_display[col]
        .fillna(0)
    )


monthly_display = (
    monthly_display
    .sort_values("Month")
    .reset_index(
        drop=True
    )
)


# ==========================================================
# FINANCIAL MONTHLY VIEW
# ==========================================================

if IS_FINANCIAL:

    monthly_total_row = pd.DataFrame(
        [{
            "Month":
                "TOTAL",

            "Customers":
                display_df[
                    "Customer Name"
                ].nunique(),

            "Invoices":
                display_df[
                    "Invoice Number"
                ].nunique(),

            "Total_Invoiced":
                display_df[
                    "Total"
                ].sum(),

            "Paid_Current_Month":
                monthly_display[
                    "Paid_Current_Month"
                ].sum(),

            "Paid_Older_Invoices":
                monthly_display[
                    "Paid_Older_Invoices"
                ].sum(),

            "Total_Paid":
                monthly_display[
                    "Total_Paid"
                ].sum(),

            "Outstanding":
                display_df[
                    "Calculated Outstanding"
                ].sum()
        }]
    )


    monthly_display = pd.concat(
        [
            monthly_display,
            monthly_total_row
        ],
        ignore_index=True
    )


    for col in [
        "Total_Invoiced",
        "Paid_Current_Month",
        "Paid_Older_Invoices",
        "Total_Paid",
        "Outstanding"
    ]:

        monthly_display[col] = (
            monthly_display[col]
            .apply(
                lambda x:
                f"£{x:,.2f}"
            )
        )


    monthly_display = (
        monthly_display
        .rename(
            columns={
                "Total_Invoiced":
                    "Invoiced",

                "Paid_Current_Month":
                    "Paid – Current Invoice Month",

                "Paid_Older_Invoices":
                    "Paid – Older Invoices",

                "Total_Paid":
                    "Total Paid",

                "Outstanding":
                    "Outstanding"
            }
        )
    )


    table_caption("Monthly invoice and payment performance", "Amounts shown in GBP")
    st.dataframe(
        monthly_display,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# PERCENTAGE MONTHLY VIEW
# ==========================================================

else:

    monthly_percentage = (
        monthly_display.copy()
    )


    monthly_percentage[
        "Paid – Current %"
    ] = np.where(
        monthly_percentage[
            "Total_Invoiced"
        ] > 0,

        (
            monthly_percentage[
                "Paid_Current_Month"
            ]
            /
            monthly_percentage[
                "Total_Invoiced"
            ]
        )
        * 100,

        0
    )


    monthly_percentage[
        "Paid – Older %"
    ] = np.where(
        monthly_percentage[
            "Total_Invoiced"
        ] > 0,

        (
            monthly_percentage[
                "Paid_Older_Invoices"
            ]
            /
            monthly_percentage[
                "Total_Invoiced"
            ]
        )
        * 100,

        0
    )


    monthly_percentage[
        "Total Paid %"
    ] = np.where(
        monthly_percentage[
            "Total_Invoiced"
        ] > 0,

        (
            monthly_percentage[
                "Total_Paid"
            ]
            /
            monthly_percentage[
                "Total_Invoiced"
            ]
        )
        * 100,

        0
    )


    monthly_percentage[
        "Outstanding %"
    ] = np.where(
        monthly_percentage[
            "Total_Invoiced"
        ] > 0,

        (
            monthly_percentage[
                "Outstanding"
            ]
            /
            monthly_percentage[
                "Total_Invoiced"
            ]
        )
        * 100,

        0
    )


    total_invoice = (
        display_df[
            "Total"
        ].sum()
    )


    total_paid_current = (
        monthly_display[
            "Paid_Current_Month"
        ].sum()
    )


    total_paid_older = (
        monthly_display[
            "Paid_Older_Invoices"
        ].sum()
    )


    total_paid_value = (
        monthly_display[
            "Total_Paid"
        ].sum()
    )


    total_outstanding = (
        display_df[
            "Calculated Outstanding"
        ].sum()
    )


    percentage_total_row = pd.DataFrame(
        [{
            "Month":
                "TOTAL",

            "Customers":
                display_df[
                    "Customer Name"
                ].nunique(),

            "Invoices":
                display_df[
                    "Invoice Number"
                ].nunique(),

            "Paid – Current %": (
                total_paid_current
                /
                total_invoice
                *
                100
                if total_invoice > 0
                else 0
            ),

            "Paid – Older %": (
                total_paid_older
                /
                total_invoice
                *
                100
                if total_invoice > 0
                else 0
            ),

            "Total Paid %": (
                total_paid_value
                /
                total_invoice
                *
                100
                if total_invoice > 0
                else 0
            ),

            "Outstanding %": (
                total_outstanding
                /
                total_invoice
                *
                100
                if total_invoice > 0
                else 0
            )
        }]
    )


    monthly_percentage = (
        monthly_percentage[
            [
                "Month",
                "Customers",
                "Invoices",
                "Paid – Current %",
                "Paid – Older %",
                "Total Paid %",
                "Outstanding %"
            ]
        ]
    )


    monthly_percentage = pd.concat(
        [
            monthly_percentage,
            percentage_total_row
        ],
        ignore_index=True
    )


    for col in [
        "Paid – Current %",
        "Paid – Older %",
        "Total Paid %",
        "Outstanding %"
    ]:

        monthly_percentage[col] = (
            monthly_percentage[col]
            .map(
                lambda x:
                f"{x:.1f}%"
            )
        )


    table_caption("Monthly collection performance", "Percent of invoiced value collected")
    st.dataframe(
        monthly_percentage,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# CUSTOMER MONTHLY BREAKDOWN
# ==========================================================

st.divider()

subsection_heading("Customer Invoice Breakdown")


show_outstanding_only = st.checkbox(
    "Show Outstanding Customers Only",
    value=True
)


months = sorted(
    display_df[
        "Month"
    ].unique()
)


rows = []


for customer in sorted(
    display_df[
        "Customer Name"
    ]
    .dropna()
    .unique()
):

    row = {
        "Customer Name":
            customer
    }


    customer_df = display_df[
        display_df[
            "Customer Name"
        ]
        ==
        customer
    ]


    total_invoice = (
        customer_df[
            "Total"
        ].sum()
    )


    total_paid = (
        customer_df[
            "Paid"
        ].sum()
    )


    for month in months:

        month_df = customer_df[
            customer_df[
                "Month"
            ]
            ==
            month
        ]


        invoice_value = (
            month_df[
                "Total"
            ].sum()
        )


        paid_value = (
            month_df[
                "Paid"
            ].sum()
        )


        if IS_FINANCIAL:

            if invoice_value == 0:

                row[month] = "-"

            elif paid_value == 0:

                row[month] = (
                    f"£0 / "
                    f"£{invoice_value:,.0f}"
                )

            elif paid_value >= invoice_value:

                row[month] = (
                    f"£{invoice_value:,.0f}"
                )

            else:

                row[month] = (
                    f"£{paid_value:,.0f} / "
                    f"£{invoice_value:,.0f}"
                )


        else:

            if invoice_value == 0:

                row[month] = "-"

            else:

                paid_pct = (
                    paid_value
                    /
                    invoice_value
                    *
                    100
                )

                row[month] = (
                    f"{paid_pct:.1f}%"
                )


    if IS_FINANCIAL:

        if total_invoice == 0:

            row["Total"] = "-"

        elif total_paid == 0:

            row["Total"] = (
                f"£0 / "
                f"£{total_invoice:,.0f}"
            )

        elif total_paid >= total_invoice:

            row["Total"] = (
                f"£{total_invoice:,.0f}"
            )

        else:

            row["Total"] = (
                f"£{total_paid:,.0f} / "
                f"£{total_invoice:,.0f}"
            )

    else:

        if total_invoice == 0:

            row["Total"] = "-"

        else:

            total_paid_pct = (
                total_paid
                /
                total_invoice
                *
                100
            )

            row["Total"] = (
                f"{total_paid_pct:.1f}%"
            )


    rows.append(row)


customer_table = pd.DataFrame(
    rows
)


# ==========================================================
# OUTSTANDING ONLY
# ==========================================================

if show_outstanding_only:

    if IS_FINANCIAL:

        def has_outstanding(
            total_value
        ):

            if total_value == "-":
                return False

            if "/" not in total_value:
                return False

            paid = float(
                total_value
                .split("/")[0]
                .replace("£", "")
                .replace(",", "")
                .strip()
            )

            invoice = float(
                total_value
                .split("/")[1]
                .replace("£", "")
                .replace(",", "")
                .strip()
            )

            return paid < invoice

    else:

        def has_outstanding(
            total_value
        ):

            if total_value == "-":
                return False

            percentage = float(
                total_value
                .replace("%", "")
                .strip()
            )

            return percentage < 100


    customer_table = (
        customer_table[
            customer_table[
                "Total"
            ].apply(
                has_outstanding
            )
        ]
    )


# ==========================================================
# GRAND TOTAL
# ==========================================================

visible_customers = (
    customer_table[
        "Customer Name"
    ].tolist()
)


grand_total_df = display_df[
    display_df[
        "Customer Name"
    ].isin(
        visible_customers
    )
].copy()


grand_row = {
    "Customer Name":
        "GRAND TOTAL"
}


grand_total_invoice = (
    grand_total_df[
        "Total"
    ].sum()
)


grand_total_paid = (
    grand_total_df[
        "Paid"
    ].sum()
)


for month in months:

    month_df = grand_total_df[
        grand_total_df[
            "Month"
        ]
        ==
        month
    ]


    month_invoice = (
        month_df[
            "Total"
        ].sum()
    )


    month_paid = (
        month_df[
            "Paid"
        ].sum()
    )


    if IS_FINANCIAL:

        if month_invoice == 0:

            grand_row[month] = "-"

        elif month_paid == 0:

            grand_row[month] = (
                f"£0 / "
                f"£{month_invoice:,.0f}"
            )

        elif month_paid >= month_invoice:

            grand_row[month] = (
                f"£{month_invoice:,.0f}"
            )

        else:

            grand_row[month] = (
                f"£{month_paid:,.0f} / "
                f"£{month_invoice:,.0f}"
            )

    else:

        if month_invoice == 0:

            grand_row[month] = "-"

        else:

            month_paid_pct = (
                month_paid
                /
                month_invoice
                *
                100
            )

            grand_row[month] = (
                f"{month_paid_pct:.1f}%"
            )


if IS_FINANCIAL:

    if grand_total_invoice == 0:

        grand_row["Total"] = "-"

    elif grand_total_paid == 0:

        grand_row["Total"] = (
            f"£0 / "
            f"£{grand_total_invoice:,.0f}"
        )

    elif grand_total_paid >= grand_total_invoice:

        grand_row["Total"] = (
            f"£{grand_total_invoice:,.0f}"
        )

    else:

        grand_row["Total"] = (
            f"£{grand_total_paid:,.0f} / "
            f"£{grand_total_invoice:,.0f}"
        )

else:

    if grand_total_invoice == 0:

        grand_row["Total"] = "-"

    else:

        grand_total_paid_pct = (
            grand_total_paid
            /
            grand_total_invoice
            *
            100
        )

        grand_row["Total"] = (
            f"{grand_total_paid_pct:.1f}%"
        )


customer_table = pd.concat(
    [
        customer_table,
        pd.DataFrame(
            [grand_row]
        )
    ],
    ignore_index=True
)


# ==========================================================
# CUSTOMER TABLE COLOURS
# ==========================================================

def colour_cells(
    value
):

    if value == "-":
        return ""


    if IS_FINANCIAL:

        if "/" not in value:

            return (
                "background-color:#d9ead3;"
            )


        paid = float(
            value
            .split("/")[0]
            .replace("£", "")
            .replace(",", "")
            .strip()
        )


        invoice = float(
            value
            .split("/")[1]
            .replace("£", "")
            .replace(",", "")
            .strip()
        )


        if paid == 0:

            return (
                "background-color:#f4cccc;"
            )


        return (
            "background-color:#fff2cc;"
        )


    percentage = float(
        value
        .replace("%", "")
        .strip()
    )


    if percentage >= 100:

        return (
            "background-color:#d9ead3;"
        )

    elif percentage <= 0:

        return (
            "background-color:#f4cccc;"
        )

    else:

        return (
            "background-color:#fff2cc;"
        )


styled = (
    customer_table
    .style
    .map(
        colour_cells,
        subset=customer_table.columns[1:]
    )
)


def highlight_grand_total(
    row
):

    if row[
        "Customer Name"
    ] == "GRAND TOTAL":

        return [
            "font-weight:bold; "
            "background-color:#e6e6e6;"
        ] * len(row)

    return [
        ""
    ] * len(row)


styled = styled.apply(
    highlight_grand_total,
    axis=1
)


table_caption("Customer invoice matrix", "Green = fully paid · Amber = partially paid · Red = unpaid")
st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True
)


# ==========================================================
# PART 3
# CUSTOMER DRILLDOWN
# ==========================================================

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
section_heading(
    "customer-details",
    "02 · Customer Drilldown",
    "Customer Details",
    "Inspect an individual customer across invoices, payments, balances and contact information."
)


# ==========================================================
# CUSTOMER FILTERS
# ==========================================================

subsection_heading("Customer Filters")


with st.container(border=True):
    st.markdown('<div class="kpi-grid-label">Customer drilldown filters</div>', unsafe_allow_html=True)
    st.markdown('<div class="filter-note">These filters control the customer list and the selected customer ledger.</div>', unsafe_allow_html=True)
    cf1, cf2, cf3, cf4, cf5 = st.columns(5)


    with cf1:

        customer_start_date = st.date_input(
            "Customer Start Date",
            value=date(
                current_year,
                1,
                1
            ),
            min_value=min_date,
            max_value=max_date,
            key="customer_start_date"
        )


    with cf2:

        customer_end_date = st.date_input(
            "Customer End Date",
            value=date(
                current_year,
                12,
                31
            ),
            min_value=min_date,
            max_value=max_date,
            key="customer_end_date"
        )


    with cf3:

        customer_service_options = [
            "All Services",
            "SEO",
            "Web Development",
            "Unclassified"
        ]


        customer_selected_service = st.selectbox(
            "Customer Service Type",
            customer_service_options,
            key="customer_service_type"
        )


    with cf4:

        customer_invoice_type_options = [
            "All Invoices",
            "New Customer",
            "Recurring Customer"
        ]


        customer_selected_invoice_type = (
            st.selectbox(
                "Invoice Type",
                customer_invoice_type_options,
                key="customer_invoice_type"
            )
        )


    with cf5:

        customer_status_options = [
            "All Customers",
            "Active",
            "Inactive"
        ]


        customer_selected_status = st.selectbox(
            "Customer Status",
            customer_status_options,
            key="customer_detail_status"
        )



# ==========================================================
# CUSTOMER DATASET
# ==========================================================

customer_display_df = invoices[
    (
        invoices["Invoice Date"]
        >= pd.Timestamp(
            customer_start_date
        )
    )
    &
    (
        invoices["Invoice Date"]
        <= pd.Timestamp(
            customer_end_date
        )
    )
].copy()


if customer_selected_service != "All Services":

    customer_display_df = (
        customer_display_df[
            customer_display_df[
                "Service Type"
            ]
            ==
            customer_selected_service
        ]
        .copy()
    )


if customer_selected_invoice_type != "All Invoices":

    customer_display_df = (
        customer_display_df[
            customer_display_df[
                "Invoice Type"
            ]
            ==
            customer_selected_invoice_type
        ]
        .copy()
    )


if customer_selected_status != "All Customers":

    selected_status_customers = set(
        contacts[
            contacts["Status"]
            .astype(str)
            .str.strip()
            .str.title()
            ==
            customer_selected_status
        ]["Display Name"]
        .astype(str)
        .str.strip()
    )


    customer_display_df = (
        customer_display_df[
            customer_display_df[
                "Customer Name"
            ]
            .astype(str)
            .str.strip()
            .isin(
                selected_status_customers
            )
        ]
        .copy()
    )


# ==========================================================
# CUSTOMER SELECTION
# ==========================================================

customer_list = sorted(
    customer_display_df[
        "Customer Name"
    ]
    .dropna()
    .unique()
)


if customer_list:

    selected_customer = st.selectbox(
        "Select Customer",
        customer_list,
        key="selected_customer"
    )


    # ======================================================
    # CUSTOMER DATA
    # ======================================================

    customer_invoices = (
        customer_display_df[
            customer_display_df[
                "Customer Name"
            ]
            ==
            selected_customer
        ]
        .copy()
    )


    customer_payments = payments[
        payments[
            "Customer Name"
        ]
        .astype(str)
        .str.strip()
        ==
        str(selected_customer).strip()
    ].copy()


    # ======================================================
    # CUSTOMER INFORMATION
    # ======================================================

    customer_info = contacts[
        contacts[
            "Display Name"
        ]
        .astype(str)
        .str.strip()
        ==
        str(selected_customer).strip()
    ].copy()


    if not customer_info.empty:

        info = customer_info.iloc[0]


        subsection_heading("Customer Information")


        customer_name = str(
            info.get(
                "Display Name",
                selected_customer
            )
        ).strip()


        phone_number = str(
            info.get(
                "Phone",
                ""
            )
        ).strip()


        alt_number = str(
            info.get(
                "Billing Phone",
                ""
            )
        ).strip()


        mobile_number = str(
            info.get(
                "MobilePhone",
                ""
            )
        ).strip()


        email_address = str(
            info.get(
                "EmailID",
                ""
            )
        ).strip()


        customer_status = str(
            info.get(
                "Status",
                "Unknown"
            )
        ).strip()


        address_parts = []


        for col in [
            "Billing Address",
            "Billing Street2",
            "Billing City",
            "Billing State",
            "Billing Country",
            "Billing County",
            "Billing Code"
        ]:

            value = info.get(
                col,
                ""
            )


            if pd.notna(value):

                value = str(
                    value
                ).strip()

                if value:

                    address_parts.append(
                        value
                    )


        customer_address = ", ".join(
            address_parts
        )


        status_lower = customer_status.lower()

        if status_lower == "active":
            status_class = "status-active"
        elif status_lower == "inactive":
            status_class = "status-inactive"
        else:
            status_class = "status-neutral"

        safe_customer_name = html_escape(customer_name or "-")
        safe_phone = html_escape(phone_number or "-")
        safe_alt = html_escape(alt_number or "-")
        safe_mobile = html_escape(mobile_number or "-")
        safe_email = html_escape(email_address or "-")
        safe_address = html_escape(customer_address or "-")
        safe_status = html_escape(customer_status or "-")

        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:10px;">
                <div class="info-card"><div class="info-card-label">Customer</div><div class="info-card-value">{safe_customer_name}</div></div>
                <div class="info-card"><div class="info-card-label">Phone</div><div class="info-card-value">{safe_phone}</div></div>
                <div class="info-card"><div class="info-card-label">Alternate</div><div class="info-card-value">{safe_alt}</div></div>
                <div class="info-card"><div class="info-card-label">Mobile</div><div class="info-card-value">{safe_mobile}</div></div>
            </div>
            <div style="display:grid;grid-template-columns:1.15fr 2fr .65fr;gap:10px;margin-bottom:4px;">
                <div class="info-card"><div class="info-card-label">Email</div><div class="info-card-value">{safe_email}</div></div>
                <div class="info-card"><div class="info-card-label">Address</div><div class="info-card-value">{safe_address}</div></div>
                <div class="info-card"><div class="info-card-label">Status</div><div class="status-pill {status_class}">{safe_status}</div></div>
            </div>
            """,
            unsafe_allow_html=True
        )


        st.divider()


    # ======================================================
    # CUSTOMER KPIs
    # ======================================================

    cust_total = (
        customer_invoices[
            "Total"
        ].sum()
    )


    cust_balance = (
        customer_invoices[
            "Calculated Outstanding"
        ].sum()
    )


    cust_paid = (
        customer_invoices[
            "Paid"
        ].sum()
    )


    k1, k2, k3 = st.columns(3)


    if IS_FINANCIAL:

        with k1:
            kpi_card("Total Invoiced", f"£{cust_total:,.2f}")

        with k2:
            kpi_card("Paid", f"£{cust_paid:,.2f}")

        with k3:
            kpi_card("Outstanding", f"£{cust_balance:,.2f}")


    else:

        customer_paid_pct = (
            cust_paid
            /
            cust_total
            *
            100
            if cust_total > 0
            else 0
        )


        customer_outstanding_pct = (
            cust_balance
            /
            cust_total
            *
            100
            if cust_total > 0
            else 0
        )


        with k1:
            kpi_card("Payment Rate", f"{customer_paid_pct:.1f}%")

        with k2:
            kpi_card("Outstanding", f"{customer_outstanding_pct:.1f}%")

        with k3:
            kpi_card("Collection", f"{customer_paid_pct:.1f}%")


    st.divider()


    # ======================================================
    # INVOICE LEDGER
    # ======================================================

    subsection_heading("Invoice Ledger")


    ledger = customer_invoices.copy()


    payment_summary = (
        customer_payments
        .groupby(
            "Invoice Number",
            as_index=False
        )
        .agg(
            Payment_Date=(
                "Date",
                "max"
            ),
            Paid_Amount=(
                "Amount Applied to Invoice",
                "sum"
            )
        )
    )


    ledger = ledger.merge(
        payment_summary,
        on="Invoice Number",
        how="left"
    )


    ledger["Paid_Amount"] = (
        ledger["Paid_Amount"]
        .fillna(0)
    )


    ledger["Outstanding"] = (
        ledger[
            "Calculated Outstanding"
        ]
    )


    # ======================================================
    # SERVICE TYPE
    # DIRECTLY CONCATENATE INVOICE ITEM NAME + ITEM DESC
    # ======================================================

    ledger["Service Type"] = (
        ledger["Item Name"]
        .fillna("")
        .astype(str)
        .str.strip()
        + " "
        + ledger["Item Desc"]
        .fillna("")
        .astype(str)
        .str.strip()
    ).str.strip()


    ledger["Paid_Amount"] = ledger[
        [
            "Paid_Amount",
            "Total"
        ]
    ].min(
        axis=1
    )


    # ======================================================
    # STATUS
    # ======================================================

    today = (
        pd.Timestamp.today()
        .normalize()
    )


    ledger["Status"] = "Current"


    ledger.loc[
        ledger["Due Date"] < today,
        "Status"
    ] = "Overdue"


    ledger.loc[
        (
            ledger[
                "Paid_Amount"
            ]
            > 0
        )
        &
        (
            ledger[
                "Outstanding"
            ]
            > 0
        ),
        "Status"
    ] = "Partially Paid"


    ledger.loc[
        ledger["Outstanding"] <= 0,
        "Status"
    ] = "Paid"


    # ======================================================
    # DAYS OVERDUE
    # ======================================================

    ledger["Days Overdue"] = np.where(
        ledger["Status"].isin(
            [
                "Overdue",
                "Partially Paid"
            ]
        ),
        (
            today
            -
            ledger["Due Date"]
        ).dt.days,
        0
    )


    ledger["Days Overdue"] = (
        ledger[
            "Days Overdue"
        ]
        .fillna(0)
        .astype(int)
    )


    # ======================================================
    # LEDGER DISPLAY
    # ======================================================

    if IS_FINANCIAL:

        ledger = ledger[
            [
                "Invoice Number",
                "Invoice Date",
                "Due Date",
                "Payment_Date",
                "Status",
                "Days Overdue",
                "Service Type",
                "Total",
                "Paid_Amount",
                "Outstanding"
            ]
        ]


        ledger = ledger.rename(
            columns={
                "Invoice Number":
                    "Invoice",

                "Payment_Date":
                    "Payment Date",

                "Total":
                    "Amount (£)",

                "Paid_Amount":
                    "Paid (£)",

                "Outstanding":
                    "Outstanding (£)"
            }
        )


    else:

        ledger["Paid %"] = np.where(
            ledger["Total"] > 0,

            (
                ledger[
                    "Paid_Amount"
                ]
                /
                ledger[
                    "Total"
                ]
            )
            * 100,

            0
        )


        ledger["Outstanding %"] = np.where(
            ledger["Total"] > 0,

            (
                ledger[
                    "Outstanding"
                ]
                /
                ledger[
                    "Total"
                ]
            )
            * 100,

            0
        )


        ledger["Paid %"] = (
            ledger["Paid %"]
            .map(
                lambda x:
                f"{x:.1f}%"
            )
        )


        ledger["Outstanding %"] = (
            ledger["Outstanding %"]
            .map(
                lambda x:
                f"{x:.1f}%"
            )
        )


        ledger = ledger[
            [
                "Invoice Number",
                "Invoice Date",
                "Due Date",
                "Payment_Date",
                "Status",
                "Days Overdue",
                "Service Type",
                "Paid %",
                "Outstanding %"
            ]
        ]


        ledger = ledger.rename(
            columns={
                "Invoice Number":
                    "Invoice",

                "Payment_Date":
                    "Payment Date"
            }
        )


    # ======================================================
    # LEDGER DATES
    # ======================================================

    for col in [
        "Invoice Date",
        "Due Date",
        "Payment Date"
    ]:

        ledger[col] = (
            pd.to_datetime(
                ledger[col],
                errors="coerce"
            )
            .dt.strftime(
                "%d-%m-%Y"
            )
        )


    ledger[
        [
            "Invoice Date",
            "Due Date",
            "Payment Date"
        ]
    ] = (
        ledger[
            [
                "Invoice Date",
                "Due Date",
                "Payment Date"
            ]
        ]
        .fillna("-")
    )


    ledger[
        "Days Overdue"
    ] = (
        ledger[
            "Days Overdue"
        ]
        .replace(
            0,
            "-"
        )
    )


    # ======================================================
    # LEDGER COLOURS
    # ======================================================

    def colour_rows(
        row
    ):

        if row["Status"] == "Paid":

            colour = (
                "background-color:#d4edda;"
                "color:black;"
            )

        elif row["Status"] == "Current":

            colour = (
                "background-color:#fff3cd;"
                "color:black;"
            )

        elif row["Status"] == "Partially Paid":

            colour = (
                "background-color:#ffe599;"
                "color:black;"
            )

        else:

            colour = (
                "background-color:#f8d7da;"
                "color:black;"
            )


        return [
            colour
        ] * len(row)


    # ======================================================
    # CURRENCY
    # ======================================================

    if IS_FINANCIAL:

        currency_columns = [
            "Amount (£)",
            "Paid (£)",
            "Outstanding (£)"
        ]


        for col in currency_columns:

            ledger[col] = (
                ledger[col]
                .apply(
                    lambda x:
                    "-"
                    if pd.isna(x) or x == 0
                    else f"£{x:,.2f}"
                )
            )


    ledger_style = (
        ledger.style
        .apply(
            colour_rows,
            axis=1
        )
    )


    table_caption("Invoice ledger", "Status is derived from payment history and invoice balance")
    st.dataframe(
        ledger_style,
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "No customers match the selected customer filters."
    )


# ==========================================================
# ==========================================================
# PART 4
# PAYMENTS RECEIVED
# ==========================================================
# ==========================================================

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
section_heading(
    "payments-received",
    "03 · Cash Received",
    "Payments Received",
    "Track cash received by actual payment date. Payment filters remain independent from the invoice filters above."
)


st.markdown(
    '<div class="filter-note">Payments use the actual payment date. These filters are completely independent of the invoice dashboard filters above.</div>',
    unsafe_allow_html=True
)


# ==========================================================
# PAYMENT DATE FILTERS
# ==========================================================
#
# IMPORTANT:
#
# We deliberately use the same FIXED 2021-2027 date range
# as the rest of the dashboard.
#
# We do NOT use the minimum/maximum date found in the
# payment file.
#
# This means the user can freely select any date in 2026.
#
# ==========================================================

payment_min_date = date(
    2021,
    1,
    1
)


payment_max_date = date(
    2027,
    12,
    31
)


payment_today = (
    pd.Timestamp.today()
    .date()
)


payment_default_start = date(
    payment_today.year,
    1,
    1
)


payment_default_end = payment_today


with st.container(border=True):
    st.markdown('<div class="kpi-grid-label">Cash period</div>', unsafe_allow_html=True)
    pf1, pf2 = st.columns(2)


    with pf1:

        payment_start_date = st.date_input(
            "Payment Start Date",
            value=payment_default_start,
            min_value=payment_min_date,
            max_value=payment_max_date,
            key="payment_start_date"
        )


    with pf2:

        payment_end_date = st.date_input(
            "Payment End Date",
            value=payment_default_end,
            min_value=payment_min_date,
            max_value=payment_max_date,
            key="payment_end_date"
        )



# ==========================================================
# VALIDATE PAYMENT DATE RANGE
# ==========================================================

if payment_start_date > payment_end_date:

    st.error(
        "Payment Start Date cannot be after "
        "Payment End Date."
    )

else:

    # ======================================================
    # BUILD PAYMENT DATASET
    # ======================================================

    daily_payments = payments.copy()


    # ======================================================
    # REQUIRED COLUMN CHECK
    # ======================================================

    required_payment_columns = [
        "Customer Name",
        "Invoice Number",
        "Date",
        "Invoice Date",
        "Amount Applied to Invoice"
    ]


    missing_payment_columns = [
        col
        for col in required_payment_columns
        if col not in daily_payments.columns
    ]


    if missing_payment_columns:

        st.error(
            "The payment file is missing required columns: "
            +
            ", ".join(
                missing_payment_columns
            )
        )

    else:

        # ==================================================
        # CLEAN PAYMENT COLUMNS
        # ==================================================

        daily_payments[
            "Customer Name"
        ] = (
            daily_payments[
                "Customer Name"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        daily_payments[
            "Invoice Number"
        ] = (
            daily_payments[
                "Invoice Number"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        # --------------------------------------------------
        # ACTUAL PAYMENT DATE
        # --------------------------------------------------

        daily_payments[
            "Date"
        ] = pd.to_datetime(
            daily_payments[
                "Date"
            ],
            errors="coerce"
        )


        # --------------------------------------------------
        # INVOICE DATE
        # --------------------------------------------------

        daily_payments[
            "Invoice Date"
        ] = pd.to_datetime(
            daily_payments[
                "Invoice Date"
            ],
            errors="coerce"
        )


        # --------------------------------------------------
        # PAYMENT AMOUNT
        # --------------------------------------------------

        daily_payments[
            "Amount Applied to Invoice"
        ] = pd.to_numeric(
            daily_payments[
                "Amount Applied to Invoice"
            ],
            errors="coerce"
        ).fillna(0)


        # ==================================================
        # FILTER USING PAYMENT DATE
        # ==================================================

        daily_payments = daily_payments[
            (
                daily_payments[
                    "Date"
                ]
                >= pd.Timestamp(
                    payment_start_date
                )
            )
            &
            (
                daily_payments[
                    "Date"
                ]
                <
                (
                    pd.Timestamp(
                        payment_end_date
                    )
                    +
                    pd.Timedelta(
                        days=1
                    )
                )
            )
        ].copy()


        # ==================================================
        # DUE DATE LOOKUP
        # ==================================================

        invoice_due_lookup = invoices[
            [
                "Invoice Number",
                "Due Date"
            ]
        ].copy()


        invoice_due_lookup[
            "Invoice Number"
        ] = (
            invoice_due_lookup[
                "Invoice Number"
            ]
            .astype(str)
            .str.strip()
        )


        invoice_due_lookup = (
            invoice_due_lookup
            .drop_duplicates(
                subset="Invoice Number",
                keep="first"
            )
        )


        # ==================================================
        # MERGE ONLY DUE DATE
        # ==================================================

        daily_payments = (
            daily_payments
            .merge(
                invoice_due_lookup,
                on="Invoice Number",
                how="left"
            )
        )


        # ==================================================
        # PAYMENT DAY
        # ==========================================================

        daily_payments[
            "Payment Day"
        ] = (
            daily_payments[
                "Date"
            ]
            .dt.normalize()
        )


        # ==================================================
        # KPI VALUES
        # ==========================================================

        payment_total = (
            daily_payments[
                "Amount Applied to Invoice"
            ].sum()
        )


        payment_entry_count = (
            len(
                daily_payments
            )
        )


        payment_customer_count = (
            daily_payments[
                "Customer Name"
            ]
            .replace(
                "",
                np.nan
            )
            .nunique()
        )


        payment_invoice_count = (
            daily_payments[
                "Invoice Number"
            ]
            .replace(
                "",
                np.nan
            )
            .nunique()
        )


        # ==================================================
        # PAYMENT KPI CARDS
        # ==================================================

        st.markdown('<div class="kpi-grid-label">Selected payment period</div>', unsafe_allow_html=True)
        pk1, pk2, pk3, pk4 = st.columns(4)


        with pk1:

            kpi_card(
                "💷 Payments Received",
                f"£{payment_total:,.2f}"
            )


        with pk2:

            kpi_card(
                "🧾 Payment Entries",
                f"{payment_entry_count:,}"
            )


        with pk3:

            kpi_card(
                "👥 Customers",
                f"{payment_customer_count:,}"
            )


        with pk4:

            kpi_card(
                "📄 Invoices Paid",
                f"{payment_invoice_count:,}"
            )


        # ==================================================
        # DAILY PAYMENT SUMMARY
        # ==================================================

        subsection_heading("Daily Payment Summary")


        if daily_payments.empty:

            st.info(
                "No payments were received during "
                "the selected payment date range."
            )

        else:

            # ------------------------------------------------
            # IMPORTANT FIX:
            #
            # Do not create "Payment Received" and then
            # rename another column to the same name.
            #
            # We build the final dataframe only once.
            # ------------------------------------------------

            daily_summary = (
                daily_payments
                .groupby(
                    "Payment Day",
                    as_index=False
                )
                .agg(
                    Payment_Entries=(
                        "Amount Applied to Invoice",
                        "count"
                    ),

                    Customers=(
                        "Customer Name",
                        "nunique"
                    ),

                    Invoices=(
                        "Invoice Number",
                        "nunique"
                    ),

                    Payment_Received=(
                        "Amount Applied to Invoice",
                        "sum"
                    )
                )
                .sort_values(
                    "Payment Day",
                    ascending=False
                )
                .reset_index(
                    drop=True
                )
            )


            # ------------------------------------------------
            # FORMAT DATE
            # ------------------------------------------------

            daily_summary[
                "Payment Date"
            ] = (
                daily_summary[
                    "Payment Day"
                ]
                .dt.strftime(
                    "%d-%m-%Y"
                )
            )


            # ------------------------------------------------
            # FORMAT MONEY
            # ------------------------------------------------

            daily_summary[
                "Payment Received"
            ] = (
                daily_summary[
                    "Payment_Received"
                ]
                .apply(
                    lambda x:
                    f"£{x:,.2f}"
                )
            )


            # ------------------------------------------------
            # FINAL COLUMN SELECTION
            #
            # This guarantees unique column names.
            # ------------------------------------------------

            daily_summary = daily_summary[
                [
                    "Payment Date",
                    "Payment_Entries",
                    "Customers",
                    "Invoices",
                    "Payment Received"
                ]
            ].copy()


            # ------------------------------------------------
            # RENAME ONLY UNIQUE COLUMNS
            # ------------------------------------------------

            daily_summary = (
                daily_summary
                .rename(
                    columns={
                        "Payment_Entries":
                            "Payment Entries"
                    }
                )
            )


            # ------------------------------------------------
            # TOTAL ROW
            # ------------------------------------------------

            daily_payment_total = pd.DataFrame(
                [{
                    "Payment Date":
                        "TOTAL",

                    "Payment Entries":
                        payment_entry_count,

                    "Customers":
                        payment_customer_count,

                    "Invoices":
                        payment_invoice_count,

                    "Payment Received":
                        f"£{payment_total:,.2f}"
                }]
            )


            daily_summary = pd.concat(
                [
                    daily_summary,
                    daily_payment_total
                ],
                ignore_index=True
            )


            # ------------------------------------------------
            # FINAL SAFETY CHECK
            # ------------------------------------------------

            daily_summary.columns = (
                daily_summary.columns
                .astype(str)
                .str.strip()
            )


            # ------------------------------------------------
            # Display
            # ------------------------------------------------

            table_caption("Daily cash received", "Grouped by the actual payment date")
            st.dataframe(
                daily_summary,
                width="stretch",
                hide_index=True
            )


            # ==================================================
            # PAYMENT DETAILS
            # ==================================================

            subsection_heading("Payment Details")


            # ------------------------------------------------
            # SERVICE TYPE FROM INVOICE TABLE
            # DIRECTLY CONCATENATE ITEM NAME + ITEM DESC
            # ------------------------------------------------

            invoice_service_lookup = invoices[
                [
                    "Invoice Number",
                    "Item Name",
                    "Item Desc"
                ]
            ].copy()

            invoice_service_lookup[
                "Invoice Number"
            ] = (
                invoice_service_lookup[
                    "Invoice Number"
                ]
                .astype(str)
                .str.strip()
            )

            invoice_service_lookup[
                "Service Type"
            ] = (
                invoice_service_lookup[
                    "Item Name"
                ]
                .fillna("")
                .astype(str)
                .str.strip()
                + " "
                + invoice_service_lookup[
                    "Item Desc"
                ]
                .fillna("")
                .astype(str)
                .str.strip()
            ).str.strip()

            invoice_service_lookup = (
                invoice_service_lookup[
                    [
                        "Invoice Number",
                        "Service Type"
                    ]
                ]
                .drop_duplicates(
                    subset="Invoice Number",
                    keep="first"
                )
            )

            payment_details = (
                daily_payments[
                    [
                        "Customer Name",
                        "Invoice Number",
                        "Invoice Date",
                        "Due Date",
                        "Date",
                        "Amount Applied to Invoice"
                    ]
                ]
                .copy()
            )

            payment_details[
                "Invoice Number"
            ] = (
                payment_details[
                    "Invoice Number"
                ]
                .astype(str)
                .str.strip()
            )

            payment_details = (
                payment_details
                .merge(
                    invoice_service_lookup,
                    on="Invoice Number",
                    how="left"
                )
            )


            # ------------------------------------------------
            # RENAME
            # ------------------------------------------------

            payment_details = (
                payment_details
                .rename(
                    columns={
                        "Invoice Number":
                            "Invoice",

                        "Date":
                            "Payment Date",

                        "Amount Applied to Invoice":
                            "Payment Received (£)"
                    }
                )
            )


            # ------------------------------------------------
            # FORMAT DATES
            # ------------------------------------------------

            for col in [
                "Invoice Date",
                "Due Date",
                "Payment Date"
            ]:

                payment_details[col] = (
                    pd.to_datetime(
                        payment_details[col],
                        errors="coerce"
                    )
                    .dt.strftime(
                        "%d-%m-%Y"
                    )
                )


            payment_details[
                [
                    "Invoice Date",
                    "Due Date",
                    "Payment Date"
                ]
            ] = (
                payment_details[
                    [
                        "Invoice Date",
                        "Due Date",
                        "Payment Date"
                    ]
                ]
                .fillna("-")
            )


            # ------------------------------------------------
            # FORMAT PAYMENT AMOUNT
            # ------------------------------------------------

            payment_details[
                "Payment Received (£)"
            ] = (
                payment_details[
                    "Payment Received (£)"
                ]
                .apply(
                    lambda x:
                    f"£{x:,.2f}"
                )
            )


            # ------------------------------------------------
            # SORT BY PAYMENT DATE
            # ------------------------------------------------

            payment_details = (
                payment_details
                .sort_values(
                    "Payment Date",
                    ascending=False
                )
                .reset_index(
                    drop=True
                )
            )


            # ------------------------------------------------
            # FINAL COLUMN ORDER
            # ------------------------------------------------

            payment_details = payment_details[
                [
                    "Customer Name",
                    "Service Type",
                    "Invoice",
                    "Invoice Date",
                    "Due Date",
                    "Payment Date",
                    "Payment Received (£)"
                ]
            ]


            table_caption("Payment details", "Service text is taken directly from Invoice Item Name + Item Desc")
            st.dataframe(
                payment_details,
                width="stretch",
                hide_index=True
            )


# ==========================================================
# POLISHED FOOTER
# ==========================================================

st.markdown(
    '<div class="footer-note">FastRanking Payments Dashboard · Accounts receivable, customer drilldown and cash received</div>',
    unsafe_allow_html=True
)
