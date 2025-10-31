# Stack Docker : Application de Gestion de Patients (Flask + MariaDB + phpMyAdmin)

Ce dépôt fournit la configuration `docker-compose` nécessaire pour déployer un environnement de développement complet pour une application de gestion de patients.

La stack technique inclut :

  * **`app`** : Un service applicatif basé sur Python 3.10+ et le micro-framework Flask.
  * **`db`** : Un service de base de données MariaDB (v10.8+).
  * **`phpmyadmin`** : Une interface web d'administration pour la base de données MariaDB.

## 1\. Prérequis

  * [Docker](https://www.docker.com/get-started)
  * [Docker Compose](https://docs.docker.com/compose/install/) (généralement inclus avec Docker Desktop)

## 2\. Structure du Projet

```
.
├── app/                  # Contient le code source de Flask
│   ├── app.py            # Point d'entrée de l'application Flask
│   ├── models.py         # Définitions des modèles SQLAlchemy (Patient, Study, User...)
│   ├── routes.py         # (Optionnel) Définition des routes de l'API
│   └── requirements.txt  # Dépendances Python
├── .env                  # Fichier de configuration (privé)
├── .env.example          # Fichier d'exemple pour la configuration
├── docker-compose.yml    # Fichier d'orchestration des services
└── Dockerfile            # Instructions de build pour l'image du service 'app'
```

## 3\. Installation et Lancement

### 3.1. Configuration

Avant le premier lancement, vous devez configurer les variables d'environnement.

1.  Copiez le fichier d'exemple :
    ```bash
    cp .env.example .env
    ```
2.  Modifiez le fichier `.env` pour y définir vos mots de passe et les paramètres de la base de données (ex: `MYSQL_ROOT_PASSWORD`, `DATABASE_URL`). Ce fichier sera utilisé par `docker-compose` pour configurer les conteneurs.

### 3.2. Démarrage

Pour construire les images (si elles n'existent pas) et démarrer tous les services en arrière-plan :

```bash
docker compose up -d --build
```

### 3.3. Arrêt

Pour arrêter et supprimer les conteneurs :

```bash
docker compose down
```

Pour arrêter les conteneurs et supprimer les volumes (y compris les données de la base \!) :

```bash
docker compose down -v
```

## 4\. Accès aux Services

Une fois les conteneurs démarrés, les services sont accessibles aux adresses suivantes (par défaut) :

  * **Application Flask** : `http://localhost:5000`
  * **phpMyAdmin** : `http://localhost:8081`
  * **Base de Données (via Hôte)** : Connexion directe sur `localhost:3306` (si le port est mappé dans `docker-compose.yml`)

-----

## 5\. Feuille de Route du Développement

Le projet est construit de manière incrémentale en suivant les phases ci-dessous.

### Phase 1 : Infrastructure et Fondations

**Objectif :** Mettre en place l'environnement technique complet, la structure de la base de données et une application "squelette" fonctionnelle.

#### 1.1. Conteneurisation (Docker)

  * **`docker-compose.yml`**

      * **Service `db` (MariaDB)** :
          * Image : `mariadb:10.8+`
          * Variables d'env : `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD` (lues depuis le fichier `.env`).
          * Persistance : Utilisation d'un volume nommé (ex: `mariadb_data`).
      * **Service `app` (Flask)** :
          * Build : Basé sur le `Dockerfile` à la racine.
          * Ports : Mapping `5000:5000`.
          * Variables d'env : `DATABASE_URL` (lue depuis le fichier `.env`).
          * Dépendance : `depends_on: [db]` pour assurer l'ordre de démarrage.
      * **Service `phpmyadmin`** :
          * Image : `phpmyadmin:latest`
          * Lien : `db`
          * Ports : Mapping (ex: `8081:80`).

  * **`Dockerfile` (Service `app`)**

      * Image de base : `python:3.10-slim`.
      * Dépendances système : `build-essential`, `default-libmysqlclient-dev` (pour la compilation de `mysqlclient`).
      * Dépendances Python : Copie de `app/requirements.txt` et exécution de `pip install -r requirements.txt`.
      * Code source : Copie du répertoire `app/` dans le conteneur.
      * Commande : `CMD` (ex: `gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"`, ou équivalent).

#### 1.2. Base de Données (Modélisation)

  * **Modélisation (via ORM SQLAlchemy)** :
      * `Role` : Table pour les 3 niveaux de droits (lecture, modification, admin).
      * `User` : Table des utilisateurs (username, password\_hash, clé étrangère vers `Role`).
      * `Patient` : Table des informations démographiques (basée sur `DcmStudy`).
      * `Study` : Table des études (basée sur `DcmStudy`, clé étrangère vers `Patient`).
  * **Initialisation** :
      * Utilisation d'un outil de migration (ex: `Flask-Migrate` / `Alembic`) pour créer le schéma.
      * Script d'initialisation (ou migration) pour insérer les 3 rôles de base et un utilisateur `admin` par défaut.

#### 1.3. Application Flask (Squelette)

  * **`requirements.txt`** :
      * `Flask`, `SQLAlchemy`, `Flask-SQLAlchemy`, `PyMySQL` (ou `mysqlclient`), `gunicorn`, `python-dotenv`, `Flask-Migrate`.
  * **Application (`app.py`)** :
      * Structure de type "Factory Pattern" (fonction `create_app()`).
      * Configuration de la `DATABASE_URL` chargée depuis les variables d'environnement.
      * Route "Health Check" (`/`) vérifiant la connexion à la BDD et retournant `{"status": "OK"}`.

**Livrable de la Phase 1 :** Un environnement complet lançable via `docker compose up`, avec une base de données structurée (vide) et une application web qui répond sur le port 5000.

-----

### Phase 2 : Gestion des Données (CRUD)

*(À venir)*

  * Implémentation des routes API (CRUD) pour les Patients et les Études.
  * Implémentation de la route de recherche (`/api/search`).
  * Création de l'interface frontend (responsive) pour l'affichage, la recherche et la saisie des données.

-----

### Phase 3 : Gestion des Droits (RBAC)

*(À venir)*

  * Implémentation de l'authentification (ex: Flask-Login).
  * Sécurisation des routes API via des décorateurs de rôles (`lecture`, `modification`, `admin`).
  * Création de l'interface d'administration pour la gestion des utilisateurs.