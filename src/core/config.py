import os
from dotenv import load_dotenv
import tekore as tk
import logging
from typing import Optional

# Configuración de logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Constantes
client_id = "35d1b955706e49e1840dc314a179780a"
client_secret = "ad3d52b0129443ce98cbfcd294288874"

logger.info("✅ client_id: %s", client_id)
logger.info("✅ client_secret: %s", "OK" if client_secret else "❌ NO SETEADO")

try:
    cred = tk.Credentials(client_id, client_secret)
    token = cred.request_client_token()
    spotify = tk.Spotify(token)
    logger.info("✅ Autenticación con Spotify exitosa.")
except Exception as e:
    logger.error("❌ Error al autenticar con Spotify: %s", e)
    raise