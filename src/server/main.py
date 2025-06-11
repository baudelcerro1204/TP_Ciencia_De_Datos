# Paso 3: main.py
# main.py

from fastapi import FastAPI
from src.api.routers import predict

app = FastAPI()
app.include_router(predict.router)