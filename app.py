# ==========================================================
# ZOHO ACCOUNTS RECEIVABLE DASHBOARD
# COMPLETE SCRIPT
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests

from datetime import date


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

    if st.session_state.get("authenticated", False):
        return True

    st.markdown(
        """
        <style>

        .login-container {
            max-width: 420px;
            margin: 80px auto;
            padding: 30px;
            border: 1px solid #e6e6e6;
            border-radius: 14px;
            background: #ffffff;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }

        .login-title {
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .login-subtitle {
            text-align: center;
            color: #666666;
            margin-bottom: 25px;
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
        '<div class="login-title">🔐 Login</div>',
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

    if login_clicked:

        email = email.strip().lower()

        users = st.secrets.get("users", {})

        if (
            email in users
            and password == users[email].get("password", "")
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


# ==========================================================
# LOGOUT
# ==========================================================

with st.sidebar:

    st.write(
        f"👤 {st.session_state.get('logged_in_email', '')}"
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
# TITLE
# ==========================================================

st.title(
    "💰 FastRanking Payments Dashboard"
)


# ==========================================================
# KPI CSS
# ==========================================================

st.markdown(
    """
    <style>

    .kpi-card{
        background:#ffffff;
        border:1px solid #e6e6e6;
        border-radius:12px;
        padding:14px;
        text-align:center;
        box-shadow:0 1px 6px rgba(0,0,0,0.08);
        margin-bottom:10px;
        min-height:118px;
        box-sizing:border-box;
        display:flex;
        flex-direction:column;
        justify-content:center;
    }

    .kpi-title{
        font-size:15px;
        color:#666666;
        margin-bottom:6px;
        font-weight:600;
        line-height:1.2;
    }

    .kpi-value{
        font-size:28px;
        font-weight:700;
        color:#111111;
        line-height:1.1;
    }

    .kpi-percentage{
        font-size:12px;
        color:#888888;
        font-weight:500;
        margin-top:4px;
        line-height:16px;
    }

    </style>
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
            f'{percentage:.1f}%'
            f'</div>'
        )

    else:

        percentage_html = ""

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
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
    # DATE COLUMNS
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


    # ------------------------------------------------------
    # PAYMENT DATE
    # ------------------------------------------------------

    if "Date" in payments.columns:

        payments["Date"] = pd.to_datetime(
            payments["Date"],
            dayfirst=True,
            errors="coerce"
        )


    # ------------------------------------------------------
    # PAYMENT INVOICE DATE
    # ------------------------------------------------------

    if "Invoice Date" in payments.columns:

        payments["Invoice Date"] = pd.to_datetime(
            payments["Invoice Date"],
            dayfirst=True,
            errors="coerce"
        )


    # ------------------------------------------------------
    # INVOICE PAYMENT APPLIED DATE
    # ------------------------------------------------------

    if "Invoice Payment Applied Date" in payments.columns:

        payments["Invoice Payment Applied Date"] = pd.to_datetime(
            payments["Invoice Payment Applied Date"],
            dayfirst=True,
            errors="coerce"
        )


    # ------------------------------------------------------
    # AR DATES
    # ------------------------------------------------------

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
    # NUMERIC COLUMNS
    # ======================================================

    invoice_numeric = [
        "Total",
        "Balance",
        "SubTotal"
    ]

    for col in invoice_numeric:

        if col in invoices.columns:

            invoices[col] = pd.to_numeric(
                invoices[col],
                errors="coerce"
            ).fillna(0)


    payment_numeric = [
        "Amount",
        "Amount Applied to Invoice"
    ]

    for col in payment_numeric:

        if col in payments.columns:

            payments[col] = pd.to_numeric(
                payments[col],
                errors="coerce"
            ).fillna(0)


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
    # REMOVE DUPLICATE INVOICES
    # ======================================================

    invoices = (
        invoices
        .sort_values("Invoice Date")
        .drop_duplicates(
            subset="Invoice Number",
            keep="first"
        )
        .reset_index(drop=True)
    )


    # ======================================================
    # CUSTOMER FIRST INVOICE
    # ======================================================

    customer_first_invoice = (
        invoices
        .groupby("Customer Name")["Invoice Date"]
        .min()
    )


    invoices["First Customer Invoice Date"] = (
        invoices["Customer Name"]
        .map(customer_first_invoice)
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
        - invoices["Paid"]
    ).clip(
        lower=0
    )


    invoices["Outstanding"] = (
        invoices["Calculated Outstanding"]
    )


    # ======================================================
    # CUSTOMER CLASSIFICATION
    # ======================================================

    customer_first_invoice = (
        invoices
        .groupby("Customer Name")["Invoice Date"]
        .min()
    )


    invoices["First Customer Invoice Date"] = (
        invoices["Customer Name"]
        .map(customer_first_invoice)
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
        - invoices["Balance"]
    )


    invoices["Balance Reconciles"] = (
        invoices["Balance Difference"]
        .abs()
        <= 0.01
    )


    # ======================================================
    # RECONCILIATION
    # ======================================================

    invoice_total_check = (
        invoices["Total"].sum()
    )

    invoice_paid_check = (
        invoices["Paid"].sum()
    )

    invoice_outstanding_check = (
        invoices["Calculated Outstanding"].sum()
    )

    reconciliation_difference = (
        invoice_total_check
        - invoice_paid_check
        - invoice_outstanding_check
    )


    print(
        f"Invoice Total       : £{invoice_total_check:,.2f}"
    )

    print(
        f"Payments Applied    : £{invoice_paid_check:,.2f}"
    )

    print(
        f"Calculated Pending  : £{invoice_outstanding_check:,.2f}"
    )

    print(
        f"Reconciliation Diff : £{reconciliation_difference:,.2f}"
    )


    # ======================================================
    # RECONCILIATION ISSUES
    # ======================================================

    reconciliation_issues = invoices[
        invoices["Balance Difference"]
        .abs()
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
    # CLEAN AR INVOICE NUMBERS
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
    # REMOVE DUPLICATE AR INVOICES
    # ======================================================

    ar_reference = (
        ar_reference
        .drop_duplicates(
            subset="Invoice Number",
            keep="first"
        )
        .reset_index(drop=True)
    )


    # ======================================================
    # MATCH AR WITH INVOICES
    # ======================================================

    invoice_reference = invoices[
        [
            "Invoice Number",
            "Outstanding",
            "Due Date"
        ]
    ].copy()


    invoice_reference["Invoice Number"] = (
        invoice_reference["Invoice Number"]
        .astype(str)
        .str.strip()
    )


    invoice_reference = invoice_reference.rename(
        columns={
            "Outstanding":
                "Invoice Outstanding"
        }
    )


    ar_reconciliation = ar_reference.merge(
        invoice_reference,
        on="Invoice Number",
        how="outer",
        indicator=True
    )


    ar_reconciliation["Invoice Outstanding"] = (
        ar_reconciliation["Invoice Outstanding"]
        .fillna(0)
    )


    ar_reconciliation["AR Balance"] = (
        ar_reconciliation["AR Balance"]
        .fillna(0)
    )


    ar_reconciliation["Difference"] = (
        ar_reconciliation["Invoice Outstanding"]
        - ar_reconciliation["AR Balance"]
    )


    # ======================================================
    # AR MISMATCHES
    # ======================================================

    ar_mismatches = ar_reconciliation[
        (
            ar_reconciliation["Difference"]
            .abs()
            > 0.01
        )
        |
        (
            ar_reconciliation["_merge"]
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
        .sort_values("Month")
    )


    # ======================================================
    # GLOBAL KPIs
    # ======================================================

    total_customers = (
        invoices["Customer Name"]
        .nunique()
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
# LOAD
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
# MAIN FILTERS
# ==========================================================

st.subheader("Filters")


f1, f2, f3, f4, f5 = st.columns(5)


# ==========================================================
# MAIN DATE FILTER
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


current_year = pd.Timestamp.today().year


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
# INVOICE TYPE
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
# CUSTOMER STATUS
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
# APPLY MAIN FILTERS
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
        display_df["Service Type"]
        ==
        selected_service
    ].copy()


if selected_invoice_type != "All Invoices":

    display_df = display_df[
        display_df["Invoice Type"]
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
        display_df["Customer Name"]
        .astype(str)
        .str.strip()
        .isin(selected_status_customers)
    ].copy()


# ==========================================================
# MAIN KPIs
# ==========================================================

total_customers = (
    display_df["Customer Name"]
    .nunique()
)

total_invoices = (
    display_df["Invoice Number"]
    .nunique()
)

total_invoiced = (
    display_df["Total"].sum()
)

total_paid = (
    display_df["Paid"].sum()
)


collection_rate = (
    total_paid
    / total_invoiced
    * 100
    if total_invoiced > 0
    else 0
)


# ==========================================================
# AR
# ==========================================================

today = (
    pd.Timestamp.today()
    .normalize()
)


overdue_df = display_df[
    (display_df["Outstanding"] > 0)
    &
    (display_df["Due Date"] <= today)
].copy()


overdue_due = (
    overdue_df["Outstanding"].sum()
)


future_df = display_df[
    (display_df["Outstanding"] > 0)
    &
    (display_df["Due Date"] > today)
].copy()


future_due = (
    future_df["Outstanding"].sum()
)


total_pending = (
    overdue_due
    +
    future_due
)


invoice_balance = (
    display_df["Outstanding"].sum()
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

    st.subheader(
        "Unclassified Invoices"
    )

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
    / total_invoiced
    * 100
    if total_invoiced > 0
    else 0
)


pending_percentage = (
    total_pending
    / total_invoiced
    * 100
    if total_invoiced > 0
    else 0
)


future_percentage = (
    future_due
    / total_invoiced
    * 100
    if total_invoiced > 0
    else 0
)


overdue_percentage = (
    overdue_due
    / total_invoiced
    * 100
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
        / total_invoiced
        * 100
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
    display_df["Invoice Number"]
    .astype(str)
    .str.strip()
)


filtered_ar_mismatches = ar_mismatches[
    ar_mismatches["Invoice Number"]
    .astype(str)
    .str.strip()
    .isin(filtered_invoice_numbers)
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

st.subheader(
    "Monthly Invoice Summary"
)


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
    .sort_values("Month")
    .reset_index(drop=True)
)


# ==========================================================
# PAYMENT MONTH ANALYSIS
# ==========================================================

filtered_invoice_numbers = set(
    display_df["Invoice Number"]
    .astype(str)
    .str.strip()
)


monthly_payments = payments[
    payments["Invoice Number"]
    .astype(str)
    .str.strip()
    .isin(filtered_invoice_numbers)
].copy()


# ==========================================================
# ORIGINAL INVOICE DATE
# ==========================================================

invoice_dates_lookup = invoices[
    [
        "Invoice Number",
        "Invoice Date"
    ]
].copy()


invoice_dates_lookup["Invoice Number"] = (
    invoice_dates_lookup["Invoice Number"]
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
    monthly_payments["Invoice Number"]
    .astype(str)
    .str.strip()
)


monthly_payments = monthly_payments.merge(
    invoice_dates_lookup,
    on="Invoice Number",
    how="left"
)


# ==========================================================
# PAYMENT MONTH
# ==========================================================

monthly_payments["Payment Month"] = (
    monthly_payments["Date"]
    .dt.to_period("M")
    .astype(str)
)


# ==========================================================
# ORIGINAL INVOICE MONTH
# ==========================================================

monthly_payments["Invoice Month"] = (
    monthly_payments["Original Invoice Date"]
    .dt.to_period("M")
    .astype(str)
)


# ==========================================================
# PAYMENT TYPE
# ==========================================================

monthly_payments["Payment Type"] = np.where(
    monthly_payments["Payment Month"]
    ==
    monthly_payments["Invoice Month"],
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


if "Current Invoice" not in monthly_payment_summary.columns:

    monthly_payment_summary[
        "Current Invoice"
    ] = 0


if "Older Invoice" not in monthly_payment_summary.columns:

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


monthly_payment_summary["Total_Paid"] = (
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
    .reset_index(drop=True)
)


# ==========================================================
# FINANCIAL MONTHLY VIEW
# ==========================================================

if IS_FINANCIAL:

    monthly_total_row = pd.DataFrame([{

        "Month": "TOTAL",

        "Customers":
            display_df[
                "Customer Name"
            ].nunique(),

        "Invoices":
            display_df[
                "Invoice Number"
            ].nunique(),

        "Total_Invoiced":
            display_df["Total"].sum(),

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

    }])


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
        display_df["Total"].sum()
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


    percentage_total_row = pd.DataFrame([{

        "Month": "TOTAL",

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
            / total_invoice
            * 100
            if total_invoice > 0
            else 0
        ),

        "Paid – Older %": (
            total_paid_older
            / total_invoice
            * 100
            if total_invoice > 0
            else 0
        ),

        "Total Paid %": (
            total_paid_value
            / total_invoice
            * 100
            if total_invoice > 0
            else 0
        ),

        "Outstanding %": (
            total_outstanding
            / total_invoice
            * 100
            if total_invoice > 0
            else 0
        )

    }])


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


    st.dataframe(
        monthly_percentage,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# CUSTOMER MONTHLY BREAKDOWN
# ==========================================================

st.divider()

st.subheader(
    "Customer Invoice Breakdown"
)


show_outstanding_only = st.checkbox(
    "Show Outstanding Customers Only",
    value=True
)


months = sorted(
    display_df["Month"].unique()
)


rows = []


# ==========================================================
# CUSTOMER PAYMENT MATRIX
# ==========================================================

for customer in sorted(
    display_df[
        "Customer Name"
    ]
    .dropna()
    .unique()
):

    row = {
        "Customer Name": customer
    }


    customer_df = display_df[
        display_df["Customer Name"]
        ==
        customer
    ]


    total_invoice = (
        customer_df["Total"].sum()
    )


    total_paid = (
        customer_df["Paid"].sum()
    )


    for month in months:

        month_df = customer_df[
            customer_df["Month"]
            ==
            month
        ]


        invoice_value = (
            month_df["Total"].sum()
        )


        paid_value = (
            month_df["Paid"].sum()
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
                    / invoice_value
                ) * 100

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
                / total_invoice
            ) * 100

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

        def has_outstanding(total_value):

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

        def has_outstanding(total_value):

            if total_value == "-":
                return False

            percentage = float(
                total_value
                .replace("%", "")
                .strip()
            )

            return percentage < 100


    customer_table = customer_table[
        customer_table["Total"]
        .apply(has_outstanding)
    ]


# ==========================================================
# GRAND TOTAL
# ==========================================================

visible_customers = (
    customer_table[
        "Customer Name"
    ].tolist()
)


grand_total_df = display_df[
    display_df["Customer Name"]
    .isin(visible_customers)
].copy()


grand_row = {
    "Customer Name":
        "GRAND TOTAL"
}


grand_total_invoice = (
    grand_total_df["Total"].sum()
)


grand_total_paid = (
    grand_total_df["Paid"].sum()
)


for month in months:

    month_df = grand_total_df[
        grand_total_df["Month"]
        ==
        month
    ]


    month_invoice = (
        month_df["Total"].sum()
    )


    month_paid = (
        month_df["Paid"].sum()
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
                / month_invoice
            ) * 100

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
            / grand_total_invoice
        ) * 100

        grand_row["Total"] = (
            f"{grand_total_paid_pct:.1f}%"
        )


customer_table = pd.concat(
    [
        customer_table,
        pd.DataFrame([grand_row])
    ],
    ignore_index=True
)


# ==========================================================
# CUSTOMER TABLE COLOURS
# ==========================================================

def colour_cells(value):

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
    customer_table.style
    .map(
        colour_cells,
        subset=customer_table.columns[1:]
    )
)


def highlight_grand_total(row):

    if row["Customer Name"] == "GRAND TOTAL":

        return [
            "font-weight:bold; "
            "background-color:#e6e6e6;"
        ] * len(row)

    return [""] * len(row)


styled = styled.apply(
    highlight_grand_total,
    axis=1
)


st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True
)


# ==========================================================
# PART 3
# CUSTOMER DRILLDOWN
# ==========================================================

st.divider()

st.header(
    "🔍 Customer Details"
)


# ==========================================================
# CUSTOMER FILTERS
# ==========================================================

st.subheader(
    "Customer Filters"
)


cf1, cf2, cf3, cf4, cf5 = st.columns(5)


with cf1:

    customer_start_date = st.date_input(
        "Customer Start Date",
        value=date(
            pd.Timestamp.today().year,
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
            pd.Timestamp.today().year,
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


    customer_selected_invoice_type = st.selectbox(
        "Invoice Type",
        customer_invoice_type_options,
        key="customer_invoice_type"
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
        >= pd.Timestamp(customer_start_date)
    )
    &
    (
        invoices["Invoice Date"]
        <= pd.Timestamp(customer_end_date)
    )
].copy()


if customer_selected_service != "All Services":

    customer_display_df = customer_display_df[
        customer_display_df["Service Type"]
        ==
        customer_selected_service
    ].copy()


if customer_selected_invoice_type != "All Invoices":

    customer_display_df = customer_display_df[
        customer_display_df["Invoice Type"]
        ==
        customer_selected_invoice_type
    ].copy()


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


    customer_display_df = customer_display_df[
        customer_display_df["Customer Name"]
        .astype(str)
        .str.strip()
        .isin(selected_status_customers)
    ].copy()


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

else:

    st.info(
        "No customers match the selected filters."
    )

    st.stop()


# ==========================================================
# CUSTOMER DATA
# ==========================================================

customer_invoices = customer_display_df[
    customer_display_df["Customer Name"]
    ==
    selected_customer
].copy()


customer_payments = payments[
    payments["Customer Name"]
    ==
    selected_customer
].copy()


# ==========================================================
# CUSTOMER INFORMATION
# ==========================================================

customer_info = contacts[
    contacts["Display Name"]
    .astype(str)
    .str.strip()
    ==
    str(selected_customer).strip()
].copy()


if not customer_info.empty:

    info = customer_info.iloc[0]


    st.subheader(
        "Customer Information"
    )


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

            value = str(value).strip()

            if value:

                address_parts.append(
                    value
                )


    customer_address = ", ".join(
        address_parts
    )


    c1, c2 = st.columns(2)


    with c1:

        st.write(
            "**Customer Name:**",
            customer_name or "-"
        )

        st.write(
            "**Phone Number:**",
            phone_number or "-"
        )

        st.write(
            "**Alt Number:**",
            alt_number or "-"
        )

        st.write(
            "**Mobile Number:**",
            mobile_number or "-"
        )


    with c2:

        st.write(
            "**Email:**",
            email_address or "-"
        )

        st.write(
            "**Address:**",
            customer_address or "-"
        )

        st.write(
            "**Status:**",
            customer_status or "-"
        )


    st.divider()


# ==========================================================
# CUSTOMER KPIs
# ==========================================================

cust_total = (
    customer_invoices["Total"].sum()
)

cust_balance = (
    customer_invoices[
        "Calculated Outstanding"
    ].sum()
)

cust_paid = (
    customer_invoices["Paid"].sum()
)


k1, k2, k3 = st.columns(3)


if IS_FINANCIAL:

    with k1:

        st.metric(
            "Total Invoiced",
            f"£{cust_total:,.2f}"
        )


    with k2:

        st.metric(
            "Paid",
            f"£{cust_paid:,.2f}"
        )


    with k3:

        st.metric(
            "Outstanding",
            f"£{cust_balance:,.2f}"
        )


else:

    customer_paid_pct = (
        cust_paid
        / cust_total
        * 100
        if cust_total > 0
        else 0
    )


    customer_outstanding_pct = (
        cust_balance
        / cust_total
        * 100
        if cust_total > 0
        else 0
    )


    with k1:

        st.metric(
            "Payment Rate",
            f"{customer_paid_pct:.1f}%"
        )


    with k2:

        st.metric(
            "Outstanding",
            f"{customer_outstanding_pct:.1f}%"
        )


    with k3:

        st.metric(
            "Collection",
            f"{customer_paid_pct:.1f}%"
        )


st.divider()


# ==========================================================
# INVOICE LEDGER
# ==========================================================

st.subheader(
    "Invoice Ledger"
)


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
    ledger["Calculated Outstanding"]
)


ledger["Paid_Amount"] = ledger[
    [
        "Paid_Amount",
        "Total"
    ]
].min(axis=1)


# ==========================================================
# LEDGER STATUS
# ==========================================================

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
    (ledger["Paid_Amount"] > 0)
    &
    (ledger["Outstanding"] > 0),
    "Status"
] = "Partially Paid"


ledger.loc[
    ledger["Outstanding"] <= 0,
    "Status"
] = "Paid"


# ==========================================================
# DAYS OVERDUE
# ==========================================================

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
    ledger["Days Overdue"]
    .fillna(0)
    .astype(int)
)


# ==========================================================
# LEDGER DISPLAY
# ==========================================================

if IS_FINANCIAL:

    ledger = ledger[
        [
            "Invoice Number",
            "Invoice Date",
            "Due Date",
            "Payment_Date",
            "Status",
            "Days Overdue",
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
            ledger["Paid_Amount"]
            /
            ledger["Total"]
        )
        * 100,

        0
    )


    ledger["Outstanding %"] = np.where(
        ledger["Total"] > 0,

        (
            ledger["Outstanding"]
            /
            ledger["Total"]
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


# ==========================================================
# FORMAT LEDGER DATES
# ==========================================================

date_columns = [
    "Invoice Date",
    "Due Date",
    "Payment Date"
]


for col in date_columns:

    ledger[col] = pd.to_datetime(
        ledger[col],
        errors="coerce"
    ).dt.strftime(
        "%d-%m-%Y"
    )


ledger[date_columns] = (
    ledger[date_columns]
    .fillna("-")
)


ledger["Days Overdue"] = (
    ledger["Days Overdue"]
    .replace(0, "-")
)


# ==========================================================
# LEDGER ROW COLOURS
# ==========================================================

def colour_rows(row):

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


# ==========================================================
# CURRENCY
# ==========================================================

if IS_FINANCIAL:

    currency_columns = [
        "Amount (£)",
        "Paid (£)",
        "Outstanding (£)"
    ]


    for col in currency_columns:

        ledger[col] = ledger[col].apply(
            lambda x:
                "-"
                if pd.isna(x) or x == 0
                else f"£{x:,.2f}"
        )


ledger_style = (
    ledger.style
    .apply(
        colour_rows,
        axis=1
    )
)


st.dataframe(
    ledger_style,
    width="stretch",
    hide_index=True
)


# ==========================================================
# ==========================================================
# PART 4
# PAYMENTS RECEIVED
# ==========================================================
# ==========================================================
#
# IMPORTANT:
#
# THIS SECTION IS COMPLETELY INDEPENDENT FROM:
#
#   - Main invoice date filter
#   - Service filter
#   - Invoice type filter
#   - Customer status filter
#   - Customer drilldown filters
#
# It uses the ACTUAL PAYMENT DATE from:
#
#     payments["Date"]
#
# ==========================================================

st.divider()

st.header(
    "💷 Payments Received"
)


st.caption(
    "Independent view based on the actual date "
    "the payment was received."
)


# ==========================================================
# PAYMENT DATE FILTERS
# ==========================================================

pf1, pf2 = st.columns(2)


# ----------------------------------------------------------
# Available payment dates
# ----------------------------------------------------------

valid_payment_dates = payments[
    "Date"
].dropna()


if not valid_payment_dates.empty:

    payment_min_available = (
        valid_payment_dates.min().date()
    )

    payment_max_available = (
        valid_payment_dates.max().date()
    )

else:

    payment_min_available = date(
        2021,
        1,
        1
    )

    payment_max_available = (
        pd.Timestamp.today()
        .date()
    )


# ----------------------------------------------------------
# Default payment dates
#
# Default:
# last 12 months
# ----------------------------------------------------------

today_date = (
    pd.Timestamp.today()
    .date()
)


default_payment_end = min(
    today_date,
    payment_max_available
)


default_payment_start = max(
    payment_min_available,
    (
        pd.Timestamp(
            default_payment_end
        )
        -
        pd.DateOffset(months=12)
    ).date()
)


with pf1:

    payment_start_date = st.date_input(
        "Payment Start Date",
        value=default_payment_start,
        min_value=payment_min_available,
        max_value=payment_max_available,
        key="payment_start_date"
    )


with pf2:

    payment_end_date = st.date_input(
        "Payment End Date",
        value=default_payment_end,
        min_value=payment_min_available,
        max_value=payment_max_available,
        key="payment_end_date"
    )


# ==========================================================
# VALIDATE PAYMENT DATES
# ==========================================================

if payment_start_date > payment_end_date:

    st.error(
        "Payment Start Date cannot be after "
        "Payment End Date."
    )

    st.stop()


# ==========================================================
# BUILD PAYMENT DATASET
# ==========================================================
#
# DO NOT start from invoices here.
#
# The payment file already contains:
#
#   Customer Name
#   Invoice Number
#   Invoice Date
#   Date
#   Amount Applied to Invoice
#
# We only look up Due Date from invoices.
# ==========================================================

daily_payments = payments.copy()


# ----------------------------------------------------------
# Make absolutely sure payment date is datetime
# ----------------------------------------------------------

daily_payments["Date"] = pd.to_datetime(
    daily_payments["Date"],
    errors="coerce"
)


# ----------------------------------------------------------
# Clean invoice numbers
# ----------------------------------------------------------

daily_payments["Invoice Number"] = (
    daily_payments["Invoice Number"]
    .astype(str)
    .str.strip()
)


# ----------------------------------------------------------
# Clean customer names
# ----------------------------------------------------------

daily_payments["Customer Name"] = (
    daily_payments["Customer Name"]
    .astype(str)
    .str.strip()
)


# ==========================================================
# FILTER BY ACTUAL PAYMENT DATE
# ==========================================================

daily_payments = daily_payments[
    (
        daily_payments["Date"]
        >= pd.Timestamp(
            payment_start_date
        )
    )
    &
    (
        daily_payments["Date"]
        <
        (
            pd.Timestamp(
                payment_end_date
            )
            +
            pd.Timedelta(days=1)
        )
    )
].copy()


# ==========================================================
# LOOK UP DUE DATE
# ==========================================================
#
# IMPORTANT:
#
# We ONLY bring Due Date from invoices.
#
# Customer Name is NOT taken from invoices.
# Invoice Date is NOT taken from invoices.
#
# This prevents the Customer Name KeyError / merge
# collision problem from the previous implementation.
# ==========================================================

due_date_lookup = invoices[
    [
        "Invoice Number",
        "Due Date"
    ]
].copy()


due_date_lookup["Invoice Number"] = (
    due_date_lookup["Invoice Number"]
    .astype(str)
    .str.strip()
)


# ----------------------------------------------------------
# Ensure one row per invoice
# ----------------------------------------------------------

due_date_lookup = (
    due_date_lookup
    .drop_duplicates(
        subset="Invoice Number",
        keep="first"
    )
)


# ==========================================================
# MERGE ONLY DUE DATE
# ==========================================================

daily_payments = daily_payments.merge(
    due_date_lookup,
    on="Invoice Number",
    how="left"
)


# ==========================================================
# PAYMENT AMOUNT
# ==========================================================

daily_payments[
    "Amount Applied to Invoice"
] = pd.to_numeric(
    daily_payments[
        "Amount Applied to Invoice"
    ],
    errors="coerce"
).fillna(0)


# ==========================================================
# DAILY PAYMENT SUMMARY
# ==========================================================

daily_payment_summary = (
    daily_payments
    .groupby(
        "Date",
        as_index=False
    )
    .agg(
        Customers=(
            "Customer Name",
            "nunique"
        ),
        Payments=(
            "Invoice Payment ID",
            "nunique"
        ),
        Amount=(
            "Amount Applied to Invoice",
            "sum"
        )
    )
    .sort_values("Date")
)


# ==========================================================
# DISPLAY DAILY SUMMARY
# ==========================================================

if not daily_payment_summary.empty:

    st.subheader(
        "Daily Payment Summary"
    )


    daily_payment_display = (
        daily_payment_summary.copy()
    )


    daily_payment_display[
        "Date"
    ] = pd.to_datetime(
        daily_payment_display["Date"]
    ).dt.strftime(
        "%d-%m-%Y"
    )


    daily_payment_display[
        "Amount"
    ] = daily_payment_display[
        "Amount"
    ].apply(
        lambda x:
            f"£{x:,.2f}"
    )


    daily_payment_display = (
        daily_payment_display
        .rename(
            columns={
                "Date":
                    "Payment Date",

                "Customers":
                    "Customers",

                "Payments":
                    "Payments",

                "Amount":
                    "Payment Received"
            }
        )
    )


    # ------------------------------------------------------
    # TOTAL ROW
    # ------------------------------------------------------

    daily_payment_total = pd.DataFrame([{

        "Payment Date":
            "TOTAL",

        "Customers":
            daily_payments[
                "Customer Name"
            ].nunique(),

        "Payments":
            daily_payments[
                "Invoice Payment ID"
            ].nunique(),

        "Payment Received":
            f"£{daily_payments[
                'Amount Applied to Invoice'
            ].sum():,.2f}"

    }])


    daily_payment_display = pd.concat(
        [
            daily_payment_display,
            daily_payment_total
        ],
        ignore_index=True
    )


    st.dataframe(
        daily_payment_display,
        width="stretch",
        hide_index=True
    )


else:

    st.info(
        "No payments were received during the "
        "selected payment date range."
    )


# ==========================================================
# PAYMENT DETAIL
# ==========================================================

if not daily_payments.empty:

    st.subheader(
        "Payment Details"
    )


    # ------------------------------------------------------
    # Select required columns
    # ------------------------------------------------------

    payment_detail = daily_payments[
        [
            "Customer Name",
            "Invoice Number",
            "Invoice Date",
            "Due Date",
            "Date",
            "Amount Applied to Invoice"
        ]
    ].copy()


    # ------------------------------------------------------
    # Rename
    # ------------------------------------------------------

    payment_detail = (
        payment_detail
        .rename(
            columns={
                "Invoice Number":
                    "Invoice",

                "Date":
                    "Payment Date",

                "Amount Applied to Invoice":
                    "Payment Received"
            }
        )
    )


    # ------------------------------------------------------
    # Format dates
    # ------------------------------------------------------

    for col in [
        "Invoice Date",
        "Due Date",
        "Payment Date"
    ]:

        payment_detail[col] = (
            pd.to_datetime(
                payment_detail[col],
                errors="coerce"
            )
            .dt.strftime(
                "%d-%m-%Y"
            )
        )


    payment_detail[
        [
            "Invoice Date",
            "Due Date",
            "Payment Date"
        ]
    ] = (
        payment_detail[
            [
                "Invoice Date",
                "Due Date",
                "Payment Date"
            ]
        ]
        .fillna("-")
    )


    # ------------------------------------------------------
    # Format amount
    # ------------------------------------------------------

    payment_detail[
        "Payment Received"
    ] = payment_detail[
        "Payment Received"
    ].apply(
        lambda x:
            f"£{x:,.2f}"
    )


    # ------------------------------------------------------
    # Sort newest payment first
    # ------------------------------------------------------

    payment_detail = (
        payment_detail
        .sort_values(
            "Payment Date",
            ascending=False
        )
        .reset_index(drop=True)
    )


    st.dataframe(
        payment_detail,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# PAYMENT KPIs
# ==========================================================

if not daily_payments.empty:

    st.markdown(
        "### Payment Period Summary"
    )


    payment_k1, payment_k2, payment_k3 = (
        st.columns(3)
    )


    payment_total = (
        daily_payments[
            "Amount Applied to Invoice"
        ].sum()
    )


    payment_count = (
        daily_payments[
            "Invoice Payment ID"
        ].nunique()
    )


    payment_customers = (
        daily_payments[
            "Customer Name"
        ].nunique()
    )


    with payment_k1:

        st.metric(
            "💷 Payment Received",
            f"£{payment_total:,.2f}"
        )


    with payment_k2:

        st.metric(
            "🧾 Payments",
            f"{payment_count:,}"
        )


    with payment_k3:

        st.metric(
            "👥 Customers",
            f"{payment_customers:,}"
        )
