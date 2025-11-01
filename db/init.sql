-- Création de la table 'patients'
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lastname VARCHAR(100) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    birthdate DATE,
    gender ENUM('M', 'F', 'O') -- M: Male, F: Female, O: Other
);

-- Création de la table 'studies'
CREATE TABLE IF NOT EXISTS studies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    study_date DATETIME,
    study_description VARCHAR(255),
    modality VARCHAR(50),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- Insertion de quelques données de test (optionnel mais recommandé)
INSERT INTO patients (lastname, firstname, birthdate, gender) VALUES
('Dupont', 'Jean', '1985-05-20', 'M'),
('Durand', 'Marie', '1992-11-12', 'F');

INSERT INTO studies (patient_id, study_date, study_description, modality) VALUES
(1, NOW(), 'Examen du genou', 'IRM'),
(2, NOW(), 'Radio du thorax', 'RX');

-- Création de la table 'roles'
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Insertion des rôles
INSERT INTO roles (name) VALUES ('admin'), ('modification'), ('lecture');

-- Création de la table 'users'
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Insertion de l'utilisateur admin par défaut
-- Le mot de passe pour 'admin' est 'admin'
INSERT INTO users (username, password_hash, role_id) VALUES
('admin', 'scrypt:32768:8:1$sSMsEIlm7HfdvgNm$1a21bd7c80d7d62f34986f1c408e0ff2c5e1cc040cb3b3da9fcca00e1b441c0124ec8fc9858774ea82f6714064caa4da0b33cca037b7642796e5caeb42b4c493', 1);
           