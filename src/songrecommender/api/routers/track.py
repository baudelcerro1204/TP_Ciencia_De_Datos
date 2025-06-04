from fastapi import APIRouter, HTTPException, Query, Request, Body
from pydantic import BaseModel, Field
from typing import Optional
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FeaturesRequest(BaseModel):
    artist: str = Field(..., description="Nombre del artista")
    name: str = Field(..., description="Nombre de la canción")
    genre: str = Field(..., description="Género musical")
    danceability: float = Field(..., ge=0, le=1)
    energy: float = Field(..., ge=0, le=1)
    acousticness: float = Field(..., ge=0, le=1)
    instrumentalness: float = Field(..., ge=0, le=1)
    speechiness: float = Field(..., ge=0, le=1)
    loudness: float  
    duration: float = Field(..., gt=0, description="Duración en minutos")
    liveness: float = Field(..., ge=0, le=1)

@router.post("/track/features", summary="Recomendar por features manuales")
async def recommend_by_features(
    request: Request,
    features: FeaturesRequest = Body(...),
    k: int = Query(5, description="Cantidad de recomendaciones")
):
    try:
        logger.info(f"📩 POST /track/features recibido con k={k}")
        recommender = request.app.state.recommender

        features_dict = features.dict()
        logger.debug(f"📦 Payload recibido: {features_dict}")

        # Convertir duración a ms
        features_dict['duration_ms'] = int(features_dict['duration'] * 60 * 1000)
        del features_dict['duration']
        logger.debug(f"⏱️ Duración convertida a ms: {features_dict['duration_ms']}")

        # Filtrar solo las features numéricas usadas por el modelo
        filtered_features = {k: features_dict[k] for k in recommender.numeric_features if k in features_dict}
        logger.debug(f"🎯 Features filtradas usadas por modelo: {filtered_features}")

        results = recommender.recommend_by_features(features=filtered_features, n_recommendations=k)
        logger.info(f"✅ {len(results)} recomendaciones generadas con éxito")
        return results.to_dict(orient="records")

    except Exception as e:
        logger.error(f"❌ Error en recomendación por features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track", summary="Recomendar por canción")
def recommend_by_track(
    request: Request,
    artist: str = Query(...),
    track: str = Query(...),
    k: int = Query(5)
):
    try:
        logger.info(f"🎧 GET /track recibido con artista='{artist}', track='{track}', k={k}")
        recommender = request.app.state.recommender

        results = recommender.recommend_songs(track_name=track, artist_name=artist, n_recommendations=k)
        logger.info(f"✅ {len(results)} canciones recomendadas para '{track}' de '{artist}'")
        return results.to_dict(orient="records")

    except Exception as e:
        logger.error(f"❌ Error al recomendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))
