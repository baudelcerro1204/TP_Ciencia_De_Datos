# src/core/prediction_service.py

import joblib
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../../models/random_forest_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ No se encontró el modelo en '{MODEL_PATH}'")

rf_model = joblib.load(MODEL_PATH)


def predecir_popularidad(features: dict):
    """
    Recibe un diccionario con los 4 features, y predice la clase de popularidad.
    Retorna predicción y probabilidades por clase.
    """
    # Crear DataFrame con una sola fila
    df = pd.DataFrame([features])

    # Verificamos que estén las columnas correctas
    expected_cols = ['danceability', 'energy', 'valence', 'tempo']
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Falta el feature esperado: {col}")

    # Predicción de clase y probabilidades
    pred = rf_model.predict(df)[0]
    probas = rf_model.predict_proba(df)[0]
    class_labels = rf_model.classes_

    # Combinar etiquetas y probabilidades
    prob_dict = dict(zip(class_labels, probas))

    return {
        "prediccion": pred,
        "probabilidades": prob_dict
    }
