import streamlit as st
import requests
import os

st.title("Demand Prediction Service")

# URL del backend para Docker 
api_url = os.getenv("API_URL", "http://localhost:8000")

try:
    response = requests.get(f"{api_url}/health")
    if response.status_code == 200:
        st.success(f"Backend Status: {response.json()['status']}")
    else:
        st.error("Backend is down")
except Exception as e:
    st.error(f"Connection error: {e}")