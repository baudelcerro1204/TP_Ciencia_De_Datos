FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# --------------------------
# 🧱 Instalar dependencias del sistema
# --------------------------
RUN apt update && apt install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-numpy \
    python3-dev \
    scons \
    pkg-config \
    ffmpeg \
    git \
    wget \
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

# Asegurar symlink de python
RUN ln -s /usr/bin/python3 /usr/bin/python

# --------------------------
# 🧠 Clonar e instalar Essentia con extractor
# --------------------------
RUN git clone https://github.com/MTG/essentia.git /essentia && \
    cd /essentia && \
    git submodule update --init --recursive && \
    ./waf configure --with-python --with-examples && \
    ./waf && ./waf install && ldconfig

# --------------------------
# 📦 Instalar Python deps
# --------------------------
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install yt-dlp

# --------------------------
# 📁 Copiar código fuente
# --------------------------
COPY . .

ENV PYTHONPATH=/app/src
ENV INSIDE_DOCKER=1

# --------------------------
# 🚀 Iniciar FastAPI
# --------------------------
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
