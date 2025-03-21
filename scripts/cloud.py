import streamlit as st
import pandas as pd
import requests
import io
import plotly.graph_objects as go

# Variable to label map
VARIABLE_LABELS = {
    "TMP": "Temperature (°C)",
    "DP": "Dew Point (°C)",
    "RH": "Relative Humidity (%)",
    "WSPD": "Wind Speed (km/h)",
    "GUST": "Wind Gust (km/h)",
    "WDIR": "Wind Direction (°)",
    "PRECIP_ttl": "Precipitation Total (mm)",
    "PRECIP_int": "Precipitation Intensity (mm/hr)",
    "CLOUD": "Total Cloud Cover (%)",
    "LCDC": "Low Cloud Cover (%)",
    "MCDC": "Mid Cloud Cover (%)",
    "HCDC": "High Cloud Cover (%)",
    "SLP": "Sea Level Pressure (hPa)",
    "DSWRF": "Downward Shortwave Radiation (W/m²)",
    "CAPE": "CAPE (J/kg)",
    "CIN": "CIN (J/kg)",
    "PWAT": "Precipitable Water (mm)"
}

# Variables grouped by shared unit
UNIT_GROUPS = {
    "Cloud Cover (%)": ["CLOUD", "LCDC", "MCDC", "HCDC"],
    "Temperature (°C)": ["TMP", "DP"],
    "Relative Humidity (%)": ["RH"],
    "Wind Speed (km/h)": ["WSPD", "GUST"],
    "Wind Direction (°)": ["WDIR"],
    "Pressure (hPa)": ["SLP"]
}

def fetch_cloud_data():
    api_key = st.secrets["SpotWX"]
    url = f"https://spotwx.io/api.php?key={api_key}&lat=46.4392&lon=-63.8413&model=hrrr"

    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to fetch SpotWX cloud data.")
        return None

    try:
        df = pd.read_csv(io.StringIO(response.text))
        df["DATETIME"] = pd.to_datetime(df["DATETIME"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Failed to parse CSV: {e}")
        return None

def show_cloud():
    st.title("☁️ Cloud & Atmospheric Forecasts")
    df = fetch_cloud_data()
    if df is None:
        return

    #st.markdown("Below are grouped forecasts by measurement unit. Each chart combines variables with the same unit for easier comparison.")

    for unit_label, variables in UNIT_GROUPS.items():
        plot_vars = [v for v in variables if v in df.columns]

        if not plot_vars:
            continue

        fig = go.Figure()
        for var in plot_vars:
            label = VARIABLE_LABELS.get(var, var)
            fig.add_trace(go.Scatter(
                x=df["DATETIME"],
                y=df[var],
                mode="lines+markers",
                name=label
            ))

        fig.update_layout(
            title=f"{unit_label} Forecast",
            xaxis_title="Datetime",
            yaxis_title=unit_label,
            legend=dict(x=0, y=1.1, orientation="h"),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
