from flask import Blueprint, jsonify, request
from flask_login import login_required
from decorators import role_required
from werkzeug.security import generate_password_hash
from db import get_db
import pymysql

api_bp = Blueprint('api', __name__)

# --- Routes API pour les Patients ---

@api_bp.route('/patients', methods=['GET'])
@login_required
def get_patients():
    """
    Lister tous les patients avec pagination.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Nombre de résultats par page
    offset = (page - 1) * per_page

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM patients LIMIT %s OFFSET %s", (per_page, offset))
            patients = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM patients")
            total = cursor.fetchone()['COUNT(*)']

        return jsonify({
            'page': page,
            'per_page': per_page,
            'total': total,
            'data': patients
        })
    except pymysql.MySQLError as e:
        return jsonify(status="error", message=f"Erreur lors de la récupération des patients: {e}"), 500

@api_bp.route('/patients', methods=['POST'])
@login_required
@role_required('modification')
def create_patient():
    """
    Créer un patient.
    """
    data = request.get_json()
    if not data or not all(k in data for k in ['lastname', 'firstname']):
        return jsonify(status="error", message="Données manquantes pour la création du patient."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            sql = "INSERT INTO patients (lastname, firstname, birthdate, gender) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (data['lastname'], data['firstname'], data.get('birthdate'), data.get('gender')))
        db.commit()
        return jsonify(status="success", message="Patient créé avec succès.", patient_id=cursor.lastrowid), 201
    except pymysql.MySQLError as e:
        db.rollback()
        return jsonify(status="error", message=f"Erreur lors de la création du patient: {e}"), 500

@api_bp.route('/patients/<int:patient_id>', methods=['GET'])
@login_required
def get_patient(patient_id):
    """
    Voir un patient.
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
            patient = cursor.fetchone()
        if patient:
            return jsonify(patient)
        else:
            return jsonify(status="error", message="Patient non trouvé."), 404
    except pymysql.MySQLError as e:
        return jsonify(status="error", message=f"Erreur lors de la récupération du patient: {e}"), 500

@api_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@login_required
@role_required('modification')
def update_patient(patient_id):
    """
    Mettre à jour un patient.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Données manquantes pour la mise à jour."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Vérifier si le patient existe
            cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
            if not cursor.fetchone():
                return jsonify(status="error", message="Patient non trouvé."), 404

            # Construire la requête de mise à jour dynamiquement
            fields = []
            params = []
            for key, value in data.items():
                if key in ['lastname', 'firstname', 'birthdate', 'gender']:
                    fields.append(f"{key} = %s")
                    params.append(value)

            if not fields:
                return jsonify(status="error", message="Aucun champ valide à mettre à jour."), 400

            sql = f"UPDATE patients SET {', '.join(fields)} WHERE id = %s"
            params.append(patient_id)
            cursor.execute(sql, tuple(params))
        db.commit()
        return jsonify(status="success", message="Patient mis à jour avec succès.")
    except pymysql.MySQLError as e:
        db.rollback()
        return jsonify(status="error", message=f"Erreur lors de la mise à jour du patient: {e}"), 500

# --- Routes API pour les Studies ---

@api_bp.route('/studies', methods=['GET'])
@login_required
def get_studies():
    """
    Lister toutes les études.
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM studies")
            studies = cursor.fetchall()
        return jsonify(studies)
    except pymysql.MySQLError as e:
        return jsonify(status="error", message=f"Erreur lors de la récupération des études: {e}"), 500

@api_bp.route('/studies', methods=['POST'])
@login_required
@role_required('modification')
def create_study():
    """
    Créer une étude.
    """
    data = request.get_json()
    if not data or not all(k in data for k in ['patient_id', 'study_description', 'modality']):
        return jsonify(status="error", message="Données manquantes pour la création de l'étude."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Vérifier si le patient existe
            cursor.execute("SELECT id FROM patients WHERE id = %s", (data['patient_id'],))
            if not cursor.fetchone():
                return jsonify(status="error", message="Patient non trouvé pour lier l'étude."), 404

            sql = "INSERT INTO studies (patient_id, study_date, study_description, modality) VALUES (%s, NOW(), %s, %s)"
            cursor.execute(sql, (data['patient_id'], data['study_description'], data['modality']))
        db.commit()
        return jsonify(status="success", message="Étude créée avec succès.", study_id=cursor.lastrowid), 201
    except pymysql.MySQLError as e:
        db.rollback()
        return jsonify(status="error", message=f"Erreur lors de la création de l'étude: {e}"), 500

@api_bp.route('/studies/<int:study_id>', methods=['PUT'])
@login_required
@role_required('modification')
def update_study(study_id):
    """
    Mettre à jour une étude.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Données manquantes pour la mise à jour."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
             # Vérifier si l'étude existe
            cursor.execute("SELECT * FROM studies WHERE id = %s", (study_id,))
            if not cursor.fetchone():
                return jsonify(status="error", message="Étude non trouvée."), 404

            fields = []
            params = []
            for key, value in data.items():
                if key in ['study_description', 'modality']:
                    fields.append(f"{key} = %s")
                    params.append(value)

            if not fields:
                return jsonify(status="error", message="Aucun champ valide à mettre à jour."), 400

            sql = f"UPDATE studies SET {', '.join(fields)} WHERE id = %s"
            params.append(study_id)
            cursor.execute(sql, tuple(params))
        db.commit()
        return jsonify(status="success", message="Étude mise à jour avec succès.")
    except pymysql.MySQLError as e:
        db.rollback()
        return jsonify(status="error", message=f"Erreur lors de la mise à jour de l'étude: {e}"), 500

# --- Routes API pour les Utilisateurs (Admin) ---

@api_bp.route('/users', methods=['GET'])
@login_required
@role_required('admin')
def get_users():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT u.id, u.username, r.name as role, u.is_active FROM users u JOIN roles r ON u.role_id = r.id")
        users = cursor.fetchall()
    return jsonify(users)

@api_bp.route('/users', methods=['POST'])
@login_required
@role_required('admin')
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role_id = data.get('role_id')

    if not all([username, password, role_id]):
        return jsonify(status="error", message="Données manquantes."), 400

    password_hash = generate_password_hash(password)
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, password_hash, role_id) VALUES (%s, %s, %s)",
                       (username, password_hash, role_id))
    db.commit()
    return jsonify(status="success", message="Utilisateur créé."), 201

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_user(user_id):
    data = request.get_json()
    role_id = data.get('role_id')
    is_active = data.get('is_active')

    db = get_db()
    with db.cursor() as cursor:
        if role_id is not None:
            cursor.execute("UPDATE users SET role_id = %s WHERE id = %s", (role_id, user_id))
        if is_active is not None:
            cursor.execute("UPDATE users SET is_active = %s WHERE id = %s", (is_active, user_id))
    db.commit()
    return jsonify(status="success", message="Utilisateur mis à jour.")

# --- Route de Recherche ---

@api_bp.route('/search', methods=['GET'])
@login_required
def search():
    """
    Recherche multi-champs sur les patients et les études.
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify(status="error", message="Le paramètre de recherche 'q' est manquant."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Recherche combinée avec JOIN
            sql = """
                SELECT
                    p.id as patient_id, p.lastname, p.firstname, p.birthdate, p.gender,
                    s.id as study_id, s.study_date, s.study_description, s.modality
                FROM patients p
                LEFT JOIN studies s ON p.id = s.patient_id
                WHERE
                    p.lastname LIKE %s OR
                    p.firstname LIKE %s OR
                    s.study_description LIKE %s OR
                    s.modality LIKE %s
            """
            search_term = f"%{query}%"
            cursor.execute(sql, (search_term, search_term, search_term, search_term))
            results = cursor.fetchall()
        return jsonify(results)
    except pymysql.MySQLError as e:
        return jsonify(status="error", message=f"Erreur lors de la recherche: {e}"), 500
