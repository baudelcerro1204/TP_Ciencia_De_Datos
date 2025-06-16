from fastapi import APIRouter
from src.schemas.predict_cluster import ReservaInput, ClusterPrediction
from src.services.cluster_service import predecir_cluster

router = APIRouter()

@router.post("/predict-cluster", response_model=ClusterPrediction)
def predict_cluster(reserva: ReservaInput):
    cluster_id, cluster_nombre = predecir_cluster(reserva.dict())
    return {"cluster": cluster_id, "cluster_nombre": cluster_nombre}
