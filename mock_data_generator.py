import streamlit as st
import pandas as pd
from faker import Faker
import google.genai as genai  # Import the google-genai library
import random
import io

# Welcome message
st.markdown("### 📊 Welcome to MockedUp 🚀")
st.write("Define your dataset structure either manually or through AI-powered suggestions!")

# Language selection for Faker
language = st.selectbox("Choose language for data generation:", ["English", "Dutch"])

# Initialize Faker based on selected language
if language == "Dutch":
    fake = Faker("nl_NL")  # Initialize Faker for Dutch language
else:
    fake = Faker("en_US")  # Initialize Faker for English language

# User input: Choose number of tables with unique keys
num_dims = st.number_input("🟦 Number of Dimension Tables:", min_value=1, max_value=10, value=3, key="num_dims")
num_facts = st.number_input("🟥 Number of Fact Tables:", min_value=1, max_value=5, value=1, key="num_facts")

# User chooses between AI chatbot or manual configuration
mode = st.radio("How would you like to define the tables?", ["AI Chatbot Mode", "Manual Builder Mode"], key="mode")

# Dictionary to store table configurations
dim_tables = {}
fact_tables = {}

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

# Predefined context for the assistant
context = """
You are an AI assistant specialized in helping users design star schema data models for database architectures. Users will ask for help with creating dimension tables, fact tables, and generating relationships between them. Please guide them in defining table names, choosing column data types, and linking dimension tables to fact tables.
"""

# **Google Gemini Chatbot Mode**
if "messages" not in st.session_state:
    st.session_state.messages = []

if "schema_updated" not in st.session_state:
    st.session_state.schema_updated = False

# Define the layout for left (input fields) and right (AI Chatbot) sections
col1, col2 = st.columns([1, 2])  # Left column will be smaller, right column will be larger

with col1:
    # Input for manual configuration
    st.subheader("🛠️ Manual Configuration")
    num_dims = st.number_input("🟦 Number of Dimension Tables:", min_value=1, max_value=10, value=3, key="manual_num_dims")
    num_facts = st.number_input("🟥 Number of Fact Tables:", min_value=1, max_value=5, value=1, key="manual_num_facts")
    mode = st.radio("How would you like to define the tables?", ["AI Chatbot Mode", "Manual Builder Mode"], key="manual_mode")

with col2:
    # AI Chatbot Display
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

                # Logic to capture and store the table configuration from the assistant's response
                if "dimension table" in assistant_reply.lower():
                    table_name = "Dim_Product"  # Example extraction from the response
                    columns = ["Product_ID (Integer)", "Product_Name (String)", "Category (String)"]

                    dim_tables[table_name] = {
                        "columns": [{"name": col.split(" ")[0], "type": col.split(" ")[1]} for col in columns],
                        "num_rows": 100
                    }
                    st.session_state.schema_updated = True

                    # Dynamically create a button to generate mock data
                    st.session_state.generate_data_button = True

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
