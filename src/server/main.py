from fastapi import FastAPI
from src.api.routers import predict

app = FastAPI()

app.include_router(predict.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Audio Prediction App!"}