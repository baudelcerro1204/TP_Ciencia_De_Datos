import os
import time
from pathlib import Path

import pandas as pd
import numpy as np
from tqdm import tqdm

class MillionSongDataProcessor:
    def __init__(self):
        self.raw_path = Path('../data/raw')   # carpeta raw con los CSV
        self.processed_path = Path('../data/processed')  # carpeta para parquet procesado
        self.processed_path.mkdir(parents=True, exist_ok=True)

        # Archivos CSV originales
        self.music_info_file = self.raw_path / 'Music Info.csv'
        self.user_listening_file = self.raw_path / 'User Listening History.csv'

        # Archivo parquet combinado resultante
        self.processed_file = self.processed_path / 'million_song_combined.parquet'


    def safe_str_access(self, series, default=''):
        if series.dtype == object:
            return series.fillna(default).astype(str)
        return series.astype(str).fillna(default)

    def load_music_info(self) -> pd.DataFrame:
        print(f"🔍 Cargando Music Info desde {self.music_info_file}")
        df = pd.read_csv(self.music_info_file)
        print(f"   → {len(df)} filas, columnas: {list(df.columns)}")
        return df

    def clean_music_info(self, df: pd.DataFrame) -> pd.DataFrame:
        # Limpieza básica
        df = df.drop_duplicates(subset=['track_id'])
        # Normalizar texto a lowercase para algunas columnas
        for col in ['artist', 'genre', 'name']:
            if col in df.columns:
                df[col] = self.safe_str_access(df[col]).str.lower().str.strip()
        print(f"🧹 Music Info limpio: {len(df)} filas")
        return df

    def load_user_history(self) -> pd.DataFrame:
        print(f"🔍 Cargando User Listening History desde {self.user_listening_file}")
        df = pd.read_csv(self.user_listening_file)
        print(f"   → {len(df)} filas, columnas: {list(df.columns)}")
        return df

    def combine_data(self, music_info: pd.DataFrame, user_hist: pd.DataFrame) -> pd.DataFrame:
        print("🔄 Combinando datasets por track_id")
        combined = user_hist.merge(music_info, left_on='track_id', right_on='track_id', how='left')
        print(f"   → Data combinada tiene {len(combined)} filas y columnas {list(combined.columns)}")
        return combined

    def clean_unused_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # Features que vas a conservar
        features_to_keep = [
            'track_id', 'name', 'artist', 'genre',
            'duration_ms', 'danceability', 'energy',
            'loudness', 'speechiness', 'valence', 'tempo'
        ]
        df = df[[col for col in df.columns if col in features_to_keep]]
        print(f"🧹 Dataset reducido a features relevantes: {df.columns.tolist()}")
        return df


    def save_processed_data(self, df: pd.DataFrame) -> Path:
        df.to_parquet(self.processed_file, index=False)
        print(f"💾 Dataset combinado guardado en: {self.processed_file}")
        return self.processed_file

    def process_all(self) -> pd.DataFrame:
        music_info = self.load_music_info()
        music_info_clean = self.clean_music_info(music_info)

        user_hist = self.load_user_history()

        combined = self.combine_data(music_info_clean, user_hist)

        # Aquí limpiamos las columnas que no usaremos para la comparación
        combined_clean = self.clean_unused_features(combined)

        self.save_processed_data(combined_clean)

        return combined_clean


if __name__ == '__main__':
    processor = MillionSongDataProcessor()
    df_final = processor.process_all()
    print("\n🔎 Vista previa del dataset combinado (limpio):")
    print(df_final.head(10))
