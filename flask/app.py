import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Configuration de la base de données
    app.config['DB_HOST'] = os.environ.get('DB_HOST')
    app.config['DB_USER'] = os.environ.get('DB_USER')
    app.config['DB_PASSWORD'] = os.environ.get('DB_PASSWORD')
    app.config['DB_NAME'] = os.environ.get('DB_NAME')

    # Importation et enregistrement des Blueprints
    from routes.api import api_bp
    from routes.frontend import frontend_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(frontend_bp)

    from db import init_app
    init_app(app)

    return app

app = create_app()

@app.route('/health')
def health_check():
    """A simple health check endpoint."""
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
