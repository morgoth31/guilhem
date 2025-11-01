from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from db import get_db
import pymysql

frontend_bp = Blueprint('frontend', __name__)

# Routes d'authentification
@frontend_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('frontend.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('frontend.dashboard'))
        else:
            flash('Identifiants invalides')
    return render_template('login.html')

@frontend_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.login'))

@frontend_bp.route('/')
@login_required
def dashboard():
    """
    Affiche le tableau de bord principal avec les études et la fonctionnalité de recherche.
    """
    db = get_db()
    search_query = request.args.get('q', '')

    try:
        with db.cursor() as cursor:
            if search_query:
                sql = """
                    SELECT p.id as patient_id, p.firstname, p.lastname, s.id, s.study_date, s.study_description, s.modality
                    FROM studies s
                    JOIN patients p ON s.patient_id = p.id
                    WHERE p.lastname LIKE %s OR p.firstname LIKE %s OR s.study_description LIKE %s OR s.modality LIKE %s
                    ORDER BY s.study_date DESC
                """
                search_term = f"%{search_query}%"
                cursor.execute(sql, (search_term, search_term, search_term, search_term))
            else:
                sql = """
                    SELECT p.id as patient_id, p.firstname, p.lastname, s.id, s.study_date, s.study_description, s.modality
                    FROM studies s
                    JOIN patients p ON s.patient_id = p.id
                    ORDER BY s.study_date DESC
                """
                cursor.execute(sql)
            studies = cursor.fetchall()
    except pymysql.MySQLError as e:
        # Gérer l'erreur
        return f"Erreur lors de la récupération des études: {e}", 500

    return render_template('dashboard.html', studies=studies, search_query=search_query)

@frontend_bp.route('/patient/new', methods=['GET', 'POST'])
@login_required
def new_patient():
    """
    Gère la création d'un nouveau patient.
    """
    if request.method == 'POST':
        db = get_db()
        try:
            with db.cursor() as cursor:
                sql = "INSERT INTO patients (lastname, firstname, birthdate, gender) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (
                    request.form['lastname'],
                    request.form['firstname'],
                    request.form['birthdate'],
                    request.form['gender']
                ))
            db.commit()
        except pymysql.MySQLError as e:
            db.rollback()
            return f"Erreur lors de la création du patient: {e}", 500
        return redirect(url_for('frontend.dashboard'))
    return render_template('patient_form.html')

@frontend_bp.route('/patient/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    """
    Affiche les détails d'un patient et ses études.
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            # Récupérer les infos du patient
            cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
            patient = cursor.fetchone()

            # Récupérer les études du patient
            cursor.execute("SELECT * FROM studies WHERE patient_id = %s ORDER BY study_date DESC", (patient_id,))
            studies = cursor.fetchall()
    except pymysql.MySQLError as e:
        return f"Erreur lors de la récupération du patient: {e}", 500

    if not patient:
        return "Patient non trouvé", 404

    return render_template('patient_detail.html', patient=patient, studies=studies)

@frontend_bp.route('/patient/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """
    Gère l'édition d'un patient.
    """
    db = get_db()
    if request.method == 'POST':
        try:
            with db.cursor() as cursor:
                sql = """
                    UPDATE patients
                    SET lastname=%s, firstname=%s, birthdate=%s, gender=%s
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    request.form['lastname'],
                    request.form['firstname'],
                    request.form['birthdate'],
                    request.form['gender'],
                    patient_id
                ))
            db.commit()
        except pymysql.MySQLError as e:
            db.rollback()
            return f"Erreur lors de la mise à jour du patient: {e}", 500
        return redirect(url_for('frontend.patient_detail', patient_id=patient_id))

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
            patient = cursor.fetchone()
    except pymysql.MySQLError as e:
        return f"Erreur lors de la récupération du patient: {e}", 500

    if not patient:
        return "Patient non trouvé", 404

    return render_template('patient_form.html', patient=patient)

@frontend_bp.route('/study/new', methods=['GET', 'POST'])
@login_required
def new_study():
    """
    Gère la création d'une nouvelle étude.
    """
    db = get_db()
    if request.method == 'POST':
        try:
            with db.cursor() as cursor:
                sql = "INSERT INTO studies (patient_id, study_description, modality, study_date) VALUES (%s, %s, %s, NOW())"
                cursor.execute(sql, (
                    request.form['patient_id'],
                    request.form['study_description'],
                    request.form['modality']
                ))
            db.commit()
        except pymysql.MySQLError as e:
            db.rollback()
            return f"Erreur lors de la création de l'étude: {e}", 500
        return redirect(url_for('frontend.dashboard'))

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id, lastname, firstname FROM patients ORDER BY lastname, firstname")
            patients = cursor.fetchall()
    except pymysql.MySQLError as e:
        return f"Erreur lors de la récupération des patients: {e}", 500

    return render_template('study_form.html', patients=patients)

@frontend_bp.route('/study/edit/<int:study_id>', methods=['GET', 'POST'])
@login_required
def edit_study(study_id):
    """
    Gère l'édition d'une étude.
    """
    db = get_db()
    if request.method == 'POST':
        try:
            with db.cursor() as cursor:
                sql = """
                    UPDATE studies
                    SET study_description=%s, modality=%s
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    request.form['study_description'],
                    request.form['modality'],
                    study_id
                ))
            db.commit()
        except pymysql.MySQLError as e:
            db.rollback()
            return f"Erreur lors de la mise à jour de l'étude: {e}", 500
        return redirect(url_for('frontend.dashboard'))

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM studies WHERE id = %s", (study_id,))
            study = cursor.fetchone()

            cursor.execute("SELECT id, lastname, firstname FROM patients ORDER BY lastname, firstname")
            patients = cursor.fetchall()
    except pymysql.MySQLError as e:
        return f"Erreur lors de la récupération de l'étude: {e}", 500

    if not study:
        return "Étude non trouvée", 404

    return render_template('study_form.html', study=study, patients=patients)

@frontend_bp.route('/study/<int:study_id>')
@login_required
def study_detail(study_id):
    """
    Affiche les détails d'une étude.
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            sql = """
                SELECT s.*, p.lastname as patient_lastname, p.firstname as patient_firstname
                FROM studies s
                JOIN patients p ON s.patient_id = p.id
                WHERE s.id = %s
            """
            cursor.execute(sql, (study_id,))
            study = cursor.fetchone()
    except pymysql.MySQLError as e:
        return f"Erreur lors de la récupération de l'étude: {e}", 500

    if not study:
        return "Étude non trouvée", 404

    return render_template('study_detail.html', study=study)

# --- Route pour l'administration des utilisateurs ---

@frontend_bp.route('/admin/users')
@login_required
def admin_users():
    """
    Affiche la page de gestion des utilisateurs pour les admins.
    """
    if current_user.role != 'admin':
        return "Accès interdit", 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT u.id, u.username, r.name as role_name, u.is_active FROM users u JOIN roles r ON u.role_id = r.id ORDER BY u.username")
            users = cursor.fetchall()
            cursor.execute("SELECT * FROM roles")
            roles = cursor.fetchall()
    except pymysql.MySQLError as e:
        return f"Erreur lors de la récupération des utilisateurs: {e}", 500

    return render_template('admin_users.html', users=users, roles=roles)
