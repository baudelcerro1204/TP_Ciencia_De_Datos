from fastapi import APIRouter, HTTPException
from src.schemas.booking import BookingInput, BookingEvaluation
from src.services.booking_service import crear_reserva, obtener_todas_las_reservas, obtener_reserva
from src.services.evaluation_service import evaluar_reserva
from typing import List
from src.schemas.booking import BookingOut
from uuid import UUID

router = APIRouter()

@router.post("/create-booking")
def create_booking(input_data: BookingInput):
    reserva_id = crear_reserva(input_data.dict())
    return {"reserva_id": reserva_id}

@router.get("/evaluate-booking/{reserva_id}", response_model=BookingEvaluation)
def evaluate_booking(reserva_id: str):
    try:
        reserva_uuid = UUID(reserva_id)  # asegura que sea UUID válido
        result = evaluar_reserva(str(reserva_uuid))

        if result is None:
            raise HTTPException(status_code=404, detail="Reserva no encontrada.")

        return result

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
@router.get("/all-bookings", response_model=List[BookingOut])
def get_all_bookings():
    return obtener_todas_las_reservas()

@router.get("/booking/{reserva_id}", response_model=BookingOut)
def get_booking(reserva_id: str):
    return obtener_reserva(reserva_id)
