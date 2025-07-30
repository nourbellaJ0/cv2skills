FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libxml2 libxslt1-dev curl unzip \
 && rm -rf /var/lib/apt/lists/*

COPY . /app

# Mettre à jour pip
RUN pip install --upgrade pip

# ✅ Installer toutes les dépendances avec accès au dépôt Apryse
RUN pip install --no-cache-dir --extra-index-url=https://pypi.apryse.com -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
