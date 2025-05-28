# src/songrecommender/server/app.py
from fastapi import FastAPI
from songrecommender.api.routers.track import router as track_router
from songrecommender.api.routers.genres import router as genre_router
from songrecommender.api.routers.data import router as data_router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    from songrecommender.recommender.model import SongRecommender
    app.state.recommender = SongRecommender(use_pca=False, exclude_same_artist=False)

# Registramos los routers
app.include_router(track_router, prefix="/recommend", tags=["Tracks"])
app.include_router(genre_router, prefix="/recommend/genre", tags=["Genres"])
app.include_router(data_router, prefix="/data", tags=["Data Processing"])

