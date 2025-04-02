import streamlit as st
import pandas as pd
import random
from faker import Faker

# Function to generate a mock schema (simulated AI response)
def generate_mock_schema():
    # Dummy schema generation (using Faker for this simulation)
    schema = {
        "tables": {
            "Product": {
                "columns": ["Product_ID", "Product_Name", "Category"],
                "data_types": ["Integer", "String", "String"]
            },
            "Category": {
                "columns": ["Category_ID", "Category_Name"],
                "data_types": ["Integer", "String"]
            }
        },
        "relationships": {
            "Product": {
                "foreign_key": "Category_ID",
                "references": "Category"
            }
        }
    }
    return schema

# Initialize Faker for data generation
language = st.selectbox("Choose language for data generation.", ["English", "Dutch"])

if language == "Dutch":
    fake = Faker("nl_NL")
else:
    fake = Faker("en_US")

# Store user input for schema and mock data generation
if 'schema' not in st.session_state:
    st.session_state.schema = {}
    st.session_state.schema_updated = False
    st.session_state.generate_data_button = False

# Chatbot handling based on selected mode
mode = st.radio("How would you like to define the tables?", ["AI Chatbot Mode", "Manual Builder Mode"])

if mode == "AI Chatbot Mode":
    st.title("AI Chatbot Mode - Schema Generation")
    prompt = st.text_input("Please define your schema prompt for the AI model:")
    
    if prompt:
        # Mock AI response (using Faker to simulate schema generation)
        schema_info = generate_mock_schema()
        
        # Store the mock schema info
        st.session_state.schema = schema_info
        st.session_state.schema_updated = True

elif mode == "Manual Builder Mode":
    st.title("Manual Builder Mode - Define Schema")
    st.session_state.schema_updated = False
    # Manually define tables, columns, and data types here as the user prefers

# Populate form fields with the mock schema
if st.session_state.schema_updated and 'tables' in st.session_state.schema:
    # Show the tables and columns that were generated by AI (mocked)
    for table_name, table_info in st.session_state.schema['tables'].items():
        st.subheader(f"Table: {table_name}")
        columns = st.text_area(f"Columns for {table_name}", value=", ".join(table_info["columns"]))
        data_types = st.text_area(f"Data Types for {table_name}", value=", ".join(table_info["data_types"]))

        # Populate relationships if any
        relationships = st.text_area(f"Relationships for {table_name}", value="")
        st.session_state.schema['tables'][table_name]["columns"] = columns.split(", ")
        st.session_state.schema['tables'][table_name]["data_types"] = data_types.split(", ")

# Button to generate mock data
if st.session_state.schema_updated:
    if st.button("Generate Mock Data"):
        st.session_state.generate_data_button = True
        # Generate mock data
        excel_data = generate_mock_data(st.session_state.schema)
        # Show download button for the generated Excel file
        st.download_button(
            label="Download Excel File",
            data=excel_data,
            file_name="generated_schema.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Function to generate mock data based on schema
def generate_mock_data(schema):
    fact_df = pd.DataFrame()

    for table_name, table_info in schema["tables"].items():
        columns = table_info["columns"]
        data_types = table_info["data_types"]

        # Create random mock data for each column
        data = {}
        for col, data_type in zip(columns, data_types):
            if data_type == "Integer":
                data[col] = [random.randint(1, 1000) for _ in range(10)]
            elif data_type == "String":
                data[col] = [fake.name() for _ in range(10)]
            elif data_type == "Float":
                data[col] = [round(random.uniform(1.0, 1000.0), 2) for _ in range(10)]
            else:
                data[col] = [fake.word() for _ in range(10)]

        df = pd.DataFrame(data)
        fact_df = pd.concat([fact_df, df], axis=1)

    # Convert to Excel and return as bytes for download
    output = pd.ExcelWriter("/mnt/data/generated_schema.xlsx", engine="xlsxwriter")
    fact_df.to_excel(output, index=False)
    output.save()
    return output.path
