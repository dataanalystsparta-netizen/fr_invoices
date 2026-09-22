# ==========================================================
# ZOHO ACCOUNTS RECEIVABLE DASHBOARD
# COMPLETE UPDATED SCRIPT
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np

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

    contacts = pd.read_excel(
        CONTACTS_FILE
    )


    # ======================================================
    # CLEAN COLUMN NAMES
    # ======================================================

    for df in [
        invoices,
        payments,
        ar_current,
        ar_overdue,
        contacts
    ]:

        df.columns = (
            df.columns
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
    # DATES
    # ======================================================

    invoice_date_columns = [
        "Invoice Date",
        "Due Date",
        "Last Payment Date",
        "Expected Payment Date"
    ]


    for col in invoice_date_columns:

        if col in invoices.columns:

            invoices[col] = pd.to_datetime(
                invoices[col],
                dayfirst=True,
                errors="coerce"
            )


    payment_date_columns = [
        "Date",
        "Invoice Date",
        "Invoice Payment Applied Date"
    ]


    for col in payment_date_columns:

        if col in payments.columns:

            payments[col] = pd.to_datetime(
                payments[col],
                dayfirst=True,
                errors="coerce"
            )


    for df in [
        ar_current,
        ar_overdue
    ]:

        for col in [
            "date",
            "due_date"
        ]:

            if col in df.columns:

                df[col] = pd.to_datetime(
                    df[col],
                    dayfirst=True,
                    errors="coerce"
                )


    # ======================================================
    # NUMERICS
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


    for col in [
        "Amount",
        "Amount Applied to Invoice"
    ]:

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

    if "Invoice Status" in invoices.columns:

        invoices = invoices[
            ~invoices["Invoice Status"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.casefold()
            .isin(
                [
                    "draft",
                    "void"
                ]
            )
        ].copy()


    # ======================================================
    # CLEAN INVOICE NUMBERS
    # ======================================================

    if "Invoice Number" in invoices.columns:

        invoices["Invoice Number"] = (
            invoices["Invoice Number"]
            .fillna("")
            .astype(str)
            .str.strip()
        )


    if "Invoice Number" in payments.columns:

        payments["Invoice Number"] = (
            payments["Invoice Number"]
            .fillna("")
            .astype(str)
            .str.strip()
        )


    # ======================================================
    # CLEAN CUSTOMER NAMES
    # ======================================================

    if "Customer Name" in invoices.columns:

        invoices["Customer Name"] = (
            invoices["Customer Name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )


    if "Customer Name" in payments.columns:

        payments["Customer Name"] = (
            payments["Customer Name"]
            .fillna("")
            .astype(str)
            .str.strip()
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
    # MONTH
    # ======================================================

    invoices["Month"] = (
        invoices["Invoice Date"]
        .dt.to_period("M")
        .astype(str)
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


    invoices["First Customer Invoice Date"] = (
        invoices["Customer Name"]
        .map(
            customer_first_invoice
        )
    )


    invoices["Invoice Type"] = np.where(
        invoices["Invoice Date"]
        ==
        invoices[
            "First Customer Invoice Date"
        ],
        "New Customer",
        "Recurring Customer"
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
    # AUTHORITATIVE OUTSTANDING
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
    # ZOHO BALANCE RECONCILIATION
    # ======================================================

    if "Balance" in invoices.columns:

        invoices["Balance Difference"] = (
            invoices["Calculated Outstanding"]
            -
            invoices["Balance"]
        )

    else:

        invoices["Balance Difference"] = (
            invoices["Calculated Outstanding"]
        )


    invoices["Balance Reconciles"] = (
        invoices["Balance Difference"]
        .abs()
        <= 0.01
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
                "Outstanding",
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
            [
                "Month",
                "Service Type"
            ],
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
                "Outstanding",
                "sum"
            )
        )
        .sort_values(
            [
                "Month",
                "Service Type"
            ]
        )
    )


    # ======================================================
    # CONTACTS
    # ======================================================

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
        customer_summary,
        monthly_summary,
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
    customer_summary,
    monthly_summary,
    contacts
) = load_data()


# ==========================================================
# MAIN FILTERS
# ==========================================================

st.subheader(
    "Filters"
)


f1, f2, f3, f4, f5 = st.columns(5)


# ==========================================================
# MAIN DATE FILTERS
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
    pd.Timestamp.today()
    .year
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
        max_value=max_date,
        key="main_start_date"
    )


with f2:

    end_date = st.date_input(
        "End Date",
        value=default_end,
        min_value=min_date,
        max_value=max_date,
        key="main_end_date"
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
        service_options,
        key="main_service_type"
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
# VALIDATE MAIN DATE RANGE
# ==========================================================

if start_date > end_date:

    st.error(
        "Start Date cannot be after End Date."
    )

    st.stop()


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

    if (
        not contacts.empty
        and
        "Status" in contacts.columns
        and
        "Display Name" in contacts.columns
    ):

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

    else:

        selected_status_customers = set()


    display_df = display_df[
        display_df["Customer Name"]
        .astype(str)
        .str.strip()
        .isin(
            selected_status_customers
        )
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
    display_df["Total"]
    .sum()
)

total_paid = (
    display_df["Paid"]
    .sum()
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
    (
        display_df["Due Date"]
        <= today
    )
].copy()


overdue_due = (
    overdue_df["Outstanding"]
    .sum()
)


future_df = display_df[
    (display_df["Outstanding"] > 0)
    &
    (
        display_df["Due Date"]
        > today
    )
].copy()


future_due = (
    future_df["Outstanding"]
    .sum()
)


total_pending = (
    overdue_due
    +
    future_due
)


# ==========================================================
# PERCENTAGES
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
# UNCLASSIFIED INVOICES
# ==========================================================

if selected_service == "Unclassified":

    st.subheader(
        "Unclassified Invoices"
    )


    unclassified_columns = [
        "Invoice Number",
        "Customer Name",
        "Service Type",
        "Item Name",
        "Item Desc",
        "Invoice Date",
        "Due Date",
        "Total"
    ]


    unclassified_columns = [
        col
        for col in unclassified_columns
        if col in display_df.columns
    ]


    unclassified_display = (
        display_df[
            unclassified_columns
        ].copy()
    )


    for col in [
        "Invoice Date",
        "Due Date"
    ]:

        if col in unclassified_display.columns:

            unclassified_display[col] = (
                pd.to_datetime(
                    unclassified_display[col],
                    errors="coerce"
                )
                .dt.strftime(
                    "%d-%m-%Y"
                )
                .fillna("-")
            )


    if "Total" in unclassified_display.columns:

        unclassified_display["Total"] = (
            unclassified_display["Total"]
            .apply(
                lambda x:
                f"£{x:,.2f}"
            )
        )


    st.dataframe(
        unclassified_display,
        width="stretch",
        hide_index=True
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
# RECONCILIATION
# ==========================================================

st.expander(
    "🔧 Reconciliation",
    expanded=False
)


with st.expander(
    "🔧 Reconciliation",
    expanded=False
):

    filtered_invoice_numbers = set(
        display_df["Invoice Number"]
        .astype(str)
        .str.strip()
    )


    reconciliation_issues = invoices[
        invoices["Balance Difference"]
        .abs()
        > 0.01
    ].copy()


    filtered_ar_mismatches = (
        reconciliation_issues[
            reconciliation_issues[
                "Invoice Number"
            ]
            .astype(str)
            .str.strip()
            .isin(
                filtered_invoice_numbers
            )
        ]
        .copy()
    )


    st.write(
        f"Invoice/payment reconciliation mismatches "
        f"in current filtered data: "
        f"{len(filtered_ar_mismatches):,}"
    )


    if not filtered_ar_mismatches.empty:

        diagnostic_columns = [
            "Invoice Number",
            "Customer Name",
            "Service Type",
            "Invoice Outstanding",
            "Balance",
            "Balance Difference"
        ]


        diagnostic_columns = [
            col
            for col in diagnostic_columns
            if col in filtered_ar_mismatches.columns
        ]


        diagnostic_display = (
            filtered_ar_mismatches[
                diagnostic_columns
            ]
            .sort_values(
                "Balance Difference",
                key=lambda x: x.abs(),
                ascending=False
            )
            .copy()
        )


        if "Invoice Outstanding" not in diagnostic_display.columns:

            diagnostic_display[
                "Invoice Outstanding"
            ] = filtered_ar_mismatches[
                "Calculated Outstanding"
            ]


        if "Balance" in diagnostic_display.columns:

            diagnostic_display["Balance"] = (
                diagnostic_display["Balance"]
                .apply(
                    lambda x:
                    f"£{x:,.2f}"
                )
            )


        if "Invoice Outstanding" in diagnostic_display.columns:

            diagnostic_display[
                "Invoice Outstanding"
            ] = (
                diagnostic_display[
                    "Invoice Outstanding"
                ]
                .apply(
                    lambda x:
                    f"£{x:,.2f}"
                )
            )


        if "Balance Difference" in diagnostic_display.columns:

            diagnostic_display[
                "Balance Difference"
            ] = (
                diagnostic_display[
                    "Balance Difference"
                ]
                .apply(
                    lambda x:
                    f"£{x:,.2f}"
                )
            )


        st.dataframe(
            diagnostic_display,
            width="stretch",
            hide_index=True
        )

    else:

        st.success(
            "✅ Invoice/Payment data reconciles."
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
        [
            "Month",
            "Service Type"
        ],
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
        [
            "Month",
            "Service Type"
        ]
    )
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
    .isin(
        filtered_invoice_numbers
    )
].copy()


# ==========================================================
# INVOICE LOOKUP
# ==========================================================

invoice_lookup = invoices[
    [
        "Invoice Number",
        "Invoice Date",
        "Service Type"
    ]
].copy()


invoice_lookup["Invoice Number"] = (
    invoice_lookup["Invoice Number"]
    .astype(str)
    .str.strip()
)


invoice_lookup = (
    invoice_lookup
    .drop_duplicates(
        subset="Invoice Number",
        keep="first"
    )
)


monthly_payments = monthly_payments.merge(
    invoice_lookup,
    on="Invoice Number",
    how="left",
    suffixes=(
        "",
        "_Invoice"
    )
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
    monthly_payments["Invoice Date"]
    .dt.to_period("M")
    .astype(str)
)


# ==========================================================
# SERVICE TYPE
# ==========================================================

monthly_payments["Service Type"] = (
    monthly_payments["Service Type"]
    .fillna("Unclassified")
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
            "Service Type",
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
        index=[
            "Payment Month",
            "Service Type"
        ],
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
# COMBINE MONTHLY INVOICE + PAYMENT DATA
# ==========================================================

monthly_display = (
    monthly_invoice_summary
    .merge(
        monthly_payment_summary[
            [
                "Month",
                "Service Type",
                "Paid_Current_Month",
                "Paid_Older_Invoices",
                "Total_Paid"
            ]
        ],
        on=[
            "Month",
            "Service Type"
        ],
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


monthly_display["Service Type"] = (
    monthly_display["Service Type"]
    .fillna("Unclassified")
)


monthly_display = (
    monthly_display
    .sort_values(
        [
            "Month",
            "Service Type"
        ]
    )
    .reset_index(drop=True)
)


# ==========================================================
# FINANCIAL MONTHLY VIEW
# ==========================================================

if IS_FINANCIAL:

    monthly_total_row = pd.DataFrame(
        [{
            "Month": "TOTAL",
            "Service Type": "ALL SERVICES",

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


    st.dataframe(
        monthly_display[
            [
                "Month",
                "Service Type",
                "Customers",
                "Invoices",
                "Invoiced",
                "Paid – Current Invoice Month",
                "Paid – Older Invoices",
                "Total Paid",
                "Outstanding"
            ]
        ],
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


    percentage_total_row = pd.DataFrame(
        [{
            "Month": "TOTAL",
            "Service Type": "ALL SERVICES",

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
                "Service Type",
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
    display_df[
        "Month"
    ]
    .dropna()
    .unique()
)


rows = []


# ==========================================================
# CUSTOMER + SERVICE MATRIX
# ==========================================================

customer_service_groups = (
    display_df[
        [
            "Customer Name",
            "Service Type"
        ]
    ]
    .drop_duplicates()
    .sort_values(
        [
            "Customer Name",
            "Service Type"
        ]
    )
)


for _, group_row in customer_service_groups.iterrows():

    customer = (
        group_row["Customer Name"]
    )

    service_type = (
        group_row["Service Type"]
    )


    row = {
        "Customer Name": customer,
        "Service Type": service_type
    }


    customer_df = display_df[
        (
            display_df[
                "Customer Name"
            ]
            ==
            customer
        )
        &
        (
            display_df[
                "Service Type"
            ]
            ==
            service_type
        )
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
                    /
                    invoice_value
                    *
                    100
                )

                row[month] = (
                    f"{paid_pct:.1f}%"
                )


    # ======================================================
    # TOTAL
    # ======================================================

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


customer_table = pd.DataFrame(rows)


# ==========================================================
# OUTSTANDING ONLY
# ==========================================================

if show_outstanding_only:

    if not customer_table.empty:

        def has_outstanding(
            total_value
        ):

            if total_value == "-":
                return False

            if "/" not in total_value:
                return False

            try:

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

            except Exception:

                return False


        customer_table = customer_table[
            customer_table["Total"]
            .apply(
                has_outstanding
            )
        ].copy()


# ==========================================================
# GRAND TOTAL
# ==========================================================

if not customer_table.empty:

    visible_pairs = set(
        zip(
            customer_table["Customer Name"],
            customer_table["Service Type"]
        )
    )

else:

    visible_pairs = set()


grand_total_df = display_df[
    display_df.apply(
        lambda row:
        (
            row["Customer Name"],
            row["Service Type"]
        )
        in visible_pairs,
        axis=1
    )
].copy()


grand_row = {
    "Customer Name": "GRAND TOTAL",
    "Service Type": "ALL SERVICES"
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


        try:

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

        except Exception:

            return ""


        if paid == 0:

            return (
                "background-color:#f4cccc;"
            )

        return (
            "background-color:#fff2cc;"
        )


    try:

        percentage = float(
            value
            .replace("%", "")
            .strip()
        )

    except Exception:

        return ""


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


if not customer_table.empty:

    styled = customer_table.style.map(
        colour_cells,
        subset=customer_table.columns[2:]
    )


    def highlight_grand_total(row):

        if row["Customer Name"] == "GRAND TOTAL":

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


    st.dataframe(
        styled,
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "No customer data matches the selected filters."
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
# CUSTOMER DATE VALIDATION
# ==========================================================

if customer_start_date > customer_end_date:

    st.error(
        "Customer Start Date cannot be after "
        "Customer End Date."
    )

else:

    # ======================================================
    # CUSTOMER DATASET
    # ======================================================

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


    # ------------------------------------------------------
    # SERVICE FILTER
    # ------------------------------------------------------

    if (
        customer_selected_service
        !=
        "All Services"
    ):

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


    # ------------------------------------------------------
    # INVOICE TYPE
    # ------------------------------------------------------

    if (
        customer_selected_invoice_type
        !=
        "All Invoices"
    ):

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


    # ------------------------------------------------------
    # STATUS
    # ------------------------------------------------------

    if (
        customer_selected_status
        !=
        "All Customers"
    ):

        if (
            not contacts.empty
            and
            "Status" in contacts.columns
            and
            "Display Name" in contacts.columns
        ):

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

        else:

            selected_status_customers = set()


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


    # ======================================================
    # CUSTOMER LIST
    # ======================================================

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


        # ==================================================
        # CUSTOMER INVOICES
        # ==================================================

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


        # ==================================================
        # CUSTOMER PAYMENTS
        # ==================================================

        customer_payments = payments[
            payments["Customer Name"]
            .astype(str)
            .str.strip()
            ==
            str(selected_customer).strip()
        ].copy()


        # ==================================================
        # CUSTOMER INFORMATION
        # ==================================================

        if (
            not contacts.empty
            and
            "Display Name" in contacts.columns
        ):

            customer_info = contacts[
                contacts["Display Name"]
                .astype(str)
                .str.strip()
                ==
                str(selected_customer).strip()
            ].copy()

        else:

            customer_info = pd.DataFrame()


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


        # ==================================================
        # CUSTOMER KPIs
        # ==================================================

        cust_total = (
            customer_invoices["Total"]
            .sum()
        )


        cust_balance = (
            customer_invoices[
                "Calculated Outstanding"
            ]
            .sum()
        )


        cust_paid = (
            customer_invoices["Paid"]
            .sum()
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


        # ==================================================
        # INVOICE LEDGER
        # ==================================================

        st.subheader(
            "Invoice Ledger"
        )


        ledger = customer_invoices.copy()


        # --------------------------------------------------
        # PAYMENT SUMMARY
        # --------------------------------------------------

        if not customer_payments.empty:

            customer_payment_summary = (
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

        else:

            customer_payment_summary = pd.DataFrame(
                columns=[
                    "Invoice Number",
                    "Payment_Date",
                    "Paid_Amount"
                ]
            )


        ledger = ledger.merge(
            customer_payment_summary,
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


        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        ledger["Status"] = "Current"


        ledger.loc[
            ledger["Due Date"] < today,
            "Status"
        ] = "Overdue"


        ledger.loc[
            (
                ledger["Paid_Amount"] > 0
            )
            &
            (
                ledger["Outstanding"] > 0
            ),
            "Status"
        ] = "Partially Paid"


        ledger.loc[
            ledger["Outstanding"] <= 0,
            "Status"
        ] = "Paid"


        # --------------------------------------------------
        # DAYS OVERDUE
        # --------------------------------------------------

        ledger["Days Overdue"] = np.where(
            ledger[
                "Status"
            ].isin(
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


        # --------------------------------------------------
        # LEDGER DISPLAY
        # --------------------------------------------------

        if IS_FINANCIAL:

            ledger_display = ledger[
                [
                    "Invoice Number",
                    "Customer Name",
                    "Service Type",
                    "Invoice Date",
                    "Due Date",
                    "Payment_Date",
                    "Status",
                    "Days Overdue",
                    "Total",
                    "Paid_Amount",
                    "Outstanding"
                ]
            ].copy()


            ledger_display = (
                ledger_display
                .rename(
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
            )


            for col in [
                "Invoice Date",
                "Due Date",
                "Payment Date"
            ]:

                ledger_display[col] = (
                    pd.to_datetime(
                        ledger_display[col],
                        errors="coerce"
                    )
                    .dt.strftime(
                        "%d-%m-%Y"
                    )
                    .fillna("-")
                )


            ledger_display["Days Overdue"] = (
                ledger_display[
                    "Days Overdue"
                ]
                .replace(
                    0,
                    "-"
                )
            )


            for col in [
                "Amount (£)",
                "Paid (£)",
                "Outstanding (£)"
            ]:

                ledger_display[col] = (
                    ledger_display[col]
                    .apply(
                        lambda x:
                        "-"
                        if pd.isna(x)
                        or x == 0
                        else f"£{x:,.2f}"
                    )
                )


        else:

            ledger_display = ledger.copy()


            ledger_display["Paid %"] = np.where(
                ledger_display["Total"] > 0,
                (
                    ledger_display["Paid_Amount"]
                    /
                    ledger_display["Total"]
                )
                * 100,
                0
            )


            ledger_display["Outstanding %"] = np.where(
                ledger_display["Total"] > 0,
                (
                    ledger_display["Outstanding"]
                    /
                    ledger_display["Total"]
                )
                * 100,
                0
            )


            ledger_display["Paid %"] = (
                ledger_display["Paid %"]
                .map(
                    lambda x:
                    f"{x:.1f}%"
                )
            )


            ledger_display["Outstanding %"] = (
                ledger_display["Outstanding %"]
                .map(
                    lambda x:
                    f"{x:.1f}%"
                )
            )


            ledger_display = ledger_display[
                [
                    "Invoice Number",
                    "Customer Name",
                    "Service Type",
                    "Invoice Date",
                    "Due Date",
                    "Payment_Date",
                    "Status",
                    "Days Overdue",
                    "Paid %",
                    "Outstanding %"
                ]
            ].copy()


            ledger_display = (
                ledger_display
                .rename(
                    columns={
                        "Invoice Number":
                            "Invoice",

                        "Payment_Date":
                            "Payment Date"
                    }
                )
            )


            for col in [
                "Invoice Date",
                "Due Date",
                "Payment Date"
            ]:

                ledger_display[col] = (
                    pd.to_datetime(
                        ledger_display[col],
                        errors="coerce"
                    )
                    .dt.strftime(
                        "%d-%m-%Y"
                    )
                    .fillna("-")
                )


            ledger_display["Days Overdue"] = (
                ledger_display[
                    "Days Overdue"
                ]
                .replace(
                    0,
                    "-"
                )
            )


        st.dataframe(
            ledger_display,
            width="stretch",
            hide_index=True
        )


    else:

        st.info(
            "No customers match the selected customer filters."
        )


# ==========================================================
# PART 4
# PAYMENTS RECEIVED
# ==========================================================

st.divider()

st.header(
    "💷 Payments Received"
)


st.caption(
    "Payments are shown based on the actual payment date. "
    "These filters are completely independent of the "
    "invoice dashboard filters above."
)


# ==========================================================
# PAYMENT DATE FILTERS
# ==========================================================
#
# IMPORTANT:
# Fixed 2021-2027 range.
# This means every date in 2026 remains selectable.
# ==========================================================

PAYMENT_MIN_DATE = date(
    2021,
    1,
    1
)

PAYMENT_MAX_DATE = date(
    2027,
    12,
    31
)


valid_payment_dates = (
    payments["Date"]
    .dropna()
)


if not valid_payment_dates.empty:

    latest_payment_date = (
        valid_payment_dates
        .max()
        .date()
    )

    default_payment_end = min(
        latest_payment_date,
        date.today()
    )

    default_payment_start = max(
        date(
            current_year,
            1,
            1
        ),
        PAYMENT_MIN_DATE
    )

else:

    default_payment_start = date(
        current_year,
        1,
        1
    )

    default_payment_end = date.today()


pf1, pf2 = st.columns(2)


with pf1:

    payment_start_date = st.date_input(
        "Payment Start Date",
        value=default_payment_start,
        min_value=PAYMENT_MIN_DATE,
        max_value=PAYMENT_MAX_DATE,
        key="payment_start_date"
    )


with pf2:

    payment_end_date = st.date_input(
        "Payment End Date",
        value=default_payment_end,
        min_value=PAYMENT_MIN_DATE,
        max_value=PAYMENT_MAX_DATE,
        key="payment_end_date"
    )


# ==========================================================
# VALIDATE PAYMENT RANGE
# ==========================================================

if payment_start_date > payment_end_date:

    st.error(
        "Payment Start Date cannot be after "
        "Payment End Date."
    )

else:

    # ======================================================
    # PAYMENT DATA
    # ======================================================

    payment_view = payments.copy()


    payment_view["Payment Date"] = pd.to_datetime(
        payment_view["Date"],
        errors="coerce"
    )


    payment_view["Payment Amount"] = pd.to_numeric(
        payment_view[
            "Amount Applied to Invoice"
        ],
        errors="coerce"
    ).fillna(0)


    payment_view["Customer Name"] = (
        payment_view["Customer Name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    payment_view["Invoice Number"] = (
        payment_view["Invoice Number"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # ======================================================
    # PAYMENT DATE FILTER
    # ======================================================

    payment_filtered = payment_view[
        (
            payment_view["Payment Date"]
            >= pd.Timestamp(
                payment_start_date
            )
        )
        &
        (
            payment_view["Payment Date"]
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


    # ======================================================
    # ADD SERVICE TYPE
    # ======================================================
    #
    # Service Type comes from the invoice associated
    # with the payment.
    # ======================================================

    payment_service_lookup = invoices[
        [
            "Invoice Number",
            "Service Type"
        ]
    ].copy()


    payment_service_lookup["Invoice Number"] = (
        payment_service_lookup[
            "Invoice Number"
        ]
        .astype(str)
        .str.strip()
    )


    payment_service_lookup = (
        payment_service_lookup
        .drop_duplicates(
            subset="Invoice Number",
            keep="first"
        )
    )


    payment_filtered = payment_filtered.merge(
        payment_service_lookup,
        on="Invoice Number",
        how="left"
    )


    payment_filtered["Service Type"] = (
        payment_filtered["Service Type"]
        .fillna("Unclassified")
    )


    # ======================================================
    # ADD DUE DATE
    # ======================================================

    payment_invoice_lookup = invoices[
        [
            "Invoice Number",
            "Due Date"
        ]
    ].copy()


    payment_invoice_lookup["Invoice Number"] = (
        payment_invoice_lookup[
            "Invoice Number"
        ]
        .astype(str)
        .str.strip()
    )


    payment_invoice_lookup = (
        payment_invoice_lookup
        .drop_duplicates(
            subset="Invoice Number",
            keep="first"
        )
    )


    payment_filtered = payment_filtered.merge(
        payment_invoice_lookup,
        on="Invoice Number",
        how="left"
    )


    # ======================================================
    # PAYMENT KPIs
    # ======================================================

    payment_total = (
        payment_filtered[
            "Payment Amount"
        ]
        .sum()
    )


    payment_entries = len(
        payment_filtered
    )


    payment_customers = (
        payment_filtered[
            "Customer Name"
        ]
        .replace(
            "",
            np.nan
        )
        .nunique()
    )


    payment_invoices = (
        payment_filtered[
            "Invoice Number"
        ]
        .replace(
            "",
            np.nan
        )
        .nunique()
    )


    # ======================================================
    # PAYMENT KPI CARDS
    # ======================================================

    pk1, pk2, pk3, pk4 = st.columns(4)


    with pk1:

        kpi_card(
            "💷 Payments Received",
            f"£{payment_total:,.2f}"
        )


    with pk2:

        kpi_card(
            "🧾 Payment Entries",
            f"{payment_entries:,}"
        )


    with pk3:

        kpi_card(
            "👥 Customers",
            f"{payment_customers:,}"
        )


    with pk4:

        kpi_card(
            "📄 Invoices Paid",
            f"{payment_invoices:,}"
        )


    # ======================================================
    # DAILY PAYMENT SUMMARY
    # ======================================================

    st.subheader(
        "Daily Payment Summary"
    )


    if payment_filtered.empty:

        st.info(
            "No payments were received during "
            "the selected payment date range."
        )

    else:

        payment_filtered["Payment Day"] = (
            payment_filtered["Payment Date"]
            .dt.normalize()
        )


        # --------------------------------------------------
        # DAILY SUMMARY BY SERVICE TYPE
        # --------------------------------------------------

        daily_summary = (
            payment_filtered
            .groupby(
                [
                    "Payment Day",
                    "Service Type"
                ],
                as_index=False
            )
            .agg(
                Payment_Entries=(
                    "Payment Amount",
                    "count"
                ),

                Customers=(
                    "Customer Name",
                    "nunique"
                ),

                Invoices_Paid=(
                    "Invoice Number",
                    "nunique"
                ),

                Amount_Received=(
                    "Payment Amount",
                    "sum"
                )
            )
            .sort_values(
                [
                    "Payment Day",
                    "Service Type"
                ],
                ascending=[
                    False,
                    True
                ]
            )
        )


        # --------------------------------------------------
        # FORMAT
        # --------------------------------------------------

        daily_summary["Payment Date"] = (
            daily_summary["Payment Day"]
            .dt.strftime(
                "%d-%m-%Y"
            )
        )


        daily_summary["Payment Received"] = (
            daily_summary[
                "Amount_Received"
            ]
            .map(
                lambda x:
                f"£{x:,.2f}"
            )
        )


        daily_summary = (
            daily_summary
            .rename(
                columns={
                    "Payment_Entries":
                        "Payment Entries",

                    "Invoices_Paid":
                        "Invoices Paid"
                }
            )
        )


        daily_summary = daily_summary[
            [
                "Payment Date",
                "Service Type",
                "Payment Entries",
                "Customers",
                "Invoices Paid",
                "Payment Received"
            ]
        ].copy()


        # --------------------------------------------------
        # TOTAL ROW
        # --------------------------------------------------

        daily_total_row = pd.DataFrame([
            {
                "Payment Date":
                    "TOTAL",

                "Service Type":
                    "ALL SERVICES",

                "Payment Entries":
                    len(payment_filtered),

                "Customers":
                    payment_filtered[
                        "Customer Name"
                    ]
                    .replace(
                        "",
                        np.nan
                    )
                    .nunique(),

                "Invoices Paid":
                    payment_filtered[
                        "Invoice Number"
                    ]
                    .replace(
                        "",
                        np.nan
                    )
                    .nunique(),

                "Payment Received":
                    (
                        "£"
                        +
                        f"{payment_filtered['Payment Amount'].sum():,.2f}"
                    )
            }
        ])


        daily_summary = pd.concat(
            [
                daily_summary,
                daily_total_row
            ],
            ignore_index=True
        )


        # --------------------------------------------------
        # ABSOLUTE COLUMN UNIQUENESS SAFETY
        # --------------------------------------------------

        daily_summary = (
            daily_summary
            .loc[
                :,
                ~daily_summary.columns.duplicated()
            ]
            .copy()
        )


        st.dataframe(
            daily_summary,
            width="stretch",
            hide_index=True
        )


        # ==================================================
        # PAYMENT DETAILS
        # ==================================================

        st.subheader(
            "Payment Details"
        )


        payment_detail_display = pd.DataFrame({
            "Customer Name":
                payment_filtered[
                    "Customer Name"
                ],

            "Service Type":
                payment_filtered[
                    "Service Type"
                ],

            "Invoice":
                payment_filtered[
                    "Invoice Number"
                ],

            "Invoice Date":
                payment_filtered.get(
                    "Invoice Date",
                    pd.Series(
                        pd.NaT,
                        index=payment_filtered.index
                    )
                ),

            "Due Date":
                payment_filtered[
                    "Due Date"
                ],

            "Payment Date":
                payment_filtered[
                    "Payment Date"
                ],

            "Payment Received (£)":
                payment_filtered[
                    "Payment Amount"
                ]
        })


        # --------------------------------------------------
        # FORMAT DATES
        # --------------------------------------------------

        for col in [
            "Invoice Date",
            "Due Date",
            "Payment Date"
        ]:

            payment_detail_display[col] = (
                pd.to_datetime(
                    payment_detail_display[col],
                    errors="coerce"
                )
                .dt.strftime(
                    "%d-%m-%Y"
                )
                .fillna("-")
            )


        # --------------------------------------------------
        # FORMAT MONEY
        # --------------------------------------------------

        payment_detail_display[
            "Payment Received (£)"
        ] = (
            payment_detail_display[
                "Payment Received (£)"
            ]
            .map(
                lambda x:
                f"£{x:,.2f}"
            )
        )


        # --------------------------------------------------
        # SORT
        # --------------------------------------------------

        payment_detail_sort_date = (
            pd.to_datetime(
                payment_filtered[
                    "Payment Date"
                ],
                errors="coerce"
            )
        )


        payment_detail_display["_sort_date"] = (
            payment_detail_sort_date
        )


        payment_detail_display = (
            payment_detail_display
            .sort_values(
                "_sort_date",
                ascending=False
            )
            .drop(
                columns="_sort_date"
            )
            .reset_index(drop=True)
        )


        # --------------------------------------------------
        # ABSOLUTE COLUMN UNIQUENESS SAFETY
        # --------------------------------------------------

        payment_detail_display = (
            payment_detail_display
            .loc[
                :,
                ~payment_detail_display.columns.duplicated()
            ]
            .copy()
        )


        st.dataframe(
            payment_detail_display,
            width="stretch",
            hide_index=True
        )
