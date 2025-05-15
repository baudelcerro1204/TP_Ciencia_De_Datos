import kagglehub
import os
from pathlib import Path
import shutil

def download_dataset(dataset_handle):
    """Descarga un dataset de Kaggle"""
    print(f"Descargando {dataset_handle}...")
    try:
        # Descargar dataset
        download_path = kagglehub.dataset_download(dataset_handle)
        
        # Mover archivos a data/raw
        for file in Path(download_path).rglob('*.*'):
            if file.is_file():
                dest = Path("data/raw") / file.name
                shutil.move(str(file), str(dest))
                print(f"Archivo movido a: {dest}")
        
        return True
    except Exception as e:
        print(f"Error descargando {dataset_handle}: {str(e)}")
        return False

if __name__ == "__main__":    
    # Lista de datasets a descargar
    datasets = [
        "atharvasoundankar/spotify-global-streaming-data-2024",
        "yelexa/spotify200",
        "maharshipandya/-spotify-tracks-dataset"
    ]
    
    for dataset in datasets:
        success = download_dataset(dataset)
        if success:
            print(f"✅ {dataset} descargado correctamente\n")
        else:
            print(f"❌ Error con {dataset}\n")
    
    print("Proceso completado. Archivos en data/raw:")
    for file in Path("data/raw").iterdir():
        print(f"- {file.name}")