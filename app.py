import streamlit as st
from scripts.about import show_about
from scripts.prediction import show_prediction
from scripts.cloud import show_cloud
from scripts.location import show_location_predictions   

st.set_page_config(layout="wide", page_title="🌤️ Energy Prediction Dashboard")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["About", "Solar Power Prediction", "Weather Forecast","Site-Specific Power Prediction"])  

if page == "About":
    show_about()
elif page == "Solar Power Prediction":
    show_prediction()
elif page == "Weather Forecast":
    show_cloud()  
elif page == "Site-Specific Power Prediction":
    show_location_predictions()
