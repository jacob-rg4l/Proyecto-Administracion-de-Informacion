
CREATE DATABASE IF NOT EXISTS stocktrack;
USE stocktrack;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(100) NOT NULL,
    contrasena VARCHAR(100) NOT NULL,
    rol ENUM('administrador', 'operario') NOT NULL
);

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    categoria VARCHAR(100),
    proveedor VARCHAR(100),
    cantidad INT,
    ubicacion VARCHAR(100),
    stock_minimo INT
);

CREATE TABLE movimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    tipo ENUM('entrada', 'salida'),
    cantidad INT,
    fecha DATETIME,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);
