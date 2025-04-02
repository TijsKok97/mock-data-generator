import streamlit as st
import pandas as pd
import io
from faker import Faker
import random

# Initialize Faker for generating mock data
fake = Faker("en_US")  # Using English for example

# Welcome message
st.markdown("### 📊 Welcome to the Retail Star Schema Generator 🚀")
st.write("Let's design your star schema data model for retail shops in the Netherlands!")

# Input: Business area (e.g., retail shops)
business_area = st.text_input("What is the business area? (e.g., Retail Shops)")

# Input: Key metrics to track
metrics = st.text_area("What key metrics do you want to track? (e.g., Sales Amount, Quantity Sold, Profit)")

# Define dimensions and fact tables dynamically based on business area and metrics
dim_tables = {}
fact_tables = {}

# Define the schema structure based on typical retail schema
def generate_schema():
    # Fact table - Sales Performance
    fact_tables['SalesPerformance'] = {
        'columns': [
            {"name": "SalesPerformanceID", "type": "Integer"},
            {"name": "ProductID", "type": "Integer"},
            {"name": "CustomerID", "type": "Integer"},
            {"name": "TimeID", "type": "Integer"},
            {"name": "SalesAmount", "type": "Decimal"},
            {"name": "QuantitySold", "type": "Integer"},
            {"name": "Profit", "type": "Decimal"},
            {"name": "StartupTime", "type": "Decimal"}
        ],
        "num_rows": 100  # Number of rows in the fact table
    }
    
    # Dimension table - Product
    dim_tables['Product'] = {
        'columns': [
            {"name": "ProductID", "type": "Integer"},
            {"name": "ProductName", "type": "String"},
            {"name": "ProductCategory", "type": "String"},
            {"name": "ProductSubcategory", "type": "String"},
            {"name": "ProductPrice", "type": "Decimal"}
        ],
        "num_rows": 10  # Number of rows in the product dimension table
    }

    # Dimension table - Customer
    dim_tables['Customer'] = {
        'columns': [
            {"name": "CustomerID", "type": "Integer"},
            {"name": "CustomerName", "type": "String"},
            {"name": "CustomerSegment", "type": "String"},
            {"name": "CustomerLocation", "type": "String"}
        ],
        "num_rows": 10  # Number of rows in the customer dimension table
    }

    # Dimension table - Time
    dim_tables['Time'] = {
        'columns': [
            {"name": "TimeID", "type": "Integer"},
            {"name": "Date", "type": "Date"},
            {"name": "Year", "type": "Integer"},
            {"name": "Quarter", "type": "String"},
            {"name": "Month", "type": "String"},
            {"name": "DayOfWeek", "type": "String"}
        ],
        "num_rows": 10  # Number of rows in the time dimension table
    }

# Function to generate mock data for each table
def generate_mock_data():
    excel_data = {}  # dictionary to hold DataFrame per table

    # Generate data for dimension tables
    for table_name, config in dim_tables.items():
        dim_data = {"ID": range(1, config["num_rows"] + 1)}  # Add an ID column
        for col in config['columns']:
            dim_data[col['name']] = [get_faker_func(col['type'])() for _ in range(config["num_rows"])]
        df = pd.DataFrame(dim_data)
        excel_data[table_name] = df

    # Generate data for fact table
    fact_data = {"SalesPerformanceID": range(1, fact_tables['SalesPerformance']["num_rows"] + 1)}
    for col in fact_tables['SalesPerformance']['columns']:
        if col["name"] != "SalesPerformanceID":
            fact_data[col["name"]] = [get_faker_func(col['type'])() for _ in range(fact_tables['SalesPerformance']["num_rows"])]
    fact_df = pd.DataFrame(fact_data)
    excel_data['SalesPerformance'] = fact_df

    return excel_data

# Helper function to get Faker function based on column type
def get_faker_func(type_str):
    if type_str == "String":
        return fake.word
    elif type_str == "Integer":
        return lambda: random.randint(1, 100)
    elif type_str == "Decimal":
        return lambda: round(random.uniform(10, 1000), 2)
    elif type_str == "Date":
        return fake.date_this_decade
    return lambda: "N/A"  # Default function if unknown type

# Button for generating mock data
if st.button("Generate Star Schema Data"):
    generate_schema()  # Generate schema based on user input
    with st.spinner("Generating mock data..."):
        # Generate the data based on the schema
        excel_data = generate_mock_data()

        # Save the generated data to an Excel file in memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            for table_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=table_name, index=False)
            writer.save()

        # Prepare the buffer for download
        buffer.seek(0)

        # Provide the download button
        st.download_button(
            label="📥 Download Excel File",
            data=buffer,
            file_name="retail_star_schema_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
