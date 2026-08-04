# ==========================================================
# COLLECTIONS DASHBOARD V2
# PART 1 - IMPORTS & DATA LOADING
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np

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
CONTACTS_FILE = "Contacts_zoho.xlsx"

# ==========================================================
# LOAD DATA
# ==========================================================

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
            ).fillna(0)
        )

    payments["Amount Applied to Invoice"] = (
        pd.to_numeric(
            payments["Amount Applied to Invoice"],
            errors="coerce"
        ).fillna(0)
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

            Paid=(
                "Amount Applied to Invoice",
                "sum"
            ),

            Last_Payment=(
                "Date",
                "max"
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

            (
                (invoices["Paid"] > 0)
                &
                (invoices["Balance"] > 0)
            ),

            invoices["Due Date"] < today

        ],

        [

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

        (
            today
            - invoices["Due Date"]
        ).dt.days,

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

        invoices

        .groupby("Customer Name")

        ["Balance"]

        .sum()

    )

    invoices["Total Due"] = (

        invoices["Customer Name"]

        .map(customer_due)

    )

    invoices["Invoice Count"] = (

        invoices

        .groupby("Customer Name")

        ["Invoice Number"]

        .transform("count")

    )

    # ------------------------------------------------------
    # Contact Details
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

    return invoices


calling_df = load_data()

# ==========================================================
# CUSTOMER LEVEL COLLECTIONS TABLE
# ==========================================================

today = pd.Timestamp.today().normalize()

# ----------------------------------------------------------
# Outstanding invoices only
# ----------------------------------------------------------

calling_df = collections_df[
    collections_df["Balance"] > 0
].copy()
# Remove duplicate invoices

calling_df = (
    calling_df
    .sort_values("Invoice Date")
    .drop_duplicates("Invoice Number")
)

# ----------------------------------------------------------
# Days Overdue
# ----------------------------------------------------------

calling_df = collections_df.copy()

# ----------------------------------------------------------
# Merge Contact Details
# ----------------------------------------------------------

contacts_lookup = contacts.copy()

contacts_lookup["Display Name"] = (
    contacts_lookup["Display Name"]
    .astype(str)
    .str.strip()
)

calling_df = calling_df.merge(

    contacts_lookup[[
        "Display Name",
        "Phone",
        "MobilePhone",
        "EmailID"
    ]],

    left_on="Customer Name",

    right_on="Display Name",

    how="left"

)

calling_df["Phone"] = (
    calling_df["Phone"]
    .fillna(calling_df["MobilePhone"])
)

# ----------------------------------------------------------
# Customer Summary
# ----------------------------------------------------------

customer_table = (

    calling_df

    .groupby("Customer Name", as_index=False)

    .agg(

        Phone=("Phone","first"),

        Total_Due=("Balance","sum"),

        Invoice_Count=("Invoice Number","nunique"),

        Oldest_Due=("Due Date","min"),

        Max_Overdue=("Days Overdue","max")

    )

)

# ----------------------------------------------------------
# Priority
# ----------------------------------------------------------

customer_table["Priority"] = np.select(

    [

        customer_table["Max_Overdue"]>=90,

        customer_table["Max_Overdue"]>=30

    ],

    [

        "🔴 High",

        "🟡 Medium"

    ],

    default="🟢 Low"

)

# ----------------------------------------------------------
# Blank Collection Fields
# ----------------------------------------------------------

customer_table["Disposition"] = ""

customer_table["PTP Date"] = ""

customer_table["Remarks"] = ""

# ----------------------------------------------------------
# Formatting
# ----------------------------------------------------------

customer_table["Oldest_Due"] = (

    pd.to_datetime(customer_table["Oldest_Due"])

    .dt.strftime("%d-%m-%Y")

)

customer_table["Total Due"] = customer_table["Total_Due"].map(

    lambda x:f"£{x:,.2f}"

)

customer_table.drop(columns="Total_Due", inplace=True)

customer_table.rename(

    columns={

        "Customer Name":"Customer",

        "Invoice_Count":"Invoices",

        "Max_Overdue":"Days Overdue"

    },

    inplace=True

)

priority_order={

    "🔴 High":0,

    "🟡 Medium":1,

    "🟢 Low":2

}

customer_table["Sort"]=customer_table["Priority"].map(priority_order)

customer_table=customer_table.sort_values(

    ["Sort","Days Overdue"],

    ascending=[True,False]

).drop(columns="Sort")


# ==========================================================
# CUSTOMER SUMMARY TABLE
# ==========================================================

st.subheader("Collections Queue")

# ----------------------------------------------------------
# Build Customer Summary
# ----------------------------------------------------------

customer_summary = (
    collections_df
    .groupby("Customer Name", as_index=False)
    .agg(
        Phone=("Phone", "first"),
        Mobile=("Mobile", "first"),
        Email=("Email", "first"),
        Outstanding=("Outstanding", "sum"),
        Future_Due=("Future Due", "sum"),
        Overdue=("Overdue", "sum"),
        Oldest_Due=("Due Date", "min"),
        Invoice_Count=("Invoice Number", "nunique"),
        Last_Invoice=("Invoice Date", "max")
    )
)

# ----------------------------------------------------------
# Days Overdue
# ----------------------------------------------------------

today = pd.Timestamp.today().normalize()

customer_summary["Days Overdue"] = (
    today - customer_summary["Oldest_Due"]
).dt.days.clip(lower=0)

# ----------------------------------------------------------
# Priority
# ----------------------------------------------------------

customer_summary["Priority"] = np.select(

    [
        customer_summary["Days Overdue"] >= 90,
        customer_summary["Days Overdue"] >= 60,
        customer_summary["Days Overdue"] >= 30
    ],

    [
        "🔴 High",
        "🟠 Medium",
        "🟡 Follow Up"
    ],

    default="🟢 Current"

)

# ----------------------------------------------------------
# Empty Collection Columns
# ----------------------------------------------------------

customer_summary["Disposition"] = ""
customer_summary["PTP Date"] = ""
customer_summary["Next Follow Up"] = ""
customer_summary["Remarks"] = ""

# ----------------------------------------------------------
# Rename
# ----------------------------------------------------------

customer_summary = customer_summary.rename(columns={

    "Customer Name":"Customer",

    "Outstanding":"Total Due (£)",

    "Future_Due":"Future Due (£)",

    "Overdue":"Overdue (£)",

    "Invoice_Count":"Invoices"

})

# ----------------------------------------------------------
# Dates
# ----------------------------------------------------------

customer_summary["Oldest_Due"] = pd.to_datetime(
    customer_summary["Oldest_Due"]
).dt.strftime("%d-%m-%Y")

customer_summary["Last_Invoice"] = pd.to_datetime(
    customer_summary["Last_Invoice"]
).dt.strftime("%d-%m-%Y")

# ----------------------------------------------------------
# Currency
# ----------------------------------------------------------

currency_cols = [
    "Total Due (£)",
    "Future Due (£)",
    "Overdue (£)"
]

for col in currency_cols:

    customer_summary[col] = customer_summary[col].map(
        lambda x: f"£{x:,.2f}"
    )

# ----------------------------------------------------------
# Sort
# ----------------------------------------------------------

priority_order = {
    "🔴 High":0,
    "🟠 Medium":1,
    "🟡 Follow Up":2,
    "🟢 Current":3
}

customer_summary["Sort"] = (
    customer_summary["Priority"]
    .map(priority_order)
)

customer_summary = (
    customer_summary
    .sort_values(
        ["Sort","Days Overdue"],
        ascending=[True,False]
    )
    .drop(columns="Sort")
)

# ----------------------------------------------------------
# Display
# ----------------------------------------------------------

st.dataframe(
    customer_summary,
    use_container_width=True,
    hide_index=True
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

    customer_summary.to_excel(
        writer,
        index=False,
        sheet_name="Collections"
    )

st.download_button(

    "⬇ Download Collections Queue",

    data=output.getvalue(),

    file_name="Collections_Queue.xlsx",

    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

)
