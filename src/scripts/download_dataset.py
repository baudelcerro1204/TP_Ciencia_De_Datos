import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

def download_kaggle_dataset():
    # Inicializar la API de Kaggle
    api = KaggleApi()
    api.authenticate()

    # Nombre del dataset a descargar
    dataset = "jessemostipak/hotel-booking-demand"

    # Ruta destino
    download_path = os.path.join("src", "data", "raw")
    os.makedirs(download_path, exist_ok=True)

    # Descargar y descomprimir
    print("📦 Descargando dataset desde Kaggle...")
    api.dataset_download_files(dataset, path=download_path, unzip=True)
    print("✅ Descarga completada.")

    # Mostrar archivos descargados
    print("📁 Archivos en", download_path, ":", os.listdir(download_path))

if __name__ == "__main__":
    download_kaggle_dataset()