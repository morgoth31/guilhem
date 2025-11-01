from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(role_name):
    """
    Décorateur pour restreindre l'accès à une route en fonction du rôle de l'utilisateur.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Non autorisé
            if current_user.role != role_name and current_user.role != 'admin':
                abort(403)  # Accès interdit
            return f(*args, **kwargs)
        return decorated_function
    return decorator
