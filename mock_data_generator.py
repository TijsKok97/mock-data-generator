'''
v1.0
import streamlit as st
import pandas as pd
from faker import Faker
import xlsxwriter as wt

# Initialize Faker
fake = Faker()

# Welcome message
st.markdown("### 📢 Welcome to MockedUp! 🎉\n Here, you can quickly generate randomized datasets for any purpose. Configure the settings and click the button below to generate your data. For now, it's possible to generate this data into an Excel file.")


# User input: Number of sheets
num_sheets = st.number_input("📑 Number of sheets inside your Excel file:", min_value=1, max_value=10, value=1)

# Dictionary to store sheet configurations
sheets_config = {}

for sheet_index in range(num_sheets):
    with st.expander(f"⚙️ Configure Sheet {sheet_index + 1}"):
        sheet_name = st.text_input(f"📄 Sheet {sheet_index + 1} Name:", value=f"Sheet_{sheet_index + 1}")
        num_rows = st.number_input(f"🔢 Number of rows for {sheet_name}:", min_value=1, max_value=100000, value=100, key=f"rows_{sheet_index}")

        # Column selection
        st.write("🛠️ **Define the dataset structure**")
        columns = {}
        column_types = {
            "Name": "name",
            "Email": "email",
            "Date": "date",
            "Address": "address",  # Full address
            "Street Address": "street_address",
            "City": "city",
            "State": "state",
            "Zipcode": "zipcode",
            "Country": "country",
            "Birthdate": "birthdate",
            "Phone Number": "phone_number",
            "Company": "company",
            "Job Title": "job",
            "URL": "url",
            "Boolean": "boolean",
            "Credit Card": "credit_card",
            "Color": "color",
            "Random Text": "text"
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
        elif data_type == "address":
            dataset[column_name] = [fake.address() for _ in range(num_rows)]
        elif data_type == "street_address":
            dataset[column_name] = [fake.street_address() for _ in range(num_rows)]
        elif data_type == "city":
            dataset[column_name] = [fake.city() for _ in range(num_rows)]
        elif data_type == "state":
            dataset[column_name] = [fake.state() for _ in range(num_rows)]
        elif data_type == "zipcode":
            dataset[column_name] = [fake.zipcode() for _ in range(num_rows)]
        elif data_type == "country":
            dataset[column_name] = [fake.country() for _ in range(num_rows)]
        elif data_type == "birthdate":
            dataset[column_name] = [fake.date_of_birth() for _ in range(num_rows)]
        elif data_type == "phone_number":
            dataset[column_name] = [fake.phone_number() for _ in range(num_rows)]
        elif data_type == "company":
            dataset[column_name] = [fake.company() for _ in range(num_rows)]
        elif data_type == "job":
            dataset[column_name] = [fake.job() for _ in range(num_rows)]
        elif data_type == "url":
            dataset[column_name] = [fake.url() for _ in range(num_rows)]
        elif data_type == "boolean":
            dataset[column_name] = [fake.boolean() for _ in range(num_rows)]
        elif data_type == "credit_card":
            dataset[column_name] = [fake.credit_card_number() for _ in range(num_rows)]
        elif data_type == "color":
            dataset[column_name] = [fake.color_name() for _ in range(num_rows)]
        elif data_type == "text":
            dataset[column_name] = [fake.text() for _ in range(num_rows)]
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
'''

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
        st.write("(AI processing to generate tables will go here)")  # Placeholder for AI logic

else:
    for i in range(num_dims):
        with st.expander(f"Dimension Table {i+1}"):
            table_name = st.text_input(f"Name for Dimension {i+1}", value=f"Dim_{i+1}")
            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=1, max_value=100000, value=100)
            columns = {"ID": "Integer"}  # Primary key for dimension table
            num_columns = st.number_input(f"Columns in {table_name} (excluding ID)", min_value=1, max_value=10, value=3)
            for j in range(num_columns):
                col_name = st.text_input(f"Column {j+1} Name ({table_name})", value=f"Column_{j+1}")
                col_type = st.selectbox(f"Column {j+1} Type ({table_name})", list(data_types.keys()))
                columns[col_name] = col_type
            dim_tables[table_name] = {"columns": columns, "num_rows": num_rows}

    for i in range(num_facts):
        with st.expander(f"Fact Table {i+1}"):
            table_name = st.text_input(f"Name for Fact {i+1}", value=f"Fact_{i+1}")
            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=1, max_value=100000, value=1000)
            columns = {"Fact_ID": "Integer"}  # Primary key for fact table
            for dim_name in dim_tables.keys():
                columns[f"{dim_name}_ID"] = "Integer"  # Foreign keys from dimension tables
            num_columns = st.number_input(f"Additional columns in {table_name}", min_value=1, max_value=10, value=3)
            for j in range(num_columns):
                col_name = st.text_input(f"Column {j+1} Name ({table_name})", value=f"Column_{j+1}")
                col_type = st.selectbox(f"Column {j+1} Type ({table_name})", list(data_types.keys()))
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
