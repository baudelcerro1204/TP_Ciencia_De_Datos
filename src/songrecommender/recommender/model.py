import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from songrecommender.core.spotify_service import SpotifyService
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
        self.spotify = SpotifyService()

        project_root = Path(__file__).resolve().parents[3]
        default_path = project_root / 'data' / 'processed' / 'million_song_combined.parquet'
        self.data_path = Path(data_path) if data_path else default_path

        if not self.data_path.exists():
            raise FileNotFoundError(f"❌ No se encontró el parquet en: {self.data_path}")

        logger.info(f"📦 Cargando datos desde: {self.data_path}")
        self.df = pd.read_parquet(self.data_path)

        # 🔥 Eliminar duplicados por artista + nombre de canción
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=["artist", "name"])
        after = len(self.df)
        logger.info(f"🧹 Eliminados {before - after} duplicados. Quedan {after} canciones únicas.")

        self.exclude_same_artist = exclude_same_artist

        self._normalize_genres()
        self._add_recency_feature()

        candidate_num = [
            'danceability', 'energy', 'valence',
            'acousticness', 'instrumentalness', 'speechiness',
            'loudness', 'tempo', 'duration_ms',
            'playcount', 'year', 'days_since_release'
        ]
        self.numeric_features = [f for f in candidate_num if f in self.df.columns]
        missing = set(candidate_num) - set(self.numeric_features)
        if missing:
            logger.warning(f"⚠️ Ignorando features inexistentes: {missing}")

        self._encode_genres(n_top=10)
        self._validate_features()

        X = self.df[self.all_features].fillna(0)

        self.use_pca = use_pca
        if self.use_pca:
            logger.info("🧬 Aplicando PCA")
            self.pca = PCA(n_components=pca_n_components)
            X = self.pca.fit_transform(X)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        self.model.fit(X_scaled)
        logger.info("✅ Modelo KNN entrenado")


    def _normalize_genres(self):
        self.df['genre'] = (
            self.df.get('genre', pd.Series(dtype=str))
            .fillna('unknown')
            .str.lower()
            .str.replace('-', '', regex=False)
            .str.strip()
        )

    def _add_recency_feature(self):
        if 'year' in self.df.columns:
            current_year = pd.Timestamp.now().year
            self.df['days_since_release'] = (current_year - self.df['year']) * 365
        else:
            self.df['days_since_release'] = 0
            logger.warning("⚠️ No se encontró columna 'year', usando días desde lanzamiento = 0")

    def _encode_genres(self, n_top: int = 10):
        top = self.df['genre'].value_counts().nlargest(n_top).index
        self.df['genre_enc'] = np.where(self.df['genre'].isin(top), self.df['genre'], 'other')
        ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        mat = ohe.fit_transform(self.df[['genre_enc']])
        cols = [f"genre_{g}" for g in ohe.categories_[0]]
        df_ohe = pd.DataFrame(mat, columns=cols, index=self.df.index)
        self.df = pd.concat([self.df, df_ohe], axis=1)
        self.genre_ohe_cols = cols

    def _validate_features(self):
        self.all_features = list(self.numeric_features) + self.genre_ohe_cols
        missing = [f for f in self.all_features if f not in self.df.columns]
        if missing:
            raise KeyError(f"❌ Faltan features en DataFrame: {missing}")
        
    def recommend_songs(self, track_name: str, artist_name: str, n_recommendations: int = 5) -> pd.DataFrame:
        logger.info(f"🎧 Recomendando similares a: {artist_name} - {track_name}")
        mask = (
            self.df['artist'].str.lower() == artist_name.lower().strip()
        ) & (
            self.df['name'].str.lower() == track_name.lower().strip()
        )

        if not mask.any():
            logger.info("🔍 Canción no encontrada en el dataset. Buscando en Spotify...")
            track = self.spotify.search_track(track_name, artist_name)
            if not track:
                raise ValueError(f"No se encontró en Spotify: {artist_name} - {track_name}")
            
            track_id = track.get("id")
            if not track_id:
                raise ValueError("❌ Track ID no disponible.")

            features = self.spotify.get_track_features(track_id)
            if not features:
                raise ValueError(f"❌ No se pudieron obtener los features para el track ID: {track_id}")

            input_vec = self._create_vector_from_features(features)
            dists, inds = self.model.kneighbors(input_vec, n_neighbors=n_recommendations + 10)
            recs = self.df.iloc[inds[0]].copy()
        else:
            idx = self.df[mask].index[0]
            vec = self._prepare_vector(idx)
            dists, inds = self.model.kneighbors(vec, n_neighbors=n_recommendations + 10)
            recs = self.df.iloc[inds[0][1:]].copy()  # saltamos el propio track

        print(f"🔬 Vector usado para '{track_name}':")
        if 'vec' in locals():
            print(vec)
        else:
            print(input_vec)

        recs = recs.drop_duplicates(subset=["artist", "name"]).head(n_recommendations)

        if recs.empty:
            logger.warning("⚠️ No se encontraron recomendaciones similares.")
            return pd.DataFrame([{"mensaje": "No se encontraron recomendaciones similares."}])

        cols = ['artist', 'name', 'genre', 'playcount'] + [
            f for f in self.numeric_features if f not in ['playcount', 'days_since_release']
        ]
        return recs[cols]



    def _prepare_vector(self, idx: int):
        row = self.df.loc[idx, self.all_features].fillna(0).values.reshape(1, -1)
        if self.use_pca:
            row = self.pca.transform(row)
        return self.scaler.transform(row)

    def _create_vector_from_features(self, features: dict):
        feature_dict = {
            'danceability': features.get('danceability'),
            'energy': features.get('energy'),
            'valence': features.get('valence'),
            'acousticness': features.get('acousticness'),
            'instrumentalness': features.get('instrumentalness'),
            'speechiness': features.get('speechiness'),
            'loudness': features.get('loudness'),
            'tempo': features.get('tempo'),
            'duration_ms': features.get('duration_ms'),
        }
        row = [feature_dict.get(f, 0) for f in self.numeric_features]
        logger.debug(f"🎯 Vector sin PCA: {row}")
        if self.use_pca:
            row = self.pca.transform([row])
            logger.debug(f"🔄 Vector con PCA: {row}")
        return self.scaler.transform([row])

    def recommend_by_genre(self, genre: str, n: int = 10) -> pd.DataFrame:
        g = genre.lower().replace('-', '').strip()
        df_g = self.df[self.df['genre'] == g]
        if df_g.empty:
            raise ValueError(f"Género no encontrado: {genre}")
        return df_g.sort_values('playcount', ascending=False).head(n)[
            ['artist', 'name', 'genre', 'playcount']
        ]

    def list_genres(self) -> list:
        return sorted(self.df['genre'].dropna().unique())
