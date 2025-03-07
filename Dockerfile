# Utiliser l'image de base Python 3.9

FROM python:3.9-slim as builder

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Copier le code de l'application
COPY app.py .

# Ajouter le répertoire des dépendances au PATH
ENV PATH=/root/.local/bin:$PATH

# Exposer le port sur lequel l'application va écouter
EXPOSE 80

# Commande pour démarrer l'application avec Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
