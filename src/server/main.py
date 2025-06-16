from fastapi import FastAPI
from src.api.routers import predict, audio_features

app = FastAPI()

app.include_router(predict.router)
app.include_router(audio_features.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Audio Prediction App!"}