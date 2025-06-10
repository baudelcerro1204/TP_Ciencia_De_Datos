import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

# Inicialización del API
api = KaggleApi()
api.authenticate()

# Dataset que querés descargar
dataset = "devdope/900k-spotify"

# Carpeta donde lo vas a guardar
download_path = os.path.join("data", "raw")
os.makedirs(download_path, exist_ok=True)

# Descargar el dataset ZIP
print("Descargando dataset desde Kaggle...")
api.dataset_download_files(dataset, path=download_path, unzip=True)
print("Descarga completada.")

# Mostrar los archivos descargados
print("Archivos en", download_path, ":", os.listdir(download_path))
