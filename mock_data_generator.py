import streamlit as st
import pandas as pd
from faker import Faker
import xlsxwriter as wt
import openai

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
    "Email": fake.email
}

# Helper to convert string keys to functions
def get_faker_func(type_str):
    return data_types.get(type_str, lambda: "N/A")

if mode == "AI Chatbot Mode":
    user_input = st.text_area("Describe your data model needs (e.g., 'Sales transactions with customers and products'):")
    if st.button("Generate Model Suggestion") and user_input:
        with st.spinner("Consulting AI to build your model..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a data model expert. Given a user description, output a JSON dictionary with two top-level keys: 'dim_tables' and 'fact_tables'. Each should be a dictionary where keys are table names and values are dictionaries with 'columns' (a dictionary of column_name: type_string) and 'num_rows' (an integer). Types can be: String, Integer, Boolean, City, Name, Date, Email."},
                        {"role": "user", "content": user_input}
                    ]
                )
                tables = eval(response.choices[0].message.content)
                dim_tables = tables.get("dim_tables", {})
                fact_tables = tables.get("fact_tables", {})

                st.success("✅ Model suggestion received. You can now generate the data!")
                st.json(tables)
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if mode == "Manual Builder Mode" or (dim_tables and fact_tables):
    for i, (table_name, config) in enumerate(dim_tables.items()):
        with st.expander(f"Dimension Table {i+1}: {table_name}"):
            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=1, max_value=100000, value=config.get("num_rows", 100))
            columns = config.get("columns", {"ID": "Integer"})
            for col_name in list(columns):
                col_type = columns[col_name]
                columns[col_name] = st.selectbox(f"Type of '{col_name}'", list(data_types.keys()), index=list(data_types.keys()).index(col_type) if col_type in data_types else 0)
            dim_tables[table_name] = {"columns": columns, "num_rows": num_rows}

    for i, (table_name, config) in enumerate(fact_tables.items()):
        with st.expander(f"Fact Table {i+1}: {table_name}"):
            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=1, max_value=100000, value=config.get("num_rows", 1000))
            columns = config.get("columns", {"Fact_ID": "Integer"})
            for col_name in list(columns):
                col_type = columns[col_name]
                columns[col_name] = st.selectbox(f"Type of '{col_name}'", list(data_types.keys()), index=list(data_types.keys()).index(col_type) if col_type in data_types else 0)
            fact_tables[table_name] = {"columns": columns, "num_rows": num_rows}

if st.button("🚀 Generate Mock Data"):
    with st.spinner("Generating data..."):
        excel_file = "mock_data.xlsx"
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            # Generate dimension tables
            for table_name, config in dim_tables.items():
                df = pd.DataFrame({col: [get_faker_func(col_type)() for _ in range(config["num_rows"])] for col, col_type in config["columns"].items()})
                if "ID" in df.columns:
                    df["ID"] = range(1, config["num_rows"] + 1)  # Ensure sequential unique IDs
                df.to_excel(writer, sheet_name=table_name, index=False)
                dim_data[table_name] = df  # Store for reference

            # Generate fact tables
            for table_name, config in fact_tables.items():
                fact_df = pd.DataFrame()
                fact_df["Fact_ID"] = range(1, config["num_rows"] + 1)
                for dim_name in dim_tables.keys():
                    if f"{dim_name}_ID" in config["columns"]:
                        fact_df[f"{dim_name}_ID"] = dim_data[dim_name]["ID"].sample(n=config["num_rows"], replace=True).values
                for col, col_type in config["columns"].items():
                    if col not in fact_df.columns:
                        fact_df[col] = [get_faker_func(col_type)() for _ in range(config["num_rows"])]
                fact_df.to_excel(writer, sheet_name=table_name, index=False)

        st.success("✅ Excel file created successfully!")
        with open(excel_file, "rb") as file:
            st.download_button(
                label="📥 Download Excel File",
                data=file,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
