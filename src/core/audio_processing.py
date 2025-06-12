import subprocess
import json
import os
import uuid
from pathlib import Path

TMP_AUDIO_DIR = Path("tmp_audio")
TMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def extract_features_from_file(file_path: str) -> dict:
    """
    Extrae features musicales desde un archivo de audio usando essentia_streaming_extractor_music.
    """
    temp_id = str(uuid.uuid4())[:8]
    output_json = TMP_AUDIO_DIR / f"features_{temp_id}.json"

    subprocess.run([
        "essentia_streaming_extractor_music",
        file_path,
        str(output_json)
    ], check=True)

    with open(output_json, "r") as f:
        data = json.load(f)

    os.remove(output_json)

    loudness = data["lowlevel"]["average_loudness"]
    danceability = data["rhythm"]["danceability"]
    tempo = data["rhythm"]["bpm"]
    valence = data.get("mood_happy", 0) or data.get("mood", {}).get("valence", 0)

    return {
        "danceability": float(danceability),
        "energy": float(loudness),
        "valence": float(valence),
        "tempo": float(tempo)
    }

def extract_features_from_name_and_artist(track_name: str, artist_name: str) -> dict:
    """
    Busca una canción en YouTube por nombre y artista, descarga el .mp3 con yt-dlp,
    extrae sus features y elimina el archivo temporal.
    """
    unique_id = str(uuid.uuid4())[:8]
    base_filename = f"{artist_name} - {track_name}".replace(" ", "_")
    temp_filename = f"{base_filename}_{unique_id}.mp3"
    temp_filepath = TMP_AUDIO_DIR / temp_filename

    query = f"{artist_name} {track_name}"
    print(f"🔎 Buscando en YouTube: {query}")

    try:
        subprocess.run([
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "--output", str(temp_filepath),
            f"ytsearch1:{query}"
        ], check=True)

        print(f"🎧 MP3 descargado en: {temp_filepath}")
        features = extract_features_from_file(str(temp_filepath))

        os.remove(temp_filepath)
        return features

    except subprocess.CalledProcessError as e:
        print(f"❌ Error al descargar o procesar el audio: {e}")
        raise RuntimeError("Falló la descarga o extracción de features.")
    
def normalize_features(raw_features: dict) -> dict:
    """
    Transforma los features extraídos por Essentia al mismo rango
    que usó el dataset original para entrenar el modelo (0–100, etc.).
    """
    return {
        "danceability": int(raw_features["danceability"] * 100),
        "energy": int(min(max(raw_features["energy"] + 60, 0), 100)),  # escala dB (-60 a 0) → (0 a 100)
        "valence": int(raw_features["valence"] * 100),
        "tempo": raw_features["tempo"] / 250  # normalizás a aprox. 0–1 como en el dataset
    }

