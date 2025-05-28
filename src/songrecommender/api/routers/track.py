# src/songrecommender/api/routers/track.py
from fastapi import APIRouter, HTTPException, Query, Request
import logging

router = APIRouter()

# Configurar logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.get("/track", summary="Recomendar por canción")
def recommend_by_track(
    request: Request,
    artist: str = Query(...),
    track: str = Query(...),
    k: int = Query(5)
):
    try:
        recommender = request.app.state.recommender
        results = recommender.recommend_songs(track_name=track, artist_name=artist, n_recommendations=k)
        return results.to_dict(orient="records")
    except Exception as e:
        logger.error(f"❌ Error al recomendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


