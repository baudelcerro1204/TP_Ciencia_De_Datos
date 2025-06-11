FROM python:3.10-slim

# Evitar errores interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Crear carpeta de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt update && apt install -y \
    ffmpeg \
    libfftw3-dev \
    libsamplerate0-dev \
    libyaml-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libtag1-dev \
    libchromaprint-tools \
    libeigen3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instalar Essentia desde PyPI alternativo oficial
RUN pip install essentia --extra-index-url https://essentia.upf.edu/pypi

# Opcional: otros paquetes adicionales
RUN pip install yt-dlp

# Copiar código fuente
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app/src
ENV INSIDE_DOCKER=1

# Ejecutar el servidor
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]

