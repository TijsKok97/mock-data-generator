import streamlit as st
import pandas as pd
from faker import Faker
import google.genai as genai  # Import the google-genai library
import random
import io
import plotly.express as px


# STEP 1: Create a class (our object blueprint)
class Smoothie:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def describe(self):
        return f"{self.name} smoothie costs €{self.price:.2f}"

# STEP 2: Let the user choose a smoothie
smoothie_choice = st.selectbox("Choose a smoothie:", ["Strawberry", "Banana", "Mango"])
price_dict = {"Strawberry": 3.50, "Banana": 3.00, "Mango": 4.00}

# STEP 3: Create a Smoothie object
my_smoothie = Smoothie(smoothie_choice, price_dict[smoothie_choice])

# STEP 4: Use a method to show info
st.subheader("Smoothie Info")
st.write(my_smoothie.describe());


