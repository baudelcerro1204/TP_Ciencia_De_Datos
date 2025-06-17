import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
import shap
from shap import TreeExplainer
from src.services.booking_service import obtener_reserva

# Modelo de regresión (pipeline)
model = joblib.load("src/model/hotel_cancellation_predictor.pkl")
classifier = model.named_steps["classifier"]
preprocessor = model.named_steps["preprocessor"]
feature_names = preprocessor.get_feature_names_out()

# SHAP Explainer específico para árboles
explainer = TreeExplainer(classifier)

# Modelo de cluster
kmeans = joblib.load("src/model/modelo_clusters_kmeans.pkl")
cluster_map = {
    0: "Reservas anticipadas de adultos",
    1: "Viajes familiares con planificación media",
    2: "Reservas especiales y confiables"
}

# Probabilidad histórica de cancelación por cluster
proba_cancelacion_por_cluster = {
    0: 0.37,
    1: 0.37,
    2: 0.18
}

# Escalador usado para clustering
scaler = StandardScaler()
scaler.mean_ = np.array([105.6, 3.5, 1.9, 0.5, 0.1, 0.05, 0.2, 125])
scaler.scale_ = np.array([30, 1.0, 0.5, 0.8, 0.3, 0.2, 0.6, 40])

def evaluar_reserva(reserva_id: str):
    try:
        reserva = obtener_reserva(reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada.")

        # Preparar datos
        data = reserva.__dict__.copy()
        data.pop("_sa_instance_state", None)
        data["total_nights"] = data["stays_in_weekend_nights"] + data["stays_in_week_nights"]

        df = pd.DataFrame([data])
        df.drop(columns=[c for c in ["reservation_status_date", "id"] if c in df.columns], inplace=True)

        # Predicción
        pred = model.predict(df)[0]
        proba = model.predict_proba(df)[0][1]

        # SHAP
        X_trans = preprocessor.transform(df)
        if hasattr(X_trans, "toarray"):
            X_trans = X_trans.toarray()

        shap_values = explainer.shap_values(X_trans)

        # Soporte para modelos con 1 o más clases
        if isinstance(shap_values, list) and len(shap_values) > 1:
            shap_class_values = shap_values[1]
        else:
            shap_class_values = shap_values[0]

        contributions = sorted(
            zip(feature_names, shap_class_values[0]),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        top_features = [{"feature": name, "impact": round(val, 4)} for name, val in contributions[:5]]

        # Clustering
        orden = ["lead_time", "total_nights", "adults", "children",
                 "babies", "previous_cancellations", "booking_changes", "adr"]
        x = np.array([[data[k] for k in orden]])
        x_scaled = scaler.transform(x)
        cluster = kmeans.predict(x_scaled)[0]
        cluster_nombre = cluster_map.get(cluster, "Desconocido")

        return {
            "prediccion": "Alta probabilidad de cancelación" if pred == 1 else "Baja probabilidad de cancelación",
            "probabilidad_cancelacion": round(proba, 4),
            "cluster": cluster,
            "cluster_nombre": cluster_nombre,
            "probabilidad_cancelacion_cluster": proba_cancelacion_por_cluster[cluster],
            "explicacion_shap": top_features
        }

    except Exception as e:
        logging.exception("Error al evaluar reserva:")
        raise ValueError("No se pudo evaluar la reserva.")
