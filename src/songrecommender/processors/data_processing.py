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

    def save_processed_data(self, df: pd.DataFrame) -> Path:
        df.to_parquet(self.processed_file, index=False)
        print(f"💾 Dataset combinado guardado en: {self.processed_file}")
        return self.processed_file

    def process_all(self) -> pd.DataFrame:
        music_info = self.load_music_info()
        music_info_clean = self.clean_music_info(music_info)

        user_hist = self.load_user_history()

        combined = self.combine_data(music_info_clean, user_hist)

        self.save_processed_data(combined)

        return combined


if __name__ == '__main__':
    processor = MillionSongDataProcessor()
    df_final = processor.process_all()
    print("\n🔎 Vista previa del dataset combinado:")
    print(df_final.head(10))

    # def enrich_data(self, df: pd.DataFrame, sleep_sec: float = 0.1) -> pd.DataFrame:
    #     musicbrainz_headers = {
    #         "User-Agent": "MiRecommender/1.0 (tu_email@ejemplo.com)"
    #     }

    #     # Inicializo listas para las variables que extraeremos
    #     danceable_prob = []
    #     genre_electronic_prob = []
    #     mood_happy_prob = []
    #     tonal_prob = []
    #     instrumental_prob = []
    #     rhythm_mfcc_1 = []
    #     rhythm_mfcc_2 = []
    #     length_sec = []
    #     bit_rate = []

    #     for _, row in tqdm(df.iterrows(), total=len(df), desc="🔄 Enriqueciendo AB"):
    #         artist = row['artist_name']
    #         track = row.get('track_name') or row['album_name']

    #         mbid = None
    #         try:
    #             mb_resp = requests.get(
    #                 "https://musicbrainz.org/ws/2/recording",
    #                 headers=musicbrainz_headers,
    #                 params={
    #                     "query": f'recording:"{track}" AND artist:"{artist}"',
    #                     "limit": 1,
    #                     "fmt": "json"
    #                 },
    #                 timeout=5
    #             )
    #             recs = mb_resp.json().get("recordings", [])
    #             if recs:
    #                 mbid = recs[0]["id"]
    #         except Exception as e:
    #             print(f"⚠️ MusicBrainz error: {e}")

    #         if not mbid:
    #             danceable_prob.append(np.nan)
    #             genre_electronic_prob.append(np.nan)
    #             mood_happy_prob.append(np.nan)
    #             tonal_prob.append(np.nan)
    #             instrumental_prob.append(np.nan)
    #             rhythm_mfcc_1.append(np.nan)
    #             rhythm_mfcc_2.append(np.nan)
    #             length_sec.append(np.nan)
    #             bit_rate.append(np.nan)
    #             time.sleep(sleep_sec)
    #             continue

    #         try:
    #             resp = requests.get(f"https://acousticbrainz.org/api/v1/{mbid}/high-level", timeout=5).json()
    #             hl = resp.get('highlevel', {})
    #             danceable_prob.append(hl.get('danceability', {}).get('all', {}).get('danceable', np.nan))
    #             genre_electronic_prob.append(hl.get('genre_electronic', {}).get('all', {}).get('electronic', np.nan))
    #             mood_happy_prob.append(hl.get('mood_happy', {}).get('all', {}).get('happy', np.nan))
    #             tonal_prob.append(hl.get('tonal_atonal', {}).get('all', {}).get('tonal', np.nan))
    #             instrumental_prob.append(hl.get('voice_instrumental', {}).get('all', {}).get('instrumental', np.nan))
    #         except Exception as e:
    #             print(f"⚠️ AcousticBrainz high-level error: {e}")
    #             danceable_prob.append(np.nan)
    #             genre_electronic_prob.append(np.nan)
    #             mood_happy_prob.append(np.nan)
    #             tonal_prob.append(np.nan)
    #             instrumental_prob.append(np.nan)

    #         try:
    #             resp_ll = requests.get(f"https://acousticbrainz.org/api/v1/{mbid}/low-level", timeout=5).json()
    #             ll = resp_ll.get('lowlevel', {})
    #             mfcc = ll.get('rhythm_mfcc', [])
    #             rhythm_mfcc_1.append(mfcc[0] if len(mfcc) > 0 else np.nan)
    #             rhythm_mfcc_2.append(mfcc[1] if len(mfcc) > 1 else np.nan)
    #         except Exception as e:
    #             print(f"⚠️ AcousticBrainz low-level error: {e}")
    #             rhythm_mfcc_1.append(np.nan)
    #             rhythm_mfcc_2.append(np.nan)

    #         try:
    #             metadata = resp.get('metadata', {}).get('audio_properties', {})
    #             length_sec.append(metadata.get('length', np.nan))
    #             bit_rate.append(metadata.get('bit_rate', np.nan))
    #         except Exception as e:
    #             length_sec.append(np.nan)
    #             bit_rate.append(np.nan)

    #         time.sleep(sleep_sec)

    #     df2 = df.copy().reset_index(drop=True)
    #     df2['danceable_prob'] = danceable_prob
    #     df2['genre_electronic_prob'] = genre_electronic_prob
    #     df2['mood_happy_prob'] = mood_happy_prob
    #     df2['tonal_prob'] = tonal_prob
    #     df2['instrumental_prob'] = instrumental_prob
    #     df2['rhythm_mfcc_1'] = rhythm_mfcc_1
    #     df2['rhythm_mfcc_2'] = rhythm_mfcc_2
    #     df2['length_sec'] = length_sec
    #     df2['bit_rate'] = bit_rate

    #     return df2