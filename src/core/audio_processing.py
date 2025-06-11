# src/core/audio_processing.py
import essentia
import essentia.standard as es
import numpy as np

def extract_features_from_file(file_path: str) -> dict:
    loader = es.MonoLoader(filename=file_path)
    audio = loader()

    extractor = es.Extractor(lowlevel=['danceability', 'energy', 'valence', 'tempo',
                                       'liveness', 'speechiness', 'acousticness', 'instrumentalness'],
                             stats=['mean'])
    result = extractor(audio)
    return {k: float(v) for k, v in result.items() if k.endswith('mean')}