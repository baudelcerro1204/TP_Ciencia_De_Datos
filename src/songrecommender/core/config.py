from pydantic_settings import BaseSettings, SettingsConfigDict

# Clase para manejar la configuración de la aplicación
class Settings(BaseSettings):
    SPOTIPY_CLIENT_ID: str  # ID del cliente de Spotify
    SPOTIPY_CLIENT_SECRET: str  # Secreto del cliente de Spotify
    PORT: int = 8000  # Puerto por defecto para la aplicación

    # Configuración del modelo para cargar variables desde un archivo .env
    model_config = SettingsConfigDict(
        env_file=".env",  # Archivo de entorno
        extra="ignore"    # Ignora variables no listadas en el modelo
    )

# Instancia de configuración
settings = Settings()