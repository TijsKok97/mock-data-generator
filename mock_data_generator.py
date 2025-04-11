import streamlit as st
import pandas as pd
from faker import Faker
import google.genai as genai
import random
import io
import plotly.graph_objects as go
import networkx as nx
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# ------------------ Init Session State ------------------ #
if "messages" not in st.session_state:
    st.session_state.messages = []
if "schema_updated" not in st.session_state:
    st.session_state.schema_updated = False
if "generate_data_button" not in st.session_state:
    st.session_state.generate_data_button = False
if "dim_tables" not in st.session_state:
    st.session_state.dim_tables = {}
if "fact_tables" not in st.session_state:
    st.session_state.fact_tables = {}
if "dim_links" not in st.session_state:
    st.session_state.dim_links = []

# ------------------ App Header ------------------ #
st.markdown("### 📊 Welcome to MockedUp 🚀")
st.write("Design your star schema with manual input and AI-powered help — side by side!")

left, right = st.columns(2)

# ------------------ LEFT: Manual Schema Builder ------------------ #
with left:
    st.header("🛠️ Manual Builder Mode")

    language = st.selectbox("Choose language for data generation:", ["English", "Dutch"])
    fake = Faker("nl_NL") if language == "Dutch" else Faker("en_US")

    data_types = {
        "String": lambda: fake.word(),
        "Integer": lambda: fake.random_int(min=1, max=1000),
        "Boolean": lambda: fake.random_element(elements=[0, 1]),
        "City": lambda: fake.city(),
        "Name": lambda: fake.name(),
        "Date": lambda: fake.date_this_decade(),
        "Email": lambda: fake.email(),
        "Street Address": lambda: fake.street_address(),
        "Country": lambda: fake.country(),
        "Postal Code": lambda: fake.postcode(),
        "Phone Number": lambda: fake.phone_number(),
        "Company": lambda: fake.company(),
        "Currency Amount": lambda: fake.pydecimal(left_digits=5, right_digits=2, positive=True),
        "Custom": lambda value=None: value
    }

    def get_faker_func(type_str, constant_value=None):
        if constant_value:
            return lambda: constant_value
        return data_types.get(type_str, lambda: "N/A")

    num_dims = st.number_input("🟦 Number of Dimension Tables:", min_value=1, max_value=10, value=2)
    num_facts = st.number_input("🟥 Number of Fact Tables:", min_value=1, max_value=5, value=1)

    dim_tables = {}
    fact_tables = {}
    dim_links = []

    st.subheader("Define Dimension Tables")
    for i in range(num_dims):
        with st.expander(f"🟦 Dimension Table {i+1}"):
            table_key = f"dim_{i}"
            table_name = st.text_input(f"Name for Dimension Table {i+1}", key=f"{table_key}_name")
            if not table_name.strip():
                continue

            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=10, max_value=5000, value=100, key=f"{table_key}_rows")
            num_cols = st.number_input(f"Number of columns (excluding ID)", min_value=1, max_value=10, value=3, key=f"{table_key}_cols")

            columns = []
            for j in range(num_cols):
                col_name = st.text_input(f"Column {j+1} name", key=f"{table_key}_colname_{j}")
                col_type = st.selectbox(f"Column {j+1} type", options=list(data_types.keys()), key=f"{table_key}_coltype_{j}")
                if col_name:
                    columns.append({"name": col_name, "type": col_type})

            dim_tables[table_name] = {"columns": columns, "num_rows": num_rows}

            # Add option to link this dimension to others
            st.markdown("🔗 Link to Other Dimensions:")
            for other_table in dim_tables.keys():
                if other_table != table_name:
                    key = f"{table_key}_link_dim_{other_table}"
                    if st.checkbox(f"Link to: {other_table}", key=key):
                        dim_links.append((table_name, other_table))

    st.subheader("Define Fact Tables")
    for i in range(num_facts):
        with st.expander(f"🟥 Fact Table {i+1}"):
            table_key = f"fact_{i}"
            table_name = st.text_input(f"Name for Fact Table {i+1}", key=f"{table_key}_name")
            if not table_name.strip():
                continue

            num_rows = st.number_input(f"Number of rows for {table_name}", min_value=10, max_value=5000, value=200, key=f"{table_key}_rows")

            linked_dims = []
            for dim_name in dim_tables.keys():
                if st.checkbox(f"Link to Dimension: {dim_name}", key=f"{table_key}_link_{dim_name}"):
                    linked_dims.append(dim_name)

            num_cols = st.number_input(f"Additional fact columns", min_value=0, max_value=10, value=2, key=f"{table_key}_cols")
            columns = []
            for j in range(num_cols):
                col_name = st.text_input(f"Fact Column {j+1} name", key=f"{table_key}_colname_{j}")
                col_type = st.selectbox(f"Fact Column {j+1} type", options=list(data_types.keys()), key=f"{table_key}_coltype_{j}")
                if col_name:
                    columns.append({"name": col_name, "type": col_type})

            fact_tables[table_name] = {
                "columns": columns,
                "num_rows": num_rows,
                "linked_dimensions": linked_dims
            }

    st.session_state.dim_tables = dim_tables
    st.session_state.fact_tables = fact_tables
    st.session_state.dim_links = dim_links
    st.session_state.generate_data_button = True

# ------------------ RIGHT: AI Assistant ------------------ #
with right:
    st.header("🤖 AI Chat Assistant")
    context = f"""
    You are an AI assistant specialized in helping users design star schema data models.
    Assist in defining {num_dims} dimension tables and {num_facts} fact tables.
    """

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help with your schema?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            full_prompt = context + "\n" + prompt
            client = genai.Client(api_key=st.secrets["google_api_key"])
            response = client.models.generate_content(model="gemini-2.0-flash", contents=full_prompt)
            assistant_reply = response.text.strip()
            st.markdown(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# ------------------ Generate Mock Data ------------------ #
def generate_mock_data():
    excel_data = {}
    for table_name, config in st.session_state.dim_tables.items():
        dim_data = {"ID": range(1, config["num_rows"] + 1)}
        for col in config["columns"]:
            dim_data[col['name']] = [get_faker_func(col['type'])() for _ in range(config["num_rows"])]
        excel_data[table_name] = pd.DataFrame(dim_data)

    for table_name, config in st.session_state.fact_tables.items():
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

# ------------------ Visual Schema Graph ------------------ #
def draw_schema_graph(dim_tables, fact_tables):
    G = nx.Graph()

    for dim in dim_tables:
        G.add_node(dim, title=f"Dimension: {dim}", color='lightblue')

    for fact, config in fact_tables.items():
        G.add_node(fact, title=f"Fact: {fact}", color='salmon')
        for dim in config.get("linked_dimensions", []):
            if dim in dim_tables:
                G.add_edge(fact, dim, color="gray")

    for src, tgt in st.session_state.get("dim_links", []):
        if src in dim_tables and tgt in dim_tables:
            G.add_edge(src, tgt, color="blue")

    net = Network(height="500px", width="100%", notebook=False, directed=False)
    net.from_nx(G)

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".html") as f:
        net.save_graph(f.name)
        html_file = f.name

    components.html(net.generate_html(), height=550)

# ------------------ Generate + Download ------------------ #
if st.session_state.generate_data_button and st.button("📥 Generate and Download Excel"):
    with st.spinner("Generating mock data..."):
        excel_data = generate_mock_data()
        if not excel_data:
            st.error("No data was generated.")
        else:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                for table_name, df in excel_data.items():
                    df.to_excel(writer, sheet_name=table_name, index=False)
            st.success("✅ Excel file is ready!")
            buffer.seek(0)
            st.download_button(
                label="Download Mock Excel File",
                data=buffer,
                file_name="mock_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ------------------ Render Diagram ------------------ #
if st.session_state.dim_tables or st.session_state.fact_tables:
    st.subheader("🗺️ Visual Schema Diagram")
    draw_schema_graph(st.session_state.dim_tables, st.session_state.fact_tables)
