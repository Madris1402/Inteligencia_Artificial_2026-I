DROP DATABASE IF EXISTS horarios;
CREATE DATABASE IF NOT EXISTS horarios;
USE horarios;

-- Profesores
CREATE TABLE profesores (
    id_profesor INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    paterno VARCHAR(100) NOT NULL,
    materno VARCHAR(100) NULL,
    correo VARCHAR(100)
);

-- Salones
CREATE TABLE salones (
    id_salon INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL
);

-- Materias
CREATE TABLE materias (
    id_materia INT PRIMARY KEY AUTO_INCREMENT,
    clave INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    semestre INT NOT NULL
);

-- Grupos
CREATE TABLE grupos (
    id_grupo INT PRIMARY KEY AUTO_INCREMENT,
    id_materia INT NOT NULL,
    id_profesor INT NOT NULL,
    id_salon INT NOT NULL,
    turno ENUM('Matutino', 'Vespertino') NOT NULL,
    grupo INT,
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia),
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
    FOREIGN KEY (id_salon) REFERENCES salones(id_salon)
);

-- Horarios de grupos
CREATE TABLE horarios_grupo (
    id_horario INT PRIMARY KEY AUTO_INCREMENT,
    id_grupo INT NOT NULL,
    dia_semana ENUM('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado') NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo) ON DELETE CASCADE
);