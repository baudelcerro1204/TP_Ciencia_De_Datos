# src/songrecommender/api/routers/albums.py
from fastapi import APIRouter, HTTPException, Query
from songrecommender.recommender.model import SpotifyRecommender

router = APIRouter()

@router.get("/", summary="Recomendar por álbum")
def recommend_album(
    artist: str = Query(..., description="Nombre del artista"),
    album:  str = Query(..., description="Nombre del álbum"),
    k:      int = Query(5, description="Cantidad de recomendaciones")
):
    try:
        recs = SpotifyRecommender().recommend_songs(
            album_name=album,
            artist_name=artist,
            n_recommendations=k
        )
        return recs.to_dict(orient="records")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
