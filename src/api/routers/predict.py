from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import pandas as pd

router = APIRouter()

# Cargar el modelo
model_path = "src/model/hotel_cancellation_predictor.pkl"
model = joblib.load(model_path)

# Obtener columnas usadas por el modelo entrenado (para explicar)
feature_names = model.named_steps["preprocessor"].get_feature_names_out()
classifier = model.named_steps["classifier"]

class BookingInput(BaseModel):
    hotel: str
    lead_time: int
    arrival_date_year: int
    arrival_date_month: str
    arrival_date_week_number: int
    arrival_date_day_of_month: int
    stays_in_weekend_nights: int
    stays_in_week_nights: int
    adults: int
    children: float
    babies: int
    meal: str
    country: str
    market_segment: str
    distribution_channel: str
    is_repeated_guest: int
    previous_cancellations: int
    previous_bookings_not_canceled: int
    reserved_room_type: str
    assigned_room_type: str
    booking_changes: int
    deposit_type: str
    days_in_waiting_list: int
    customer_type: str
    adr: float
    required_car_parking_spaces: int
    total_of_special_requests: int
    reservation_status_date: str

@router.post("/predict")
def predict_cancel(input_data: BookingInput):
    # Convertir input en DataFrame
    data_dict = input_data.dict()
    df = pd.DataFrame([data_dict])

    # Agregar columna derivada si el modelo la usó
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]

    # Eliminar columna que no se usó
    if "reservation_status_date" in df.columns:
        df.drop(columns=["reservation_status_date"], inplace=True)

    # Predicción
    pred = model.predict(df)[0]
    proba = model.predict_proba(df)[0][1]  # probabilidad de cancelación (clase 1)

    # Obtener importancia de features si el modelo lo permite
    if hasattr(classifier, "feature_importances_"):
        importances = classifier.feature_importances_
        top_features = sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        )[:5]
    else:
        top_features = []

    return {
        "prediccion": "Cancelada" if pred == 1 else "No cancelada",
        "probabilidad_cancelacion": round(proba, 4),
        "factores_principales": [
            {"feature": name, "importancia": round(score, 4)}
            for name, score in top_features
        ]
    }
