# Imagem Ubuntu oficial com suporte a versões recentes do GDAL/Python
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.10.1 

# Instala pip e venv 
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

# Copia e instala dependencias
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

# gcloud
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

