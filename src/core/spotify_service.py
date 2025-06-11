import os
import logging
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, Any, Optional
import pandas as pd
import joblib

# Cargar modelos
rf_model = joblib.load("models/random_forest_popularity.pkl")
scaler = joblib.load("models/zscore_scaler.pkl")

# Cargar variables de entorno
load_dotenv()

# Constantes
client_id = "35d1b955706e49e1840dc314a179780a"
client_secret = "ad3d52b0129443ce98cbfcd294288874"

# Configurar logger
logger = logging.getLogger(__name__)

logger.info("Inicializando autenticación con Spotify...")

if not client_id or not client_secret:
    logger.error("❌ SPOTIFY_CLIENT_ID o SPOTIFY_CLIENT_SECRET no están definidos.")
else:
    logger.debug(f"✅ Client ID: {client_id}")
    logger.debug(f"✅ Client Secret: {'*' * len(client_secret)}")

try:
    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
        cache_handler=spotipy.cache_handler.MemoryCacheHandler())
    token = auth_manager.get_access_token(as_dict=False)
    sp = spotipy.Spotify(auth=token)

    logger.info("✅ Autenticación con Spotify exitosa.")
except Exception as e:
    logger.exception("❌ Error al autenticar con Spotify.")

class SpotifyService:
    """
    Clase para interactuar con la API de Spotify.
    """

    def search_track(self, track_name: str, artist_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca un track en Spotify.

        Args:
            track_name (str): Nombre del track.
            artist_name (str): Nombre del artista.

        Returns:
            Optional[Dict[str, Any]]: Información del track si se encuentra, None en caso contrario.

        Raises:
            Exception: Si ocurre un error durante la búsqueda.
        """
        query = f"{track_name} {artist_name}"
        logger.debug(f"🔎 Buscando track: {query}")
        try:
            results = sp.search(q=query, type='track', limit=1)
            track = results['tracks']['items'][0] if results['tracks']['items'] else None
            if track:
                logger.info(f"✅ Track encontrado: {track['name']} - {track['id']}")
            else:
                logger.warning("⚠️ No se encontró ningún track con esa búsqueda.")
            return track
        except Exception as e:
            logger.exception("❌ Error en búsqueda de track")
            return None

    def get_track_features(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene las características de un track.

        Args:
            track_id (str): ID del track en Spotify.

        Returns:
            Optional[Dict[str, Any]]: Características del track si se encuentran, None en caso contrario.

        Raises:
            Exception: Si ocurre un error al obtener las características.
        """
        logger.debug(f"🎛 Obteniendo features para track_id: {track_id}")
        try:
            features = sp.audio_features([track_id])[0]
            if features:
                logger.info("✅ Features obtenidos correctamente")
            else:
                logger.warning("⚠️ No se encontraron features para este track")
            return features
        except Exception as e:
            logger.exception("❌ Error al obtener audio features")
            return None
        

    def predict_popularity_from_spotify(self, track_name: str, artist_name: str) -> Optional[Dict[str, Any]]:
        """
        Predice la popularidad estimada de una canción a partir de su nombre y artista usando el modelo entrenado.
        """
        track = self.search_track(track_name, artist_name)
        if not track:
            return {"error": "No se encontró el track"}

        features = self.get_track_features(track["id"])
        if not features:
            return {"error": "No se pudieron obtener los features de audio"}

        # Filtrar solo las columnas que el modelo espera
        required_features = ['danceability', 'energy', 'valence', 'tempo',
                             'liveness', 'speechiness', 'acousticness', 'instrumentalness']
        input_data = {k: features[k] for k in required_features}
        df = pd.DataFrame([input_data])
        X_scaled = scaler.transform(df)
        pred = rf_model.predict(X_scaled)[0]

        return {
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "popularidad_predicha": round(pred, 2),
            "features_normalizados": dict(zip(df.columns, X_scaled[0]))
        }
