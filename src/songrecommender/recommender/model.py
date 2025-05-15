import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA

from songrecommender.core.config import settings


class SpotifyRecommender:
    def __init__(
        self,
        data_path: str = None,
        n_neighbors: int = 10,
        use_pca: bool = False,
        pca_n_components: float = 0.9,
        exclude_same_artist: bool = True
    ):
        # Determinar ruta a parquet fully enriched si no se provee
        project_root = Path(__file__).resolve().parents[3]
        default_path = project_root / 'data' / 'processed' / 'spotify_fully_enriched.parquet'
        self.data_path = Path(data_path) if data_path else default_path

        if not self.data_path.exists():
            raise FileNotFoundError(f"No se encontró el parquet en: {self.data_path}")

        # Cargar DataFrame
        self.df = pd.read_parquet(self.data_path)
        self.exclude_same_artist = exclude_same_artist

        # Normalizar nombres y géneros
        self._normalize_column_names()
        self._normalize_genres()

        # Agregar feature de recencia
        self._add_recency_feature()

        # Determinar numeric_features presentes
        candidate_num = [
            'avg_danceability', 'avg_energy', 'avg_valence',
            'acousticness', 'instrumentalness', 'speechiness',
            'loudness', 'tempo', 'duration_ms',
            'avg_daily_streams', 'total_streams',
            'album_total_tracks', 'album_popularity',
            'artist_followers', 'artist_popularity',
            'days_since_release'
        ]
        self.numeric_features = [f for f in candidate_num if f in self.df.columns]
        missing = set(candidate_num) - set(self.numeric_features)
        if missing:
            print(f"⚠️ Ignorando features inexistentes: {missing}")

        # One-hot encode de géneros top
        self._encode_genres(n_top=10)

        # Validar y combinar features
        self._validate_features()
        X = self.df[self.all_features].fillna(0)

        # PCA opcional
        self.use_pca = use_pca
        if self.use_pca:
            self.pca = PCA(n_components=pca_n_components)
            X = self.pca.fit_transform(X)

        # Escalar y entrenar KNN
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        self.model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        self.model.fit(X_scaled)

    def _normalize_column_names(self):
        col_map = {
            'artists': 'artist_name', 'artist': 'artist_name',
            'album': 'album_name', 'title': 'album_name'
        }
        self.df.rename(columns={k: v for k, v in col_map.items() if k in self.df}, inplace=True)

    def _normalize_genres(self):
        self.df['genre'] = (
            self.df.get('genre', pd.Series(dtype=str))
            .fillna('unknown')
            .str.lower()
            .str.replace('-', '', regex=False)
            .str.strip()
        )

    def _add_recency_feature(self):
        self.df['album_release_date'] = pd.to_datetime(
            self.df.get('album_release_date'), errors='coerce'
        )
        today = pd.Timestamp.now()
        self.df['days_since_release'] = (
            today - self.df['album_release_date']
        ).dt.days.fillna(0)

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
        # Combinar numéricas y OHE
        self.all_features = list(self.numeric_features) + self.genre_ohe_cols
        missing = [f for f in self.all_features if f not in self.df.columns]
        if missing:
            raise KeyError(f"Faltan features en DataFrame: {missing}")

    def recommend_songs(self, album_name: str, artist_name: str, n_recommendations: int = 5) -> pd.DataFrame:
        mask = (
            self.df['artist_name'].str.lower() == artist_name.lower().strip()
        ) & (
            self.df['album_name'].str.lower() == album_name.lower().strip()
        )
        if not mask.any():
            raise ValueError(f"No se encontró: {artist_name} - {album_name}")
        idx = self.df[mask].index[0]

        vec = self._prepare_vector(idx)
        dists, inds = self.model.kneighbors(vec, n_neighbors=n_recommendations + 1)
        recs = self.df.iloc[inds[0][1:]].copy()
        if self.exclude_same_artist:
            recs = recs[recs['artist_name'] != artist_name]
        cols = ['artist_name', 'album_name', 'genre'] + self.numeric_features
        return recs[cols]

    def _prepare_vector(self, idx: int):
        row = self.df.loc[idx, self.all_features].fillna(0).values.reshape(1, -1)
        if self.use_pca:
            row = self.pca.transform(row)
        return self.scaler.transform(row)

    def list_genres(self) -> list:
        return sorted(self.df['genre'].unique())

    def recommend_by_genre(self, genre: str, n: int = 10) -> pd.DataFrame:
        g = genre.lower().replace('-', '').strip()
        df_g = self.df[self.df['genre'] == g]
        if df_g.empty:
            raise ValueError(f"Género no encontrado: {genre}")
        return df_g.sort_values('total_streams', ascending=False).head(n)[
            ['artist_name', 'album_name', 'genre', 'total_streams']
        ]
