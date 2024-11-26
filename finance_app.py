import pandas as pd
import csv
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt

# Class for handling CSV operations
class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        """Initialize the CSV file if it doesn't exist."""
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        """Add a new transaction to the CSV file."""
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        st.success("Transaction added successfully!")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        """Retrieve transactions within a date range."""
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=cls.FORMAT)
        start_date = datetime.strptime(start_date, cls.FORMAT)
        end_date = datetime.strptime(end_date, cls.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            st.warning("No transactions found in the given date range.")
            return pd.DataFrame(columns=cls.COLUMNS)
        else:
            st.success(f"Transactions from {start_date.strftime(cls.FORMAT)} to {end_date.strftime(cls.FORMAT)}:")
            return filtered_df


def plot_transactions_matplotlib(df):
    """Plot income and expenses using Matplotlib."""
    df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
    df.set_index("date", inplace=True)

    income_df = df[df["category"] == "Income"].resample("D").sum()
    expense_df = df[df["category"] == "Expense"].resample("D").sum()

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses Over Time")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

# Initialize the CSV
CSV.initialize_csv()

# Streamlit App Interface
st.title("Finance Tracker")
st.sidebar.title("Menu")

# Sidebar Menu
menu = st.sidebar.selectbox("Select an option:", ["Add Transaction", "View Transactions"])

if menu == "Add Transaction":
    st.header("Add New Transaction")
    with st.form("add_transaction_form"):
        date = st.date_input("Transaction Date", datetime.today())
        amount = st.number_input("Amount", min_value=0.01, format="%.2f")
        category = st.selectbox("Category", ["Income", "Expense"])
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            CSV.add_entry(date.strftime(CSV.FORMAT), amount, category, description)

elif menu == "View Transactions":
    st.header("View Transactions")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Show Transactions"):
        df = CSV.get_transactions(start_date.strftime(CSV.FORMAT), end_date.strftime(CSV.FORMAT))
        if not df.empty:
            st.dataframe(df)

            # Show Summary
            total_income = df[df["category"] == "Income"]["amount"].sum()
            total_expense = df[df["category"] == "Expense"]["amount"].sum()
            st.write("### Summary")
            st.write(f"**Total Income:** ${total_income:.2f}")
            st.write(f"**Total Expense:** ${total_expense:.2f}")
            st.write(f"**Net Savings:** ${total_income - total_expense:.2f}")

            # Option to Plot
            plot_type = st.selectbox("Select Visualization Type:", ["Matplotlib"])
            if plot_type == "Matplotlib":
                plot_transactions_matplotlib(df)