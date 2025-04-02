import streamlit as st
import pandas as pd
import io
import zipfile
import os
import google.genai as genai  # Assuming access to Google's Gemini API

# Initialize Faker for generating mock data
fake = Faker("en_US")

# Streamlit chatbot initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to generate sample data for each table
def generate_sample_data():
    # Define the sample data for each dimension and the fact table
    # Product Dimension
    products_data = {
        'product_id': [1, 2, 3],
        'product_name': ['Laptop', 'Smartphone', 'Tablet'],
        'category': ['Electronics', 'Electronics', 'Electronics'],
        'price': [1000, 500, 300]
    }
    products_df = pd.DataFrame(products_data)

    # Customer Dimension
    customers_data = {
        'customer_id': [1, 2, 3],
        'customer_name': ['Alice', 'Bob', 'Charlie'],
        'city': ['New York', 'Los Angeles', 'Chicago'],
        'state': ['NY', 'CA', 'IL']
    }
    customers_df = pd.DataFrame(customers_data)

    # Date Dimension
    dates_data = {
        'date_id': [1, 2, 3],
        'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'year': [2023, 2023, 2023],
        'month': [1, 1, 1],
        'day': [1, 2, 3]
    }
    dates_df = pd.DataFrame(dates_data)

    # Fact Table - Sales
    sales_data = {
        'sale_id': [1, 2, 3],
        'customer_id': [1, 2, 3],
        'product_id': [1, 2, 3],
        'date_id': [1, 2, 3],
        'quantity': [1, 2, 3],
        'total_sales': [1000, 1000, 900]
    }
    sales_df = pd.DataFrame(sales_data)

    return products_df, customers_df, dates_df, sales_df

# Function to generate a ZIP archive with CSV files
def create_zip(products_df, customers_df, dates_df, sales_df):
    # Create a memory buffer to hold the ZIP file
    buffer = io.BytesIO()

    # Create a ZipFile object
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Write each dataframe as a CSV in the zip file
        with io.StringIO() as products_csv:
            products_df.to_csv(products_csv, index=False)
            zf.writestr('products.csv', products_csv.getvalue())
        
        with io.StringIO() as customers_csv:
            customers_df.to_csv(customers_csv, index=False)
            zf.writestr('customers.csv', customers_csv.getvalue())

        with io.StringIO() as dates_csv:
            dates_df.to_csv(dates_csv, index=False)
            zf.writestr('dates.csv', dates_csv.getvalue())

        with io.StringIO() as sales_csv:
            sales_df.to_csv(sales_csv, index=False)
            zf.writestr('sales.csv', sales_csv.getvalue())

    # Seek to the beginning of the buffer
    buffer.seek(0)

    return buffer

# Chatbot interaction using Gemini API
def chatbot_input():
    st.title("Retail Star Schema Generator")
    
    # Display previous messages in the conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Tell me about your data model:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Use Gemini API to process user input and generate schema (ensure you have the API key)
        client = genai.Client(api_key=st.secrets["google_api_key"])
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )

        assistant_reply = response.text.strip()
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        # Now that we have the schema from the assistant, let's generate the data
        if "customers" in assistant_reply.lower() and "products" in assistant_reply.lower() and "dates" in assistant_reply.lower() and "sales" in assistant_reply.lower():
            st.session_state.messages.append({"role": "assistant", "content": "I have generated the schema and data for your retail model. Click below to download."})

            # Generate sample data
            products_df, customers_df, dates_df, sales_df = generate_sample_data()

            # Create a ZIP file with the CSVs
            zip_buffer = create_zip(products_df, customers_df, dates_df, sales_df)

            # Provide a download button
            st.download_button(
                label="Download Star Schema Data (ZIP)",
                data=zip_buffer,
                file_name="star_schema_data.zip",
                mime="application/zip"
            )

# Call the chatbot function to initiate the conversation
chatbot_input()
