# src/scripts/train_model.py — con features ajustadas de Essentia

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import os

# Definir las únicas columnas que realmente podemos extraer con Essentia
essentia_columns = ['danceability', 'energy', 'valence', 'tempo']

# Verificar si el modelo ya está entrenado
if os.path.exists("models/random_forest_popularity.pkl") and os.path.exists("models/zscore_scaler.pkl"):
    print("✅ Modelos ya existen. Skipping training.")
else:
    # Cargar dataset con columnas compatibles
    dataset_path = "data/processed/spotify_full_dataset.csv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"❌ No se encontró el dataset en {dataset_path}")

    source_dataset = pd.read_csv(dataset_path)

    # Filtrar columnas necesarias
    df = source_dataset[essentia_columns + ['popularity']].dropna()

    X = df[essentia_columns]
    y = df['popularity']

    # Escalar los features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Entrenar modelo de regresión
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_scaled, y)

    # Guardar modelos entrenados
    os.makedirs("models", exist_ok=True)
    joblib.dump(rf, "models/random_forest_popularity.pkl")
    joblib.dump(scaler, "models/zscore_scaler.pkl")

    print("✅ Modelo entrenado y guardado correctamente con features ajustados.")
