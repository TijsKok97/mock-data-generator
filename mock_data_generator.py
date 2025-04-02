import streamlit as st
import openai
from faker import Faker

# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI API key

# Initialize Faker for data generation
language = st.selectbox("Choose language for data generation.", ["English", "Dutch"])

if language == "Dutch":
    fake = Faker("nl_NL")
else:
    fake = Faker("en_US")

# Store user input for schema and mock data generation
if 'schema' not in st.session_state:
    st.session_state.schema = {'dimensions': [], 'facts': []}
    st.session_state.schema_updated = False

# Mode selection
mode = st.radio("Select Mode", ["AI Chatbot Mode", "Manual Mode"])

# Function to generate schema using OpenAI GPT
def generate_ai_schema():
    prompt = """
    Generate a database schema with the following details:
    - Create two dimension tables: Product and Category.
    - Create one fact table: Sales.
    - Product table should have columns: Product_ID, Product_Name, Category_ID.
    - Category table should have columns: Category_ID, Category_Name.
    - Sales table should have columns: Sale_ID, Product_ID, Quantity, Total_Price.
    - Provide data types: Integer, String, Float for appropriate columns.
    """

    # Request to OpenAI's GPT-3 for schema generation
    response = openai.Completion.create(
        model="text-davinci-003",  # You can choose a different model as needed
        prompt=prompt,
        max_tokens=500
    )

    # Extracting relevant schema data from GPT response (simplified)
    generated_schema = {
        'dimensions': [
            {"table_name": "Product", "columns": ["Product_ID", "Product_Name", "Category_ID"], "data_types": ["Integer", "String", "Integer"]},
            {"table_name": "Category", "columns": ["Category_ID", "Category_Name"], "data_types": ["Integer", "String"]}
        ],
        'facts': [
            {"table_name": "Sales", "columns": ["Sale_ID", "Product_ID", "Quantity", "Total_Price"], "data_types": ["Integer", "Integer", "Integer", "Float"]}
        ]
    }

    return generated_schema

# AI Mode: Generate schema based on simulated AI response
if mode == "AI Chatbot Mode":
    st.title("AI Chatbot Mode - Schema Generation")

    # Generate schema using GPT
    ai_schema = generate_ai_schema()

    # Pre-fill the schema in session state
    st.session_state.schema = ai_schema
    st.session_state.schema_updated = True

elif mode == "Manual Mode":
    st.title("Manual Mode - Define Schema")
    st.session_state.schema_updated = False

# Manual input: Define dimensions and facts manually
if st.session_state.schema_updated or mode == "Manual Mode":
    # Input for Dimensions
    st.subheader("Define Dimensions (Tables)")
    num_dimensions = st.number_input("How many dimensions?", min_value=1, max_value=10, value=2)
    for i in range(num_dimensions):
        with st.expander(f"Dimension {i+1}"):
            table_name = st.text_input(f"Table name for Dimension {i+1}", key=f"dim_{i}_table_name", value=st.session_state.schema['dimensions'][i]['table_name'] if i < len(st.session_state.schema['dimensions']) else "")
            columns = st.text_area(f"Columns for Dimension {i+1} (comma separated)", key=f"dim_{i}_columns", value=", ".join(st.session_state.schema['dimensions'][i]['columns']) if i < len(st.session_state.schema['dimensions']) else "")
            data_types = st.text_area(f"Data Types for Dimension {i+1} (comma separated)", key=f"dim_{i}_data_types", value=", ".join(st.session_state.schema['dimensions'][i]['data_types']) if i < len(st.session_state.schema['dimensions']) else "")

            # Save input to session state
            st.session_state.schema['dimensions'][i] = {
                'table_name': table_name,
                'columns': columns.split(','),
                'data_types': data_types.split(',')
            }

    # Input for Facts
    st.subheader("Define Facts (Tables)")
    num_facts = st.number_input("How many facts?", min_value=1, max_value=10, value=1)
    for i in range(num_facts):
        with st.expander(f"Fact {i+1}"):
            table_name = st.text_input(f"Table name for Fact {i+1}", key=f"fact_{i}_table_name", value=st.session_state.schema['facts'][i]['table_name'] if i < len(st.session_state.schema['facts']) else "")
            columns = st.text_area(f"Columns for Fact {i+1} (comma separated)", key=f"fact_{i}_columns", value=", ".join(st.session_state.schema['facts'][i]['columns']) if i < len(st.session_state.schema['facts']) else "")
            data_types = st.text_area(f"Data Types for Fact {i+1} (comma separated)", key=f"fact_{i}_data_types", value=", ".join(st.session_state.schema['facts'][i]['data_types']) if i < len(st.session_state.schema['facts']) else "")

            # Save input to session state
            st.session_state.schema['facts'][i] = {
                'table_name': table_name,
                'columns': columns.split(','),
                'data_types': data_types.split(',')
            }

    # Button to show the generated schema (for validation)
    if st.button("Show Generated Schema"):
        st.write(st.session_state.schema)
