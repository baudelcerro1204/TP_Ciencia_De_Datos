import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler

# Ruta al modelo
MODEL_PATH = "src/model/modelo_clusters_kmeans.pkl"

# Nombres de clusters
cluster_map = {
    0: "Reservas anticipadas de adultos",
    1: "Viajes familiares con planificación media",
    2: "Reservas especiales y confiables"
}

# Cargar modelo y scaler
kmeans = joblib.load(MODEL_PATH)

# Escalador base (mismo orden de features que al entrenar)
scaler = StandardScaler()
scaler.mean_ = np.array([105.6, 3.5, 1.9, 0.5, 0.1, 0.05, 0.2, 125])  # promedio ejemplo
scaler.scale_ = np.array([30, 1.0, 0.5, 0.8, 0.3, 0.2, 0.6, 40])     # desvío estándar ejemplo

def predecir_cluster(data: dict):
    orden = [
        "lead_time", "total_nights", "adults", "children",
        "babies", "previous_cancellations", "booking_changes", "adr"
    ]
    x = np.array([[data[clave] for clave in orden]])
    x_scaled = scaler.transform(x)
    cluster = kmeans.predict(x_scaled)[0]
    return cluster, cluster_map.get(cluster, "Desconocido")
