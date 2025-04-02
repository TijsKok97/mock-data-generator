import streamlit as st
import pandas as pd
from faker import Faker
import google.genai as genai  # Import the google-genai library
import random
import io

# Initialize the Faker library
language = st.selectbox("Choose language for data generation:", ["English", "Dutch"])
if language == "Dutch":
    fake = Faker("nl_NL")  # Initialize Faker for Dutch language
else:
    fake = Faker("en_US")  # Initialize Faker for English language

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

# Store dimension and fact table configurations
dim_tables = {}
fact_tables = {}

# Predefined context for the assistant
context = """
You are an AI assistant specialized in helping users design star schema data models for database architectures. Users will ask for help with creating dimension tables, fact tables, and generating relationships between them. Please guide them in defining table names, choosing column data types, and linking dimension tables to fact tables.
"""

# **Google Gemini Chatbot Mode**
if "messages" not in st.session_state:
    st.session_state.messages = []

if "schema_updated" not in st.session_state:
    st.session_state.schema_updated = False

if mode == "AI Chatbot Mode":
    st.title("The Mockbot")

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input handling
    if prompt := st.chat_input("How can I help you with your star schema?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Include number of dimensions and facts in context
        full_prompt = f"{context}\nYou are working with {num_dims} dimension tables and {num_facts} fact tables.\n" + prompt

        with st.chat_message("assistant"):
            # Using Google's Gemini API with context for specialization
            client = genai.Client(api_key=st.secrets["google_api_key"])
            response = client.models.generate_content(
                model="gemini-2.0-flash", contents=full_prompt
            )

            assistant_reply = response.text.strip()
            st.write(assistant_reply)  # Display the response
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

            # Process feedback into table definitions (example)
            if "dimension table" in assistant_reply.lower():
                table_name = "Dim_Product"  # Example table name from response
                columns = ["Product_ID (Integer)", "Product_Name (String)", "Category (String)"]

                # Store the table definition in dim_tables
                dim_tables[table_name] = {
                    "columns": [{"name": col.split(" ")[0], "type": col.split(" ")[1]} for col in columns],
                    "num_rows": 100  # Default number of rows
                }
                st.session_state.schema_updated = True  # Mark schema as updated

                # Dynamically create a button to generate mock data
                st.session_state.generate_data_button = True  # Flag to show the data generation button

# Function to generate mock data based on schema
def generate_mock_data():
    excel_data = {}  # dict to hold DataFrame per table
    # Generate dimension tables
    for table_name, config in dim_tables.items():
        # Create the dataframe with the ID column as the first column
        dim_data = {"ID": range(1, config["num_rows"] + 1)}  # Add ID column first
        for col in config["columns"]:
            dim_data[col['name']] = [get_faker_func(col['type'])() for _ in range(config["num_rows"])]
        # Ensure ID is always the first column
        df = pd.DataFrame(dim_data)
        excel_data[table_name] = df

    # Generate fact tables (if any)
    for table_name, config in fact_tables.items():
        fact_df = pd.DataFrame()
        fact_df["Fact_ID"] = range(1, config["num_rows"] + 1)  # Unique Fact ID
        # Automatically add foreign key columns for each linked dimension
        for dim_name in config["linked_dimensions"]:
            dim_table = dim_tables[dim_name]
            dim_id_column = f"{dim_name}_ID"
            fact_df[dim_id_column] = excel_data[dim_name]["ID"].sample(n=config["num_rows"], replace=True).values
        for col in config["columns"]:
            if col["name"] != "Fact_ID" and not col["name"].endswith("_ID"):
                fact_df[col["name"]] = [get_faker_func(col["type"])() for _ in range(config["num_rows"])]
        excel_data[table_name] = fact_df

    return excel_data

# Dynamically generate button and download the Excel file when the schema is ready
if "generate_data_button" in st.session_state and st.session_state.generate_data_button:
    if st.button("Generate Mock Data"):
        with st.spinner("Generating data..."):
            excel_data = generate_mock_data()  # Generate the mock data based on the schema

            # Check if excel_data is populated correctly
            if not excel_data:
                st.error("No data was generated. Please make sure to define your tables and columns.")
            else:
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
