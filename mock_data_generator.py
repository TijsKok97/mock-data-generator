import streamlit as st
import pandas as pd
from faker import Faker
import xlsxwriter as wt
import openai
import random
import io

# Set your OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

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

# Available data types
data_types = {
    "String": fake.word,
    "Integer": lambda: fake.random_int(min=1, max=1000),
    "Boolean": lambda: fake.random_element(elements=[0, 1]),
    "City": fake.city,
    "Name": fake.name,
    "Date": fake.date_this_decade,
    "Email": fake.email,
    "Street Address": fake.street_address,
    "Country": fake.country,
    "Postal Code": fake.postcode,
    "Phone Number": fake.phone_number,
    "Company": fake.company,
    "Currency Amount": lambda: fake.pydecimal(left_digits=5, right_digits=2, positive=True),
    "Custom": lambda value: value
}

# Helper to convert string keys to functions
def get_faker_func(type_str, constant_value=None):
    if constant_value:
        return lambda: constant_value
    return data_types.get(type_str, lambda: "N/A")

# Manual Builder Mode
if mode == "Manual Builder Mode":
    # Table configuration
    for i in range(num_dims):
        with st.expander(f"Dimension Table {i+1}"):
            table_name = st.text_input(f"Table Name (Dimension {i+1})", f"Dim_Table_{i+1}", key=f"dim_table_name_{i}")
            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=1, max_value=100000, value=100, key=f"dim_num_rows_{i}")
            columns = []
            num_columns = st.number_input(f"Number of Columns for {table_name}", min_value=1, max_value=10, value=3, key=f"dim_columns_{i}")
            for c in range(num_columns):
                column_name = st.text_input(f"Column {c+1} Name for {table_name}", f"Column_{c+1}", key=f"{table_name}_col_name_{c}")
                column_type = st.selectbox(
                    f"Type for {column_name}", 
                    list(data_types.keys()),
                    key=f"{table_name}_col_{c}_{column_name}"  # Unique key
                )
                constant_value = None
                if column_type == "Custom":
                    constant_value = st.text_input(f"Constant Value for {column_name}", "", key=f"{table_name}_col_custom_{c}")
                columns.append({"name": column_name, "type": column_type, "constant": constant_value})
            dim_tables[table_name] = {"columns": columns, "num_rows": num_rows}
    
    for i in range(num_facts):
        with st.expander(f"Fact Table {i+1}"):
            table_name = st.text_input(f"Table Name (Fact {i+1})", f"Fact_Table_{i+1}", key=f"fact_table_name_{i}")
            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=1, max_value=100000, value=1000, key=f"fact_num_rows_{i}")
            columns = []
            num_columns = st.number_input(f"Number of Columns for {table_name}", min_value=1, max_value=10, value=3, key=f"fact_columns_{i}")
            linked_dimensions = []
            for dim_name in dim_tables:
                if st.checkbox(f"Link to {dim_name} for {table_name}", False, key=f"link_to_{dim_name}_{table_name}"):
                    linked_dimensions.append(dim_name)
            for c in range(num_columns):
                column_name = st.text_input(f"Column {c+1} Name for {table_name}", f"Column_{c+1}", key=f"{table_name}_fact_col_name_{c}")
                column_type = st.selectbox(
                    f"Type for {column_name}",
                    list(data_types.keys()),
                    key=f"{table_name}_fact_col_{c}_{column_name}"  # Unique key
                )
                constant_value = None
                if column_type == "Custom":
                    constant_value = st.text_input(f"Constant Value for {column_name}", "", key=f"{table_name}_fact_col_custom_{c}")
                columns.append({"name": column_name, "type": column_type, "constant": constant_value})
            fact_tables[table_name] = {"columns": columns, "num_rows": num_rows, "linked_dimensions": linked_dimensions}

# Generate Mock Data
if st.button("🚀 Generate Mock Data"):
    with st.spinner("Generating data..."):
        excel_data = {}  # dict to hold DataFrame per table
        # Generate dimension tables
        for table_name, config in dim_tables.items():
            df = pd.DataFrame({col['name']: [get_faker_func(col['type'], col['constant'])() for _ in range(config["num_rows"])] 
                               for col in config["columns"]})
            if "ID" not in df.columns:
                df["ID"] = range(1, config["num_rows"] + 1)  # Ensure sequential unique IDs
            excel_data[table_name] = df

        # Generate fact tables
        for table_name, config in fact_tables.items():
            fact_df = pd.DataFrame()
            fact_df["Fact_ID"] = range(1, config["num_rows"] + 1)  # Unique Fact ID
            for dim_name in config["linked_dimensions"]:
                if f"{dim_name}_ID" in dim_tables[dim_name]["columns"]:
                    fact_df[f"{dim_name}_ID"] = excel_data[dim_name]["ID"].sample(n=config["num_rows"], replace=True).values
            for col in config["columns"]:
                if col["name"] != "Fact_ID":
                    fact_df[col["name"]] = [get_faker_func(col["type"], col["constant"])() for _ in range(config["num_rows"])]
            excel_data[table_name] = fact_df
        
        # Create the Excel file in memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            for table_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=table_name, index=False)

        # Now that the buffer is populated, you can provide it for downloading
        st.success("✅ Excel file created successfully!")
        buffer.seek(0)
        st.download_button(
            label="📥 Download Excel File",
            data=buffer,
            file_name="mock_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
