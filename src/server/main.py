from fastapi import FastAPI
from src.api.routers import booking_controller
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hotel Booking Cancellation Predictor",
    description="API para predecir si una reserva será cancelada",
    version="1.0"
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # O ["*"] para todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(booking_controller.router, prefix="/api")
