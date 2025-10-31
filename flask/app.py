import os
import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

# Récupération des variables d'environnement pour la connexion DB
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')

def get_db_connection():
    """
    Établit une connexion à la base de données.
    """
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        app.logger.error(f"Erreur de connexion à la base de données: {e}")
        return None

@app.route('/')
def index():
    """
    Route principale.
    """
    return jsonify(message="Serveur Flask opérationnel.")

@app.route('/db-test')
def db_test():
    """
    Route de test pour la connexion à la base de données.
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Exécute une simple requête de version
                cursor.execute("SELECT version();")
                result = cursor.fetchone()
                db_version = result.get('version()', 'inconnue')
            conn.close()
            return jsonify(
                status="success",
                message="Connexion à la base de données réussie.",
                db_version=db_version
            )
        except pymysql.MySQLError as e:
            return jsonify(status="error", message=f"Erreur lors de la requête: {e}"), 500
        finally:
            if conn.open:
                conn.close()
    else:
        return jsonify(status="error", message="Échec de la connexion à la base de données."), 500

if __name__ == '__main__':
    # L'application est lancée via la commande 'flask run'
    # mais ceci est conservé pour d'autres contextes d'exécution.
    app.run(host='0.0.0.0', port=5000)