import streamlit as st
import pandas as pd
from faker import Faker
import xlsxwriter as wt

# Initialize Faker
fake = Faker()

# Welcome message
st.markdown("### 📊 Welcome to Dimensional Model Generator for Power BI 🚀")
st.write("Define your dataset structure either manually or through AI-powered suggestions!")

# User input: Choose number of tables
num_dims = st.number_input("🟦 Number of Dimension Tables:", min_value=1, max_value=10, value=3)
num_facts = st.number_input("🟥 Number of Fact Tables:", min_value=1, max_value=5, value=1)

# User chooses between AI chatbot or manual configuration
mode = st.radio("How would you like to define the tables?", ["AI Chatbot Mode", "Manual Builder Mode"])

# Dictionary to store table configurations
dim_tables = {}
fact_tables = {}
dim_data = {}  # Store generated dimension table data

data_types = {
    "String": fake.word,
    "Integer": lambda: fake.random_int(min=1, max=1000),
    "Boolean": lambda: fake.random_element(elements=[0, 1]),
    "City": fake.city,
    "Name": fake.name,
    "Date": fake.date_this_decade,
    "Email": fake.email
}

if mode == "AI Chatbot Mode":
    user_input = st.text_area("Describe your data model needs (e.g., 'Sales transactions with customers and products'):")
    if st.button("Generate Model Suggestion"):
        # Simulated AI-generated table structures
        dim_tables = {
            "Dim_Customer": {"columns": {"ID": "Integer", "Name": "String", "City": "City"}, "num_rows": 100},
            "Dim_Product": {"columns": {"ID": "Integer", "Product_Name": "String", "Category": "String"}, "num_rows": 50}
        }
        fact_tables = {
            "Fact_Sales": {"columns": {"Fact_ID": "Integer", "Dim_Customer_ID": "Integer", "Dim_Product_ID": "Integer", "Sales_Amount": "Integer"}, "num_rows": 500}
        }
        mode = "Manual Builder Mode"  # Switch to manual mode with prefilled data

if mode == "Manual Builder Mode":
    for i, (table_name, config) in enumerate(dim_tables.items() if dim_tables else [(f"Dim_{i+1}", {"columns": {"ID": "Integer"}, "num_rows": 100}) for i in range(num_dims)]):
        with st.expander(f"Dimension Table {i+1}"):
            table_name = st.text_input(f"Name for Dimension {i+1}", value=table_name)
            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=1, max_value=100000, value=config.get("num_rows", 100))
            columns = config.get("columns", {"ID": "Integer"})
            num_columns = st.number_input(f"Columns in {table_name} (excluding ID)", min_value=1, max_value=10, value=max(1, len(columns) - 1))
            for j, (col_name, col_type) in enumerate(columns.items() if columns else []):
                if col_name != "ID":
                    col_name = st.text_input(f"Column {j+1} Name ({table_name})", value=col_name)
                    col_type = st.selectbox(f"Column {j+1} Type ({table_name})", list(data_types.keys()), index=list(data_types.keys()).index(col_type) if col_type in data_types else 0)
                    columns[col_name] = col_type
            dim_tables[table_name] = {"columns": columns, "num_rows": num_rows}

    for i, (table_name, config) in enumerate(fact_tables.items() if fact_tables else [(f"Fact_{i+1}", {"columns": {"Fact_ID": "Integer"}, "num_rows": 1000}) for i in range(num_facts)]):
        with st.expander(f"Fact Table {i+1}"):
            table_name = st.text_input(f"Name for Fact {i+1}", value=table_name)
            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=1, max_value=100000, value=config.get("num_rows", 1000))
            columns = config.get("columns", {"Fact_ID": "Integer"})
            for dim_name in dim_tables.keys():
                columns[f"{dim_name}_ID"] = "Integer"  # Foreign keys from dimension tables
            num_columns = st.number_input(f"Additional columns in {table_name}", min_value=1, max_value=10, value=max(1, len(columns) - len(dim_tables) - 1))
            for j, (col_name, col_type) in enumerate(columns.items() if columns else []):
                if col_name not in ["Fact_ID"] + [f"{dim}_ID" for dim in dim_tables.keys()]:
                    col_name = st.text_input(f"Column {j+1} Name ({table_name})", value=col_name)
                    col_type = st.selectbox(f"Column {j+1} Type ({table_name})", list(data_types.keys()), index=list(data_types.keys()).index(col_type) if col_type in data_types else 0)
                    columns[col_name] = col_type
            fact_tables[table_name] = {"columns": columns, "num_rows": num_rows}

if st.button("🚀 Generate Mock Data"):
    with st.spinner("Generating data..."):
        excel_file = "mock_data.xlsx"
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            for table_name, config in dim_tables.items():
                df = pd.DataFrame({col: [data_types[col_type]() for _ in range(config["num_rows"])] for col, col_type in config["columns"].items()})
                df["ID"] = range(1, config["num_rows"] + 1)  # Ensure sequential unique IDs
                df.to_excel(writer, sheet_name=table_name, index=False)
                dim_data[table_name] = df  # Store for reference

            for table_name, config in fact_tables.items():
                fact_df = pd.DataFrame()
                fact_df["Fact_ID"] = range(1, config["num_rows"] + 1)
                for dim_name in dim_tables.keys():
                    fact_df[f"{dim_name}_ID"] = dim_data[dim_name]["ID"].sample(n=config["num_rows"], replace=True).values
                for col, col_type in config["columns"].items():
                    if col not in ["Fact_ID"] + [f"{dim}_ID" for dim in dim_tables.keys()]:
                        fact_df[col] = [data_types[col_type]() for _ in range(config["num_rows"])]
                fact_df.to_excel(writer, sheet_name=table_name, index=False)

        st.success("✅ Excel file created successfully!")
        with open(excel_file, "rb") as file:
            st.download_button(
                label="📥 Download Excel File",
                data=file,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
