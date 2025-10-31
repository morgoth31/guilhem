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
