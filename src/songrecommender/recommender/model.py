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
        logger.info("🟦 Inicializando SongRecommender...")

        project_root = Path(__file__).resolve().parents[3]
        default_path = project_root / 'data' / 'processed' / 'million_song_combined.parquet'
        self.data_path = Path(data_path) if data_path else default_path

        logger.debug(f"📁 Ruta del archivo parquet: {self.data_path}")
        if not self.data_path.exists():
            raise FileNotFoundError(f"❌ No se encontró el parquet en: {self.data_path}")

        logger.info(f"📦 Cargando datos desde: {self.data_path}")
        self.df = pd.read_parquet(self.data_path)

        logger.debug(f"📊 Dataset cargado con {len(self.df)} canciones (antes de eliminar duplicados)")
        self.df = self.df.drop_duplicates(subset=["artist", "name"])
        logger.debug(f"🎯 Dataset limpio con {len(self.df)} canciones únicas")

        self.exclude_same_artist = exclude_same_artist

        self.numeric_features = [
            'duration_ms', 'danceability', 'energy', 'loudness', 'speechiness', 'tempo'
        ]

        missing_cols = [f for f in self.numeric_features if f not in self.df.columns]
        if missing_cols:
            raise KeyError(f"❌ Faltan features en DataFrame: {missing_cols}")
        logger.info("✅ Todas las columnas necesarias están presentes.")

        X = self.df[self.numeric_features].fillna(0)

        self.use_pca = use_pca
        if self.use_pca:
            from sklearn.decomposition import PCA
            logger.info("🧬 Aplicando PCA")
            self.pca = PCA(n_components=pca_n_components)
            X = self.pca.fit_transform(X)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        logger.debug("🔍 Entrenando modelo NearestNeighbors")
        self.model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        self.model.fit(X_scaled)
        logger.info("✅ Modelo KNN entrenado con éxito.")

    def _create_vector_from_features(self, features: dict):
        row = [features.get(f, 0) for f in self.numeric_features]
        logger.debug(f"🎯 Vector numérico de entrada: {row}")

        if self.use_pca:
            full_vector = self.pca.transform([row])
        else:
            full_vector = [row]

        transformed = self.scaler.transform(full_vector)
        logger.debug(f"📏 Vector escalado final: {transformed.tolist()}")
        return transformed

    def recommend_by_features(self, features: dict, n_recommendations: int = 5) -> pd.DataFrame:
        logger.info(f"🔎 Recomendando por features con top-{n_recommendations}")
        input_vec = self._create_vector_from_features(features)

        dists, inds = self.model.kneighbors(input_vec, n_neighbors=n_recommendations)
        logger.debug(f"🔍 Vecinos encontrados (índices): {inds}")
        logger.debug(f"📐 Distancias: {dists}")

        recs = self.df.iloc[inds[0]].copy()
        cols = ['artist', 'name', 'genre'] + self.numeric_features

        if recs.empty:
            logger.warning("⚠️ No se encontraron recomendaciones similares.")
            return pd.DataFrame([{"mensaje": "No se encontraron recomendaciones similares."}])

        return recs[cols]

    def recommend_songs(self, track_name: str, artist_name: str, n_recommendations: int = 5) -> pd.DataFrame:
        logger.info(f"🔎 Buscando canción: '{track_name}' de '{artist_name}'")

        track_name_norm = track_name.lower().strip()
        artist_name_norm = artist_name.lower().strip()
        logger.debug(f"🧪 Normalizados: artista='{artist_name_norm}', canción='{track_name_norm}'")

        mask = (
            self.df['artist'].str.lower().str.strip() == artist_name_norm
        ) & (
            self.df['name'].str.lower().str.strip() == track_name_norm
        )

        matches = self.df[mask]
        logger.debug(f"🔍 Matches encontrados: {len(matches)}")

        if matches.empty:
            logger.error(f"❌ No se encontró en dataset: {artist_name_norm} - {track_name_norm}")
            raise ValueError(f"No se encontró en dataset: {artist_name} - {track_name}")

        idx = matches.index[0]
        logger.info(f"🎯 Índice del track encontrado: {idx}")

        row_features = self.df.loc[idx, self.numeric_features].fillna(0).to_dict()
        logger.debug(f"📋 Features del track seleccionado: {row_features}")

        input_vec = self._create_vector_from_features(row_features)

        dists, inds = self.model.kneighbors(input_vec, n_neighbors=n_recommendations + 1)
        logger.debug(f"🔁 Vecinos calculados (incluye mismo track): {inds[0].tolist()}")

        inds_filtered = [i for i in inds[0] if i != idx][:n_recommendations]
        logger.debug(f"✅ Vecinos filtrados (sin el track mismo): {inds_filtered}")

        recs = self.df.iloc[inds_filtered].copy()
        cols = ['artist', 'name', 'genre'] + self.numeric_features

        logger.info(f"🎵 {len(recs)} recomendaciones generadas.")
        return recs[cols]
