FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar todo o código
COPY . .

# Copiar credencial Firebase
COPY firebase_key.json /app/firebase_key.json
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/firebase_key.json"

EXPOSE 80

# Rodar FastAPI com Gunicorn + Uvicorn Worker
CMD ["gunicorn", "main:upkeep", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:80", \
     "--workers", "3", \
     "--timeout", "120"]
