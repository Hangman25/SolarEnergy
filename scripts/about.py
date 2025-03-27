import streamlit as st
import pandas as pd
import plotly.express as px

def show_about():
    st.title("About CIRRUS")

    st.markdown(
        """
        ## CIRRUS - Cloud-based Intelligent Resource for Renewable Utility and Solar Prediction
        
        **CIRRUS** is a solar energy prediction model that uses real-time METAR and forecasted TAF-weather data from Charlottetown Airport
        to estimate the hourly solar power output for Slemon Park, Summerside, PE.

         ### Key Features:
          - **Real-time Weather Data**: Fetches METAR and TAF data to incorporate dynamic environmental conditions.
          - **Machine Learning Predictions**: Uses an optimized XGBoost model for accurate solar power forecasts.
          - **Cloud Coverage Integration**: Accounts for low, mid, and high-level clouds affecting solar radiation.
          - **Solar Position Calculations**: Computes solar elevation and azimuth angles for better prediction accuracy.

        """
    )

    st.markdown(
     """### What is on: """
     )
    with st.expander("Solar Power Prediction?"):
          st.markdown(
               """
                - **4-Hour Solar Energy Prediction**: This page displays a CSV file containing four hours of solar energy predictions, starting from the time the website is loaded.  
                - **Handling Missing Values**: If any information is missing in the input, the previous values are used to fill in the gaps.    
                
               """
          )
    with st.expander ("Weather forecast?"):
         st.markdown(
              """
              - **Forecasting Model**: The program utilizes the *HRRR (High-Resolution Rapid Refresh)* model, provided by *NOAA (National Oceanic and Atmospheric Administration)*.
              - **Resolution**: The HRRR model has a *3 km resolution* and provides *18-hour advanced forecasts*.
              - **Cloud Coverage**: In addition to regular weather forecasts, the HRRR model offers *detailed cloud coverage information*.
              - **Cloud Coverage Types**: The HRRR model provides **three different cloud coverage levels** at various altitudes:
                  - **Low Cloud Coverage (LCC)**
                  - **Mid Cloud Coverage (MCC)**
                  - **High Cloud Coverage (HCC)**
              """
         )
    with st.expander ("Site-Specific Power Prediction?"):
         st.markdown(
              """
                - **xyz**: xyz.
              """
         )

    st.markdown("### Our Predictions So Far:")

    sheet_url = "https://docs.google.com/spreadsheets/d/1cKWiYx03RO6zrKr-x0oCjHWIUrR_8nGGRRx6xv_oULA/export?format=csv&gid=6909974"

    try:
        df = pd.read_csv(sheet_url)

        expected_cols = ['Timestamp', 'Predicted Power Output (kW)']
        if set(expected_cols).issubset(df.columns):
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df = df.sort_values(by='Timestamp').reset_index(drop=True)

            # Plot Power Output
            fig_power = px.line(
                df, x='Timestamp', y='Predicted Power Output (kW)',
                title='Predicted Solar Power Output Over Time',
                labels={'Predicted Power Output (kW)': 'Power (kW)', 'Timestamp': 'Time'},
                markers=True
            )
            fig_power.update_layout(template="plotly_white")

            st.plotly_chart(fig_power, use_container_width=True)

            # Show Raw Data, with Timestamp first and no index
            with st.expander("View Raw Data"):
                 ordered_cols = ['Timestamp'] + [col for col in df.columns if col != 'Timestamp']
                 st.dataframe(
                     df[ordered_cols],
                     use_container_width=True,
                     hide_index=True
                     )

        else:
            st.warning("The Google Sheet must contain 'Timestamp' and 'Predicted Power Output (kW)' columns.")

    except Exception as e:
        st.error(f"Failed to load data from Google Sheets. Error: {e}")

    st.markdown("---\n*© Developed by PEIEC Design Group for Design 2025. All rights reserved.*")
