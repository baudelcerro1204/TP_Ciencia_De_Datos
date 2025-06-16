from pydantic import BaseModel

class ReservaInput(BaseModel):
    lead_time: float
    total_nights: float
    adults: int
    children: float
    babies: float
    previous_cancellations: int
    booking_changes: int
    adr: float

class ClusterPrediction(BaseModel):
    cluster: int
    cluster_nombre: str
