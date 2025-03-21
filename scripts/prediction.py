import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import pytz
import os
import plotly.graph_objects as go
from scripts.model import load_model, get_model_features, predict_power

# Constants
API_KEY = st.secrets["API_KEY"]
BASE_URL = st.secrets["BASE_URL"]
LAT = 46.2382
LON = -63.1311
LOCAL_TZ = pytz.timezone("America/Halifax")

def fetch_weather_forecast():
    now_utc = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    formatted_now = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        'param': ['temperature', 'dewpoint_temperature', 'relative_humidity', 
                  'total_cloud_cover', 'wind_speed', 'wind_direction'],
        'lat': LAT,
        'lon': LON,
        'model': 'HRRR',
        'start': formatted_now,
        'end': (now_utc + timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'freq': 'H',
        'format': 'json'
    }

    response = requests.get(BASE_URL, params=params, headers={'api-key': API_KEY})

    if response.status_code != 200:
        st.error(f"❌ API Request Failed! Status Code: {response.status_code}")
        st.write("🔍 Raw API Response:", response.text)
        return None

    try:
        api_response = response.json()
        weather_data = json.loads(api_response["data"])

        columns = weather_data["columns"]
        timestamps = weather_data["index"]  
        data_values = weather_data["data"]

        local_timestamps = [
            datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)
            for ts in timestamps
        ]

        df = pd.DataFrame(data_values, columns=columns)
        df.insert(0, "Timestamp", local_timestamps)

        return df

    except Exception as e:
        st.error(f"⚠️ JSON Processing Error: {e}")
        st.write("🔍 Raw API Response for Debugging:", response.text)
        return None

def load_ghi_csv():
    csv_path = os.path.join("csv", "solar.csv")
    ghi_df = pd.read_csv(csv_path)

    ghi_df["timestamp"] = pd.to_datetime(ghi_df["timestamp"], format="%Y-%m-%d %H:%M")
    ghi_df["timestamp"] = ghi_df["timestamp"].dt.tz_localize("America/Halifax", ambiguous='NaT', nonexistent='shift_forward')
    ghi_df["Timestamp"] = ghi_df["timestamp"]

    return ghi_df[["Timestamp", "GHI"]]

def show_prediction():
    st.title("🔆 Solar Power Energy Predictions")

    forecast_df = fetch_weather_forecast()
    if forecast_df is None:
        st.error("❌ Weather data could not be retrieved. Please check API response.")
        return

    ghi_df = load_ghi_csv()

    forecast_df["Timestamp"] = pd.to_datetime(forecast_df["Timestamp"], errors='coerce')
    ghi_df["Timestamp"] = pd.to_datetime(ghi_df["Timestamp"], errors='coerce')

    forecast_df = forecast_df.dropna(subset=["Timestamp"])
    ghi_df = ghi_df.dropna(subset=["Timestamp"])

    # Rename API response columns to match model input features
    rename_map = {
        'temperature (degC)': 'temperature_degC',
        'dewpoint_temperature (degC)': 'dewpoint_temperature_degC',
        'relative_humidity (0-1)': 'relative_humidity',
        'wind_speed (m/s)': 'wind_speed_mps',
        'wind_direction (deg)': 'wind_direction_deg',
        'total_cloud_cover (0-1)': 'total_cloud_cover'
    }
    forecast_df = forecast_df.rename(columns=rename_map)

    # Merge with GHI data
    merged_df = pd.merge(forecast_df, ghi_df, on="Timestamp", how="left")

    model = load_model()
    expected_features = get_model_features(model)

    for feature in expected_features:
        merged_df[feature] = pd.to_numeric(merged_df[feature], errors='coerce')
    if "GHI" in merged_df.columns:
        merged_df["GHI"] = pd.to_numeric(merged_df["GHI"], errors='coerce')

    missing = [f for f in expected_features if f not in merged_df.columns]
    if missing:
        st.error(f"Missing features for prediction: {missing}")
        st.write("🔍 Columns in Merged DF:", merged_df.columns.tolist())
        st.stop()

    predictions = []
    for _, row in merged_df.iterrows():
        input_df = pd.DataFrame([row[expected_features].values], columns=expected_features).astype(float)
        prediction = predict_power(model, expected_features, input_df)
        predictions.append(prediction)

    output_df = merged_df.copy()
    output_df["Predicted Power Output (kW)"] = predictions

    final_columns = ["Timestamp", "Predicted Power Output (kW)"] + expected_features
    output_df = output_df[final_columns]

    st.subheader("Predicted Solar Power")
    st.dataframe(output_df.set_index("Timestamp"), use_container_width=True)
    
    # Prepare data
    plot_df = output_df.copy()
    plot_df["Timestamp"] = pd.to_datetime(plot_df["Timestamp"])

    fig = go.Figure()

    # Add predicted power line
    fig.add_trace(go.Scatter(
        x=plot_df["Timestamp"],
        y=plot_df["Predicted Power Output (kW)"],
        mode='lines+markers',
        name="Predicted Power Output (kW)"
    ))
    # Layout config
    fig.update_layout(
        title="Solar Power Trend",
        xaxis_title="Timestamp",
        yaxis_title="Predicted Power Output (kW)",
        legend=dict(x=0, y=1.1, orientation="h"),
        xaxis=dict(
            tickformat="%H:%M",
            dtick=3600000,  # milliseconds = 1 hour
            tickangle=0,
        ),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)