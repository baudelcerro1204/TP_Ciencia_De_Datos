from fastapi import APIRouter, UploadFile, File, HTTPException
from src.core.audio_processing import extract_features_from_file, normalize_features
from src.services.predict_service import predecir_popularidad
import tempfile
import shutil

router = APIRouter()

@router.post("/predict-audio")
def predict_from_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp3', '.wav')):
        raise HTTPException(status_code=400, detail="Formato no soportado. Solo .mp3 o .wav")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        features = extract_features_from_file(tmp_path)
        normalized = normalize_features(features)
        
        # ✅ Imprimir features extraídos
        print("🎛️ Features extraídos por Essentia:")
        for key, value in normalized.items():
            print(f"  {key}: {value}")

        return predecir_popularidad(features)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el procesamiento: {str(e)}")

