import streamlit as st
import pandas as pd
from faker import Faker
import openai
import random
import io

# Set your OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]
st.write(st.secrets)
