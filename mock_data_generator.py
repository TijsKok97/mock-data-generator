import streamlit as st
import pandas as pd
import io
from faker import Faker
import plotly.graph_objects as go

# ------------------ Config ------------------ #
st.set_page_config(layout="wide")

if "dim_tables" not in st.session_state:
    st.session_state.dim_tables = {}
if "fact_tables" not in st.session_state:
    st.session_state.fact_tables = {}

fake = Faker()

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
}

def get_faker_func(type_str):
    return data_types.get(type_str, lambda: "N/A")

# ------------------ Layout ------------------ #
st.title("🧱 Star Schema Builder")

left, right = st.columns(2)

# ------------------ Manual Inputs ------------------ #
with left:
    st.header("Manual Builder")

    num_dims = st.number_input("Number of Dimension Tables", 1, 10, 2, key="num_dims")
    num_facts = st.number_input("Number of Fact Tables", 1, 5, 1, key="num_facts")

    # DIMENSIONS
    for i in range(num_dims):
        key = f"dim_{i}"
        with st.expander(f"Dimension Table {i+1}", expanded=True):
            name = st.text_input(f"Name", key=f"{key}_name")
            if name:
                if key not in st.session_state.dim_tables:
                    st.session_state.dim_tables[key] = {}
                st.session_state.dim_tables[key]["name"] = name
                st.session_state.dim_tables[key]["rows"] = st.number_input("Rows", 10, 5000, 100, key=f"{key}_rows")
                cols = st.number_input("Columns", 1, 10, 3, key=f"{key}_cols")
                columns = []
                for j in range(cols):
                    cname = st.text_input(f"Col {j+1} name", key=f"{key}_colname_{j}")
                    ctype = st.selectbox(f"Col {j+1} type", options=list(data_types.keys()), key=f"{key}_coltype_{j}")
                    if cname:
                        columns.append({"name": cname, "type": ctype})
                st.session_state.dim_tables[key]["columns"] = columns

    # FACTS
    for i in range(num_facts):
        key = f"fact_{i}"
        with st.expander(f"Fact Table {i+1}", expanded=True):
            name = st.text_input(f"Name", key=f"{key}_name")
            if name:
                if key not in st.session_state.fact_tables:
                    st.session_state.fact_tables[key] = {}
                st.session_state.fact_tables[key]["name"] = name
                st.session_state.fact_tables[key]["rows"] = st.number_input("Rows", 10, 5000, 200, key=f"{key}_rows")

                valid_dims = {
                    k: v["name"]
                    for k, v in st.session_state.dim_tables.items()
                    if "name" in v and v["name"].strip() != ""
                }

                links = []
                for dkey, dname in valid_dims.items():
                    if st.checkbox(f"Link to {dname}", key=f"{key}_link_{dkey}"):
                        links.append(dname)
                st.session_state.fact_tables[key]["linked"] = links

                cols = st.number_input("Fact Columns", 0, 10, 2, key=f"{key}_cols")
                columns = []
                for j in range(cols):
                    cname = st.text_input(f"Fact Col {j+1} name", key=f"{key}_colname_{j}")
                    ctype = st.selectbox(f"Fact Col {j+1} type", options=list(data_types.keys()), key=f"{key}_coltype_{j}")
                    if cname:
                        columns.append({"name": cname, "type": ctype})
                st.session_state.fact_tables[key]["columns"] = columns

# ------------------ Generate Data ------------------ #
def generate_data():
    data = {}
    # Dimension tables
    for d in st.session_state.dim_tables.values():
        if not d.get("name"):
            continue
        df = pd.DataFrame({"ID": range(1, d["rows"] + 1)})
        for col in d.get("columns", []):
            df[col["name"]] = [get_faker_func(col["type"])() for _ in range(d["rows"])]
        data[d["name"]] = df

    # Fact tables
    for f in st.session_state.fact_tables.values():
        if not f.get("name"):
            continue
        df = pd.DataFrame({"Fact_ID": range(1, f["rows"] + 1)})
        for dim_name in f.get("linked", []):
            if dim_name in data:
                df[f"{dim_name}_ID"] = data[dim_name]["ID"].sample(n=f["rows"], replace=True).values
        for col in f.get("columns", []):
            df[col["name"]] = [get_faker_func(col["type"])() for _ in range(f["rows"])]
        data[f["name"]] = df
    return data

if left.button("Generate Mock Data"):
    excel_data = generate_data()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        for tname, df in excel_data.items():
            df.to_excel(writer, sheet_name=tname, index=False)
    buffer.seek(0)
    st.download_button("📥 Download Excel", data=buffer, file_name="mock_data.xlsx")

# ------------------ Visual Schema ------------------ #
def draw_schema():
    fig = go.Figure()
    dim_pos = {}
    annotations = []

    spacing_x = 250
    spacing_y = 200
    width = 160
    height = 60

    dims = [d for d in st.session_state.dim_tables.values() if d.get("name")]
    facts = [f for f in st.session_state.fact_tables.values() if f.get("name")]

    for i, d in enumerate(dims):
        x = i * spacing_x
        y = 0
        cx = x + width / 2
        cy = y + height / 2
        dim_pos[d["name"]] = (cx, y + height)
        fig.add_shape(type="rect", x0=x, y0=y, x1=x+width, y1=y+height, line_color="blue", fillcolor="lightblue")
        annotations.append(dict(x=cx, y=cy, text=d["name"], showarrow=False))

    for i, f in enumerate(facts):
        x = i * spacing_x + 100
        y = spacing_y
        cx = x + width / 2
        cy = y + height / 2
        fig.add_shape(type="rect", x0=x, y0=y, x1=x+width, y1=y+height, line_color="red", fillcolor="mistyrose")
        annotations.append(dict(x=cx, y=cy, text=f["name"], showarrow=False))

        for dim_name in f.get("linked", []):
            if dim_name in dim_pos:
                dx, dy = dim_pos[dim_name]
                fig.add_annotation(ax=cx, ay=y, x=dx, y=dy,
                                   showarrow=True, arrowhead=3, arrowcolor="gray")

    fig.update_layout(height=400, showlegend=False, annotations=annotations,
                      xaxis=dict(visible=False), yaxis=dict(visible=False),
                      margin=dict(l=10, r=10, t=10, b=10))
    st.subheader("🗺️ Schema Diagram")
    st.plotly_chart(fig, use_container_width=True)

draw_schema()
