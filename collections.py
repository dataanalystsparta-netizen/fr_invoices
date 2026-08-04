# ==========================================================
# COLLECTIONS DASHBOARD
# PART 1 - IMPORTS, DATA LOADING & KPIs
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

st.set_page_config(
    page_title="Collections Dashboard",
    page_icon="📞",
    layout="wide"
)

st.title("📞 FastRanking Collections Dashboard")

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

@st.cache_data(show_spinner=False)
def load_data():

    invoices = pd.read_excel(INVOICE_FILE)
    payments = pd.read_excel(PAYMENT_FILE)
    contacts = pd.read_excel(CONTACTS_FILE)

    invoices.columns = invoices.columns.str.strip()
    payments.columns = payments.columns.str.strip()
    contacts.columns = contacts.columns.str.strip()

    # ------------------------------------------------------
    # Dates
    # ------------------------------------------------------

    for col in [
        "Invoice Date",
        "Due Date",
        "Last Payment Date",
        "Expected Payment Date"
    ]:

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

    # ------------------------------------------------------
    # Numeric
    # ------------------------------------------------------

    for col in [
        "Total",
        "Balance"
    ]:

        invoices[col] = (
            pd.to_numeric(
                invoices[col],
                errors="coerce"
            )
            .fillna(0)
        )

    payments["Amount Applied to Invoice"] = (
        pd.to_numeric(
            payments["Amount Applied to Invoice"],
            errors="coerce"
        )
        .fillna(0)
    )

    # ------------------------------------------------------
    # Remove Draft / Void
    # ------------------------------------------------------

    invoices = invoices[
        ~invoices["Invoice Status"].isin(
            ["Draft", "Void"]
        )
    ].copy()

    # ------------------------------------------------------
    # Remove duplicate invoices
    # ------------------------------------------------------

    invoices = (
        invoices
        .sort_values("Invoice Date")
        .drop_duplicates(
            subset="Invoice Number",
            keep="first"
        )
        .reset_index(drop=True)
    )

    # ------------------------------------------------------
    # Payment Summary
    # ------------------------------------------------------

    payment_summary = (
        payments
        .groupby(
            "Invoice Number",
            as_index=False
        )
        .agg(
            Paid=("Amount Applied to Invoice","sum"),
            Last_Payment=("Date","max")
        )
    )

    invoices = invoices.merge(
        payment_summary,
        on="Invoice Number",
        how="left"
    )

    invoices["Paid"] = invoices["Paid"].fillna(0)

    # ------------------------------------------------------
    # Outstanding Only
    # ------------------------------------------------------

    invoices = invoices[
        invoices["Balance"] > 0
    ].copy()

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    today = pd.Timestamp.today().normalize()

    invoices["Status"] = np.select(

        [

            invoices["Paid"] >= invoices["Total"],

            (
                (invoices["Paid"] > 0)
                &
                (invoices["Balance"] > 0)
            ),

            invoices["Due Date"] < today

        ],

        [

            "Paid",

            "Partially Paid",

            "Overdue"

        ],

        default="Current"

    )

    # ------------------------------------------------------
    # Days Overdue
    # ------------------------------------------------------

    invoices["Days Overdue"] = np.where(

        invoices["Due Date"] < today,

        (today - invoices["Due Date"]).dt.days,

        0

    )

    invoices["Days Overdue"] = (
        invoices["Days Overdue"]
        .fillna(0)
        .astype(int)
    )

    # ------------------------------------------------------
    # Customer Total Due
    # ------------------------------------------------------

    customer_due = (
        invoices.groupby("Customer Name")["Balance"]
        .sum()
    )

    invoices["Total Due"] = (
        invoices["Customer Name"]
        .map(customer_due)
    )

    # ------------------------------------------------------
    # Merge Contact Details
    # ------------------------------------------------------

    contacts["Display Name"] = (
        contacts["Display Name"]
        .astype(str)
        .str.strip()
    )

    invoices["Customer Name"] = (
        invoices["Customer Name"]
        .astype(str)
        .str.strip()
    )

    invoices = invoices.merge(

        contacts[

            [
                "Display Name",
                "Phone",
                "MobilePhone",
                "EmailID"
            ]

        ],

        left_on="Customer Name",

        right_on="Display Name",

        how="left"

    )

    # ------------------------------------------------------
    # Priority
    # ------------------------------------------------------

    invoices["Priority"] = np.select(

        [

            invoices["Days Overdue"] >= 90,

            invoices["Days Overdue"] >= 30,

            invoices["Status"] == "Partially Paid"

        ],

        [

            "🔴 High",

            "🟡 Medium",

            "🟦 Follow Up"

        ],

        default="🟢 Low"

    )

    return invoices


calling_df = load_data()

# ==========================================================
# KPIs
# ==========================================================

total_customers = calling_df["Customer Name"].nunique()

total_invoices = len(calling_df)

current_due = calling_df.loc[
    calling_df["Status"] == "Current",
    "Balance"
].sum()

overdue_due = calling_df.loc[
    calling_df["Status"] == "Overdue",
    "Balance"
].sum()

partial_due = calling_df.loc[
    calling_df["Status"] == "Partially Paid",
    "Balance"
].sum()

total_due = calling_df["Balance"].sum()

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("👥 Customers", f"{total_customers:,}")
c2.metric("📄 Invoices", f"{total_invoices:,}")
c3.metric("🟢 Current", f"£{current_due:,.2f}")
c4.metric("🟡 Partial", f"£{partial_due:,.2f}")
c5.metric("🔴 Overdue", f"£{overdue_due:,.2f}")
c6.metric("💰 Total Due", f"£{total_due:,.2f}")

st.divider()

# ==========================================================
# PART 2 - FILTERS & COLLECTION TABLE
# ==========================================================

st.subheader("Filters")

f1, f2, f3, f4 = st.columns(4)

# ----------------------------------------------------------
# Customer Search
# ----------------------------------------------------------

with f1:

    search = st.text_input(
        "Search Customer",
        placeholder="Customer / Invoice..."
    )

# ----------------------------------------------------------
# Status
# ----------------------------------------------------------

with f2:

    status_filter = st.multiselect(

        "Status",

        options=[
            "Current",
            "Overdue",
            "Partially Paid"
        ],

        default=[
            "Current",
            "Overdue",
            "Partially Paid"
        ]

    )

# ----------------------------------------------------------
# Priority
# ----------------------------------------------------------

with f3:

    priority_filter = st.multiselect(

        "Priority",

        options=[
            "🔴 High",
            "🟡 Medium",
            "🟦 Follow Up",
            "🟢 Low"
        ],

        default=[
            "🔴 High",
            "🟡 Medium",
            "🟦 Follow Up",
            "🟢 Low"
        ]

    )

# ----------------------------------------------------------
# Minimum Days Overdue
# ----------------------------------------------------------

with f4:

    min_days = st.number_input(

        "Minimum Days Overdue",

        min_value=0,

        value=0,

        step=30

    )

# ==========================================================
# APPLY FILTERS
# ==========================================================

display_df = calling_df.copy()

display_df = display_df[
    display_df["Status"].isin(status_filter)
]

display_df = display_df[
    display_df["Priority"].isin(priority_filter)
]

display_df = display_df[
    display_df["Days Overdue"] >= min_days
]

if search:

    search = search.lower().strip()

    display_df = display_df[

        display_df["Customer Name"]
        .str.lower()
        .str.contains(search, na=False)

        |

        display_df["Invoice Number"]
        .astype(str)
        .str.contains(search)

    ]

# ==========================================================
# SORTING
# ==========================================================

priority_order = {

    "🔴 High":0,

    "🟡 Medium":1,

    "🟦 Follow Up":2,

    "🟢 Low":3

}

display_df["Priority Sort"] = (
    display_df["Priority"]
    .map(priority_order)
)

display_df = (

    display_df

    .sort_values(

        [

            "Priority Sort",

            "Days Overdue",

            "Balance"

        ],

        ascending=[

            True,

            False,

            False

        ]

    )

    .drop(columns="Priority Sort")

)

# ==========================================================
# DISPLAY TABLE
# ==========================================================

table = display_df[

    [

        "Priority",

        "Customer Name",

        "Invoice Number",

        "Phone",

        "MobilePhone",

        "EmailID",

        "Invoice Date",

        "Due Date",

        "Status",

        "Days Overdue",

        "Total",

        "Paid",

        "Balance",

        "Total Due"

    ]

].copy()

table = table.rename(columns={

    "Customer Name":"Customer",

    "Invoice Number":"Invoice",

    "Phone":"Phone",

    "MobilePhone":"Mobile",

    "EmailID":"Email",

    "Total":"Invoice Amount",

    "Paid":"Paid (£)",

    "Balance":"Outstanding (£)"

})

# ==========================================================
# FORMAT DATES
# ==========================================================

for col in [

    "Invoice Date",

    "Due Date"

]:

    table[col] = pd.to_datetime(

        table[col]

    ).dt.strftime("%d-%m-%Y")

# ==========================================================
# FORMAT CURRENCY
# ==========================================================

currency_cols = [

    "Invoice Amount",

    "Paid (£)",

    "Outstanding (£)",

    "Total Due"

]

for col in currency_cols:

    table[col] = table[col].map(

        lambda x: f"£{x:,.2f}"

    )

# ==========================================================
# ROW COLOURS
# ==========================================================

def colour_rows(row):

    if row["Priority"] == "🔴 High":

        colour = "#f8d7da"

    elif row["Priority"] == "🟡 Medium":

        colour = "#fff3cd"

    elif row["Priority"] == "🟦 Follow Up":

        colour = "#d1ecf1"

    else:

        colour = "#d4edda"

    return [

        f"background-color:{colour}; color:black;"

    ] * len(row)

styled_table = (

    table.style

    .apply(

        colour_rows,

        axis=1

    )

)

st.subheader("Outstanding Collections")

st.dataframe(

    styled_table,

    use_container_width=True,

    hide_index=True,

    height=700

)

# ==========================================================
# DOWNLOAD
# ==========================================================

from io import BytesIO

output = BytesIO()

with pd.ExcelWriter(

    output,

    engine="openpyxl"

) as writer:

    table.to_excel(

        writer,

        index=False,

        sheet_name="Collections"

    )

st.download_button(

    "⬇ Download Collections List",

    data=output.getvalue(),

    file_name="Collections_List.xlsx",

    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

)

# ==========================================================
# PART 3 - CUSTOMER / INVOICE DETAILS
# ==========================================================

st.divider()

st.header("📄 Invoice Details")

# ----------------------------------------------------------
# Select Invoice
# ----------------------------------------------------------

invoice_list = (
    display_df["Invoice Number"]
    .astype(str)
    .sort_values()
    .unique()
)

selected_invoice = st.selectbox(

    "Select Invoice",

    invoice_list

)

invoice = display_df[
    display_df["Invoice Number"].astype(str)
    == selected_invoice
].iloc[0]

# ----------------------------------------------------------
# Customer Information
# ----------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Customer")

    st.write("**Customer**", invoice["Customer Name"])

    st.write("**Phone**",
             invoice.get("Phone","-"))

    st.write("**Mobile**",
             invoice.get("MobilePhone","-"))

    st.write("**Email**",
             invoice.get("EmailID","-"))

with right:

    st.subheader("Invoice")

    st.write("**Invoice**",
             invoice["Invoice Number"])

    st.write("**Invoice Date**",
             invoice["Invoice Date"].strftime("%d-%m-%Y"))

    st.write("**Due Date**",
             invoice["Due Date"].strftime("%d-%m-%Y"))

    st.write("**Status**",
             invoice["Status"])

st.divider()

# ----------------------------------------------------------
# Financial Summary
# ----------------------------------------------------------

k1, k2, k3, k4 = st.columns(4)

with k1:

    st.metric(

        "Invoice Amount",

        f"£{invoice['Total']:,.2f}"

    )

with k2:

    st.metric(

        "Paid",

        f"£{invoice['Paid']:,.2f}"

    )

with k3:

    st.metric(

        "Outstanding",

        f"£{invoice['Balance']:,.2f}"

    )

with k4:

    st.metric(

        "Days Overdue",

        int(invoice["Days Overdue"])

    )

st.divider()

# ----------------------------------------------------------
# Customer Outstanding Invoices
# ----------------------------------------------------------

st.subheader("Customer Outstanding Invoices")

customer_invoices = display_df[

    display_df["Customer Name"]

    ==

    invoice["Customer Name"]

].copy()

customer_table = customer_invoices[

    [

        "Invoice Number",

        "Invoice Date",

        "Due Date",

        "Status",

        "Total",

        "Paid",

        "Balance"

    ]

]

customer_table = customer_table.rename(columns={

    "Invoice Number":"Invoice",

    "Total":"Invoice Amount",

    "Paid":"Paid",

    "Balance":"Outstanding"

})

for col in [

    "Invoice Date",

    "Due Date"

]:

    customer_table[col] = pd.to_datetime(

        customer_table[col]

    ).dt.strftime("%d-%m-%Y")

for col in [

    "Invoice Amount",

    "Paid",

    "Outstanding"

]:

    customer_table[col] = customer_table[col].map(

        lambda x: f"£{x:,.2f}"

    )

st.dataframe(

    customer_table,

    use_container_width=True,

    hide_index=True

)

st.divider()

# ==========================================================
# COLLECTION NOTES (Placeholder)
# ==========================================================

st.subheader("📝 Collection Notes")

st.info(
    "Collection Notes, Disposition, Promise To Pay and "
    "Call History will be added in Version 2."
)
