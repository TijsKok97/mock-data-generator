import streamlit as st
import pandas as pd
from faker import Faker
import random
import io

# Welcome message
st.markdown("### 📊 Welcome to MockedUp 🚀")
st.write("Define your dataset structure either manually or through AI-powered suggestions!")

# Define the data types available from Faker
data_types = {
    "String": "String",
    "Integer": "Integer",
    "Boolean": "Boolean",
    "City": "City",
    "Name": "Name",
    "Date": "Date",
    "Email": "Email",
    "Street Address": "Street Address",
    "Country": "Country",
    "Postal Code": "Postal Code",
    "Phone Number": "Phone Number",
    "Company": "Company",
    "Currency Amount": "Currency Amount",
    "Custom": "Custom"
}

# Initialize Faker for data generation
fake = Faker("en_US")  # Default to English for simplicity

# Function to get the corresponding Faker function based on the data type
def get_faker_func(data_type):
    if data_type == "String":
        return fake.word
    elif data_type == "Integer":
        return lambda: fake.random_int(min=1, max=1000)
    elif data_type == "Boolean":
        return lambda: fake.random_element(elements=[True, False])
    elif data_type == "City":
        return fake.city
    elif data_type == "Name":
        return fake.name
    elif data_type == "Date":
        return fake.date_this_decade
    elif data_type == "Email":
        return fake.email
    elif data_type == "Street Address":
        return fake.street_address
    elif data_type == "Country":
        return fake.country
    elif data_type == "Postal Code":
        return fake.postcode
    elif data_type == "Phone Number":
        return fake.phone_number
    elif data_type == "Company":
        return fake.company
    elif data_type == "Currency Amount":
        return lambda: fake.pydecimal(left_digits=5, right_digits=2, positive=True)
    else:
        return lambda: "Custom Data"  # Default case for custom data type

# Manual configuration inputs
st.subheader("🛠️ Manual Configuration")
language = st.selectbox("Choose language for data generation:", ["English", "Dutch"], key="manual_language")
num_dims = st.number_input("🟦 Number of Dimension Tables:", min_value=1, max_value=10, value=3, key="manual_num_dims")
num_facts = st.number_input("🟥 Number of Fact Tables:", min_value=1, max_value=5, value=1, key="manual_num_facts")

# Dictionary to store table configurations
dim_tables = {}
fact_tables = {}

# Define the layout for left (input fields) and right (AI Chatbot) sections
col1, col2 = st.columns([3, 1])  # Left column will be larger, right column smaller for chatbot

with col1:
    # Dimension and Fact Table Configuration
    st.markdown("### Configure Your Tables")
    dimension_table_configs = []
    fact_table_configs = []

    # Dimension table configuration
    for i in range(num_dims):
        st.subheader(f"Dimension Table {i+1}")
        dim_name = st.text_input(f"Dimension Table {i+1} Name", key=f"dim_name_{i}")
        num_columns = st.number_input(f"Number of Columns for Dimension Table {i+1}", min_value=1, max_value=10, value=3, key=f"dim_num_columns_{i}")
        
        column_names = []
        column_types = []
        
        for j in range(num_columns):
            col_name = st.text_input(f"Column Name {j+1} for {dim_name}", key=f"dim_{i}_col_{j}_name")
            col_type = st.selectbox(f"Data Type for Column {j+1}", options=list(data_types.keys()), key=f"dim_{i}_col_{j}_type")
            column_names.append(col_name)
            column_types.append(col_type)

        dimension_table_configs.append({"name": dim_name, "columns": column_names, "types": column_types})

    # Fact table configuration
    for i in range(num_facts):
        st.subheader(f"Fact Table {i+1}")
        fact_name = st.text_input(f"Fact Table {i+1} Name", key=f"fact_name_{i}")
        num_columns = st.number_input(f"Number of Columns for Fact Table {i+1}", min_value=1, max_value=10, value=3, key=f"fact_num_columns_{i}")
        
        column_names = []
        column_types = []
        
        for j in range(num_columns):
            col_name = st.text_input(f"Column Name {j+1} for {fact_name}", key=f"fact_{i}_col_{j}_name")
            col_type = st.selectbox(f"Data Type for Column {j+1}", options=list(data_types.keys()), key=f"fact_{i}_col_{j}_type")
            column_names.append(col_name)
            column_types.append(col_type)
        
        # Select related dimension tables for foreign keys
        related_dims = st.multiselect(f"Select related dimension tables for {fact_name}", options=[dim["name"] for dim in dimension_table_configs], key=f"fact_{i}_related_dims")
        
        fact_table_configs.append({"name": fact_name, "columns": column_names, "types": column_types, "related_dims": related_dims})

with col2:
    # AI Chatbot (smaller, serves as a help section)
    st.title("The Mockbot")
    
    # Display previous messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input handling for the chatbot
    if prompt := st.chat_input("How can I help you with your schema?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Use the current context to generate a response
        full_prompt = f"You are working with {num_dims} dimension tables and {num_facts} fact tables. {prompt}"

        with st.chat_message("assistant"):
            # Example response, you can replace with an AI API call
            assistant_reply = f"Here is some help with your star schema: {prompt}"
            st.write(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# Now, generating mock data based on the configured schema
def generate_mock_data():
    if not dimension_table_configs or not fact_table_configs:
        st.error("No tables configured. Please make sure to define your dimension and fact tables.")
        return {}

    excel_data = {}
    
    # Generate dimension tables
    for dim in dimension_table_configs:
        dim_data = {"ID": range(1, 101)}  # Example 100 rows of data
        for i, col_name in enumerate(dim["columns"]):
            dim_data[col_name] = [get_faker_func(dim["types"][i])() for _ in range(100)]
        df = pd.DataFrame(dim_data)
        excel_data[dim["name"]] = df

    # Generate fact tables
    for fact in fact_table_configs:
        fact_data = {"Fact_ID": range(1, 101)}  # Example 100 rows of data
        for i, col_name in enumerate(fact["columns"]):
            fact_data[col_name] = [get_faker_func(fact["types"][i])() for _ in range(100)]
        
        # Handle foreign key relationships
        for dim_name in fact["related_dims"]:
            if dim_name not in excel_data:
                st.error(f"Error: The related dimension table '{dim_name}' is missing data.")
                return {}
            fact_data[f"{dim_name}_ID"] = excel_data[dim_name]["ID"].sample(n=100, replace=True).values
        
        df = pd.DataFrame(fact_data)
        excel_data[fact["name"]] = df

    return excel_data

# Generate the Excel file for download
if st.button("Generate Mock Data"):
    with st.spinner("Generating data..."):
        excel_data = generate_mock_data()

        if excel_data:
            # Create Excel file in memory
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                for table_name, df in excel_data.items():
                    df.to_excel(writer, sheet_name=table_name, index=False)

            st.success("✅ Excel file created successfully!")
            buffer.seek(0)
            st.download_button(
                label="📥 Download Excel File",
                data=buffer,
                file_name="mock_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
