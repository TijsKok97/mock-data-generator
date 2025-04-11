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

    # Allow generating data
    st.session_state.generate_data_button = True
