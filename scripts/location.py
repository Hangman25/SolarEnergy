import streamlit as st
import pandas as pd

def show_location_predictions():
    """Displays location-based power predictions in a Streamlit application."""

    st.title("📍 Location-based Power Prediction")

    # Streamlit UI: File Uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        # Load DataFrame
        df = pd.read_csv(uploaded_file)

        # Drop Irrelevant Columns Efficiently
        columns_to_remove = [
            "temperature_degC", "dewpoint_temperature_degC", "relative_humidity",
            "wind_speed_mps", "wind_direction_deg", "total_cloud_cover",
            "GHI"
        ]
        df.drop(columns=[col for col in columns_to_remove if col in df.columns], inplace=True)

        # Ensure 'Predicted Power (kW)' Column Exists
        if "Predicted Power Output (kW)" not in df.columns:
            st.error("❌ The uploaded CSV does not contain the required 'Predicted Power Output (kW)' column.")
        else:
            # Convert Predicted Power to List
            preds_list = df["Predicted Power Output (kW)"].tolist()

            # Sidebar User Inputs for Power Calculation
            st.sidebar.header("Settings")

            # Predefined Locations for Dropdown Selection
            location_options = ["Brackly", "Slemon Park", "Rustico", "New Glasgow", "Crapaud"]

            # Dropdown to Select Location
            loc = st.sidebar.selectbox("Select Location", options=location_options, index=0)

            # Numerical Inputs for Capacities
            slemonpark_capacity = st.sidebar.number_input("Slemon Park Capacity (kW)", value=12500)
            brackly_capacity = st.sidebar.number_input(f"{loc} Capacity (kW)", value=1000)

            # Calculate Percentages for Location Power
            percent_slemonpark = [power / slemonpark_capacity for power in preds_list]
            percent_brackly = [power * brackly_capacity for power in percent_slemonpark]

            # Add New Column to DataFrame
            df[f'Predicted Power in {loc} (kW)'] = percent_brackly

            # Display Data
            st.success(f"✅ Data processed successfully for {loc}!")
            st.dataframe(df)

            # Allow Download of Processed Data
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Processed CSV", data=csv, file_name=f"processed_location_data_{loc}.csv", mime="text/csv")
    else:
        st.info("📂 Please upload a CSV file to proceed.")
