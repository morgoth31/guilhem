# Stack Docker Compose : Flask + MariaDB + phpMyAdmin

Ce projet fournit une configuration `docker-compose` pour démarrer rapidement un environnement de développement web complet comprenant :

* **`flask_app`** : Un service applicatif basé sur Python (Flask).
* **`db`** : Un service de base de données MariaDB.
* **`phpmyadmin`** : Une interface web d'administration pour MariaDB.

## 1. Prérequis

* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/) (généralement inclus avec Docker Desktop)

## 2. Structure du Projet


### lancer le projet

docker compose logs -f flask_app