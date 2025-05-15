import os
import pandas as pd
import numpy as np
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from songrecommender.core.config import settings


class SpotifyDataProcessor:
    def __init__(self):
        self.raw_path = Path('data/raw')
        self.processed_path = Path('data/processed')
        self.enriched_path = self.processed_path / 'spotify_enriched.parquet'
        
    def safe_str_access(self, series, default=''):
        """Manejo seguro para operaciones .str"""
        return series.astype(str) if series.dtype != object else series.fillna('').astype(str)
        
    def load_raw_data(self):
        """Carga los datasets con configuraciones específicas y manejo de errores"""
        print("Cargando datasets con configuración específica...")
        try:
            streaming = pd.read_csv(self.raw_path / 'spotify_global_streaming_data.csv',
                                     low_memory=False)
            streaming['data_type'] = 'streaming'
            
            rankings = pd.read_csv(self.raw_path / 'spotify200_daily.csv',
                                   low_memory=False)
            rankings['data_type'] = 'ranking'
            
            features = pd.read_csv(self.raw_path / 'dataset.csv',
                                   low_memory=False)
            features['data_type'] = 'features'
            
            return streaming, rankings, features
            
        except Exception as e:
            print(f"Error cargando archivos: {e}")
            for f in self.raw_path.iterdir():
                print(f"- {f.name}")
            raise
            
    def clean_data(self, df_dict):
        """Limpieza avanzada y normalización de cada dataset"""
        cleaned = {}
        
        # 1) Eliminar columnas índice sobrantes en todos
        for key, df in df_dict.items():
            df = df.drop(columns=[c for c in df.columns if c.startswith('Unnamed')], errors='ignore')
            df_dict[key] = df
        
        # 2) STREAMING
        streaming = df_dict['streaming'].copy()
        streaming = streaming.rename(columns={
            'Artist':'artist_name', 'Album':'album_name', 'Genre':'genre',
            'Release Year':'release_year',
            'Monthly Listeners (Millions)':'monthly_listeners',
            'Total Streams (Millions)':'total_streams',
            'Total Hours Streamed (Millions)':'total_hours_streamed',
            'Avg Stream Duration (Min)':'avg_duration_min',
            'Streams Last 30 Days (Millions)':'streams_last_30',
            'Skip Rate (%)':'skip_rate',
            'Platform Type':'platform_type'
        })

        # Normalizar texto básico
        for col in ['artist_name', 'album_name']:
            if col in streaming.columns:
                streaming[col] = self.safe_str_access(streaming[col]).str.strip()
        # Normalizar género a minúsculas y sin espacios extra
        if 'genre' in streaming.columns:
            streaming['genre'] = (self.safe_str_access(streaming['genre'])
                                  .str.lower().str.strip())

        # Conversión numérica
        for col in ['monthly_listeners','total_streams','total_hours_streamed',
                    'avg_duration_min','streams_last_30','skip_rate']:
            if col in streaming:
                streaming[col] = pd.to_numeric(
                    self.safe_str_access(streaming[col]).str.replace(',',''),
                    errors='coerce'
                )
        # Eliminar outliers extremos en total_streams (>99 percentil)
        if 'total_streams' in streaming:
            cutoff = streaming['total_streams'].quantile(0.99)
            streaming = streaming[
                (streaming['total_streams'] > 0) &
                (streaming['total_streams'] <= cutoff)
            ]
        cleaned['streaming'] = streaming

        # 3) RANKINGS
        ranking = df_dict['ranking'].copy()
        ranking = ranking.rename(columns={
            'track_name':'track_name','artist_names':'artist_name',
            'streams':'daily_streams','peak_rank':'peak_rank',
            'weeks_on_chart':'weeks_on_chart'
        })
        # Numéricos y fecha
        numeric_cols = [
            'daily_streams','rank','peak_rank','previous_rank','weeks_on_chart',
            'danceability','energy','loudness','speechiness','acousticness',
            'instrumentalness','liveness','valence','tempo','duration'
        ]
        for col in numeric_cols:
            if col in ranking:
                ranking[col] = pd.to_numeric(self.safe_str_access(ranking[col]),
                                             errors='coerce')
        if 'week' in ranking:
            ranking['week'] = pd.to_datetime(ranking['week'], errors='coerce')
        # Strip en artista
        if 'artist_name' in ranking.columns:
            ranking['artist_name'] = self.safe_str_access(ranking['artist_name']).str.strip()
        cleaned['ranking'] = ranking

        # 4) FEATURES
        features = df_dict['features'].copy()
        features = features.rename(columns={'artists':'artist_name','track_genre':'genre'})
        features = features.dropna(subset=['track_id','track_name','album_name'])
        if 'duration_ms' in features:
            features = features[features['duration_ms'] > 0]
        # Manejo de múltiples artistas
        features['artist_name'] = (
            self.safe_str_access(features['artist_name'])
                .str.split(';').str[0].str.strip()
        )
        # Normalizar texto básico
        for col in ['artist_name', 'album_name']:
            if col in features.columns:
                features[col] = self.safe_str_access(features[col]).str.strip()
        # Normalizar géneros
        features['genre'] = (
            self.safe_str_access(features['genre'])
                .str.lower().str.strip()
        )
        cleaned['features'] = features
        
        return cleaned
        
    
    def merge_datasets(self, cleaned_data):
        """Versión definitiva con todas las correcciones y normalización post-merge"""
        try:
            # 1. Pre-procesamiento de features
            features_clean = (
                cleaned_data['features']
                .sort_values('popularity', ascending=False)
                .drop_duplicates(subset=['artist_name', 'album_name'], keep='first')
                .rename(columns={'genre': 'genre_feat'})
            )
            
            # 2. Pre-procesamiento de streaming
            streaming_clean = cleaned_data['streaming'].copy()
            if 'genre' in streaming_clean.columns:
                streaming_clean = streaming_clean.rename(columns={'genre': 'genre_stream'})
            
            # 3. Validar columnas
            required_columns = {
                'streaming': ['artist_name', 'album_name'],
                'features': ['artist_name', 'album_name']
            }
            for ds, cols in required_columns.items():
                missing = [c for c in cols if c not in cleaned_data[ds].columns]
                if missing:
                    raise ValueError(f"Dataset {ds} falta columnas: {missing}")
            
            # 4. Merge inicial
            merged = pd.merge(
                streaming_clean,
                features_clean,
                on=['artist_name', 'album_name'],
                how='left',
                suffixes=('_stream', '_feat')
            )
            
            # 5. Unificar columna de género
            genre_sources = [c for c in ['genre_feat','genre_stream'] if c in merged.columns]
            if genre_sources:
                merged['genre'] = merged[genre_sources[0]]
                for src in genre_sources[1:]:
                    merged['genre'] = merged['genre'].fillna(merged[src])
            else:
                merged['genre'] = 'unknown'
            
            # 6. Normalizar género post-merge
            merged['genre'] = (
                self.safe_str_access(merged['genre'])
                    .str.lower().str.strip()
            )
            
            # 7. Procesamiento de rankings
            ranking = cleaned_data['ranking'].copy()
            def safe_convert_to_float(series):
                num = pd.to_numeric(series, errors='coerce')
                if num.isna().mean() > 0.5:
                    mask = series.astype(str).str.lower() != series.name.lower()
                    num = pd.to_numeric(series[mask], errors='coerce')
                return num
            
            for col in ['daily_streams','peak_rank','weeks_on_chart',
                        'danceability','energy','valence']:
                if col in ranking.columns:
                    ranking[col] = safe_convert_to_float(ranking[col])
                    na_count = ranking[col].isna().sum()
                    if na_count > 0:
                        print(f"⚠️ Advertencia: {na_count} valores no numéricos en '{col}'")
            
            # 8. Estadísticas por artista
            artist_stats = (
                ranking.groupby('artist_name')
                .agg({
                    'daily_streams':'mean',
                    'peak_rank':'min',
                    'weeks_on_chart':'max',
                    'danceability':'mean',
                    'energy':'mean',
                    'valence':'mean'
                })
                .reset_index()
                .rename(columns={
                    'daily_streams':'avg_daily_streams',
                    'peak_rank':'best_rank',
                    'weeks_on_chart':'max_weeks_on_chart',
                    'danceability':'avg_danceability',
                    'energy':'avg_energy',
                    'valence':'avg_valence'
                })
            )
            
            # 9. Merge final
            final_df = pd.merge(
                merged,
                artist_stats,
                on='artist_name',
                how='left'
            )
            
            # 10. Selección de columnas
            base_columns = [
                'artist_name','album_name','genre','total_streams',
                'avg_duration_min','popularity','avg_danceability',
                'avg_energy','avg_valence','avg_daily_streams',
                'best_rank','max_weeks_on_chart'
            ]
            additional = [c for c in ['Country','Release Year','Platform Type'] if c in final_df]
            final_columns = base_columns + additional
            
            return final_df[final_columns]
            
        except Exception as e:
            print(f"\n❌ Error en merge_datasets: {e}")
            raise
    
    def save_processed_data(self, df):
        """Guarda los datos procesados con validación y normalización final"""
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
        # Reasegurar género en minúsculas
        if 'genre' in df.columns:
            df['genre'] = self.safe_str_access(df['genre']).str.lower().str.strip()
        
        df = df.drop_duplicates(subset=['artist_name','album_name'], keep='first')
        df = df.dropna(subset=['artist_name','album_name'])
        
        # Cast numéricos
        for col in ['total_streams','popularity','avg_danceability',
                    'avg_energy','avg_valence','avg_daily_streams']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        output_path = self.processed_path / 'spotify_processed.parquet'
        df.to_parquet(output_path, index=False)
        
        print(f"\n✅ Datos guardados en {output_path}")
        print(f"🎶 Géneros únicos: {df['genre'].nunique()}")
        print(df['genre'].value_counts().head(10))
        
        return output_path
        
    def process_all(self):
        """Ejecuta todo el pipeline con logging detallado"""
        try:
            print("🔍 Cargando datos crudos...")
            streaming, rankings, features = self.load_raw_data()

            print("Archivos en data/raw:")
            for f in self.raw_path.iterdir():
                print(f"- {f.name} ({f.stat().st_size/1024:.1f} KB)")
            
            print("\n🧹 Limpiando datos...")
            cleaned = self.clean_data({
                'streaming': streaming,
                'ranking': rankings,
                'features': features
            })
            
            print("\n🔗 Combinando datasets...")
            merged = self.merge_datasets(cleaned)
            
            print("\n💾 Guardando datos procesados...")
            self.save_processed_data(merged)

            print("\n🔍 Diagnóstico final:")
            print(f"Total registros combinados: {len(merged)}")
            print(f"Artistas únicos: {merged['artist_name'].nunique()}")
            print(f"Valores faltantes en columnas clave:")
            print(merged.isnull().mean()[merged.isnull().mean() > 0].sort_values(ascending=False))
            
            return merged
            
        except Exception as e:
            print(f"\n❌ Error en el procesamiento: {str(e)}")
            print("\n💡 Posibles soluciones:")
            print("1. Verifica que los archivos están en data/raw/")
            print("2. Revisa los nombres de las columnas en los CSVs")
            print("3. Comprueba que los archivos no están corruptos")
            print("4. Asegúrate de tener las dependencias actualizadas")
            raise

    def enrich_data(self, parquet_path=None):
        """Enriquece el parquet procesado rellenando nulos con Spotipy."""
        # 1) Determinar ruta y cargar parquet base
        path = parquet_path or self.processed_path/'spotify_processed.parquet'
        print("🔍 Cargando parquet para enriquecer:", path)
        df = pd.read_parquet(path)

        # 2) Autenticación Spotipy con tus credenciales (antes de usar `sp`)
        auth = SpotifyClientCredentials(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth)

        # 3) Traer lanzamientos recientes y concatenar
        df_new = self.fetch_new_releases(sp, country="US", limit=50)
        df = pd.concat([df, df_new], ignore_index=True)
        df = df.drop_duplicates(subset=["artist_name","album_name"], keep="first")

        # 4) Rellenar nulos de audio-features y popularidad
        to_fix = df[['avg_danceability','avg_energy','avg_valence']].isna().any(axis=1)
        for idx, row in df[to_fix].iterrows():
            q   = f"track:{row['album_name']} artist:{row['artist_name']}"
            res = sp.search(q=q, type='track', limit=1)['tracks']['items']
            if not res:
                continue
            t   = res[0]
            tid = t['id']
            df.at[idx, 'popularity']     = t.get('popularity')
            af = sp.audio_features([tid])[0] or {}
            for feat in ['danceability','energy','valence']:
                df.at[idx, f'avg_{feat}'] = af.get(feat)

        # 5) Imputar con mediana los pocos NaN restantes
        for col in ['popularity','avg_danceability','avg_energy','avg_valence']:
            if col in df:
                df[col].fillna(df[col].median(), inplace=True)

        # 6) Guardar enriched parquet
        print("💾 Guardando datos enriquecidos en:", self.enriched_path)
        df.to_parquet(self.enriched_path, index=False)
        print("✅ Enriquecimiento completado!")
        return self.enriched_path

    
    def fetch_new_releases(self, sp, country="US", limit=50):
        """Trae los últimos álbumes, extrae audio-features y popularidad."""
        results = sp.new_releases(country=country, limit=limit)
        albums = results["albums"]["items"]
        enriched = []
        for alb in albums:
            album_id   = alb["id"]
            name       = alb["name"]
            artist     = alb["artists"][0]["name"]
            release_dt = alb.get("release_date")
            total_tracks = alb.get("total_tracks")

            # 1) Obtener todas las pistas del álbum
            tracks = sp.album_tracks(album_id)["items"]
            track_ids = [t["id"] for t in tracks]

            if not track_ids:
                continue

            # 2) Audio features en bloque
            feats = sp.audio_features(track_ids)
            df_feats = pd.DataFrame([f for f in feats if f])  # filtra None

            # 3) Popularidad promedio de las pistas como proxy
            popularities = []
            for tid in track_ids:
                try:
                    t = sp.track(tid)
                    popularities.append(t.get("popularity", 0))
                except:
                    pass

            enriched.append({
                "artist_name":       artist,
                "album_name":        name,
                "release_date":      release_dt,
                "total_tracks":      total_tracks,
                "avg_danceability":  df_feats["danceability"].mean(),
                "avg_energy":        df_feats["energy"].mean(),
                "avg_valence":       df_feats["valence"].mean(),
                "avg_tempo":         df_feats["tempo"].mean(),
                "avg_duration_ms":   df_feats["duration_ms"].mean(),
                "avg_popularity":    np.mean(popularities) if popularities else None,
                "genre_spotify":     ", ".join(art["name"] for art in alb["genres"] or []),
            })
        return pd.DataFrame(enriched)


    def enrich_spotify_metadata(self, df: pd.DataFrame, market: str = "US") -> pd.DataFrame:
        """
        Enriquecer el DataFrame con metadatos de Spotify:
         - album_id, album_release_date, album_total_tracks, album_popularity, preview_url
         - artist_id, artist_followers, artist_popularity, artist_genres
        """
        # 1) inicializar cliente Spotify
        auth = SpotifyClientCredentials(
            client_id=settings.SPOTIPY_CLIENT_ID,
            client_secret=settings.SPOTIPY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth)

        df_en = df.copy().reset_index(drop=True)

        # 2) preparar columnas nuevas
        new_cols = [
            "album_id", "album_release_date", "album_total_tracks", "album_popularity", "preview_url",
            "artist_id", "artist_followers", "artist_popularity", "artist_genres"
        ]
        for c in new_cols:
            df_en[c] = None

        album_cache  = {}
        artist_cache = {}

        # 3) iterar filas
        for idx, row in df_en.iterrows():
            artist = row["artist_name"]
            album  = row["album_name"]
            key    = (artist, album)

            # — ALBUM —
            if key not in album_cache:
                q = f"album:{album} artist:{artist}"
                res = sp.search(q=q, type="album", market=market, limit=1)["albums"]["items"]
                if res:
                    alb = res[0]
                    # metadata de álbum
                    meta = {
                        "album_id":            alb["id"],
                        "album_release_date":  alb.get("release_date"),
                        "album_total_tracks":  alb.get("total_tracks"),
                        "album_popularity":    alb.get("popularity")
                    }
                    # preview de la primera pista
                    tracks = sp.album_tracks(alb["id"])["items"]
                    meta["preview_url"] = tracks[0].get("preview_url") if tracks else None
                else:
                    meta = {k: None for k in ["album_id","album_release_date","album_total_tracks","album_popularity","preview_url"]}
                album_cache[key] = meta

            # asignar valores de álbum
            for c in ["album_id","album_release_date","album_total_tracks","album_popularity","preview_url"]:
                df_en.at[idx, c] = album_cache[key][c]

            # — ARTISTA —
            if artist not in artist_cache:
                # intentar reutilizar artist_id del álbum
                art_id = album_cache[key]["album_id"] and alb["artists"][0]["id"] if album_cache[key]["album_id"] else None
                if not art_id:
                    # fallback: buscar artista por nombre
                    res2 = sp.search(q=f"artist:{artist}", type="artist", limit=1)["artists"]["items"]
                    art_id = res2[0]["id"] if res2 else None

                if art_id:
                    art = sp.artist(art_id)
                    artist_cache[artist] = {
                        "artist_id":         art_id,
                        "artist_followers":  art["followers"]["total"],
                        "artist_popularity": art["popularity"],
                        "artist_genres":     ", ".join(art["genres"])
                    }
                else:
                    artist_cache[artist] = {k: None for k in ["artist_id","artist_followers","artist_popularity","artist_genres"]}

            # asignar valores de artista
            for c in ["artist_id","artist_followers","artist_popularity","artist_genres"]:
                df_en.at[idx, c] = artist_cache[artist][c]

        # 4) normalizar texto y tipos
        df_en["artist_genres"] = df_en["artist_genres"].fillna("").str.lower().str.strip()
        df_en["album_release_date"] = pd.to_datetime(df_en["album_release_date"], errors="coerce")
        for num in ["album_total_tracks","album_popularity","artist_followers","artist_popularity"]:
            df_en[num] = pd.to_numeric(df_en[num], errors="coerce")

        return df_en