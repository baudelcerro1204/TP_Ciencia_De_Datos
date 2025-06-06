# src/songrecommender/processors/download_and_process.py
import yt_dlp
import os
from pathlib import Path
import pandas as pd
from songrecommender.processors.audio_features import extract_features_from_mp3

TEMP_DIR = Path("tmp_audio")
TEMP_DIR.mkdir(exist_ok=True)

def download_youtube_audio(query: str) -> Path:
    output_path = TEMP_DIR / "%(title)s.%(ext)s"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_path),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        downloaded_file = ydl.prepare_filename(info['entries'][0])
        mp3_path = Path(downloaded_file).with_suffix(".mp3")
        return mp3_path

def process_song_and_add_to_dataset(song_name: str):
    mp3_path = download_youtube_audio(song_name)
    features = extract_features_from_mp3(str(mp3_path), original_filename=mp3_path.name)

    # Guardar en dataset
    project_root = Path(__file__).resolve().parents[3]
    parquet_path = project_root / "data" / "processed" / "million_song_combined.parquet"
    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([features])], ignore_index=True)
    df.to_parquet(parquet_path, index=False)

    mp3_path.unlink(missing_ok=True)  # Limpieza

    return features
