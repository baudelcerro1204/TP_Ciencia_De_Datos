from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

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
    departure_date: str                      
    guest_name: str                          


class FeatureImpact(BaseModel):
    feature: str
    impact: float


class BookingEvaluation(BaseModel):
    prediccion: str
    probabilidad_cancelacion: float
    cluster: int
    cluster_nombre: str
    probabilidad_cancelacion_cluster: Optional[float]
    explicacion_shap: Optional[List[FeatureImpact]]

class BookingOut(BookingInput):
    id: UUID
