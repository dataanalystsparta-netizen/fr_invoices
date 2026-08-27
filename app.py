# ==========================================================
# ZOHO ACCOUNTS RECEIVABLE DASHBOARD
# COMPLETE VERSION
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

st.title("💰 FastRanking Payments Dashboard")


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

    invoices = pd.read_excel(INVOICE_FILE)
    payments = pd.read_excel(PAYMENT_FILE)
    ar_current = pd.read_excel(AR_CURRENT_FILE)
    ar_overdue = pd.read_excel(AR_OVERDUE_FILE)

    try:
        contacts = pd.read_excel(CONTACTS_FILE)
    except Exception:
        contacts = pd.DataFrame()

    # ------------------------------------------------------
    # CLEAN COLUMN NAMES
    # ------------------------------------------------------

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

    if not contacts.empty:
        contacts.columns = (
            contacts.columns
            .astype(str)
            .str.strip()
        )

    # ------------------------------------------------------
    # INVOICE DATE COLUMNS
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # PAYMENT DATE COLUMNS
    # ------------------------------------------------------

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

    if "Invoice Payment Applied Date" in payments.columns:

        payments["Invoice Payment Applied Date"] = pd.to_datetime(
            payments["Invoice Payment Applied Date"],
            dayfirst=True,
            errors="coerce"
        )

    # ------------------------------------------------------
    # AR DATE COLUMNS
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # NUMERIC COLUMNS - INVOICES
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # NUMERIC COLUMNS - PAYMENTS
    # ------------------------------------------------------

    for col in [
        "Amount",
        "Amount Applied to Invoice"
    ]:

        if col in payments.columns:

            payments[col] = pd.to_numeric(
                payments[col],
                errors="coerce"
            ).fillna(0)

    # ------------------------------------------------------
    # NUMERIC COLUMNS - AR
    # ------------------------------------------------------

    for df in [ar_current, ar_overdue]:

        for col in [
            "balance",
            "amount"
        ]:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).fillna(0)

    # ------------------------------------------------------
    # REMOVE DRAFT / VOID
    # ------------------------------------------------------

    if "Invoice Status" in invoices.columns:

        invoices = invoices[
            ~invoices["Invoice Status"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["draft", "void"])
        ].copy()

    # ------------------------------------------------------
    # CLEAN INVOICE NUMBER
    # ------------------------------------------------------

    if "Invoice Number" in invoices.columns:

        invoices["Invoice Number"] = (
            invoices["Invoice Number"]
            .astype(str)
            .str.strip()
        )

    if "Invoice Number" in payments.columns:

        payments["Invoice Number"] = (
            payments["Invoice Number"]
            .astype(str)
            .str.strip()
        )

    # ------------------------------------------------------
    # REMOVE DUPLICATE INVOICES
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
    # MONTH
    # ------------------------------------------------------

    invoices["Month"] = (
        invoices["Invoice Date"]
        .dt.to_period("M")
        .astype(str)
    )

    # ------------------------------------------------------
    # PAYMENT SUMMARY
    #
    # IMPORTANT:
    # We deliberately do NOT use Invoice Payment ID.
    # Your payment file does not need that column.
    # ------------------------------------------------------

    if (
        "Invoice Number" in payments.columns
        and "Amount Applied to Invoice" in payments.columns
    ):

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

    else:

        payment_summary = pd.DataFrame(
            columns=[
                "Invoice Number",
                "Paid"
            ]
        )

    # ------------------------------------------------------
    # MERGE PAYMENT TOTALS INTO INVOICES
    # ------------------------------------------------------

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
    # CALCULATED OUTSTANDING
    # ------------------------------------------------------

    invoices["Calculated Outstanding"] = (
        invoices["Total"]
        - invoices["Paid"]
    ).clip(lower=0)

    # Dashboard outstanding
    invoices["Outstanding"] = (
        invoices["Calculated Outstanding"]
    )

    # ------------------------------------------------------
    # CUSTOMER SUMMARY
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # MONTHLY SUMMARY
    # ------------------------------------------------------

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
                "Outstanding",
                "sum"
            )
        )
        .sort_values("Month")
    )

    # ------------------------------------------------------
    # KPI VALUES
    # ------------------------------------------------------

    total_customers = (
        invoices["Customer Name"]
        .nunique()
    )

    total_invoiced = (
        invoices["Total"]
        .sum()
    )

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
        total_pending,
        contacts
    )


# ==========================================================
# LOAD EVERYTHING
# ==========================================================

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
# PART 2
# INVOICE DASHBOARD
# ==========================================================

st.subheader("Filters")


# ----------------------------------------------------------
# INVOICE DATE FILTERS
# ----------------------------------------------------------

f1, f2 = st.columns(2)

INVOICE_MIN_DATE = date(2021, 1, 1)
INVOICE_MAX_DATE = date(2027, 12, 31)

valid_invoice_dates = (
    invoices["Invoice Date"]
    .dropna()
)

if len(valid_invoice_dates):

    default_invoice_start = (
        valid_invoice_dates
        .min()
        .date()
    )

    default_invoice_end = (
        valid_invoice_dates
        .max()
        .date()
    )

else:

    default_invoice_start = date(2025, 1, 1)
    default_invoice_end = date.today()


with f1:

    start_date = st.date_input(
        "Invoice Start Date",
        value=default_invoice_start,
        min_value=INVOICE_MIN_DATE,
        max_value=INVOICE_MAX_DATE,
        key="invoice_start_date"
    )


with f2:

    end_date = st.date_input(
        "Invoice End Date",
        value=default_invoice_end,
        min_value=INVOICE_MIN_DATE,
        max_value=INVOICE_MAX_DATE,
        key="invoice_end_date"
    )


# ----------------------------------------------------------
# SAFETY
# ----------------------------------------------------------

if start_date > end_date:

    st.error(
        "Invoice Start Date cannot be after Invoice End Date."
    )

    st.stop()


# ----------------------------------------------------------
# FILTER INVOICES
# ----------------------------------------------------------

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


# ----------------------------------------------------------
# KPI VALUES
# ----------------------------------------------------------

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

# Live AR snapshot
current_total = (
    ar_current["balance"]
    .sum()
)

overdue_total = (
    ar_overdue["balance"]
    .sum()
)

total_pending = (
    current_total
    + overdue_total
)


# ==========================================================
# KPI CARDS
# ==========================================================

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


# ==========================================================
# MONTHLY INVOICE SUMMARY
# ==========================================================

st.subheader("Monthly Invoice Summary")


monthly_display = (
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
            "Balance",
            "sum"
        )
    )
)


monthly_display = monthly_display.rename(
    columns={
        "Total_Invoiced": "Invoiced (£)",
        "Outstanding": "Outstanding (£)"
    }
)


# ----------------------------------------------------------
# GRAND TOTAL
# ----------------------------------------------------------

grand_total = pd.DataFrame([
    {
        "Month": "TOTAL",
        "Customers": monthly_display["Customers"].sum(),
        "Invoices": monthly_display["Invoices"].sum(),
        "Invoiced (£)": monthly_display["Invoiced (£)"].sum(),
        "Outstanding (£)": monthly_display["Outstanding (£)"].sum()
    }
])


monthly_display = pd.concat(
    [
        monthly_display,
        grand_total
    ],
    ignore_index=True
)


st.dataframe(
    monthly_display,
    width="stretch",
    hide_index=True
)


# ==========================================================
# RECONCILIATION
# ==========================================================

st.subheader("Invoice vs AR Reconciliation")


invoice_open = invoices[
    invoices["Balance"] > 0
].copy()


invoice_open["Invoice Number"] = (
    invoice_open["Invoice Number"]
    .astype(str)
    .str.strip()
)


ar_all = pd.concat(
    [
        ar_current,
        ar_overdue
    ],
    ignore_index=True
)


if "transaction_number" in ar_all.columns:

    ar_all["transaction_number"] = (
        ar_all["transaction_number"]
        .astype(str)
        .str.strip()
    )

    ar_invoice_numbers = set(
        ar_all["transaction_number"]
    )

else:

    ar_invoice_numbers = set()


missing_from_ar = invoice_open[
    ~invoice_open["Invoice Number"]
    .isin(ar_invoice_numbers)
].copy()


invoice_balance = (
    invoice_open["Balance"]
    .sum()
)

ar_balance = (
    ar_current["balance"].sum()
    + ar_overdue["balance"].sum()
)

difference = (
    invoice_balance
    - ar_balance
)


c1, c2, c3 = st.columns(3)


with c1:

    st.metric(
        "Invoice Register Outstanding",
        f"£{invoice_balance:,.2f}"
    )


with c2:

    st.metric(
        "AR Reports Outstanding",
        f"£{ar_balance:,.2f}"
    )


with c3:

    st.metric(
        "Difference",
        f"£{difference:,.2f}"
    )


if len(missing_from_ar):

    st.warning(
        f"{len(missing_from_ar)} outstanding invoice(s) "
        "exist in the Invoice Register but are not "
        "present in the AR reports."
    )

    reconciliation_columns = [
        "Invoice Number",
        "Customer Name",
        "Invoice Date",
        "Due Date",
        "Invoice Status",
        "Balance"
    ]

    reconciliation_columns = [
        c
        for c in reconciliation_columns
        if c in missing_from_ar.columns
    ]

    reconciliation_table = (
        missing_from_ar[
            reconciliation_columns
        ]
        .copy()
    )

    for col in [
        "Invoice Date",
        "Due Date"
    ]:

        if col in reconciliation_table.columns:

            reconciliation_table[col] = (
                pd.to_datetime(
                    reconciliation_table[col],
                    errors="coerce"
                )
                .dt.strftime("%d-%m-%Y")
                .fillna("-")
            )

    if "Balance" in reconciliation_table.columns:

        reconciliation_table["Balance"] = (
            reconciliation_table["Balance"]
            .map(
                lambda x:
                f"£{x:,.2f}"
            )
        )

    st.dataframe(
        reconciliation_table,
        width="stretch",
        hide_index=True
    )

else:

    st.success(
        "✅ Invoice Register and AR reports are fully reconciled."
    )


# ==========================================================
# CUSTOMER INVOICE BREAKDOWN
# ==========================================================

st.divider()

st.subheader("Customer Invoice Breakdown")


show_outstanding_only = st.checkbox(
    "Show Outstanding Customers Only",
    value=False
)


months = sorted(
    display_df["Month"]
    .dropna()
    .unique()
)


grand_invoice = {
    m: 0
    for m in months
}

grand_paid = {
    m: 0
    for m in months
}


overall_invoice = 0
overall_paid = 0

rows = []


# ----------------------------------------------------------
# CUSTOMER ROWS
# ----------------------------------------------------------

for customer in sorted(
    display_df["Customer Name"]
    .dropna()
    .unique()
):

    row = {
        "Customer Name": customer
    }

    customer_df = display_df[
        display_df["Customer Name"]
        == customer
    ]

    total_invoice = 0
    total_paid = 0


    for month in months:

        month_df = customer_df[
            customer_df["Month"]
            == month
        ]

        invoice_value = (
            month_df["Total"]
            .sum()
        )

        paid_value = (
            month_df["Paid"]
            .sum()
        )

        grand_invoice[month] += invoice_value
        grand_paid[month] += paid_value

        total_invoice += invoice_value
        total_paid += paid_value

        overall_invoice += invoice_value
        overall_paid += paid_value


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

    rows.append(row)


# ==========================================================
# GRAND TOTAL ROW
# ==========================================================

total_row = {
    "Customer Name": "GRAND TOTAL"
}


for month in months:

    invoice_value = grand_invoice[month]
    paid_value = grand_paid[month]

    if invoice_value == 0:

        total_row[month] = "-"

    elif paid_value == 0:

        total_row[month] = (
            f"£0 / £{invoice_value:,.0f}"
        )

    elif paid_value >= invoice_value:

        total_row[month] = (
            f"£{invoice_value:,.0f}"
        )

    else:

        total_row[month] = (
            f"£{paid_value:,.0f} / "
            f"£{invoice_value:,.0f}"
        )


if overall_invoice == 0:

    total_row["Total"] = "-"

elif overall_paid == 0:

    total_row["Total"] = (
        f"£0 / £{overall_invoice:,.0f}"
    )

elif overall_paid >= overall_invoice:

    total_row["Total"] = (
        f"£{overall_invoice:,.0f}"
    )

else:

    total_row["Total"] = (
        f"£{overall_paid:,.0f} / "
        f"£{overall_invoice:,.0f}"
    )


rows.append(total_row)


customer_table = pd.DataFrame(rows)


# ==========================================================
# OUTSTANDING ONLY
# ==========================================================

if show_outstanding_only:

    def has_outstanding(total_value):

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
        .apply(has_outstanding)
    ]


# ==========================================================
# CELL COLOURS
# ==========================================================

def colour_cells(value):

    if value == "-":
        return ""

    if "/" not in value:
        return "background-color:#d9ead3;"

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

        return "background-color:#f4cccc;"

    return "background-color:#fff2cc;"


styled = customer_table.style.map(
    colour_cells,
    subset=customer_table.columns[1:]
)


st.dataframe(
    styled,
    width="stretch",
    hide_index=True
)


# ==========================================================
# PART 3
# CUSTOMER DETAILS
# ==========================================================

st.divider()

st.header("🔍 Customer Details")


customer_list = sorted(
    display_df["Customer Name"]
    .dropna()
    .unique()
)


if len(customer_list):

    selected_customer = st.selectbox(
        "Select Customer",
        customer_list,
        key="customer_selector"
    )

else:

    st.info(
        "No customers found for the selected invoice dates."
    )

    selected_customer = None


if selected_customer:

    # ------------------------------------------------------
    # CUSTOMER INFORMATION
    # ------------------------------------------------------

    if (
        not contacts.empty
        and "Display Name" in contacts.columns
    ):

        customer_info = contacts[
            contacts["Display Name"]
            == selected_customer
        ].copy()

    else:

        customer_info = pd.DataFrame()


    # ------------------------------------------------------
    # CUSTOMER INVOICES
    # ------------------------------------------------------

    customer_invoices = display_df[
        display_df["Customer Name"]
        == selected_customer
    ].copy()


    # ------------------------------------------------------
    # CUSTOMER PAYMENTS
    # ------------------------------------------------------

    customer_payments = payments[
        payments["Customer Name"]
        == selected_customer
    ].copy()


    # ------------------------------------------------------
    # CUSTOMER KPIs
    # ------------------------------------------------------

    cust_total = (
        customer_invoices["Total"]
        .sum()
    )

    cust_balance = (
        customer_invoices["Balance"]
        .sum()
    )

    cust_paid = (
        cust_total
        - cust_balance
    )


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


    # ======================================================
    # INVOICE LEDGER
    # ======================================================

    st.subheader("Invoice Ledger")


    ledger = customer_invoices.copy()


    # ------------------------------------------------------
    # CUSTOMER PAYMENT SUMMARY
    # ------------------------------------------------------

    if len(customer_payments):

        payment_summary_customer = (
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

        payment_summary_customer = pd.DataFrame(
            columns=[
                "Invoice Number",
                "Payment_Date",
                "Paid_Amount"
            ]
        )


    ledger = ledger.merge(
        payment_summary_customer,
        on="Invoice Number",
        how="left"
    )


    ledger["Paid_Amount"] = (
        ledger["Paid_Amount"]
        .fillna(0)
    )


    ledger["Outstanding"] = (
        ledger["Balance"]
    )


    # ------------------------------------------------------
    # STATUS
    # ------------------------------------------------------

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


    # ------------------------------------------------------
    # DAYS OVERDUE
    # ------------------------------------------------------

    ledger["Days Overdue"] = np.where(

        ledger["Status"] == "Overdue",

        (
            today
            - ledger["Due Date"]
        ).dt.days,

        0
    )


    ledger["Days Overdue"] = (
        ledger["Days Overdue"]
        .fillna(0)
        .astype(int)
    )


    # ------------------------------------------------------
    # DISPLAY
    # ------------------------------------------------------

    ledger_columns = [
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


    ledger_columns = [
        c
        for c in ledger_columns
        if c in ledger.columns
    ]


    ledger = ledger[
        ledger_columns
    ].copy()


    ledger = ledger.rename(
        columns={
            "Invoice Number": "Invoice",
            "Payment_Date": "Payment Date",
            "Total": "Amount (£)",
            "Paid_Amount": "Paid (£)",
            "Outstanding": "Outstanding (£)"
        }
    )


    # ------------------------------------------------------
    # FORMAT DATES
    # ------------------------------------------------------

    for col in [
        "Invoice Date",
        "Due Date",
        "Payment Date"
    ]:

        if col in ledger.columns:

            ledger[col] = (
                pd.to_datetime(
                    ledger[col],
                    errors="coerce"
                )
                .dt.strftime("%d-%m-%Y")
                .fillna("-")
            )


    if "Days Overdue" in ledger.columns:

        ledger["Days Overdue"] = (
            ledger["Days Overdue"]
            .replace(0, "-")
        )


    # ------------------------------------------------------
    # FORMAT CURRENCY
    # ------------------------------------------------------

    for col in [
        "Amount (£)",
        "Paid (£)",
        "Outstanding (£)"
    ]:

        if col in ledger.columns:

            ledger[col] = ledger[col].apply(
                lambda x:
                "-"
                if pd.isna(x) or x == 0
                else f"£{x:,.2f}"
            )


    st.dataframe(
        ledger,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# ==========================================================
# PART 4
# PAYMENTS RECEIVED
# ==========================================================
# ==========================================================

st.divider()

st.header("💷 Payments Received")

st.caption(
    "Payments are shown based on the actual payment date. "
    "These filters are completely independent of the "
    "invoice dashboard filters above."
)


# ==========================================================
# PAYMENT DATE RANGE
#
# IMPORTANT:
# This is completely independent from invoice filters.
# Fixed selectable range allows all of 2026.
# ==========================================================

PAYMENT_MIN_DATE = date(2021, 1, 1)
PAYMENT_MAX_DATE = date(2027, 12, 31)


# ----------------------------------------------------------
# FIND VALID PAYMENT DATES
# ----------------------------------------------------------

if "Date" in payments.columns:

    valid_payment_dates = (
        payments["Date"]
        .dropna()
    )

else:

    valid_payment_dates = pd.Series(
        dtype="datetime64[ns]"
    )


# ----------------------------------------------------------
# DEFAULT PAYMENT START
# ----------------------------------------------------------

if len(valid_payment_dates):

    # Use a sensible default rather than forcing
    # the full historical payment period.

    latest_payment_date = (
        valid_payment_dates
        .max()
        .date()
    )

    default_payment_end = latest_payment_date

    # Default to roughly the latest 8 months
    # while still allowing 2026 selection.

    default_payment_start = max(
        date(2025, 1, 1),
        date(
            latest_payment_date.year,
            latest_payment_date.month,
            1
        )
    )

else:

    default_payment_start = date(
        2025,
        1,
        1
    )

    default_payment_end = date.today()


# ----------------------------------------------------------
# PAYMENT FILTERS
# ----------------------------------------------------------

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


# ----------------------------------------------------------
# VALIDATE
# ----------------------------------------------------------

if payment_start_date > payment_end_date:

    st.error(
        "Payment Start Date cannot be after "
        "Payment End Date."
    )

    st.stop()


# ==========================================================
# PREPARE PAYMENT DATA
# ==========================================================

payment_view = payments.copy()


# ----------------------------------------------------------
# PAYMENT DATE
# ----------------------------------------------------------

if "Date" in payment_view.columns:

    payment_view["Payment Date"] = pd.to_datetime(
        payment_view["Date"],
        errors="coerce"
    )

else:

    payment_view["Payment Date"] = pd.NaT


# ----------------------------------------------------------
# PAYMENT AMOUNT
# ----------------------------------------------------------

if "Amount Applied to Invoice" in payment_view.columns:

    payment_view["Payment Amount"] = pd.to_numeric(
        payment_view[
            "Amount Applied to Invoice"
        ],
        errors="coerce"
    ).fillna(0)

else:

    payment_view["Payment Amount"] = 0.0


# ==========================================================
# FILTER BY ACTUAL PAYMENT DATE
# ==========================================================

payment_filtered = payment_view[
    (
        payment_view["Payment Date"]
        >= pd.Timestamp(payment_start_date)
    )
    &
    (
        payment_view["Payment Date"]
        <= pd.Timestamp(payment_end_date)
    )
].copy()


# ==========================================================
# PAYMENT KPIs
# ==========================================================

payment_total = (
    payment_filtered["Payment Amount"]
    .sum()
)


payment_entries = (
    len(payment_filtered)
)


if "Customer Name" in payment_filtered.columns:

    payment_customers = (
        payment_filtered["Customer Name"]
        .nunique()
    )

else:

    payment_customers = 0


if "Invoice Number" in payment_filtered.columns:

    payment_invoices = (
        payment_filtered["Invoice Number"]
        .nunique()
    )

else:

    payment_invoices = 0


# ==========================================================
# PAYMENT KPI CARDS
# ==========================================================

pk1, pk2, pk3, pk4 = st.columns(4)


with pk1:

    st.metric(
        "💷 Payments Received",
        f"£{payment_total:,.2f}"
    )


with pk2:

    st.metric(
        "🧾 Payment Entries",
        f"{payment_entries:,}"
    )


with pk3:

    st.metric(
        "👥 Customers",
        f"{payment_customers:,}"
    )


with pk4:

    st.metric(
        "📄 Invoices Paid",
        f"{payment_invoices:,}"
    )


# ==========================================================
# DAILY PAYMENT SUMMARY
# ==========================================================

st.subheader("Daily Payment Summary")


if payment_filtered.empty:

    st.info(
        "No payments were received during the selected "
        "payment date range."
    )

else:

    # ------------------------------------------------------
    # DAILY SUMMARY
    #
    # Explicitly construct every column.
    #
    # This prevents the duplicate-column-name problem
    # that was causing the PyArrow ValueError.
    # ------------------------------------------------------

    daily_base = (
        payment_filtered
        .copy()
    )


    # Ensure the grouping date is date-only
    daily_base["Payment Day"] = (
        daily_base["Payment Date"]
        .dt.normalize()
    )


    # ------------------------------------------------------
    # AMOUNT BY DAY
    # ------------------------------------------------------

    daily_amount = (
        daily_base
        .groupby(
            "Payment Day",
            as_index=False
        )[
            "Payment Amount"
        ]
        .sum()
        .rename(
            columns={
                "Payment Day": "Payment Date",
                "Payment Amount": "Amount Received (£)"
            }
        )
    )


    # ------------------------------------------------------
    # ENTRIES BY DAY
    # ------------------------------------------------------

    daily_entries = (
        daily_base
        .groupby(
            "Payment Day"
        )
        .size()
        .reset_index(
            name="Payment Entries"
        )
        .rename(
            columns={
                "Payment Day": "Payment Date"
            }
        )
    )


    # ------------------------------------------------------
    # CUSTOMERS BY DAY
    # ------------------------------------------------------

    if "Customer Name" in daily_base.columns:

        daily_customers = (
            daily_base
            .groupby(
                "Payment Day"
            )[
                "Customer Name"
            ]
            .nunique()
            .reset_index(
                name="Customers"
            )
            .rename(
                columns={
                    "Payment Day": "Payment Date"
                }
            )
        )

    else:

        daily_customers = pd.DataFrame(
            columns=[
                "Payment Date",
                "Customers"
            ]
        )


    # ------------------------------------------------------
    # INVOICES BY DAY
    # ------------------------------------------------------

    if "Invoice Number" in daily_base.columns:

        daily_invoices = (
            daily_base
            .groupby(
                "Payment Day"
            )[
                "Invoice Number"
            ]
            .nunique()
            .reset_index(
                name="Invoices Paid"
            )
            .rename(
                columns={
                    "Payment Day": "Payment Date"
                }
            )
        )

    else:

        daily_invoices = pd.DataFrame(
            columns=[
                "Payment Date",
                "Invoices Paid"
            ]
        )


    # ------------------------------------------------------
    # MERGE
    # ------------------------------------------------------

    daily_summary = daily_amount.merge(
        daily_entries,
        on="Payment Date",
        how="left"
    )


    daily_summary = daily_summary.merge(
        daily_customers,
        on="Payment Date",
        how="left"
    )


    daily_summary = daily_summary.merge(
        daily_invoices,
        on="Payment Date",
        how="left"
    )


    # ------------------------------------------------------
    # ABSOLUTE SAFETY:
    # REMOVE ANY DUPLICATE COLUMN NAMES
    # ------------------------------------------------------

    daily_summary = (
        daily_summary
        .loc[
            :,
            ~daily_summary.columns.duplicated()
        ]
        .copy()
    )


    # ------------------------------------------------------
    # SORT
    # ------------------------------------------------------

    daily_summary = (
        daily_summary
        .sort_values(
            "Payment Date",
            ascending=False
        )
        .reset_index(drop=True)
    )


    # ------------------------------------------------------
    # FORMAT DATE
    # ------------------------------------------------------

    daily_summary["Payment Date"] = (
        pd.to_datetime(
            daily_summary["Payment Date"],
            errors="coerce"
        )
        .dt.strftime("%d-%m-%Y")
    )


    # ------------------------------------------------------
    # FORMAT CURRENCY
    # ------------------------------------------------------

    daily_summary["Amount Received (£)"] = (
        daily_summary[
            "Amount Received (£)"
        ]
        .map(
            lambda x:
            f"£{x:,.2f}"
        )
    )


    # ------------------------------------------------------
    # FINAL COLUMN ORDER
    # ------------------------------------------------------

    daily_summary = daily_summary[
        [
            "Payment Date",
            "Amount Received (£)",
            "Payment Entries",
            "Customers",
            "Invoices Paid"
        ]
    ].copy()


    # ------------------------------------------------------
    # FINAL COLUMN UNIQUENESS CHECK
    # ------------------------------------------------------

    daily_summary.columns = [
        str(col).strip()
        for col in daily_summary.columns
    ]


    # If somehow duplicated, make unique.
    if daily_summary.columns.duplicated().any():

        seen = {}

        new_columns = []

        for col in daily_summary.columns:

            if col not in seen:

                seen[col] = 0
                new_columns.append(col)

            else:

                seen[col] += 1

                new_columns.append(
                    f"{col}_{seen[col]}"
                )

        daily_summary.columns = new_columns


    # ------------------------------------------------------
    # DISPLAY
    # ------------------------------------------------------

    st.dataframe(
        daily_summary,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# PAYMENT DETAIL
# ==========================================================

st.subheader("Payment Details")


if payment_filtered.empty:

    st.info(
        "No payment records found for the selected dates."
    )

else:

    payment_detail = payment_filtered.copy()


    # ------------------------------------------------------
    # JOIN INVOICE INFORMATION
    #
    # We use Invoice Number only.
    # No Invoice Payment ID is required.
    # ------------------------------------------------------

    invoice_lookup_columns = [
        "Invoice Number",
        "Customer Name",
        "Invoice Date",
        "Due Date",
        "Item Name"
    ]


    invoice_lookup_columns = [
        col
        for col in invoice_lookup_columns
        if col in invoices.columns
    ]


    invoice_lookup = (
        invoices[
            invoice_lookup_columns
        ]
        .copy()
    )


    # ------------------------------------------------------
    # REMOVE POSSIBLE DUPLICATES
    # ------------------------------------------------------

    if "Invoice Number" in invoice_lookup.columns:

        invoice_lookup = (
            invoice_lookup
            .drop_duplicates(
                subset="Invoice Number",
                keep="first"
            )
        )


    # ------------------------------------------------------
    # ONLY MERGE COLUMNS THAT DO NOT ALREADY EXIST
    #
    # Customer Name / Invoice Date may already be present
    # in the payment file.
    # ------------------------------------------------------

    merge_columns = [
        "Invoice Number"
    ]


    extra_invoice_columns = []

    for col in [
        "Invoice Date",
        "Due Date",
        "Item Name"
    ]:

        if col in invoice_lookup.columns:

            if col not in payment_detail.columns:

                extra_invoice_columns.append(col)


    merge_columns.extend(
        extra_invoice_columns
    )


    invoice_lookup_for_merge = (
        invoice_lookup[
            merge_columns
        ]
        .copy()
    )


    # ------------------------------------------------------
    # MERGE
    # ------------------------------------------------------

    payment_detail = payment_detail.merge(
        invoice_lookup_for_merge,
        on="Invoice Number",
        how="left"
    )


    # ------------------------------------------------------
    # CUSTOMER NAME
    # ------------------------------------------------------

    if "Customer Name" not in payment_detail.columns:

        payment_detail["Customer Name"] = "-"

    else:

        payment_detail["Customer Name"] = (
            payment_detail["Customer Name"]
            .fillna("-")
        )


    # ------------------------------------------------------
    # ITEM DESCRIPTION
    # ------------------------------------------------------

    if "Item Name" in payment_detail.columns:

        payment_detail["Item Description"] = (
            payment_detail["Item Name"]
            .fillna("-")
        )

    else:

        payment_detail["Item Description"] = "-"


    # ------------------------------------------------------
    # DATE COLUMNS
    # ------------------------------------------------------

    if "Invoice Date" not in payment_detail.columns:

        payment_detail["Invoice Date"] = pd.NaT


    if "Due Date" not in payment_detail.columns:

        payment_detail["Due Date"] = pd.NaT


    # ------------------------------------------------------
    # BUILD A BRAND NEW DISPLAY TABLE
    #
    # This is safer than renaming the original dataframe
    # and accidentally retaining duplicate columns.
    # ------------------------------------------------------

    payment_detail_display = pd.DataFrame({
        "Customer Name": payment_detail[
            "Customer Name"
        ],

        "Invoice": payment_detail[
            "Invoice Number"
        ],

        "Item Description": payment_detail[
            "Item Description"
        ],

        "Invoice Date": payment_detail[
            "Invoice Date"
        ],

        "Due Date": payment_detail[
            "Due Date"
        ],

        "Payment Date": payment_detail[
            "Payment Date"
        ],

        "Amount Received (£)": payment_detail[
            "Payment Amount"
        ]
    })


    # ------------------------------------------------------
    # FORMAT DATES
    # ------------------------------------------------------

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
            .dt.strftime("%d-%m-%Y")
            .fillna("-")
        )


    # ------------------------------------------------------
    # FORMAT AMOUNT
    # ------------------------------------------------------

    payment_detail_display[
        "Amount Received (£)"
    ] = (
        payment_detail_display[
            "Amount Received (£)"
        ]
        .map(
            lambda x:
            f"£{x:,.2f}"
        )
    )


    # ------------------------------------------------------
    # SORT BY PAYMENT DATE
    # ------------------------------------------------------

    sort_dates = pd.to_datetime(
        payment_detail["Payment Date"],
        errors="coerce"
    )


    payment_detail_display["_sort_date"] = (
        sort_dates
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


    # ------------------------------------------------------
    # ABSOLUTE DUPLICATE COLUMN SAFETY
    # ------------------------------------------------------

    payment_detail_display = (
        payment_detail_display
        .loc[
            :,
            ~payment_detail_display.columns.duplicated()
        ]
        .copy()
    )


    # ------------------------------------------------------
    # DISPLAY
    # ------------------------------------------------------

    st.dataframe(
        payment_detail_display,
        width="stretch",
        hide_index=True
    )


# ==========================================================
# END
# ==========================================================
