import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class SongRecommender:
    def __init__(
        self,
        data_path: str = None,
        n_neighbors: int = 10,
        use_pca: bool = False,
        pca_n_components: float = 0.9,
        exclude_same_artist: bool = True,
    ):
        logger.info("Inicializando SongRecommender...")

        project_root = Path(__file__).resolve().parents[3]
        default_path = project_root / 'data' / 'processed' / 'million_song_combined.parquet'
        self.data_path = Path(data_path) if data_path else default_path

        if not self.data_path.exists():
            raise FileNotFoundError(f"❌ No se encontró el parquet en: {self.data_path}")

        logger.info(f"📦 Cargando datos desde: {self.data_path}")
        self.df = pd.read_parquet(self.data_path)

        # Eliminar duplicados por artista + nombre de canción
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=["artist", "name"])
        after = len(self.df)
        logger.info(f"🧹 Eliminados {before - after} duplicados. Quedan {after} canciones únicas.")

        self.exclude_same_artist = exclude_same_artist

        # Solo estas 8 columnas numéricas para recomendación
        self.numeric_features = [
            'duration_ms', 'danceability', 'energy', 'loudness',
            'speechiness', 'acousticness', 'instrumentalness', 'liveness'
        ]

        # Validar que existan todas las columnas necesarias
        missing_cols = [f for f in self.numeric_features if f not in self.df.columns]
        if missing_cols:
            raise KeyError(f"❌ Faltan features en DataFrame: {missing_cols}")

        # Dataset para entrenamiento (solo 8 cols, rellena NaN con 0)
        X = self.df[self.numeric_features].fillna(0)

        self.use_pca = use_pca
        if self.use_pca:
            from sklearn.decomposition import PCA
            logger.info("🧬 Aplicando PCA")
            self.pca = PCA(n_components=pca_n_components)
            X = self.pca.fit_transform(X)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        self.model.fit(X_scaled)
        logger.info("✅ Modelo KNN entrenado")

    def _create_vector_from_features(self, features: dict):
        # Crea vector con solo las 8 features numéricas en orden
        row = [features.get(f, 0) for f in self.numeric_features]

        logger.debug(f"🎯 Vector de entrada: {row}")

        if self.use_pca:
            full_vector = self.pca.transform([row])
        else:
            full_vector = [row]

        return self.scaler.transform(full_vector)

    def recommend_by_features(self, features: dict, n_recommendations: int = 5) -> pd.DataFrame:
        # Prepara vector entrada
        input_vec = self._create_vector_from_features(features)

        # Busca vecinos
        dists, inds = self.model.kneighbors(input_vec, n_neighbors=n_recommendations)

        recs = self.df.iloc[inds[0]].copy()

        cols = ['artist', 'name', 'genre'] + self.numeric_features

        if recs.empty:
            logger.warning("⚠️ No se encontraron recomendaciones similares.")
            return pd.DataFrame([{"mensaje": "No se encontraron recomendaciones similares."}])

        return recs[cols]

    def recommend_songs(self, track_name: str, artist_name: str, n_recommendations: int = 5) -> pd.DataFrame:
        # Busca canción en dataset
        mask = (
            self.df['artist'].str.lower() == artist_name.lower().strip()
        ) & (
            self.df['name'].str.lower() == track_name.lower().strip()
        )

        if not mask.any():
            raise ValueError(f"No se encontró en dataset: {artist_name} - {track_name}")

        idx = self.df[mask].index[0]
        # Crea vector desde fila del df
        row_features = self.df.loc[idx, self.numeric_features].fillna(0).to_dict()
        input_vec = self._create_vector_from_features(row_features)

        # Busca vecinos, saltando el mismo track
        dists, inds = self.model.kneighbors(input_vec, n_neighbors=n_recommendations + 1)
        inds_filtered = [i for i in inds[0] if i != idx][:n_recommendations]

        recs = self.df.iloc[inds_filtered].copy()

        cols = ['artist', 'name', 'genre'] + self.numeric_features
        return recs[cols]
