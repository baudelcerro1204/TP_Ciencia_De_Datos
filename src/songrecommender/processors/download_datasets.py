import os
import zipfile
from pathlib import Path
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi

from kaggle.api.kaggle_api_extended import KaggleApi
import os

def download_and_extract_dataset(dataset_ref, dest_path='data/raw'):
    api = KaggleApi()
    api.authenticate()
    
    os.makedirs(dest_path, exist_ok=True)
    print(f"Descargando dataset {dataset_ref} en {dest_path} ...")
    
    api.dataset_download_files(dataset_ref, path=dest_path, unzip=True, quiet=False)
    
    print("Descarga y extracción finalizadas!")



def load_msd_challenge_data(data_folder="data/raw"):
    # Cambia según archivos que traiga el dataset
    # Ejemplo: cargamos CSVs que tenga
    csv_files = list(Path(data_folder).glob("*.csv"))
    print(f"Archivos CSV encontrados: {[str(f) for f in csv_files]}")
    
    # Ejemplo cargando uno de ellos
    df = pd.read_csv(csv_files[0])
    print(f"Primeras filas del archivo {csv_files[0].name}:")
    print(df.head())
    return df

if __name__ == '__main__':
    dataset_ref = 'undefinenull/million-song-dataset-spotify-lastfm'
    #dataset_ref = 'kfoster150/million-song-dataset-metadata-lyrics-terms'
    download_and_extract_dataset(dataset_ref)
    # load_msd_challenge_data()
    df = load_msd_challenge_data()
