from fastapi import FastAPI
from src.api.routers import cluster

app = FastAPI()

app.include_router(cluster.router, prefix="/api")
