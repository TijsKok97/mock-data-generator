input("Press Enter to exit...")

import streamlit as st
import pandas as pd
from faker import Faker

# Initialize Faker
fake = Faker()

# Title of the app
st.title("📊 Mock Data Generator")

# User input: Number of rows
num_rows = st.number_input("🔢 Enter the number of rows:", min_value=1, max_value=10000, value=100)

# User input: Select columns
st.write("🛠️ **Define your dataset structure**")
columns = {}

# Default column types for selection
column_types = {
    "Name": "name",
    "Email": "email",
    "Date": "date",
    "Integer (1-1000)": "integer",
    "City": "city",
    "Company": "company"
}

# Let user add columns
num_columns = st.number_input("➕ How many columns?", min_value=1, max_value=10, value=3)
for i in range(num_columns):
    col_name = st.text_input(f"Column {i+1} Name:", value=f"Column_{i+1}")
    col_type = st.selectbox(f"Column {i+1} Type:", list(column_types.keys()), key=f"type_{i}")
    columns[col_name] = column_types[col_type]

# Generate mock data
def generate_mock_data(columns, num_rows):
    dataset = {}
    for column_name, data_type in columns.items():
        if data_type == "name":
            dataset[column_name] = [fake.name() for _ in range(num_rows)]
        elif data_type == "email":
            dataset[column_name] = [fake.email() for _ in range(num_rows)]
        elif data_type == "date":
            dataset[column_name] = [fake.date_this_decade() for _ in range(num_rows)]
        elif data_type == "integer":
            dataset[column_name] = [fake.random_int(min=1, max=1000) for _ in range(num_rows)]
        elif data_type == "city":
            dataset[column_name] = [fake.city() for _ in range(num_rows)]
        elif data_type == "company":
            dataset[column_name] = [fake.company() for _ in range(num_rows)]
    return pd.DataFrame(dataset)

# Button to generate and display data
if st.button("🚀 Generate Mock Data"):
    df = generate_mock_data(columns, num_rows)
    st.success("✅ Dataset created successfully!")
    st.dataframe(df)  # Show the dataset preview

    # Save as Excel
    file_name = "mock_data.xlsx"
    df.to_excel(file_name, index=False)

    # Create a download button
    with open(file_name, "rb") as file:
        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
