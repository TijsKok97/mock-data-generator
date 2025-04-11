import streamlit as st
import pandas as pd
from faker import Faker
import google.genai as genai
import random
import io

# ------------------ Welcome Message ------------------ #
st.markdown("### 📊 Welcome to MockedUp 🚀")
st.write("Define your dataset structure either manually or through AI-powered suggestions!")

# ------------------ Language Setup ------------------ #
language = st.selectbox("Choose language for data generation:", ["English", "Dutch"])
fake = Faker("nl_NL") if language == "Dutch" else Faker("en_US")

# ------------------ Table Settings ------------------ #
num_dims = st.number_input("🟦 Number of Dimension Tables:", min_value=1, max_value=10, value=2)
num_facts = st.number_input("🟥 Number of Fact Tables:", min_value=1, max_value=5, value=1)
mode = st.radio("How would you like to define the tables?", ["AI Chatbot Mode", "Manual Builder Mode"])

dim_tables = {}
fact_tables = {}

# ------------------ Data Type Options ------------------ #
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

def get_faker_func(type_str, constant_value=None):
    if constant_value:
        return lambda: constant_value
    return data_types.get(type_str, lambda: "N/A")

# ------------------ Manual Builder Mode ------------------ #
if mode == "Manual Builder Mode":
    st.title("Manual Schema Builder")

    st.subheader("Define Dimension Tables")
    for i in range(num_dims):
        with st.expander(f"🟦 Dimension Table {i+1}"):
            table_name = st.text_input(f"Name for Dimension Table {i+1}", key=f"dim_name_{i}")
            num_rows = st.number_input(f"Number of rows for {table_name or f'Dimension_{i+1}'}", min_value=10, max_value=5000, value=100, key=f"dim_rows_{i}")

            num_cols = st.number_input(f"Number of columns (excluding ID)", min_value=1, max_value=10, value=3, key=f"dim_cols_{i}")
            columns = []

            for j in range(num_cols):
                col_name = st.text_input(f"Column {j+1} name", key=f"dim_colname_{i}_{j}")
                col_type = st.selectbox(f"Column {j+1} type", options=list(data_types.keys()), key=f"dim_coltype_{i}_{j}")
                if col_name:
                    columns.append({"name": col_name, "type": col_type})

            if table_name:
                dim_tables[table_name] = {
                    "columns": columns,
                    "num_rows": num_rows
                }

    st.subheader("Define Fact Tables")
    for i in range(num_facts):
        with st.expander(f"🟥 Fact Table {i+1}"):
            table_name = st.text_input(f"Name for Fact Table {i+1}", key=f"fact_name_{i}")
            num_rows = st.number_input(f"Number of rows for {table_name or f'Fact_{i+1}'}", min_value=10, max_value=5000, value=200, key=f"fact_rows_{i}")

            linked_dims = []
            for dim_name in dim_tables.keys():
                if st.checkbox(f"Link to Dimension: {dim_name}", key=f"link_{i}_{dim_name}"):
                    linked_dims.append(dim_name)

            num_cols = st.number_input(f"Number of additional fact columns (excluding Fact_ID and FKs)", min_value=0, max_value=10, value=2, key=f"fact_cols_{i}")
            columns = []

            for j in range(num_cols):
                col_name = st.text_input(f"Fact Column {j+1} name", key=f"fact_colname_{i}_{j}")
                col_type = st.selectbox(f"Fact Column {j+1} type", options=list(data_types.keys()), key=f"fact_coltype_{i}_{j}")
                if col_name:
                    columns.append({"name": col_name, "type": col_type})

            if table_name:
                fact_tables[table_name] = {
                    "columns": columns,
                    "num_rows": num_rows,
                    "linked_dimensions": linked_dims
                }

    st.session_state.generate_data_button = True

# ------------------ AI Chatbot Mode ------------------ #
context = """
You are an AI assistant specialized in helping users design star schema data models for database architectures. Users will ask for help with creating dimension tables, fact tables, and generating relationships between them. Please guide them in defining table names, choosing column data types, and linking dimension tables to fact tables.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "schema_updated" not in st.session_state:
    st.session_state.schema_updated = False

if mode == "AI Chatbot Mode":
    st.title("The Mockbot")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you with your star schema?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        full_prompt = f"{context}\nYou are working with {num_dims} dimension tables and {num_facts} fact tables.\n" + prompt

        with st.chat_message("assistant"):
            client = genai.Client(api_key=st.secrets["google_api_key"])
            response = client.models.generate_content(model="gemini-2.0-flash", contents=full_prompt)

            assistant_reply = response.text.strip()
            st.write(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

            if "dimension table" in assistant_reply.lower():
                table_name = "Dim_Product"
                columns = ["Product_ID (Integer)", "Product_Name (String)", "Category (String)"]
                dim_tables[table_name] = {
                    "columns": [{"name": col.split(" ")[0], "type": col.split(" ")[1]} for col in columns],
                    "num_rows": 100
                }
                st.session_state.schema_updated = True
                st.session_state.generate_data_button = True

# ------------------ Data Generator ------------------ #
def generate_mock_data():
    excel_data = {}

    for table_name, config in dim_tables.items():
        dim_data = {"ID": range(1, config["num_rows"] + 1)}
        for col in config["columns"]:
            dim_data[col['name']] = [get_faker_func(col['type'])() for _ in range(config["num_rows"])]
        df = pd.DataFrame(dim_data)
        excel_data[table_name] = df

    for table_name, config in fact_tables.items():
        fact_df = pd.DataFrame()
        fact_df["Fact_ID"] = range(1, config["num_rows"] + 1)
        for dim_name in config["linked_dimensions"]:
            dim_id_col = f"{dim_name}_ID"
            fact_df[dim_id_col] = excel_data[dim_name]["ID"].sample(n=config["num_rows"], replace=True).values
        for col in config["columns"]:
            if col["name"] != "Fact_ID" and not col["name"].endswith("_ID"):
                fact_df[col["name"]] = [get_faker_func(col["type"])() for _ in range(config["num_rows"])]
        excel_data[table_name] = fact_df

    return excel_data

# ------------------ Download Button ------------------ #
if "generate_data_button" in st.session_state and st.session_state.generate_data_button:
    if st.button("Generate Mock Data"):
        with st.spinner("Generating data..."):
            excel_data = generate_mock_data()

            if not excel_data:
                st.error("No data was generated. Please make sure to define your tables and columns.")
            else:
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
