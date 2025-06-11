# src/core/prediction_service.py

import joblib
import pandas as pd
import os

MODEL_PATH = "models/random_forest_popularity.pkl"
SCALER_PATH = "models/zscore_scaler.pkl"

if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
    raise FileNotFoundError("❌ No se encontraron los archivos del modelo o escalador en la carpeta 'models/'")

rf_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

def predecir_popularidad(features: dict):
    """
    Recibe un diccionario de 4 features de Essentia,
    los escala y devuelve una predicción de popularidad (0-100).
    """
    df = pd.DataFrame([features])
    X_scaled = scaler.transform(df)

    pred_popularity = rf_model.predict(X_scaled)[0]
    entrada_escalada = dict(zip(df.columns, X_scaled[0]))

    return {
        "popularidad": round(pred_popularity, 2),
        "features_normalizados": entrada_escalada
    }
