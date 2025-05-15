# src/songrecommender/api/routers/genres.py
from fastapi import APIRouter, HTTPException, Query
from songrecommender.recommender.model import SpotifyRecommender

router = APIRouter()

@router.get("/", summary="Recomendar por género")
def recommend_genre(
    genre: str = Query(..., description="Nombre del género"),
    k:     int = Query(5, description="Cantidad de recomendaciones")
):
    try:
        recs = SpotifyRecommender().recommend_by_genre(
            genre=genre,
            n=k
        )
        return recs.to_dict(orient="records")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/list", summary="Listar géneros disponibles")
def list_genres():
    return SpotifyRecommender().list_genres()
