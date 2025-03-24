import streamlit as st
import pandas as pd
import plotly.express as px
import os

def show_about():
    st.title("About CIRRUS")

    st.markdown(
        """
        ## CIRRUS - Cloud-based Intelligent Resource for Renewable Utility and Solar Prediction
        
        **CIRRUS** is a solar energy prediction model that uses real-time METAR and forecased TAF-weather data from Charlotetown Airport
        to estimate the hourly solar power output for Slemon Park, Summerside, PE. It integrates weather station 
        data from Environment Canada and advanced machine learning model to provide 4-Hr solar power prediction.

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
    
    with st.expander("Predictions Page?"):
          st.markdown(
               """
                - **4-Hour Solar Energy Prediction**: This page displays a CSV file containing four hours of solar energy predictions, starting from the time the website is loaded.  
                - **METAR**: The first predicted solar energy value is based on the current METAR input, along with solar parameters such as *Solar Elevation*, *Solar Azimuth*, etc.  
                - **TAF**: The following three rows are predicted using the forecasted TAF and the corresponding solar parameters for each hour.  
                - **Handling Missing Values**: If any information is missing in the TAF, the previous values from METAR are used to fill in the gaps.  
                - **Assumptions**: Since the altimeter is only present in METAR (measured at the current time), it is assumed to remain constant for subsequent hours during the predictions.  
                
               """
          )
    
    with st.expander("METAR Page?"):
         st.markdown(
              '''
                - **What is METAR?**: METAR is a standardized format for reporting weather information. It is primarily used by aircraft pilots and meteorologists, who analyze aggregated METAR data to aid in weather forecasting.  
                - **Validity**: Since a METAR report is based on current weather conditions, it is only valid for one hour.  
                - **Location**: This program uses a *predefined location (Charlottetown, PE)* and retrieves the METAR report from the area's airport.  

              '''
         )
    
    with st.expander("TAF Page?"):
         st.markdown(
              """
              - **What is TAF?**: In meteorology and aviation, a *Terminal Aerodrome Forecast (TAF)* is a format used for reporting weather forecast information. TAFs complement and follow a similar encoding structure as *METAR* reports. They are produced by human forecasters stationed on the ground.
              - **Validity**: Since TAFs are weather forecasts, they remain valid for the *six hours* following their issuance.
              - **Location**: Similar to METAR, a TAF report is specific to a *predefined location*. In this case, the forecast is retrieved from the *Charlottetown, PE* airport.

              """
         )

    with st.expander ("Cloud Forecast?"):
         st.markdown(
              """
              - **Forecasting Model**: The program utilizes the *HRRR (High-Resolution Rapid Refresh)* model, provided by *NOAA (National Oceanic and Atmospheric Administration)*.
              - **Resolution**: The HRRR model has a *3 km resolution* and provides *18-hour advanced forecasts*.
              - **Location**: Unlike *TAF* and *METAR*, this model’s predefined location is *Slemon Park, Summerside, PE*.
              - **Cloud Coverage**: In addition to regular weather forecasts, the HRRR model offers *detailed cloud coverage information*.
              - **Cloud Coverage Types**: The HRRR model provides **three different cloud coverage levels** at various altitudes:
                  - **Low Cloud Coverage (LCC)**
                  - **Mid Cloud Coverage (MCC)**
                  - **High Cloud Coverage (HCC)**

              """
         )
     
    with st.expander ("Solar Page?"):
         st.markdown(
              """
                - **Solar Elevation**: Sun's height above the horizon. Measured in degrees.
                - **Solar Azimuthd**: Sun's direction along the horizon. Measured in degrees.
                - **Solar Declination**: Sun's angle relative to the Earth's equatorial plane. Measured in degrees.
                - **Hour Angle**: Sun's position relative to solar noon. Measured in degrees.
             
              """
         )

    st.markdown("### Our Predictions So Far:")

    # Load CSV dynamically
    csv_path = os.path.join("csv", "residuals.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

        # Ensure 'Timestamp' remains a column (not an index)
        if {'Timestamp', 'Actual Values', 'Predicted Values', 'Residuals'}.issubset(df.columns):
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])  # Convert Timestamp to datetime format
            df = df[['Timestamp', 'Actual Values', 'Predicted Values', 'Residuals']]  # Explicit column order

            # Sort data based on Timestamp to avoid incorrect order
            df = df.sort_values(by='Timestamp').reset_index(drop=True)

            # Plot Actual vs Predicted using Plotly
            fig1 = px.line(df, x=df.index, y=['Actual Values', 'Predicted Values'], 
                           labels={'index': 'Time Step', 'value': 'Solar Energy Output'},
                           title="Actual vs. Predicted Solar Energy Graph",
                           markers=True)

            fig1.update_layout(
                xaxis_title="Datapoints",
                yaxis_title="Solar Energy Output (kW)",
                legend_title="Legend",
                template="plotly_white"
            )

            st.plotly_chart(fig1, use_container_width=True)

            # Plot Residuals using Plotly
            st.markdown("### Residuals Graph")
            fig2 = px.bar(df, x=df.index, y='Residuals',
                          labels={'index': 'Time Step', 'Residuals': 'Prediction Error'},
                          title="Prediction Error (Residuals)")

            fig2.update_layout(
                xaxis_title="Datapoints",
                yaxis_title="Residuals (Actual - Predicted)",
                template="plotly_white"
            )

            st.plotly_chart(fig2, use_container_width=True)

            # Display Raw CSV in an Expander
            with st.expander("View Raw Data"):
                st.dataframe(df, use_container_width=True)  # Display dataframe with scroll

        else:
            st.warning("CSV file must contain columns: 'Timestamp', 'Actual Values', 'Predicted Values', and 'Residuals'.")
    else:
        st.error("No CSV file found. Please upload or generate a predictions.csv file in the 'csv' folder.")

    st.markdown(
        """
        ---
        *© Developed by PEIEC Design Group for ENGN-3720 2025. All rights reserved.*
        """
    )  
