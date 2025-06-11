# src/api/routers/predict.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from src.core.audio_processing import extract_features_from_file
from src.core.spotify_service import predecir_popularidad
#from pydantic import BaseModel
#from src.core.spotify_service import SpotifyService
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
        return predecir_popularidad(features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el procesamiento: {str(e)}")
    

#class TrackRequest(BaseModel):
 #   track_name: str
 #   artist_name: str

#spotify_service = SpotifyService()

#@router.post("/predict-by-name")
#def predict_by_name(data: TrackRequest):
#    return spotify_service.predict_popularity_from_spotify(
#        data.track_name, data.artist_name
#    )
