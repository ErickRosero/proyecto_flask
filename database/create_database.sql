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

-- Usar la base de datos
USE desarrollo_web;

-- Crear la tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL
);

-- Mostrar la estructura de la tabla
DESCRIBE productos;

-- Insertar algunos productos de ejemplo (opcional)
INSERT INTO productos (nombre, precio, stock) VALUES 
('Laptop HP', 899.99, 10),
('Mouse Inalámbrico', 25.50, 30),
('Teclado Mecánico', 75.00, 15),
('Monitor 24"', 189.99, 8),
('Disco SSD 1TB', 129.99, 20);

-- Mostrar los productos insertados
SELECT * FROM productos;