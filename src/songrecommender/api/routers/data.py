# src/songrecommender/api/routers/data.py
from fastapi import APIRouter, HTTPException
from songrecommender.processors.data_processing import SpotifyDataProcessor

router = APIRouter()

@router.post("/process", summary="Procesar todos los datos brutos")
def process_all():
    try:
        proc = SpotifyDataProcessor()
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
        proc = SpotifyDataProcessor()
        path = proc.enrich_data()
        return {
            "message": "Enriquecimiento completado",
            "ruta_parquet": str(path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
