import streamlit as st
import pandas as pd
from faker import Faker
import google.genai as genai  # Import the google-genai library
import random
import io
import plotly.express as px


# Data inladen
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/TijsKok97/mock-data-generator/refs/heads/main/exclusieve_schoenen_verkoop_met_locatie.csv"
    return pd.read_csv(url)

df = load_data()

st.title("🥿 Exclusieve Schoenen Verkoop Dashboard")

# Filters
landen = st.multiselect("Filter op land:", df['land'].unique(), default=df['land'].unique())

filtered_df = df[df['land'].isin(landen)]

# KPI’s
st.metric("Totale omzet", f"€ {filtered_df['totaal_bedrag'].sum():,.2f}")
st.metric("Aantal bestellingen", filtered_df['order_id'].nunique())

# Grafiek: Omzet per merk
fig = px.bar(filtered_df.groupby('merk')['totaal_bedrag'].sum().reset_index(),
             x='merk', y='totaal_bedrag',
             title='Omzet per merk', labels={'totaal_bedrag': 'Totale omzet (€)'})
st.plotly_chart(fig)

# Grafiek: Aantal aankopen per maand
filtered_df['aankoopdatum'] = pd.to_datetime(filtered_df['aankoopdatum'])
monthly_sales = filtered_df.resample('M', on='aankoopdatum')['order_id'].count().reset_index()
fig2 = px.line(monthly_sales, x='aankoopdatum', y='order_id',
               title='Aantal aankopen per maand', markers=True,
               labels={'order_id': 'Aantal bestellingen'})
st.plotly_chart(fig2)

