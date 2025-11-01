from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db

class User(UserMixin):
    def __init__(self, id, username, password_hash, role_id, is_active=True):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role_id = role_id
        self.is_active = is_active

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['password_hash'], user_data['role_id'], user_data['is_active'])
        return None

    @staticmethod
    def get_by_username(username):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['password_hash'], user_data['role_id'], user_data['is_active'])
        return None

    @property
    def role(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM roles WHERE id = %s", (self.role_id,))
        role_data = cursor.fetchone()
        return role_data['name'] if role_data else None
