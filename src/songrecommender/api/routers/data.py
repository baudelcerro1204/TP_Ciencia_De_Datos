# src/songrecommender/api/routers/data.py
from fastapi import APIRouter, HTTPException
from songrecommender.processors.data_processing import MillionSongDataProcessor
from fastapi.responses import JSONResponse
import pandas as pd
from pathlib import Path

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
        # Buscar el archivo como en SongRecommender
        project_root = Path(__file__).resolve().parents[4]
        processed_file = project_root / 'data' / 'processed' / 'million_song_combined.parquet'

        if not processed_file.exists():
            raise HTTPException(status_code=404, detail=f"Archivo procesado no encontrado en: {processed_file}")

        df = pd.read_parquet(processed_file)
        songs = df[['track_id', 'name', 'artist', 'genre', 'year']].drop_duplicates().to_dict(orient="records")
        return JSONResponse(content=songs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
