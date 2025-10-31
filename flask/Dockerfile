# Utilisation d'une image Python officielle et légère
FROM python:3.10-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier des dépendances
COPY requirements.txt .

# Installation des dépendances Python
# --no-cache-dir réduit la taille de l'image
# --trusted-host pour éviter les problèmes SSL potentiels avec pip
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copie du reste du code de l'application
# (Note: sera écrasé par le volume mount en développement)
COPY . .

# Exposition du port standard de Flask
EXPOSE 5000

# Commande pour lancer l'application (utilisera les variables FLASK_*)
CMD ["flask", "run"]

