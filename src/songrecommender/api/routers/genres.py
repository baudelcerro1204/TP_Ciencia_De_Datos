# src/songrecommender/api/routers/genres.py
from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter()

@router.get("/", summary="Recomendar por género")
def recommend_genre(
    request: Request,
    genre: str = Query(..., description="Nombre del género"),
    k: int = Query(5, description="Cantidad de recomendaciones")
):
    try:
        recommender = request.app.state.recommender
        recs = recommender.recommend_by_genre(genre=genre, n=k)
        return recs.to_dict(orient="records")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/list", summary="Obtener géneros únicos del dataset")
def list_genres(request: Request):
    recommender = request.app.state.recommender
    return recommender.list_genres()

