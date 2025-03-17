-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS desarrollo_web;

-- Usar la base de datos
USE desarrollo_web;

-- Crear la tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar algunos datos de prueba
INSERT INTO usuarios (nombre, email) VALUES 
('Juan Pérez', 'juan@ejemplo.com'),
('María García', 'maria@ejemplo.com'),
('Carlos López', 'carlos@ejemplo.com');

-- Mostrar la estructura de la tabla
DESCRIBE usuarios;

-- Mostrar los registros insertados
SELECT * FROM usuarios;