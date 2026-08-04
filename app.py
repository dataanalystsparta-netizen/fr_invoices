# ==========================================================
# ZOHO ACCOUNTS RECEIVABLE DASHBOARD
# PART 1 - IMPORTS, DATA LOADING & PREPARATION
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

st.set_page_config(
    page_title="FastRanking Dashboard",
    page_icon="💰",
    layout="wide"
)

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
# ----------------------------------------------------------
# DATE FILTERS
# ----------------------------------------------------------

st.subheader("Filters")

f1, f2 = st.columns(2)

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
# FILTER DATA
# ----------------------------------------------------------

display_df = invoices[
    (invoices["Invoice Date"] >= pd.Timestamp(start_date)) &
    (invoices["Invoice Date"] <= pd.Timestamp(end_date))
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
# KPI CARDS
# ----------------------------------------------------------

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
with c1:
    kpi_card("👥 Customers", f"{total_customers:,}")

with c2:
    kpi_card("📄 Invoices", f"{total_invoices:,}")

with c3:
    kpi_card("💷 Invoiced", f"£{total_invoiced:,.2f}")

with c4:
    kpi_card("✅ Paid", f"£{total_paid:,.2f}")

with c5:
    kpi_card("⏳ Pending", f"£{total_pending:,.2f}")

with c6:
    kpi_card("📅 Future Due", f"£{future_due:,.2f}")

with c7:
    kpi_card("🔴 Overdue", f"£{overdue_total:,.2f}")

with c8:
    kpi_card("📊 Collection", f"{collection_rate:.1f}%")
# ----------------------------------------------------------
# MONTHLY BREAKDOWN
# ----------------------------------------------------------

st.subheader("Monthly Invoice Summary")

monthly_display = (
    display_df
    .groupby("Month", as_index=False)
    .agg(
        Customers=("Customer Name", "nunique"),
        Invoices=("Invoice Number", "nunique"),
        Total_Invoiced=("Total", "sum"),
        Outstanding=("Balance", "sum")
    )
)

monthly_display = monthly_display.rename(columns={
    "Month":"Month",
    "Customers":"Customers",
    "Invoices":"Invoices",
    "Total_Invoiced":"Invoiced (£)",
    "Outstanding":"Outstanding (£)"
})


# ----------------------------------------------------------
# GRAND TOTAL
# ----------------------------------------------------------

grand_total = pd.DataFrame([{
    "Month": "TOTAL",
    "Customers": monthly_display["Customers"].sum(),
    "Invoices": monthly_display["Invoices"].sum(),
    "Invoiced (£)": monthly_display["Invoiced (£)"].sum(),
    "Outstanding (£)": monthly_display["Outstanding (£)"].sum()
}])

monthly_display = pd.concat(
    [monthly_display, grand_total],
    ignore_index=True
)


##########




st.dataframe(
    monthly_display,
    use_container_width=True,
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
for customer in sorted(display_df["Customer Name"].unique()):

    row = {"Customer Name": customer}

    customer_df = display_df[
        display_df["Customer Name"] == customer
    ]

    total_invoice = 0
    total_paid = 0

    for month in months:

        month_df = customer_df[
            customer_df["Month"] == month
        ]

        invoice_value = month_df["Total"].sum()
        paid_value = month_df["Paid"].sum()
        grand_invoice[month] += invoice_value
        grand_paid[month] += paid_value

        total_invoice += invoice_value
        total_paid += paid_value
        overall_invoice += invoice_value
        overall_paid += paid_value

        if invoice_value == 0:
            row[month] = "-"

        elif paid_value == 0:
            row[month] = f"£0 / £{invoice_value:,.0f}"

        elif paid_value >= invoice_value:
            row[month] = f"£{invoice_value:,.0f}"

        else:
            row[month] = f"£{paid_value:,.0f} / £{invoice_value:,.0f}"

    if total_invoice == 0:
        row["Total"] = "-"
    
    elif total_paid == 0:
        row["Total"] = f"£0 / £{total_invoice:,.0f}"
    
    elif total_paid >= total_invoice:
        row["Total"] = f"£{total_invoice:,.0f}"
    
    else:
        row["Total"] = f"£{total_paid:,.0f} / £{total_invoice:,.0f}"

    rows.append(row)


# ----------------------------------------------------------
# GRAND TOTAL ROW
# ----------------------------------------------------------

total_row = {
    "Customer Name": "GRAND TOTAL"
}

for month in months:

    invoice = grand_invoice[month]
    paid = grand_paid[month]

    if invoice == 0:
        total_row[month] = "-"

    elif paid == 0:
        total_row[month] = f"£0 / £{invoice:,.0f}"

    elif paid >= invoice:
        total_row[month] = f"£{invoice:,.0f}"

    else:
        total_row[month] = f"£{paid:,.0f} / £{invoice:,.0f}"

if overall_invoice == 0:
    total_row["Total"] = "-"

elif overall_paid == 0:
    total_row["Total"] = f"£0 / £{overall_invoice:,.0f}"

elif overall_paid >= overall_invoice:
    total_row["Total"] = f"£{overall_invoice:,.0f}"

else:
    total_row["Total"] = f"£{overall_paid:,.0f} / £{overall_invoice:,.0f}"

rows.append(total_row)












customer_table = pd.DataFrame(rows)

# ----------------------------------------------------------
# OUTSTANDING ONLY FILTER
# ----------------------------------------------------------

if show_outstanding_only:

    def has_outstanding(total_value):

        if total_value == "-":
            return False

        # Green cells contain only one amount (fully paid)
        if "/" not in total_value:
            return False

        paid = float(
            total_value.split("/")[0]
            .replace("£", "")
            .replace(",", "")
            .strip()
        )

        invoice = float(
            total_value.split("/")[1]
            .replace("£", "")
            .replace(",", "")
            .strip()
        )

        return paid < invoice

    customer_table = customer_table[
        customer_table["Total"].apply(has_outstanding)
    ]











def colour_cells(value):

    if value == "-":
        return ""

    if "/" not in value:
        return "background-color:#d9ead3;"

    paid = float(
        value.split("/")[0]
        .replace("£", "")
        .replace(",", "")
        .strip()
    )

    invoice = float(
        value.split("/")[1]
        .replace("£", "")
        .replace(",", "")
        .strip()
    )

    if paid == 0:
        return "background-color:#f4cccc;"

    return "background-color:#fff2cc;"





styled = customer_table.style.map(
    colour_cells,
    subset=customer_table.columns[1:]
)

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

# ----------------------------------------------------------
# CUSTOMER KPIs
# ----------------------------------------------------------

cust_total = customer_invoices["Total"].sum()
cust_balance = customer_invoices["Balance"].sum()
cust_paid = cust_total - cust_balance

k1, k2, k3 = st.columns(3)

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
    "Invoice Number":"Invoice",
    "Payment_Date":"Payment Date",
    "Total":"Amount (£)",
    "Paid_Amount":"Paid (£)",
    "Outstanding":"Outstanding (£)"
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

currency_columns = [
    "Amount (£)",
    "Paid (£)",
    "Outstanding (£)"
]

for col in currency_columns:

    ledger[col] = ledger[col].apply(
        lambda x: "-" if pd.isna(x) or x == 0 else f"£{x:,.2f}"
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
# ==========================================================
# PART 4 - COLLECTIONS CALLING LIST
# ==========================================================

st.divider()
st.header("📞 Collections Calling List")

calling_df = invoices.copy()

# ----------------------------------------------------------
# Payment Summary (ALL invoices)
# ----------------------------------------------------------

payment_summary_all = (
    payments
    .groupby("Invoice Number", as_index=False)
    .agg(
        Paid_Amount=("Amount Applied to Invoice", "sum"),
        Payment_Date=("Date", "max")
    )
)

calling_df = calling_df.merge(
    payment_summary_all,
    on="Invoice Number",
    how="left"
)

calling_df["Paid_Amount"] = (
    calling_df["Paid_Amount"]
    .fillna(0)
)

calling_df["Outstanding"] = calling_df["Balance"]

today = pd.Timestamp.today().normalize()

# ----------------------------------------------------------
# Status
# ----------------------------------------------------------

calling_df["Status"] = "Current"

calling_df.loc[
    calling_df["Due Date"] < today,
    "Status"
] = "Overdue"

calling_df.loc[
    (calling_df["Paid_Amount"] > 0) &
    (calling_df["Outstanding"] > 0),
    "Status"
] = "Partially Paid"

calling_df.loc[
    calling_df["Outstanding"] <= 0,
    "Status"
] = "Paid"

# ----------------------------------------------------------
# Only invoices requiring action
# ----------------------------------------------------------

calling_df = calling_df[
    calling_df["Outstanding"] > 0
].copy()

# ----------------------------------------------------------
# Days overdue
# ----------------------------------------------------------

calling_df["Days Overdue"] = (
    today - calling_df["Due Date"]
).dt.days

calling_df["Days Overdue"] = (
    calling_df["Days Overdue"]
    .clip(lower=0)
)

# ----------------------------------------------------------
# Total Due (Customer)
# ----------------------------------------------------------

total_due = (
    calling_df.groupby("Customer Name")["Outstanding"]
    .sum()
)

calling_df["Total Due"] = (
    calling_df["Customer Name"]
    .map(total_due)
)

# ----------------------------------------------------------
# Merge Contact Details
# ----------------------------------------------------------

contact_cols = [
    "Display Name",
    "Phone",
    "MobilePhone",
    "EmailID"
]

calling_df = calling_df.merge(
    contacts[contact_cols],
    left_on="Customer Name",
    right_on="Display Name",
    how="left"
)

calling_df = calling_df.drop(columns="Display Name")

calling_df.rename(columns={
    "MobilePhone": "Mobile",
    "EmailID": "Email"
}, inplace=True)

calling_df["Phone"] = calling_df["Phone"].fillna("")
calling_df["Mobile"] = calling_df["Mobile"].fillna("")
calling_df["Email"] = calling_df["Email"].fillna("")

# ----------------------------------------------------------
# Priority
# ----------------------------------------------------------

calling_df["Priority"] = np.select(

    [
        calling_df["Days Overdue"] >= 90,

        calling_df["Days Overdue"] >= 30,

        calling_df["Status"] == "Partially Paid"
    ],

    [
        "🔴 High",

        "🟡 Medium",

        "🟦 Follow Up"
    ],

    default="🟢 Low"

)

# ----------------------------------------------------------
# Blank collection fields
# ----------------------------------------------------------

calling_df["Disposition"] = ""
calling_df["PTP Date"] = ""
calling_df["Remarks"] = ""
# ----------------------------------------------------------
# Remove Duplicate Invoice Numbers
# ----------------------------------------------------------

calling_df = (
    calling_df
    .sort_values("Invoice Date")
    .drop_duplicates(
        subset="Invoice Number",
        keep="first"
    )
    .reset_index(drop=True)
)
# ----------------------------------------------------------
# Select Columns
# ----------------------------------------------------------

calling_df = calling_df[
    [
        "Priority",
        "Customer Name",
        "Invoice Number",
        "Invoice Date",
        "Due Date",
        "Status",
        "Phone",
        "Mobile",
        "Email",
        "Total",
        "Paid_Amount",
        "Outstanding",
        "Total Due",
        "Days Overdue",
        "Disposition",
        "PTP Date",
        "Remarks"
    ]
]

calling_df = calling_df.rename(columns={

    "Customer Name":"Customer",

    "Invoice Number":"Invoice",

    "Total":"Invoice Amount",

    "Paid_Amount":"Paid (£)",

    "Outstanding":"Outstanding (£)"

})

# ----------------------------------------------------------
# Dates
# ----------------------------------------------------------

for col in ["Invoice Date","Due Date"]:

    calling_df[col] = pd.to_datetime(
        calling_df[col]
    ).dt.strftime("%d-%m-%Y")

# ----------------------------------------------------------
# Currency
# ----------------------------------------------------------

currency_cols = [
    "Invoice Amount",
    "Paid (£)",
    "Outstanding (£)",
    "Total Due"
]

for col in currency_cols:

    calling_df[col] = calling_df[col].map(
        lambda x: f"£{x:,.2f}"
    )

# ----------------------------------------------------------
# Sort
# ----------------------------------------------------------

priority_order = {
    "🔴 High":0,
    "🟡 Medium":1,
    "🟦 Follow Up":2,
    "🟢 Low":3
}

calling_df["Sort"] = calling_df["Priority"].map(priority_order)

calling_df["Outstanding_Sort"] = calling_df["Outstanding (£)"].str.replace("£", "", regex=False)
calling_df["Outstanding_Sort"] = (
    calling_df["Outstanding_Sort"]
    .str.replace(",", "", regex=False)
    .astype(float)
)

calling_df = (
    calling_df
    .sort_values(
        ["Sort", "Days Overdue", "Outstanding_Sort"],
        ascending=[True, False, False]
    )
    .drop(columns=["Sort", "Outstanding_Sort"])
)
# ----------------------------------------------------------
# Display
# ----------------------------------------------------------

st.dataframe(
    calling_df,
    use_container_width=True,
    hide_index=True
)

# ----------------------------------------------------------
# Download Excel
# ----------------------------------------------------------

from io import BytesIO

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    calling_df.to_excel(
        writer,
        index=False,
        sheet_name="Calling List"
    )

st.download_button(

    "⬇ Download Calling List (Excel)",

    data=output.getvalue(),

    file_name="Collections_Calling_List.xlsx",

    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

)
