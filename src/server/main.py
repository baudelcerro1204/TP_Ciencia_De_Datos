from fastapi import FastAPI
from src.api.routers import cluster
from src.api.routers import predict


app = FastAPI(
    title="Hotel Booking Cancellation Predictor",
    description="API para predecir si una reserva será cancelada",
    version="1.0"
)

app.include_router(cluster.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
