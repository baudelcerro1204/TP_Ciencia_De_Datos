FROM ubuntu:22.04

# Instalar dependencias del sistema, incluyendo eigen3
RUN apt update && apt install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-numpy \
    git \
    wget \
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


RUN ln -s /usr/bin/python3 /usr/bin/python

# Clonar e instalar Essentia
RUN git clone https://github.com/MTG/essentia.git /essentia && \
    cd /essentia && \
    git submodule update --init --recursive && \
    ./waf configure --with-python --with-examples && \
    ./waf && \
    ./waf install && \
    ldconfig

# Crear carpeta de trabajo
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install yt-dlp

COPY . .

ENV PYTHONPATH=/app/src

ENV INSIDE_DOCKER=1

CMD ["uvicorn", "songrecommender.server.main:app", "--host", "0.0.0.0", "--port", "8000"]



