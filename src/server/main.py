from fastapi import FastAPI
from src.api.routers import booking_controller


app = FastAPI(
    title="Hotel Booking Cancellation Predictor",
    description="API para predecir si una reserva será cancelada",
    version="1.0"
)

app.include_router(booking_controller.router, prefix="/api")
