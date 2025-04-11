import streamlit as st
import pandas as pd
from faker import Faker
import google.genai as genai
import random
import io
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ------------------ Data Types ------------------ #
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

# ------------------ Session State ------------------ #
if "messages" not in st.session_state:
    st.session_state.messages = []
if "schema_updated" not in st.session_state:
    st.session_state.schema_updated = False
if "generate_data_button" not in st.session_state:
    st.session_state.generate_data_button = False

dim_tables = {}
fact_tables = {}

# ------------------ Layout ------------------ #
st.markdown("### 📊 Welcome to MockedUp 🚀")
st.write("Design your star schema with manual input and AI-powered help — side by side!")

left, right = st.columns(2)

# ------------------ LEFT: Manual Mode ------------------ #
with left:
    st.header("🛠️ Manual Builder Mode")

    language = st.selectbox("Choose language for data generation:", ["English", "Dutch"])
    fake = Faker("nl_NL") if language == "Dutch" else Faker("en_US")

    num_dims = st.number_input("🟦 Number of Dimension Tables:", min_value=1, max_value=10, value=2)
    num_facts = st.number_input("🟥 Number of Fact Tables:", min_value=1, max_value=5, value=1)

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
            num_cols = st.number_input(f"Additional fact columns", min_value=0, max_value=10, value=2, key=f"fact_cols_{i}")
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

# ------------------ Data Generator ------------------ #
def generate_mock_data():
    excel_data = {}
    for table_name, config in dim_tables.items():
        dim_data = {"ID": range(1, config["num_rows"] + 1)}
        for col in config["columns"]:
            dim_data[col['name']] = [get_faker_func(col['type'])() for _ in range(config["num_rows"])]
        excel_data[table_name] = pd.DataFrame(dim_data)

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

# ------------------ Download Excel ------------------ #
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

def draw_schema(dim_tables, fact_tables):
    fig = go.Figure()

    node_x = []
    node_y = []
    annotations = []
    lines = []

    spacing_x = 200
    spacing_y = 200
    width = 150
    height = 60

    # Position dimension tables on top row
    for i, (table_name, config) in enumerate(dim_tables.items()):
        x = i * spacing_x
        y = 0
        fig.add_shape(type="rect", x0=x, y0=y, x1=x+width, y1=y+height, line_color="blue", fillcolor="lightblue")
        annotations.append(dict(x=x+width/2, y=y+height/2, text=table_name, showarrow=False, font=dict(size=12)))
        dim_tables[table_name]["pos"] = (x+width/2, y+height)

    # Position fact tables below
    for i, (fact_name, config) in enumerate(fact_tables.items()):
        x = i * spacing_x + 100
        y = spacing_y
        fig.add_shape(type="rect", x0=x, y0=y, x1=x+width, y1=y+height, line_color="red", fillcolor="mistyrose")
        annotations.append(dict(x=x+width/2, y=y+height/2, text=fact_name, showarrow=False, font=dict(size=12)))
        fx, fy = x+width/2, y  # Bottom center of box

        # Draw lines to related dimension tables
        for dim_name in config["linked_dimensions"]:
            dx, dy = dim_tables[dim_name]["pos"]
            fig.add_shape(type="line", x0=fx, y0=fy, x1=dx, y1=dy, line=dict(color="gray", width=2))

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        shapes=fig.layout.shapes + tuple(),
        annotations=annotations
    )

    st.subheader("🗺️ Visual Schema Diagram")
    st.plotly_chart(fig, use_container_width=True)
