-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS desarrollo_web;

-- Usar la base de datos
USE desarrollo_web;

-- Crear la tabla de usuarios con soporte para autenticación
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);