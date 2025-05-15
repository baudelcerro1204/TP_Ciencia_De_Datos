# src/songrecommender/server/app.py
from fastapi import FastAPI
from songrecommender.api.routers.albums import router as album_router
from songrecommender.api.routers.genres import router as genre_router
from songrecommender.api.routers.data   import router as data_router

app = FastAPI(title="🎵 Song Recommender API")

app.include_router(album_router, prefix="/recommend/album", tags=["Albums"])
app.include_router(genre_router, prefix="/recommend/genre", tags=["Genres"])
app.include_router(data_router,  prefix="/data",              tags=["Data"])
