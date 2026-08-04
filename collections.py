# ==========================================================
# COLLECTIONS DASHBOARD
# PART 1 - IMPORTS & DATA PREPARATION
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

st.set_page_config(
    page_title="Collections Dashboard",
    page_icon="📞",
    layout="wide"
)

st.title("📞 Collections Dashboard")

# ----------------------------------------------------------
# FILES
# ----------------------------------------------------------

INVOICE_FILE = "Invoice_zoho.xlsx"
PAYMENT_FILE = "Customer_Payment_zoho.xlsx"
AR_CURRENT_FILE = "AR_current_zoho.xlsx"
AR_OVERDUE_FILE = "AR_overdue_zoho.xlsx"
CONTACTS_FILE = "Contacts_zoho.xlsx"

NOTES_FILE = "Collections_Notes.xlsx"

# ----------------------------------------------------------
# CREATE NOTES DATABASE
# ----------------------------------------------------------

if not Path(NOTES_FILE).exists():

    pd.DataFrame(columns=[

        "Invoice Number",
        "Disposition",
        "PTP Date",
        "Next Follow Up",
        "Assigned To",
        "Remarks",
        "Last Updated"

    ]).to_excel(
        NOTES_FILE,
        index=False
    )

# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_data():

    invoices = pd.read_excel(INVOICE_FILE)
    payments = pd.read_excel(PAYMENT_FILE)
    contacts = pd.read_excel(CONTACTS_FILE)

    # -----------------------------
    # Clean headers
    # -----------------------------

    invoices.columns = invoices.columns.str.strip()
    payments.columns = payments.columns.str.strip()
    contacts.columns = contacts.columns.str.strip()

    # -----------------------------
    # Dates
    # -----------------------------

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

    # -----------------------------
    # Numeric
    # -----------------------------

    for col in [

        "Total",
        "Balance"

    ]:

        invoices[col] = pd.to_numeric(
            invoices[col],
            errors="coerce"
        ).fillna(0)

    payments["Amount Applied to Invoice"] = pd.to_numeric(

        payments["Amount Applied to Invoice"],
        errors="coerce"

    ).fillna(0)

    # -----------------------------
    # Remove Draft / Void
    # -----------------------------

    invoices = invoices[
        ~invoices["Invoice Status"].isin(
            ["Draft","Void"]
        )
    ].copy()

    # -----------------------------
    # Remove duplicate invoices
    # -----------------------------

    invoices = (
        invoices
        .sort_values("Invoice Date")
        .drop_duplicates(
            "Invoice Number",
            keep="first"
        )
    )

    # -----------------------------
    # Payment Summary
    # -----------------------------

    payment_summary = (

        payments

        .groupby(
            "Invoice Number",
            as_index=False
        )

        .agg(

            Paid=("Amount Applied to Invoice","sum"),
            Last Payment=("Date","max")

        )

    )

    invoices = invoices.merge(

        payment_summary,

        on="Invoice Number",

        how="left"

    )

    invoices["Paid"] = invoices["Paid"].fillna(0)

    invoices["Outstanding"] = invoices["Balance"]

    # -----------------------------
    # Only Outstanding Invoices
    # -----------------------------

    collections = invoices[
        invoices["Outstanding"] > 0
    ].copy()

    # -----------------------------
    # Customer Total Due
    # -----------------------------

    customer_due = (

        collections

        .groupby("Customer Name")["Outstanding"]

        .sum()

    )

    collections["Total Due"] = (
        collections["Customer Name"]
        .map(customer_due)
    )

    # -----------------------------
    # Days Overdue
    # -----------------------------

    today = pd.Timestamp.today().normalize()

    collections["Days Overdue"] = (

        today

        - collections["Due Date"]

    ).dt.days

    collections["Days Overdue"] = (
        collections["Days Overdue"]
        .clip(lower=0)
    )

    # -----------------------------
    # Status
    # -----------------------------

    collections["Status"] = np.select(

        [

            collections["Outstanding"] <= 0,

            (
                (collections["Paid"] > 0)
                &
                (collections["Outstanding"] > 0)
            ),

            collections["Due Date"] < today

        ],

        [

            "Paid",
            "Partially Paid",
            "Overdue"

        ],

        default="Current"

    )

    # -----------------------------
    # Priority
    # -----------------------------

    collections["Priority Score"] = 0

    collections.loc[
        collections["Days Overdue"] >= 90,
        "Priority Score"
    ] += 100

    collections.loc[
        collections["Days Overdue"] >= 60,
        "Priority Score"
    ] += 50

    collections.loc[
        collections["Days Overdue"] >= 30,
        "Priority Score"
    ] += 25

    collections.loc[
        collections["Status"]=="Partially Paid",
        "Priority Score"
    ] += 40

    collections.loc[
        collections["Outstanding"]>=500,
        "Priority Score"
    ] += 30

    # -----------------------------
    # Priority Text
    # -----------------------------

    collections["Priority"] = np.select(

        [

            collections["Priority Score"]>=120,

            collections["Priority Score"]>=70,

            collections["Priority Score"]>=30

        ],

        [

            "🔴 High",

            "🟡 Medium",

            "🟢 Low"

        ],

        default="⚪ Monitor"

    )

    # -----------------------------
    # Merge Contact Details
    # -----------------------------

    contacts = contacts.rename(columns={

        "Display Name":"Customer Name"

    })

    collections = collections.merge(

        contacts[

            [

                "Customer Name",

                "Company Name",

                "Phone",

                "MobilePhone",

                "EmailID"

            ]

        ],

        on="Customer Name",

        how="left"

    )

    # -----------------------------
    # Sort
    # -----------------------------

    collections = collections.sort_values(

        [

            "Priority Score",

            "Days Overdue",

            "Outstanding"

        ],

        ascending=[False,False,False]

    ).reset_index(drop=True)

    return collections, payments

collections, payments = load_data()

# ==========================================================
# PART 2 - KPI DASHBOARD & FILTERS
# ==========================================================

st.divider()

# ----------------------------------------------------------
# KPI CALCULATIONS
# ----------------------------------------------------------

today = pd.Timestamp.today().normalize()

total_customers = collections["Customer Name"].nunique()

total_invoices = len(collections)

total_outstanding = collections["Outstanding"].sum()

overdue_amount = collections.loc[
    collections["Status"] == "Overdue",
    "Outstanding"
].sum()

future_due = collections.loc[
    collections["Status"] == "Current",
    "Outstanding"
].sum()

partial_amount = collections.loc[
    collections["Status"] == "Partially Paid",
    "Outstanding"
].sum()

collection_rate = (
    (
        collections["Paid"].sum()
        /
        (
            collections["Paid"].sum()
            + total_outstanding
        )
    ) * 100
    if (collections["Paid"].sum() + total_outstanding) > 0
    else 0
)

# ----------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------

k1,k2,k3,k4,k5,k6,k7 = st.columns(7)

with k1:
    st.metric(
        "👥 Customers",
        f"{total_customers:,}"
    )

with k2:
    st.metric(
        "📄 Invoices",
        f"{total_invoices:,}"
    )

with k3:
    st.metric(
        "💰 Outstanding",
        f"£{total_outstanding:,.2f}"
    )

with k4:
    st.metric(
        "🔴 Overdue",
        f"£{overdue_amount:,.2f}"
    )

with k5:
    st.metric(
        "🟡 Future Due",
        f"£{future_due:,.2f}"
    )

with k6:
    st.metric(
        "🟦 Partial",
        f"£{partial_amount:,.2f}"
    )

with k7:
    st.metric(
        "✅ Collection %",
        f"{collection_rate:.1f}%"
    )

st.divider()

# ==========================================================
# FILTERS
# ==========================================================

st.subheader("Filters")

c1,c2,c3,c4 = st.columns(4)

# ----------------------------------------------------------
# SEARCH
# ----------------------------------------------------------

with c1:

    search = st.text_input(
        "🔍 Search Customer / Invoice",
        ""
    )

# ----------------------------------------------------------
# PRIORITY
# ----------------------------------------------------------

with c2:

    priority_filter = st.multiselect(

        "Priority",

        options=[
            "🔴 High",
            "🟡 Medium",
            "🟢 Low",
            "⚪ Monitor"
        ],

        default=[
            "🔴 High",
            "🟡 Medium",
            "🟢 Low",
            "⚪ Monitor"
        ]
    )

# ----------------------------------------------------------
# STATUS
# ----------------------------------------------------------

with c3:

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
# DAYS OVERDUE
# ----------------------------------------------------------

with c4:

    overdue_days = st.slider(

        "Minimum Days Overdue",

        0,

        int(collections["Days Overdue"].max()),

        0

    )

# ==========================================================
# OUTSTANDING RANGE
# ==========================================================

amount_filter = st.slider(

    "Outstanding Amount (£)",

    min_value=0,

    max_value=int(collections["Outstanding"].max()),

    value=(0,int(collections["Outstanding"].max()))

)

# ==========================================================
# APPLY FILTERS
# ==========================================================

display_df = collections.copy()

# Search

if search:

    s = search.lower()

    display_df = display_df[

        display_df["Customer Name"]
        .astype(str)
        .str.lower()
        .str.contains(s)

        |

        display_df["Invoice Number"]
        .astype(str)
        .str.contains(search)

    ]

# Priority

display_df = display_df[
    display_df["Priority"].isin(priority_filter)
]

# Status

display_df = display_df[
    display_df["Status"].isin(status_filter)
]

# Days overdue

display_df = display_df[
    display_df["Days Overdue"] >= overdue_days
]

# Outstanding amount

display_df = display_df[

    display_df["Outstanding"].between(

        amount_filter[0],

        amount_filter[1]

    )

]

st.caption(
    f"Showing **{len(display_df):,}** invoices across **{display_df['Customer Name'].nunique():,}** customers."
)

st.divider()

# ==========================================================
# PART 3 - COLLECTIONS WORK QUEUE
# ==========================================================

st.header("📋 Collections Work Queue")

# ----------------------------------------------------------
# DISPLAY TABLE
# ----------------------------------------------------------

queue = display_df.copy()

queue = queue[[
    "Priority",
    "Customer Name",
    "Invoice Number",
    "Phone",
    "Outstanding",
    "Total Due",
    "Due Date",
    "Days Overdue",
    "Status"
]]

queue = queue.rename(columns={

    "Customer Name":"Customer",

    "Invoice Number":"Invoice",

    "Outstanding":"Outstanding (£)",

    "Total Due":"Customer Total (£)"

})

# ----------------------------------------------------------
# FORMAT
# ----------------------------------------------------------

queue["Due Date"] = (
    pd.to_datetime(queue["Due Date"])
    .dt.strftime("%d-%m-%Y")
)

for col in [

    "Outstanding (£)",
    "Customer Total (£)"

]:

    queue[col] = queue[col].map(
        lambda x: f"£{x:,.2f}"
    )

queue["Days Overdue"] = queue["Days Overdue"].replace(
    0,
    "-"
)

# ----------------------------------------------------------
# ROW COLOURING
# ----------------------------------------------------------

def colour_queue(row):

    if row["Status"] == "Overdue":

        return [
            "background-color:#f8d7da;color:black;"
        ] * len(row)

    if row["Status"] == "Partially Paid":

        return [
            "background-color:#fff3cd;color:black;"
        ] * len(row)

    return [
        "background-color:#d4edda;color:black;"
    ] * len(row)

styled_queue = (
    queue.style
    .apply(colour_queue, axis=1)
)

st.dataframe(

    styled_queue,

    use_container_width=True,

    hide_index=True,

    height=650

)

# ==========================================================
# LIVE SUMMARY
# ==========================================================

st.divider()

left,right = st.columns([2,1])

with left:

    st.info(

        f"""
**Current Queue**

• Customers : **{display_df['Customer Name'].nunique():,}**

• Outstanding Invoices : **{len(display_df):,}**

• Total Outstanding : **£{display_df['Outstanding'].sum():,.2f}**

• Average Invoice : **£{display_df['Outstanding'].mean():,.2f}**
"""

    )

with right:

    st.success(

        f"""
### Queue Breakdown

🔴 High : {(display_df['Priority']=='🔴 High').sum()}

🟡 Medium : {(display_df['Priority']=='🟡 Medium').sum()}

🟢 Low : {(display_df['Priority']=='🟢 Low').sum()}

⚪ Monitor : {(display_df['Priority']=='⚪ Monitor').sum()}
"""

    )

st.divider()

# ==========================================================
# CUSTOMER SELECTOR
# ==========================================================

customer_list = sorted(
    display_df["Customer Name"].unique()
)

selected_customer = st.selectbox(

    "🔍 Open Customer Account",

    customer_list

)

selected_customer_df = display_df[
    display_df["Customer Name"] == selected_customer
].copy()


# ==========================================================
# PART 4 - CUSTOMER WORKSPACE
# ==========================================================

st.header("👤 Customer Workspace")

customer = selected_customer_df.iloc[0]

# ----------------------------------------------------------
# CUSTOMER INFORMATION
# ----------------------------------------------------------

c1, c2 = st.columns([2,2])

with c1:

    st.subheader("Customer Information")

    st.write("**Company**", customer.get("Company Name","-"))
    st.write("**Customer**", customer.get("Customer Name","-"))
    st.write("**Phone**", customer.get("Phone","-"))
    st.write("**Mobile**", customer.get("MobilePhone","-"))
    st.write("**Email**", customer.get("EmailID","-"))

with c2:

    st.subheader("Collections Summary")

    st.metric(
        "Outstanding",
        f"£{selected_customer_df['Outstanding'].sum():,.2f}"
    )

    st.metric(
        "Invoices",
        len(selected_customer_df)
    )

    st.metric(
        "Oldest Due",
        f"{selected_customer_df['Days Overdue'].max()} days"
    )

st.divider()

# ==========================================================
# OPEN INVOICES
# ==========================================================

st.subheader("Outstanding Invoices")

ledger = selected_customer_df.copy()

ledger = ledger[[
    "Invoice Number",
    "Invoice Date",
    "Due Date",
    "Total",
    "Paid",
    "Outstanding",
    "Status",
    "Priority"
]]

ledger = ledger.rename(columns={

    "Invoice Number":"Invoice",

    "Total":"Invoice Amount",

    "Paid":"Paid (£)",

    "Outstanding":"Outstanding (£)"

})

# ----------------------------------------------------------
# FORMAT
# ----------------------------------------------------------

for col in [

    "Invoice Date",

    "Due Date"

]:

    ledger[col] = pd.to_datetime(

        ledger[col]

    ).dt.strftime("%d-%m-%Y")

for col in [

    "Invoice Amount",

    "Paid (£)",

    "Outstanding (£)"

]:

    ledger[col] = ledger[col].map(

        lambda x: f"£{x:,.2f}"

    )

# ----------------------------------------------------------
# ROW COLOURING
# ----------------------------------------------------------

def colour_invoice(row):

    if row["Status"] == "Overdue":

        colour = "#f8d7da"

    elif row["Status"] == "Partially Paid":

        colour = "#fff3cd"

    else:

        colour = "#d4edda"

    return [

        f"background-color:{colour};color:black;"

    ] * len(row)

st.dataframe(

    ledger.style.apply(
        colour_invoice,
        axis=1
    ),

    use_container_width=True,

    hide_index=True

)

st.divider()

# ==========================================================
# PAYMENT HISTORY
# ==========================================================

st.subheader("Payment History")

customer_payments = payments[
    payments["Customer Name"] == selected_customer
].copy()

if len(customer_payments):

    payment_display = customer_payments[[
        "Date",
        "Invoice Number",
        "Amount Applied to Invoice"
    ]].copy()

    payment_display = payment_display.rename(columns={

        "Invoice Number":"Invoice",

        "Amount Applied to Invoice":"Amount Paid"

    })

    payment_display["Date"] = pd.to_datetime(
        payment_display["Date"]
    ).dt.strftime("%d-%m-%Y")

    payment_display["Amount Paid"] = payment_display[
        "Amount Paid"
    ].map(

        lambda x: f"£{x:,.2f}"

    )

    st.dataframe(

        payment_display,

        use_container_width=True,

        hide_index=True

    )

else:

    st.info("No payments recorded.")

st.divider()

# ==========================================================
# QUICK ACTIONS
# ==========================================================

st.subheader("Quick Actions")

b1,b2,b3,b4 = st.columns(4)

with b1:

    st.button(
        "☎ Called",
        use_container_width=True
    )

with b2:

    st.button(
        "📅 Promise To Pay",
        use_container_width=True
    )

with b3:

    st.button(
        "❌ No Answer",
        use_container_width=True
    )

with b4:

    st.button(
        "📧 Send Reminder",
        use_container_width=True
    )

# ==========================================================
# PART 5 - COLLECTIONS NOTES
# ==========================================================

st.divider()
st.header("📝 Collections Notes")

from pathlib import Path

NOTES_FILE = "Collections_Notes.xlsx"

# ----------------------------------------------------------
# LOAD NOTES
# ----------------------------------------------------------

if Path(NOTES_FILE).exists():

    notes_db = pd.read_excel(NOTES_FILE)

else:

    notes_db = pd.DataFrame(columns=[

        "Invoice Number",
        "Disposition",
        "PTP Date",
        "Next Follow Up",
        "Assigned To",
        "Remarks",
        "Last Updated"

    ])

# ==========================================================
# SELECT INVOICE
# ==========================================================

invoice_list = sorted(
    selected_customer_df["Invoice Number"].astype(str)
)

selected_invoice = st.selectbox(
    "Invoice",
    invoice_list
)

# ----------------------------------------------------------
# EXISTING RECORD
# ----------------------------------------------------------

record = notes_db[
    notes_db["Invoice Number"].astype(str)
    ==
    selected_invoice
]

if len(record):

    record = record.iloc[0]

    default_disposition = record["Disposition"]
    default_remarks = record["Remarks"]
    default_assigned = record["Assigned To"]

    default_ptp = pd.to_datetime(
        record["PTP Date"],
        errors="coerce"
    )

    default_follow = pd.to_datetime(
        record["Next Follow Up"],
        errors="coerce"
    )

else:

    default_disposition = ""

    default_remarks = ""

    default_assigned = ""

    default_ptp = None

    default_follow = None

# ==========================================================
# INPUTS
# ==========================================================

left,right = st.columns(2)

with left:

    disposition = st.selectbox(

        "Disposition",

        [

            "",

            "No Answer",

            "Voicemail",

            "Promise To Pay",

            "Part Payment",

            "Paid",

            "Dispute",

            "Wrong Number",

            "Call Back",

            "Escalated"

        ],

        index=0 if default_disposition == "" else
        [

            "",

            "No Answer",

            "Voicemail",

            "Promise To Pay",

            "Part Payment",

            "Paid",

            "Dispute",

            "Wrong Number",

            "Call Back",

            "Escalated"

        ].index(default_disposition)

        if default_disposition in
        [

            "",

            "No Answer",

            "Voicemail",

            "Promise To Pay",

            "Part Payment",

            "Paid",

            "Dispute",

            "Wrong Number",

            "Call Back",

            "Escalated"

        ]
        else 0

    )

    ptp = st.date_input(

        "PTP Date",

        value=default_ptp

    )

    follow = st.date_input(

        "Next Follow Up",

        value=default_follow

    )

with right:

    assigned = st.text_input(

        "Assigned To",

        value=default_assigned

    )

    remarks = st.text_area(

        "Remarks",

        value=default_remarks,

        height=180

    )

# ==========================================================
# SAVE
# ==========================================================

if st.button(
    "💾 Save Collection Notes",
    use_container_width=True
):

    new_row = {

        "Invoice Number": selected_invoice,

        "Disposition": disposition,

        "PTP Date": ptp,

        "Next Follow Up": follow,

        "Assigned To": assigned,

        "Remarks": remarks,

        "Last Updated": datetime.now()

    }

    notes_db = notes_db[
        notes_db["Invoice Number"].astype(str)
        !=
        selected_invoice
    ]

    notes_db = pd.concat(

        [

            notes_db,

            pd.DataFrame([new_row])

        ],

        ignore_index=True

    )

    notes_db.to_excel(
        NOTES_FILE,
        index=False
    )

    st.success("Notes saved successfully.")

    st.cache_data.clear()

# ==========================================================
# CURRENT NOTES
# ==========================================================

if len(record):

    st.divider()

    st.subheader("Current Notes")

    st.write("**Disposition:**", record["Disposition"])

    st.write("**PTP Date:**", record["PTP Date"])

    st.write("**Next Follow Up:**", record["Next Follow Up"])

    st.write("**Assigned To:**", record["Assigned To"])

    st.write("**Last Updated:**", record["Last Updated"])

    st.write("**Remarks:**")

    st.info(record["Remarks"])


# ==========================================================
# PART 6 - CALL HISTORY
# ==========================================================

st.divider()
st.header("☎ Update Collection Notes")

NOTES_FILE = "collections_notes.xlsx"

# ----------------------------------------------------------
# Load Existing Notes
# ----------------------------------------------------------

try:

    notes = pd.read_excel(NOTES_FILE)

except:

    notes = pd.DataFrame(columns=[
        "Invoice Number",
        "Disposition",
        "PTP Date",
        "Remarks",
        "Last Updated"
    ])

# ----------------------------------------------------------
# Merge Notes
# ----------------------------------------------------------

calling_df = calling_df.merge(

    notes,

    on="Invoice Number",

    how="left"

)

calling_df["Disposition"] = calling_df["Disposition"].fillna("")
calling_df["Remarks"] = calling_df["Remarks"].fillna("")
calling_df["PTP Date"] = calling_df["PTP Date"].fillna("")

# ----------------------------------------------------------
# Select Invoice
# ----------------------------------------------------------

invoice_choice = st.selectbox(

    "Select Invoice",

    calling_df["Invoice"].astype(str)

)

selected = calling_df[
    calling_df["Invoice"].astype(str) == invoice_choice
].iloc[0]

st.write("---")

c1, c2 = st.columns(2)

with c1:

    st.write("### Customer")

    st.write(selected["Customer"])

    st.write("Outstanding:", selected["Outstanding (£)"])

    st.write("Total Due:", selected["Total Due"])

with c2:

    st.write("### Invoice")

    st.write(selected["Invoice"])

    st.write("Due:", selected["Due Date"])

    st.write("Status:", selected["Status"])

# ----------------------------------------------------------
# Editable Fields
# ----------------------------------------------------------

new_disposition = st.selectbox(

    "Disposition",

    [

        "",

        "No Answer",

        "Left Voicemail",

        "Promised To Pay",

        "Paid",

        "Dispute",

        "Wrong Number",

        "Call Back",

        "Escalated"

    ],

    index=0

)

new_ptp = st.date_input(

    "PTP Date",

    value=None

)

new_remarks = st.text_area(

    "Remarks",

    value=str(selected["Remarks"]),

    height=150

)

# ----------------------------------------------------------
# Save
# ----------------------------------------------------------

if st.button("💾 Save Notes"):

    notes = notes[
        notes["Invoice Number"].astype(str)
        != invoice_choice
    ]

    notes.loc[len(notes)] = {

        "Invoice Number": invoice_choice,

        "Disposition": new_disposition,

        "PTP Date": str(new_ptp),

        "Remarks": new_remarks,

        "Last Updated": pd.Timestamp.now()

    }

    notes.to_excel(

        NOTES_FILE,

        index=False

    )

    st.success("Notes Saved Successfully!")

    st.rerun()
