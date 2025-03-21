import joblib
import xgboost as xgb
import pandas as pd

MODEL_PATH = "models/model.pkl"

def load_model():
    model = joblib.load(MODEL_PATH)
    return model

def get_model_features(model):
    return model.feature_names

def predict_power(model, expected_features, features_df):
    features_df = features_df[expected_features].copy()

    if 'GHI' in features_df.columns:
        mask = features_df['GHI'] == 0
    else:
        mask = pd.Series(False, index=features_df.index)

    dmatrix_input = xgb.DMatrix(features_df, feature_names=expected_features)

    predictions = model.predict(dmatrix_input)
    predictions[mask] = 0.0

    return float(predictions.clip(min=0)[0])
