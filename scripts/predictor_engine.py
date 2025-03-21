import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
import json
import os
from scripts.model import load_model, get_model_features, predict_power

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
        return None

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

def load_ghi_csv():
    csv_path = os.path.join("csv", "solar.csv")
    ghi_df = pd.read_csv(csv_path)
    ghi_df["timestamp"] = pd.to_datetime(ghi_df["timestamp"], format="%Y-%m-%d %H:%M")
    ghi_df["timestamp"] = ghi_df["timestamp"].dt.tz_localize("America/Halifax", ambiguous='NaT', nonexistent='shift_forward')
    ghi_df["Timestamp"] = ghi_df["timestamp"]
    return ghi_df[["Timestamp", "GHI"]]

def get_first_prediction_row():
    forecast_df = fetch_weather_forecast()
    if forecast_df is None:
        return None

    ghi_df = load_ghi_csv()
    forecast_df = forecast_df.rename(columns={
        'temperature (degC)': 'temperature_degC',
        'dewpoint_temperature (degC)': 'dewpoint_temperature_degC',
        'relative_humidity (0-1)': 'relative_humidity',
        'wind_speed (m/s)': 'wind_speed_mps',
        'wind_direction (deg)': 'wind_direction_deg',
        'total_cloud_cover (0-1)': 'total_cloud_cover'
    })

    merged_df = pd.merge(forecast_df, ghi_df, on="Timestamp", how="left")
    model = load_model()
    features = get_model_features(model)

    for f in features:
        merged_df[f] = pd.to_numeric(merged_df[f], errors='coerce')

    predictions = []
    for _, row in merged_df.iterrows():
        input_df = pd.DataFrame([row[features].values], columns=features).astype(float)
        prediction = predict_power(model, features, input_df)
        predictions.append(prediction)

    merged_df["Predicted Power Output (kW)"] = predictions

    output_df = merged_df[["Timestamp", "Predicted Power Output (kW)"] + features]
    return output_df.iloc[0]  # Return first row
