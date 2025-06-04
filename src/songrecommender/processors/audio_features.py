import os
import json
import pandas as pd
from subprocess import run
import subprocess

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]  # Ajusta si es necesario
input_dir = BASE_DIR / "data" / "raw" / "inputsong"
output_dir = BASE_DIR / "outputs"

os.makedirs(output_dir, exist_ok=True)

rows = []

def extract_features_from_mp3(filepath: str, original_filename: str):
    output_path = filepath + ".json"
    subprocess.run(["essentia_streaming_extractor_music", filepath, output_path], check=True)

    with open(output_path) as f:
        data = json.load(f)

    loudness_raw = data["lowlevel"]["average_loudness"]
    loudness_db = -60 + loudness_raw * 60

    # Nombre y artista desde el archivo
    name = original_filename.replace(".mp3", "").lower()
    artist = "unknown"
    if " - " in name:
        artist, name = name.split(" - ", 1)

    return {
        "track_id": original_filename.replace(".mp3", ""),
        "name": name.strip(),
        "artist": artist.strip(),
        "genre": None,
        "duration_ms": int(data["metadata"]["audio_properties"]["length"] * 1000),
        "danceability": data["rhythm"]["danceability"],
        "energy": loudness_raw,
        "loudness": loudness_db,
        "speechiness": data.get("tonal", {}).get("chords_changes_rate", 0),
        "valence": data.get("mood_happy", 0),
        "tempo": data["rhythm"]["bpm"]
    }


def extract_name_artist(filename: str):
    name = filename.replace(".mp3", "").strip()
    # Ejemplo simple: "Billy Preston - Nothing From Nothing" → ("Billy Preston", "Nothing From Nothing")
    parts = name.split(" - ")
    if len(parts) == 2:
        artist, title = parts
    else:
        artist, title = "unknown", name
    return title.lower(), artist.lower()

for file in os.listdir(input_dir):
    if file.endswith(".mp3"):
        in_path = os.path.join(input_dir, file)
        out_json = os.path.join(output_dir, f"{file}.json")

        print(f"\n🔍 Procesando: {file}")
        run(["essentia_streaming_extractor_music", in_path, out_json])

        with open(out_json, "r") as f:
            data = json.load(f)

        # Conversión de loudness: normalizado [0, 1] → estimado en dB negativos [-60, 0]
        avg_loudness = data["lowlevel"]["average_loudness"]
        loudness_db = -60 + avg_loudness * 60

        name, artist = extract_name_artist(file)

        rows.append({
            "track_id": file.replace(".mp3", ""),
            "name": name,
            "artist": artist,
            "genre": None,
            "duration_ms": int(data["metadata"]["audio_properties"]["length"] * 1000),
            "danceability": data["rhythm"]["danceability"],
            "energy": avg_loudness,
            "loudness": loudness_db,
            "speechiness": data.get("tonal", {}).get("chords_changes_rate", 0),
            "valence": data.get("mood_happy", 0),  # lo vas a usar después
            "tempo": data["rhythm"]["bpm"]
        })

df = pd.DataFrame(rows)
df.to_csv("features_dataset.csv", index=False)
print("\n✅ Dataset generado: features_dataset.csv con estructura alineada.")
