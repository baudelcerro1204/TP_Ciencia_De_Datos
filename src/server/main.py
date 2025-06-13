from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import predict
import os

app = FastAPI()

# 🔁 Detectar entorno: "dev" por defecto
ENV = os.getenv("ENV", "dev")

# ✅ Orígenes permitidos según entorno
if ENV == "prod":
    allow_origins = [
        "https://mi-app.vercel.app"  # ← reemplazá con tu dominio real en producción
    ]
else:
    allow_origins = [
        "http://localhost:3000"  # Next.js en modo desarrollo
    ]

# ✅ Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Registrar rutas
app.include_router(predict.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Audio Prediction App!"}
