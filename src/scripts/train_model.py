# src/scripts/train_model.py

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import os

if os.path.exists("models/random_forest_popularity.pkl"):
    print("✅ Modelos ya existen. Skipping training.")

else:
    source_dataset = pd.read_csv("data/processed/spotify_full_dataset.csv")

    essentia_columns = ['danceability', 'energy', 'valence', 'tempo',
                        'liveness', 'speechiness', 'acousticness', 'instrumentalness']

    df = source_dataset[essentia_columns + ['popularity']].dropna()
    os.makedirs("/data/processed", exist_ok=True)

    X = df[essentia_columns]
    y = df['popularity']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_scaled, y)

    os.makedirs("models", exist_ok=True)
    joblib.dump(rf, "models/random_forest_popularity.pkl")
    joblib.dump(scaler, "models/zscore_scaler.pkl")

    print("Modelo entrenado y guardado correctamente.")