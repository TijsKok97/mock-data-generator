import streamlit as st
import pandas as pd
from faker import Faker
import xlsxwriter as wt

# Initialize Faker
fake = Faker()

# Title of the app
st.title("📊 Mocked up")

# User input: Number of sheets
num_sheets = st.number_input("📑 Number of Sheets:", min_value=1, max_value=10, value=1)

# Dictionary to store sheet configurations
sheets_config = {}

for sheet_index in range(num_sheets):
    with st.expander(f"⚙️ Configure Sheet {sheet_index + 1}"):
        sheet_name = st.text_input(f"📄 Sheet {sheet_index + 1} Name:", value=f"Sheet_{sheet_index + 1}")
        num_rows = st.number_input(f"🔢 Number of rows for {sheet_name}:", min_value=1, max_value=10000, value=100, key=f"rows_{sheet_index}")

        # Column selection
        st.write("🛠️ **Define the dataset structure**")
        columns = {}
        column_types = {
            "Name": "name",
            "Email": "email",
            "Date": "date",
            "Integer (1-1000)": "integer",
            "City": "city",
            "Company": "company"
        }

        num_columns = st.number_input(f"➕ How many columns in {sheet_name}?", min_value=1, max_value=10, value=3, key=f"cols_{sheet_index}")
        for i in range(num_columns):
            col_name = st.text_input(f"Column {i+1} Name (Sheet {sheet_index + 1}):", value=f"Column_{i+1}", key=f"colname_{sheet_index}_{i}")
            col_type = st.selectbox(f"Column {i+1} Type (Sheet {sheet_index + 1}):", list(column_types.keys()), key=f"type_{sheet_index}_{i}")
            columns[col_name] = column_types[col_type]

        sheets_config[sheet_name] = {"num_rows": num_rows, "columns": columns}

# Function to generate mock data
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

# Generate and save data
if st.button("🚀 Generate Mock Data"):
    with st.spinner("Generating data..."):
        excel_file = "mock_data.xlsx"
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            for sheet_name, config in sheets_config.items():
                df = generate_mock_data(config["columns"], config["num_rows"])
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        st.success("✅ Excel file created successfully!")

        # Provide download button
        with open(excel_file, "rb") as file:
            st.download_button(
                label="📥 Download Excel File",
                data=file,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
