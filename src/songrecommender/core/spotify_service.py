import os
import logging
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Cargar variables de entorno
load_dotenv()

client_id = "35d1b955706e49e1840dc314a179780a"
client_secret = "ad3d52b0129443ce98cbfcd294288874"

# Configurar logger
logging.basicConfig(level=logging.DEBUG)
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
    def search_track(self, track_name: str, artist_name: str):
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

    def get_track_features(self, track_id: str):
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
