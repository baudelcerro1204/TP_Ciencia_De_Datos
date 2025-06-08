# src/songrecommender/api/routers/data.py
from fastapi import APIRouter, HTTPException, File, UploadFile, Body
from fastapi.responses import JSONResponse
from songrecommender.processors.data_processing import MillionSongDataProcessor
from songrecommender.processors.audio_features import extract_features_from_mp3
from songrecommender.processors.download_song_and_process import process_song_and_add_to_dataset
from tempfile import NamedTemporaryFile
from pathlib import Path
import pandas as pd
import requests
import shutil
from fastapi import Query

router = APIRouter()

@router.post("/process", summary="Procesar todos los datos brutos")
def process_all():
    try:
        proc = MillionSongDataProcessor()
        df = proc.process_all()
        return {
            "message": "Procesamiento completado",
            "registros": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enrich", summary="Enriquecer parquet con nuevos lanzamientos")
def enrich():
    try:
        proc = MillionSongDataProcessor()
        path = proc.enrich_data()
        return {
            "message": "Enriquecimiento completado",
            "ruta_parquet": str(path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs", summary="Obtener todas las canciones del dataset")
def get_all_songs():
    try:
        project_root = Path(__file__).resolve().parents[4]
        processed_file = project_root / 'data' / 'processed' / 'million_song_combined.parquet'

        if not processed_file.exists():
            raise HTTPException(status_code=404, detail=f"Archivo procesado no encontrado en: {processed_file}")

        df = pd.read_parquet(processed_file)
        songs = df[['track_id', 'name', 'artist', 'genre']].drop_duplicates().to_dict(orient="records")
        return JSONResponse(content=songs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", summary="Subir MP3, extraer features y agregar al dataset")
async def upload_and_extract(file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        print(f"🎧 Procesando archivo: {file.filename}")
        new_row = extract_features_from_mp3(tmp_path, original_filename=file.filename)

        project_root = Path(__file__).resolve().parents[4]
        parquet_path = project_root / "data" / "processed" / "million_song_combined.parquet"
        df = pd.read_parquet(parquet_path)

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_parquet(parquet_path, index=False)

        return {"message": f"✅ {file.filename} agregado al dataset", "song": new_row}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_by_name", summary="Buscar canción por nombre y agregarla automáticamente")
def add_song_by_name(name: str = Body(..., embed=True)):
    try:
        new_song = process_song_and_add_to_dataset(name)
        return {
            "message": f"✅ Canción agregada: {new_song['track_id']}",
            "song": new_song
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movie_from_name", summary="Buscar películas asociadas a una canción por nombre exacto")
def movie_from_song_name(nombre: str = Query(..., description="Nombre exacto de la canción según dataset")):
    try:
        name_clean = nombre.strip().lower()

        # Cargar dataset
        project_root = Path(__file__).resolve().parents[4]
        parquet_path = project_root / "data" / "processed" / "million_song_combined.parquet"
        if not parquet_path.exists():
            raise HTTPException(status_code=404, detail="Dataset no encontrado")

        df = pd.read_parquet(parquet_path)
        df["name_lower"] = df["name"].str.strip().str.lower()

        match = df[df["name_lower"] == name_clean]
        if match.empty:
            raise HTTPException(status_code=404, detail="Canción no encontrada en el dataset")

        song_name = match.iloc[0]["name"]

        # Consultar iTunes
        response = requests.get("https://itunes.apple.com/search", params={
            "term": song_name,
            "entity": "song",
            "limit": 10
        }, timeout=5)

        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Error al consultar iTunes Search API")

        data = response.json()
        results = data.get("results", [])
        if not results:
            return {"song": song_name, "movies": []}

        # Buscar soundtracks con criterios más amplios
        movies = set()
        keywords = [
            "motion picture",
            "soundtrack",
            "original soundtrack",
            "ost",
            "film",
            "movie",
            "series",
            "tv",
            "netflix",
            "hbo",
            "prime",
            "original score",
            "music from",
            "cinema",
            "disney",
            "pixar",
            "marvel",
            "warner",
            "dreamworks"
        ]


        for item in results:
            col = item.get("collectionName", "").lower()
            if any(keyword in col for keyword in keywords):
                movies.add(item.get("collectionName", "").strip())

        return {
            "song": song_name,
            "movies": list(movies)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")