# ==========================================================
# ZOHO ACCOUNTS RECEIVABLE DASHBOARD
# PART 1 - IMPORTS, DATA LOADING & PREPARATION
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests

# ==========================================================
# ZOHO API AUTHENTICATION
# ==========================================================

def get_zoho_access_token():

    client_id = st.secrets["zoho"]["client_id"]
    client_secret = st.secrets["zoho"]["client_secret"]
    refresh_token = st.secrets["zoho"]["refresh_token"]

    response = requests.post(
        "https://accounts.zoho.eu/oauth/v2/token",
        params={
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
        },
        timeout=30
    )

    response.raise_for_status()

    token_data = response.json()

    return token_data["access_token"]

# ==========================================================
# ZOHO API REQUEST
# ==========================================================

def zoho_api_get(endpoint, params=None):

    access_token = get_zoho_access_token()

    organization_id = (
        st.secrets["zoho"]["organization_id"]
    )

    if params is None:
        params = {}

    params["organization_id"] = organization_id

    response = requests.get(
        f"https://www.zohoapis.eu/books/v3/{endpoint}",
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}"
        },
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# GET ALL ZOHO BOOKS INVOICES
# ==========================================================

def get_all_invoices():

    all_invoices = []

    page = 1
    per_page = 200

    while True:

        data = zoho_api_get(
            "invoices",
            {
                "page": page,
                "per_page": per_page
            }
        )

        invoices = data.get(
            "invoices",
            []
        )

        all_invoices.extend(invoices)

        if not data.get(
            "page_context",
            {}
        ).get(
            "has_more_page",
            False
        ):
            break

        page += 1

    return pd.DataFrame(all_invoices)

# ==========================================================
# TEST ZOHO INVOICE RETRIEVAL
# ==========================================================

with st.spinner("Retrieving invoices from Zoho Books..."):

    zoho_invoices = get_all_invoices()

st.success(
    f"Zoho returned {len(zoho_invoices):,} invoices."
)

st.write(
    "Columns returned by Zoho:"
)

st.write(
    list(zoho_invoices.columns)
)
# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

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

    # ------------------------------------------------------
    # Validate Login
    # ------------------------------------------------------

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


# ----------------------------------------------------------
# REQUIRE LOGIN
# ----------------------------------------------------------

if not check_login():

    st.stop()
#############################################################################

# USER VIEW
# ==========================================================

USER_VIEW = st.session_state.get(
    "view",
    "financial"
)

IS_FINANCIAL = USER_VIEW == "financial"
IS_PERCENTAGE = USER_VIEW == "percentage"


#############################################################################

# ==========================================================
# LOGOUT
# ==========================================================

with st.sidebar:

    st.write(
        f"👤 {st.session_state.get('logged_in_email', '')}"
    )

    if st.button("🚪 Logout", width="stretch"):

        st.session_state.authenticated = False
        st.session_state.pop("logged_in_email", None)

        st.rerun()

#############################################################################





st.title("💰 FastRanking Payments Dashboard")
st.markdown("""
<style>

.kpi-card{
    background:#ffffff;
    border:1px solid #e6e6e6;
    border-radius:12px;
    padding:14px;
    text-align:center;
    box-shadow:0 1px 6px rgba(0,0,0,0.08);
    margin-bottom:10px;
}

.kpi-title{
    font-size:15px;
    color:#666666;
    margin-bottom:8px;
    font-weight:600;
}

.kpi-value{
    font-size:28px;
    font-weight:700;
    color:#111111;
}

</style>
""", unsafe_allow_html=True)

def kpi_card(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# SERVICE CLASSIFICATION
# ----------------------------------------------------------

def classify_service(item_name, item_desc):

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

    # Item Name takes priority
    source = item_name if item_name else item_desc

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

# ----------------------------------------------------------
# FILES
# ----------------------------------------------------------

INVOICE_FILE = "Invoice_zoho.xlsx"
PAYMENT_FILE = "Customer_Payment_zoho.xlsx"
AR_CURRENT_FILE = "AR_current_zoho.xlsx"
AR_OVERDUE_FILE = "AR_overdue_zoho.xlsx"
CONTACTS_FILE = "Contacts_zoho.xlsx"

# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------

@st.cache_data
def load_data():

    invoices = pd.read_excel(INVOICE_FILE)
    payments = pd.read_excel(PAYMENT_FILE)
    ar_current = pd.read_excel(AR_CURRENT_FILE)
    ar_overdue = pd.read_excel(AR_OVERDUE_FILE)

    # ------------------------------
    # Clean column names
    # ------------------------------

    invoices.columns = invoices.columns.str.strip()
    payments.columns = payments.columns.str.strip()
    ar_current.columns = ar_current.columns.str.strip()
    ar_overdue.columns = ar_overdue.columns.str.strip()


        
    # ------------------------------------------------------
    # SERVICE CLASSIFICATION
    # ------------------------------------------------------
    
    # Make sure the source columns exist
    if "Item Name" not in invoices.columns:
        invoices["Item Name"] = ""
    
    if "Item Desc" not in invoices.columns:
        invoices["Item Desc"] = ""
    
    # Classify each invoice
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

    


    # ------------------------------
    # Date columns
    # ------------------------------

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

    if "Date" in payments.columns:
        payments["Date"] = pd.to_datetime(
            payments["Date"],
            dayfirst=True,
            errors="coerce"
        )

    if "Invoice Date" in payments.columns:
        payments["Invoice Date"] = pd.to_datetime(
            payments["Invoice Date"],
            dayfirst=True,
            errors="coerce"
        )

    for df in [ar_current, ar_overdue]:

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




    # ------------------------------
    # Numeric columns
    # ------------------------------

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

    for df in [ar_current, ar_overdue]:

        for col in ["balance", "amount"]:

            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).fillna(0)




    # ------------------------------------------------------
    # Remove Draft/Void invoices
    # ------------------------------------------------------

    invoices = invoices[
        ~invoices["Invoice Status"].isin(
            ["Draft", "Void"]
        )
    ].copy()

    # ------------------------------------------------------
    # Month column
    # ------------------------------------------------------

    invoices["Month"] = (
        invoices["Invoice Date"]
        .dt.to_period("M")
        .astype(str)
    )
    

    # ------------------------------------------------------
# REMOVE DUPLICATE INVOICES
# ------------------------------------------------------

    invoices = (
        invoices
        .sort_values("Invoice Date")
        .drop_duplicates(subset="Invoice Number", keep="first")
        .reset_index(drop=True)
    )
    # ------------------------------------------------------
    # PAYMENT SUMMARY
    # ------------------------------------------------------
    
    payment_summary = (
        payments.groupby("Invoice Number", as_index=False)
        .agg(
            Paid=("Amount Applied to Invoice", "sum")
        )
    )
    
    invoices = invoices.merge(
        payment_summary,
        on="Invoice Number",
        how="left"
    )
    
    invoices["Paid"] = invoices["Paid"].fillna(0)
    







    # ------------------------------------------------------
    # CUSTOMER SUMMARY
    # ------------------------------------------------------

    customer_summary = (
        invoices.groupby("Customer Name", as_index=False)
        .agg(
            Total_Invoiced=("Total", "sum"),
            Outstanding=("Balance", "sum"),
            Invoice_Count=("Invoice Number", "nunique")
        )
    )

    # ------------------------------------------------------
    # MONTHLY SUMMARY
    # ------------------------------------------------------

    monthly_summary = (
        invoices.groupby("Month", as_index=False)
        .agg(
            Customers=("Customer Name", "nunique"),
            Invoices=("Invoice Number", "nunique"),
            Total_Invoiced=("Total", "sum"),
            Outstanding=("Balance", "sum")
        )
        .sort_values("Month")
    )

    # ------------------------------------------------------
    # KPI VALUES
    # ------------------------------------------------------

    total_customers = invoices["Customer Name"].nunique()

    total_invoiced = invoices["Total"].sum()

    total_pending = (
        ar_current["balance"].sum()
        + ar_overdue["balance"].sum()
    )

    contacts = pd.read_excel(CONTACTS_FILE)
    contacts.columns = contacts.columns.str.strip()



    
    return (
        invoices,
        payments,
        ar_current,
        ar_overdue,
        customer_summary,
        monthly_summary,
        total_customers,
        total_invoiced,
        total_pending,
        contacts
    )


(
    invoices,
    payments,
    ar_current,
    ar_overdue,
    customer_summary,
    monthly_summary,
    TOTAL_CUSTOMERS,
    TOTAL_INVOICED,
    TOTAL_PENDING,
    contacts
) = load_data()



# ==========================================================
# PART 2 - KPI DASHBOARD & CUSTOMER TABLE
# ==========================================================
# ==========================================================
# PART 2 - FILTERS
# ==========================================================

st.subheader("Filters")

# ----------------------------------------------------------
# DATE FILTERS
# ----------------------------------------------------------

f1, f2, f3 = st.columns(3)

from datetime import date

# Fixed selectable range
min_date = date(2021, 1, 1)
max_date = date(2027, 12, 31)

# Default dates based on actual invoice data
default_start = invoices["Invoice Date"].min().date()
default_end = invoices["Invoice Date"].max().date()

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

# ----------------------------------------------------------
# SERVICE CATEGORY FILTER
# ----------------------------------------------------------

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
# APPLY FILTERS
# ==========================================================

display_df = invoices[
    (invoices["Invoice Date"] >= pd.Timestamp(start_date)) &
    (invoices["Invoice Date"] <= pd.Timestamp(end_date))
].copy()


# ----------------------------------------------------------
# SERVICE FILTER
# ----------------------------------------------------------

if selected_service != "All Services":

    display_df = display_df[
        display_df["Service Type"] == selected_service
    ].copy()
# ----------------------------------------------------------
# RECALCULATE KPIs
# ----------------------------------------------------------

total_customers = display_df["Customer Name"].nunique()

total_invoices = display_df["Invoice Number"].nunique()

total_invoiced = display_df["Total"].sum()

total_paid = display_df["Paid"].sum()

# Live AR Snapshot (do not date filter)

current_total = ar_current["balance"].sum()
overdue_total = ar_overdue["balance"].sum()

total_pending = current_total + overdue_total

# Future invoices (not yet due)

today = pd.Timestamp.today().normalize()

future_due = display_df[
    (display_df["Balance"] > 0) &
    (display_df["Due Date"] > today)
]["Balance"].sum()

# Collection Rate

collection_rate = (
    (total_paid / total_invoiced) * 100
    if total_invoiced > 0 else 0
)
# ----------------------------------------------------------
# SHOW UNCLASSIFIED SERVICES
# ----------------------------------------------------------

if selected_service == "Unclassified":

    st.subheader("Unclassified Invoices")

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
# KPI CARDS
# ==========================================================

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

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
            f"£{total_paid:,.2f}"
        )

    with c5:
        kpi_card(
            "⏳ Pending",
            f"£{total_pending:,.2f}"
        )

    with c6:
        kpi_card(
            "📅 Future Due",
            f"£{future_due:,.2f}"
        )

    with c7:
        kpi_card(
            "🔴 Overdue",
            f"£{overdue_total:,.2f}"
        )

    with c8:
        kpi_card(
            "📊 Collection",
            f"{collection_rate:.1f}%"
        )

else:

    # ------------------------------------------------------
    # PERCENTAGE VIEW
    # ------------------------------------------------------

    paid_percentage = (
        (total_paid / total_invoiced) * 100
        if total_invoiced > 0 else 0
    )

    outstanding_percentage = (
        ((total_invoiced - total_paid) / total_invoiced) * 100
        if total_invoiced > 0 else 0
    )

    future_percentage = (
        (future_due / total_invoiced) * 100
        if total_invoiced > 0 else 0
    )

    overdue_percentage = (
        (overdue_total / total_invoiced) * 100
        if total_invoiced > 0 else 0
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
            "📅 Future Due",
            f"{future_percentage:.1f}%"
        )

    with c6:
        kpi_card(
            "🔴 Overdue",
            f"{overdue_percentage:.1f}%"
        )

    with c7:
        kpi_card(
            "📊 Collection",
            f"{collection_rate:.1f}%"
        )

    with c8:
        kpi_card(
            "📈 Payment Coverage",
            f"{paid_percentage:.1f}%"
        )
# ----------------------------------------------------------
# MONTHLY BREAKDOWN
# ----------------------------------------------------------

st.subheader("Monthly Invoice Summary")

# ==========================================================
# CREATE MONTHLY SUMMARY FROM FILTERED DATA
# ==========================================================

monthly_display = (
    display_df
    .groupby("Month", as_index=False)
    .agg(
        Customers=("Customer Name", "nunique"),
        Invoices=("Invoice Number", "nunique"),
        Total_Invoiced=("Total", "sum"),
        Total_Paid=("Paid", "sum"),
        Outstanding=("Balance", "sum")
    )
    .sort_values("Month")
    .reset_index(drop=True)
)

# ==========================================================
# FINANCIAL VIEW
# ==========================================================

if IS_FINANCIAL:

    # ------------------------------------------------------
    # TOTAL ROW
    # ------------------------------------------------------

    monthly_total_row = pd.DataFrame([{
        "Month": "TOTAL",
        "Customers": display_df["Customer Name"].nunique(),
        "Invoices": display_df["Invoice Number"].nunique(),
        "Total_Invoiced": display_df["Total"].sum(),
        "Total_Paid": display_df["Paid"].sum(),
        "Outstanding": display_df["Balance"].sum()
    }])

    monthly_display = pd.concat(
        [
            monthly_display,
            monthly_total_row
        ],
        ignore_index=True
    )

    # ------------------------------------------------------
    # FORMAT FINANCIAL VALUES
    # ------------------------------------------------------

    monthly_display["Total_Invoiced"] = (
        monthly_display["Total_Invoiced"]
        .apply(lambda x: f"£{x:,.2f}")
    )

    monthly_display["Total_Paid"] = (
        monthly_display["Total_Paid"]
        .apply(lambda x: f"£{x:,.2f}")
    )

    monthly_display["Outstanding"] = (
        monthly_display["Outstanding"]
        .apply(lambda x: f"£{x:,.2f}")
    )

    # ------------------------------------------------------
    # RENAME COLUMNS
    # ------------------------------------------------------

    monthly_display = monthly_display.rename(
        columns={
            "Total_Invoiced": "Invoiced",
            "Total_Paid": "Paid",
            "Outstanding": "Outstanding"
        }
    )

    st.dataframe(
        monthly_display,
        width="stretch",
        hide_index=True
    )

# ==========================================================
# PERCENTAGE VIEW
# ==========================================================

else:

    monthly_percentage = monthly_display.copy()

    # ------------------------------------------------------
    # CALCULATE PERCENTAGES
    # ------------------------------------------------------

    monthly_percentage["Paid %"] = np.where(
        monthly_percentage["Total_Invoiced"] > 0,
        (
            monthly_percentage["Total_Paid"]
            / monthly_percentage["Total_Invoiced"]
        ) * 100,
        0
    )

    monthly_percentage["Outstanding %"] = np.where(
        monthly_percentage["Total_Invoiced"] > 0,
        (
            monthly_percentage["Outstanding"]
            / monthly_percentage["Total_Invoiced"]
        ) * 100,
        0
    )

    # ------------------------------------------------------
    # TOTAL ROW
    # ------------------------------------------------------

    total_invoice = display_df["Total"].sum()
    total_paid_value = display_df["Paid"].sum()
    total_outstanding = display_df["Balance"].sum()

    total_paid_pct = (
        total_paid_value / total_invoice * 100
        if total_invoice > 0 else 0
    )

    total_outstanding_pct = (
        total_outstanding / total_invoice * 100
        if total_invoice > 0 else 0
    )

    percentage_total_row = pd.DataFrame([{
        "Month": "TOTAL",
        "Customers": display_df["Customer Name"].nunique(),
        "Invoices": display_df["Invoice Number"].nunique(),
        "Total_Invoiced": total_invoice,
        "Total_Paid": total_paid_value,
        "Outstanding": total_outstanding,
        "Paid %": total_paid_pct,
        "Outstanding %": total_outstanding_pct
    }])

    # ------------------------------------------------------
    # KEEP ONLY REQUIRED COLUMNS
    # ------------------------------------------------------

    monthly_percentage = monthly_percentage[
        [
            "Month",
            "Customers",
            "Invoices",
            "Paid %",
            "Outstanding %"
        ]
    ]

    # ------------------------------------------------------
    # ADD TOTAL ROW
    # ------------------------------------------------------

    monthly_percentage = pd.concat(
        [
            monthly_percentage,
            percentage_total_row[
                [
                    "Month",
                    "Customers",
                    "Invoices",
                    "Paid %",
                    "Outstanding %"
                ]
            ]
        ],
        ignore_index=True
    )

    # ------------------------------------------------------
    # FORMAT PERCENTAGES
    # ------------------------------------------------------

    monthly_percentage["Paid %"] = (
        monthly_percentage["Paid %"]
        .map(lambda x: f"{x:.1f}%")
    )

    monthly_percentage["Outstanding %"] = (
        monthly_percentage["Outstanding %"]
        .map(lambda x: f"{x:.1f}%")
    )

    st.dataframe(
        monthly_percentage,
        width="stretch",
        hide_index=True
    )

st.divider()

# ----------------------------------------------------------
# CUSTOMER MONTHLY BREAKDOWN
# ----------------------------------------------------------

st.subheader("Customer Invoice Breakdown")

# ----------------------------------------------------------
# CUSTOMER PAYMENT MATRIX
# ----------------------------------------------------------
show_outstanding_only = st.checkbox(
    "Show Outstanding Customers Only",
    value=False
)
###################################################################



months = sorted(display_df["Month"].unique())
# ----------------------------------------------------------
# GRAND TOTALS
# ----------------------------------------------------------

grand_invoice = {m: 0 for m in months}
grand_paid = {m: 0 for m in months}

overall_invoice = 0
overall_paid = 0
rows = []
########################################################
# ==========================================================
# CUSTOMER PAYMENT MATRIX
# ==========================================================

months = sorted(display_df["Month"].unique())

rows = []

for customer in sorted(
    display_df["Customer Name"].dropna().unique()
):

    row = {
        "Customer Name": customer
    }

    customer_df = display_df[
        display_df["Customer Name"] == customer
    ]

    total_invoice = customer_df["Total"].sum()
    total_paid = customer_df["Paid"].sum()

    # ------------------------------------------------------
    # MONTHLY CELLS
    # ------------------------------------------------------

    for month in months:

        month_df = customer_df[
            customer_df["Month"] == month
        ]

        invoice_value = month_df["Total"].sum()
        paid_value = month_df["Paid"].sum()

        if IS_FINANCIAL:

            if invoice_value == 0:

                row[month] = "-"

            elif paid_value == 0:

                row[month] = (
                    f"£0 / £{invoice_value:,.0f}"
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

            # --------------------------------------------------
            # PERCENTAGE VIEW
            # --------------------------------------------------

            if invoice_value == 0:

                row[month] = "-"

            else:

                paid_pct = (
                    paid_value / invoice_value
                ) * 100

                row[month] = (
                    f"{paid_pct:.1f}%"
                )

    # ------------------------------------------------------
    # TOTAL
    # ------------------------------------------------------

    if IS_FINANCIAL:

        if total_invoice == 0:

            row["Total"] = "-"

        elif total_paid == 0:

            row["Total"] = (
                f"£0 / £{total_invoice:,.0f}"
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
                total_paid / total_invoice
            ) * 100

            row["Total"] = (
                f"{total_paid_pct:.1f}%"
            )

    rows.append(row)


customer_table = pd.DataFrame(rows)

# ==========================================================
# OUTSTANDING ONLY FILTER
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
        customer_table["Total"].apply(
            has_outstanding
        )
    ]


# ==========================================================
# GRAND TOTAL ROW
# ==========================================================

# Determine which customers are currently visible
# after the Outstanding Only filter
visible_customers = customer_table["Customer Name"].tolist()

grand_total_df = display_df[
    display_df["Customer Name"].isin(visible_customers)
].copy()

# ----------------------------------------------------------
# CREATE GRAND TOTAL ROW
# ----------------------------------------------------------

grand_row = {
    "Customer Name": "GRAND TOTAL"
}

grand_total_invoice = grand_total_df["Total"].sum()
grand_total_paid = grand_total_df["Paid"].sum()

# ----------------------------------------------------------
# MONTHLY GRAND TOTALS
# ----------------------------------------------------------

for month in months:

    month_df = grand_total_df[
        grand_total_df["Month"] == month
    ]

    month_invoice = month_df["Total"].sum()
    month_paid = month_df["Paid"].sum()

    if IS_FINANCIAL:

        if month_invoice == 0:

            grand_row[month] = "-"

        elif month_paid == 0:

            grand_row[month] = (
                f"£0 / £{month_invoice:,.0f}"
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
                month_paid / month_invoice
            ) * 100

            grand_row[month] = (
                f"{month_paid_pct:.1f}%"
            )

# ----------------------------------------------------------
# GRAND TOTAL COLUMN
# ----------------------------------------------------------

if IS_FINANCIAL:

    if grand_total_invoice == 0:

        grand_row["Total"] = "-"

    elif grand_total_paid == 0:

        grand_row["Total"] = (
            f"£0 / £{grand_total_invoice:,.0f}"
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

# ----------------------------------------------------------
# APPEND GRAND TOTAL
# ----------------------------------------------------------

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

    # ------------------------------------------------------
    # FINANCIAL VIEW
    # ------------------------------------------------------

    if IS_FINANCIAL:

        if "/" not in value:

            return "background-color:#d9ead3;"

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

            return "background-color:#f4cccc;"

        return "background-color:#fff2cc;"

    # ------------------------------------------------------
    # PERCENTAGE VIEW
    # ------------------------------------------------------

    percentage = float(
        value
        .replace("%", "")
        .strip()
    )

    if percentage >= 100:

        return "background-color:#d9ead3;"

    elif percentage <= 0:

        return "background-color:#f4cccc;"

    else:

        return "background-color:#fff2cc;"


# ----------------------------------------------------------
# STYLE CUSTOMER TABLE
# ----------------------------------------------------------

styled = customer_table.style.map(
    colour_cells,
    subset=customer_table.columns[1:]
)

# ----------------------------------------------------------
# HIGHLIGHT GRAND TOTAL ROW
# ----------------------------------------------------------

def highlight_grand_total(row):

    if row["Customer Name"] == "GRAND TOTAL":

        return [
            "font-weight:bold; background-color:#e6e6e6;"
        ] * len(row)

    return [""] * len(row)


styled = styled.apply(
    highlight_grand_total,
    axis=1
)

# ----------------------------------------------------------
# DISPLAY
# ----------------------------------------------------------

st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True
)




# ==========================================================
# PART 3 - CUSTOMER DRILLDOWN
# ==========================================================

st.divider()
st.header("🔍 Customer Details")

# ----------------------------------------------------------
# CUSTOMER SELECTION
# ----------------------------------------------------------

customer_list = sorted(display_df["Customer Name"].dropna().unique())

selected_customer = st.selectbox(
    "Select Customer",
    customer_list
)
customer_info = contacts[
    contacts["Display Name"]
        .astype(str)
        .str.strip()
        ==
    str(selected_customer).strip()
].copy()

# ----------------------------------------------------------
# CUSTOMER INFORMATION
# ----------------------------------------------------------

if not customer_info.empty:

    info = customer_info.iloc[0]

    st.subheader("Customer Information")

    c1, c2 = st.columns(2)

    with c1:
        #st.write("**Company**", info.get("Company Name", "-"))
        customer_name = " ".join(
            str(info.get(col, "")).strip()
            for col in ["Salutation", "First Name", "Last Name"]
            if pd.notna(info.get(col)) and str(info.get(col)).strip()
        )
        
        st.write("**Company**", info.get("Company Name", "-"))
        st.write("**Customer**", customer_name if customer_name else "-")
        #st.write("**Status**", info.get("Status", "-"))
        st.write("**Customer Since**", pd.to_datetime(info.get("Created Time")).strftime("%d-%m-%Y"))
        st.write("**Status**", info.get("Status", "-"))
        #st.write("**Customer Since**", pd.to_datetime(info.get("Created Time")).strftime("%d-%m-%Y"))
        #st.write("**Customer**", info.get("Contact Name", "-"))


    with c2:
        address = ", ".join([
            str(info.get("Billing Address", "")),
            str(info.get("Billing City", "")),
            str(info.get("Billing Code", ""))
        ])

        st.write("**Address**", address)
        st.write("**Phone**", info.get("Phone", "-"))
        st.write("**Mobile**", info.get("MobilePhone", "-"))
        st.write("**Email**", info.get("EmailID", "-"))

    st.divider()

# ----------------------------------------------------------
# CUSTOMER DATA
# ----------------------------------------------------------

customer_invoices = display_df[
    display_df["Customer Name"] == selected_customer
].copy()

customer_payments = payments[
    payments["Customer Name"] == selected_customer
].copy()

# ==========================================================
# CUSTOMER KPIs
# ==========================================================

cust_total = customer_invoices["Total"].sum()
cust_balance = customer_invoices["Balance"].sum()
cust_paid = customer_invoices["Paid"].sum()

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
        cust_paid / cust_total * 100
        if cust_total > 0 else 0
    )

    customer_outstanding_pct = (
        cust_balance / cust_total * 100
        if cust_total > 0 else 0
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
# ----------------------------------------------------------
# INVOICE LEDGER
# ----------------------------------------------------------

st.subheader("Invoice Ledger")

ledger = customer_invoices.copy()

# ----------------------------------------------------------
# PAYMENT SUMMARY
# ----------------------------------------------------------

payment_summary = (
    customer_payments
    .groupby("Invoice Number", as_index=False)
    .agg(
        Payment_Date=("Date", "max"),
        Paid_Amount=("Amount Applied to Invoice", "sum")
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

ledger["Payment_Date"] = (
    ledger["Payment_Date"]
)

# ----------------------------------------------------------
# OUTSTANDING
# ----------------------------------------------------------

ledger["Outstanding"] = ledger["Balance"]

# Safety check

ledger["Paid_Amount"] = ledger[
    ["Paid_Amount", "Total"]
].min(axis=1)

# ----------------------------------------------------------
# STATUS
# ----------------------------------------------------------
today = pd.Timestamp.today().normalize()

ledger["Status"] = "Current"

ledger.loc[
    ledger["Due Date"] < today,
    "Status"
] = "Overdue"

ledger.loc[
    (ledger["Paid_Amount"] > 0) &
    (ledger["Outstanding"] > 0),
    "Status"
] = "Partially Paid"

ledger.loc[
    ledger["Outstanding"] <= 0,
    "Status"
] = "Paid"
# ----------------------------------------------------------
# DAYS OVERDUE
# ----------------------------------------------------------

ledger["Days Overdue"] = np.where(
    ledger["Status"].isin(["Overdue", "Partially Paid"]),
    (today - ledger["Due Date"]).dt.days,
    0
)

ledger["Days Overdue"] = (
    ledger["Days Overdue"]
    .fillna(0)
    .astype(int)
)

# ----------------------------------------------------------
# DISPLAY
# ----------------------------------------------------------

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

    ledger = ledger.rename(columns={
        "Invoice Number": "Invoice",
        "Payment_Date": "Payment Date",
        "Total": "Amount (£)",
        "Paid_Amount": "Paid (£)",
        "Outstanding": "Outstanding (£)"
    })

else:

    # ------------------------------------------------------
    # PERCENTAGE LEDGER
    # ------------------------------------------------------

    ledger["Paid %"] = np.where(
        ledger["Total"] > 0,
        (
            ledger["Paid_Amount"]
            / ledger["Total"]
        ) * 100,
        0
    )

    ledger["Outstanding %"] = np.where(
        ledger["Total"] > 0,
        (
            ledger["Outstanding"]
            / ledger["Total"]
        ) * 100,
        0
    )

    ledger["Paid %"] = ledger["Paid %"].map(
        lambda x: f"{x:.1f}%"
    )

    ledger["Outstanding %"] = ledger[
        "Outstanding %"
    ].map(
        lambda x: f"{x:.1f}%"
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

    ledger = ledger.rename(columns={
        "Invoice Number": "Invoice",
        "Payment_Date": "Payment Date"
    })
# ----------------------------------------------------------
# FORMAT DATES
# ----------------------------------------------------------

date_columns = [
    "Invoice Date",
    "Due Date",
    "Payment Date"
]

for col in date_columns:
    ledger[col] = pd.to_datetime(
        ledger[col],
        errors="coerce"
    ).dt.strftime("%d-%m-%Y")

ledger[date_columns] = ledger[date_columns].fillna("-")

# ----------------------------------------------------------
# REPLACE ZERO VALUES
# ----------------------------------------------------------

ledger["Days Overdue"] = ledger["Days Overdue"].replace(0, "-")

# ----------------------------------------------------------
# ROW COLOURS
# ----------------------------------------------------------

def colour_rows(row):

    if row["Status"] == "Paid":
        colour = "background-color:#d4edda;color:black;"

    elif row["Status"] == "Current":
        colour = "background-color:#fff3cd;color:black;"

    elif row["Status"] == "Partially Paid":
        colour = "background-color:#ffe599;color:black;"

    else:  # Overdue
        colour = "background-color:#f8d7da;color:black;"

    return [colour] * len(row)
###################################
# ----------------------------------------------------------
# DISPLAY CURRENCY
# ----------------------------------------------------------

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
    .apply(colour_rows, axis=1)
)
st.dataframe(
    ledger_style,
    width="stretch",
    hide_index=True
)
######################################################
