from sqlalchemy.orm import Session
from src.core.db import SessionLocal
from src.data.models.booking_model import Reserva
import uuid

def crear_reserva(data: dict):
    db: Session = SessionLocal()
    reserva = Reserva(**data)
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    db.close()
    return str(reserva.id)

def obtener_reserva(reserva_id: str):
    db: Session = SessionLocal()
    try:
        try:
            reserva_uuid = uuid.UUID(reserva_id)
        except ValueError:
            print(f"❌ ID inválido (no es UUID): {reserva_id}")
            return None

        reserva = db.query(Reserva).filter(Reserva.id == reserva_uuid).first()
        if not reserva:
            print(f"❌ No se encontró la reserva con ID: {reserva_uuid}")
        return reserva
    finally:
        db.close()


def obtener_todas_las_reservas():
    db: Session = SessionLocal()
    reservas = db.query(Reserva).all()
    db.close()
    return reservas

