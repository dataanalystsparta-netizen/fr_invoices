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

# ----------------------------------------------------------
# FILES
# ----------------------------------------------------------

INVOICE_FILE = "Invoice_zoho.xlsx"
PAYMENT_FILE = "Customer_Payment_zoho.xlsx"
AR_CURRENT_FILE = "AR_current_zoho.xlsx"
AR_OVERDUE_FILE = "AR_overdue_zoho.xlsx"

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

    return (
        invoices,
        payments,
        ar_current,
        ar_overdue,
        customer_summary,
        monthly_summary,
        total_customers,
        total_invoiced,
        total_pending
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
    TOTAL_PENDING
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

# Live AR Snapshot (do not date filter)
current_total = ar_current["balance"].sum()
overdue_total = ar_overdue["balance"].sum()

total_pending = current_total + overdue_total
# ----------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "👥 Total Customers",
        f"{total_customers:,}"
    )

with c2:

    st.metric(
        "📄 Total Invoices",
        f"{total_invoices:,}"
    )

with c3:

    st.metric(
        "💷 Total Invoiced",
        f"£{total_invoiced:,.2f}"
    )

with c4:

    st.metric(
        "⏳ Pending / Due",
        f"£{total_pending:,.2f}"   
    )

st.divider()

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

ledger["Status"] = np.where(
    ledger["Outstanding"] <= 0,
    "Paid",
    np.where(
        ledger["Due Date"] < today,
        "Overdue",
        "Current"
    )
)

# ----------------------------------------------------------
# DAYS OVERDUE
# ----------------------------------------------------------

ledger["Days Overdue"] = np.where(
    ledger["Status"] == "Overdue",
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

    else:
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
st.subheader("Invoice Number Data Types")

st.write("Invoices:", invoices["Invoice Number"].dtype)
st.write("Payments:", payments["Invoice Number"].dtype)
st.write("AR transaction_number:", ar_overdue["transaction_number"].dtype)
st.subheader("Sample Invoice Numbers")

st.write("Invoices")
st.write(invoices["Invoice Number"].head(10))

st.write("Payments")
st.write(payments["Invoice Number"].head(10))

st.write("AR")
st.write(ar_overdue["transaction_number"].head(10))
st.subheader("Counts")

st.write("Invoices:", len(invoices))
st.write("Unique Invoice Numbers:", invoices["Invoice Number"].nunique())

st.write("Payments:", len(payments))
st.write("Unique Payment Invoice Numbers:", payments["Invoice Number"].nunique())

st.write("Current AR:", len(ar_current))
st.write("Overdue AR:", len(ar_overdue))

duplicates = invoices[
    invoices["Invoice Number"].duplicated(keep=False)
]

st.subheader("Duplicate Invoice Numbers")

st.write("Duplicate rows:", len(duplicates))

st.dataframe(
    duplicates[
        ["Invoice Number", "Customer Name", "Total", "Balance"]
    ],
    width="stretch",
    hide_index=True
)

st.subheader("Invoices Still Outstanding")

st.dataframe(
    invoices[invoices["Balance"] > 0][
        [
            "Invoice Number",
            "Customer Name",
            "Total",
            "Balance"
        ]
    ],
    width="stretch",
    hide_index=True
)

st.subheader("Balance Check")

st.write(
    "Invoice Balance:",
    invoices["Balance"].sum()
)

st.write(
    "Current AR:",
    ar_current["balance"].sum()
)

st.write(
    "Overdue AR:",
    ar_overdue["balance"].sum()
)

st.write(
    "AR Total:",
    ar_current["balance"].sum()
    + ar_overdue["balance"].sum()
)

st.dataframe(
    invoices[
        invoices["Invoice Number"] == "242029"
    ][[
        "Invoice Number",
        "Customer Name",
        "Invoice Date",
        "Due Date",
        "Invoice Status",
        "Total",
        "Balance",
        "Expected Payment Date",
        "Last Payment Date"
    ]],
    width="stretch",
    hide_index=True
)
st.dataframe(
    invoices[
        invoices["Invoice Number"].astype(str).str.contains("242029")
    ],
    width="stretch",
    hide_index=True
)

ar_current[
    ar_current["transaction_number"] == 242029
]
ar_overdue[
    ar_overdue["transaction_number"] == 242029
]


invoices.loc[
    invoices["Invoice Number"] == "242029",
    [
        "Invoice Number",
        "Invoice Date",
        "Due Date",
        "Invoice Status",
        "Balance"
    ]
]




