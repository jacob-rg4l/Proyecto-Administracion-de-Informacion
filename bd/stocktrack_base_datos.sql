-- ===============================================
-- SISTEMA DE GESTIÓN DE INVENTARIOS - STOCKTRACK
-- Base de Datos MySQL
-- Autor: MiniMax Agent
-- Fecha: 2025-11-11
-- ===============================================

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS stocktrack_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE stocktrack_db;

-- ===============================================
-- TABLA: usuarios
-- Descripción: Gestiona los usuarios del sistema (administradores y operarios)
-- ===============================================
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    rol ENUM('administrador', 'operario') NOT NULL DEFAULT 'operario',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE,
    token_recuperacion VARCHAR(255) NULL,
    token_expiracion TIMESTAMP NULL,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_rol (rol),
    INDEX idx_activo (activo)
);

-- ===============================================
-- TABLA: categorias
-- Descripción: Categorías de productos
-- ===============================================
CREATE TABLE categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre_categoria VARCHAR(255) NOT NULL,
    descripcion TEXT,
    color_hex VARCHAR(7) DEFAULT '#007bff',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE,
    UNIQUE KEY unique_categoria (nombre_categoria),
    INDEX idx_activa (activa)
);

-- ===============================================
-- TABLA: proveedores
-- Descripción: Proveedores de los productos
-- ===============================================
CREATE TABLE proveedores (
    id_proveedor INT PRIMARY KEY AUTO_INCREMENT,
    nombre_proveedor VARCHAR(255) NOT NULL,
    contacto VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(255),
    direccion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_proveedor (nombre_proveedor),
    INDEX idx_activo (activo)
);

-- ===============================================
-- TABLA: productos
-- Descripción: Productos del inventario
-- ===============================================
CREATE TABLE productos (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    codigo_producto VARCHAR(100) UNIQUE NOT NULL,
    nombre_producto VARCHAR(255) NOT NULL,
    descripcion TEXT,
    id_categoria INT NOT NULL,
    id_proveedor INT NOT NULL,
    precio_compra DECIMAL(10,2) DEFAULT 0.00,
    precio_venta DECIMAL(10,2) DEFAULT 0.00,
    stock_minimo INT DEFAULT 5,
    stock_actual INT DEFAULT 0,
    ubicacion_almacen VARCHAR(255),
    unidad_medida VARCHAR(50) DEFAULT 'unidad',
    peso DECIMAL(8,3) NULL,
    dimensiones VARCHAR(100) NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    qr_code TEXT,
    qr_data_url TEXT,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
    INDEX idx_codigo (codigo_producto),
    INDEX idx_nombre (nombre_producto),
    INDEX idx_categoria (id_categoria),
    INDEX idx_proveedor (id_proveedor),
    INDEX idx_stock_minimo (stock_minimo),
    INDEX idx_activo (activo)
);

-- ===============================================
-- TABLA: movimientos_inventario
-- Descripción: Registra todos los movimientos de inventario
-- ===============================================
CREATE TABLE movimientos_inventario (
    id_movimiento INT PRIMARY KEY AUTO_INCREMENT,
    id_producto INT NOT NULL,
    id_usuario INT NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste', 'devolucion', 'perdida') NOT NULL,
    cantidad INT NOT NULL,
    cantidad_anterior INT NOT NULL,
    cantidad_nueva INT NOT NULL,
    motivo TEXT,
    costo_unitario DECIMAL(10,2) DEFAULT 0.00,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ubicacion_origen VARCHAR(255),
    ubicacion_destino VARCHAR(255),
    referencia_externa VARCHAR(255), -- Para facturas, guías de remisión, etc.
    observaciones TEXT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    INDEX idx_producto (id_producto),
    INDEX idx_usuario (id_usuario),
    INDEX idx_tipo (tipo_movimiento),
    INDEX idx_fecha (fecha_movimiento)
);

-- ===============================================
-- TABLA: alertas_stock
-- Descripción: Alertas de stock mínimo
-- ===============================================
CREATE TABLE alertas_stock (
    id_alerta INT PRIMARY KEY AUTO_INCREMENT,
    id_producto INT NOT NULL,
    tipo_alerta ENUM('stock_minimo', 'agotamiento', 'exceso') NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP NULL,
    resuelta BOOLEAN DEFAULT FALSE,
    prioridad ENUM('baja', 'media', 'alta', 'critica') DEFAULT 'media',
    id_usuario_responsable INT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_usuario_responsable) REFERENCES usuarios(id_usuario),
    INDEX idx_producto (id_producto),
    INDEX idx_resuelta (resuelta),
    INDEX idx_prioridad (prioridad),
    INDEX idx_fecha (fecha_creacion)
);

-- ===============================================
-- TABLA: configuraciones
-- Descripción: Configuraciones del sistema
-- ===============================================
CREATE TABLE configuraciones (
    id_config INT PRIMARY KEY AUTO_INCREMENT,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descripcion TEXT,
    tipo ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modificado_por INT NULL,
    FOREIGN KEY (modificado_por) REFERENCES usuarios(id_usuario)
);

-- ===============================================
-- TABLA: sesiones_usuario
-- Descripción: Gestiona las sesiones activas de los usuarios
-- ===============================================
CREATE TABLE sesiones_usuario (
    id_sesion VARCHAR(128) PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    activa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    INDEX idx_usuario (id_usuario),
    INDEX idx_expiracion (fecha_expiracion),
    INDEX idx_activa (activa)
);

-- ===============================================
-- DATOS INICIALES
-- ===============================================

-- Insertar categorías por defecto
INSERT INTO categorias (nombre_categoria, descripcion, color_hex) VALUES
('Electrónicos', 'Productos electrónicos y tecnológicos', '#6f42c1'),
('Ropa y Textiles', 'Prendas de vestir y productos textiles', '#fd7e14'),
('Hogar y Jardín', 'Artículos para el hogar y jardín', '#20c997'),
('Deportes', 'Artículos deportivos y recreativos', '#6c757d'),
('Alimentos', 'Productos alimenticios', '#28a745'),
('Limpieza', 'Productos de limpieza e higiene', '#17a2b8'),
('Oficina', 'Artículos de oficina y papelería', '#dc3545');

-- Insertar proveedores por defecto
INSERT INTO proveedores (nombre_proveedor, contacto, telefono, email) VALUES
('Distribuidora Nacional S.A.', 'Juan Pérez', '01-234-5678', 'contacto@distribuidoranacional.com'),
('Proveeduría Central', 'María González', '01-345-6789', 'ventas@proveedurcentral.com'),
('Importadora Global', 'Carlos Rodríguez', '01-456-7890', 'info@importadoraglobal.com'),
('Comercial Local', 'Ana Martínez', '01-567-8901', 'comercial@comercallocall.com');

-- Insertar usuario administrador por defecto
-- Password: admin123 (se debe cambiar en producción)
INSERT INTO usuarios (email, password_hash, nombre_completo, rol) VALUES
('admin@stocktrack.com', '$2b$12$LQv3c1yqBwlkLUNg1VPQweOCjNgI0ZJHJ8XG0K8d0zFnG8v8vD8m2', 'Administrador del Sistema', 'administrador');

-- Insertar configuraciones iniciales
INSERT INTO configuraciones (clave, valor, descripcion) VALUES
('empresa_nombre', 'StockTrack', 'Nombre de la empresa'),
('empresa_direccion', 'Dirección de la empresa', 'Dirección de la empresa'),
('empresa_telefono', '01-234-5678', 'Teléfono de la empresa'),
('empresa_email', 'info@stocktrack.com', 'Email de la empresa'),
('alerta_stock_minimo', 'true', 'Activar alertas de stock mínimo'),
('notificaciones_email', 'true', 'Activar notificaciones por email'),
('backup_automatico', 'true', 'Activar backup automático'),
('idioma_sistema', 'es', 'Idioma del sistema'),
('formato_fecha', 'dd/mm/yyyy', 'Formato de fecha'),
('zona_horaria', 'America/Lima', 'Zona horaria del sistema'),
('qr_base_url', 'https://stocktrack.app', 'URL base para códigos QR');

-- ===============================================
-- VISTAS ÚTILES
-- ===============================================

-- Vista: productos_con_detalles
CREATE VIEW productos_con_detalles AS
SELECT 
    p.id_producto,
    p.codigo_producto,
    p.nombre_producto,
    p.descripcion,
    c.nombre_categoria,
    pr.nombre_proveedor,
    p.precio_compra,
    p.precio_venta,
    p.stock_minimo,
    p.stock_actual,
    p.ubicacion_almacen,
    p.unidad_medida,
    p.fecha_creacion,
    p.qr_code,
    CASE 
        WHEN p.stock_actual <= p.stock_minimo THEN 'crítico'
        WHEN p.stock_actual <= p.stock_minimo * 1.5 THEN 'bajo'
        ELSE 'normal'
    END as estado_stock
FROM productos p
JOIN categorias c ON p.id_categoria = c.id_categoria
JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
WHERE p.activo = TRUE;

-- Vista: movimientos_resumidos
CREATE VIEW movimientos_resumidos AS
SELECT 
    m.id_movimiento,
    p.nombre_producto,
    p.codigo_producto,
    u.nombre_completo as usuario,
    m.tipo_movimiento,
    m.cantidad,
    m.fecha_movimiento,
    m.motivo
FROM movimientos_inventario m
JOIN productos p ON m.id_producto = p.id_producto
JOIN usuarios u ON m.id_usuario = u.id_usuario
ORDER BY m.fecha_movimiento DESC;

-- Vista: alertas_activas
CREATE VIEW alertas_activas AS
SELECT 
    a.id_alerta,
    p.nombre_producto,
    p.codigo_producto,
    a.tipo_alerta,
    a.mensaje,
    a.fecha_creacion,
    a.prioridad,
    u.nombre_completo as responsable,
    a.estado_stock
FROM alertas_stock a
JOIN productos p ON a.id_producto = p.id_producto
LEFT JOIN usuarios u ON a.id_usuario_responsable = u.id_usuario
WHERE a.resuelta = FALSE
ORDER BY a.prioridad DESC, a.fecha_creacion DESC;

-- ===============================================
-- PROCEDIMIENTOS ALMACENADOS
-- ===============================================

DELIMITER //

-- Procedimiento: Registrar movimiento de inventario
CREATE PROCEDURE sp_registrar_movimiento(
    IN p_id_producto INT,
    IN p_id_usuario INT,
    IN p_tipo_movimiento ENUM('entrada', 'salida', 'ajuste', 'devolucion', 'perdida'),
    IN p_cantidad INT,
    IN p_motivo TEXT,
    IN p_costo_unitario DECIMAL(10,2)
)
BEGIN
    DECLARE v_stock_anterior INT;
    DECLARE v_stock_nuevo INT;
    DECLARE v_error_msg VARCHAR(255);
    
    -- Iniciar transacción
    START TRANSACTION;
    
    -- Obtener stock actual
    SELECT stock_actual INTO v_stock_anterior 
    FROM productos 
    WHERE id_producto = p_id_producto AND activo = TRUE;
    
    -- Verificar si el producto existe
    IF v_stock_anterior IS NULL THEN
        SET v_error_msg = 'Producto no encontrado';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_msg;
    END IF;
    
    -- Calcular nuevo stock según el tipo de movimiento
    CASE p_tipo_movimiento
        WHEN 'entrada' THEN
            SET v_stock_nuevo = v_stock_anterior + p_cantidad;
        WHEN 'salida' THEN
            IF v_stock_anterior < p_cantidad THEN
                SET v_error_msg = 'Stock insuficiente';
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_msg;
            END IF;
            SET v_stock_nuevo = v_stock_anterior - p_cantidad;
        WHEN 'ajuste' THEN
            SET v_stock_nuevo = p_cantidad;
        WHEN 'devolucion' THEN
            SET v_stock_nuevo = v_stock_anterior + p_cantidad;
        WHEN 'perdida' THEN
            IF v_stock_anterior < p_cantidad THEN
                SET v_error_msg = 'Stock insuficiente para registrar pérdida';
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_msg;
            END IF;
            SET v_stock_nuevo = v_stock_anterior - p_cantidad;
    END CASE;
    
    -- Actualizar stock del producto
    UPDATE productos 
    SET stock_actual = v_stock_nuevo,
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id_producto = p_id_producto;
    
    -- Registrar el movimiento
    INSERT INTO movimientos_inventario (
        id_producto, id_usuario, tipo_movimiento, cantidad,
        cantidad_anterior, cantidad_nueva, motivo, costo_unitario
    ) VALUES (
        p_id_producto, p_id_usuario, p_tipo_movimiento, p_cantidad,
        v_stock_anterior, v_stock_nuevo, p_motivo, p_costo_unitario
    );
    
    -- Verificar alertas de stock mínimo
    IF v_stock_nuevo <= (SELECT stock_minimo FROM productos WHERE id_producto = p_id_producto) THEN
        INSERT INTO alertas_stock (id_producto, tipo_alerta, mensaje, prioridad)
        SELECT 
            p_id_producto,
            'stock_minimo',
            CONCAT('El producto ', (SELECT nombre_producto FROM productos WHERE id_producto = p_id_producto), 
                   ' ha alcanzado su stock mínimo'),
            'alta'
        WHERE NOT EXISTS (
            SELECT 1 FROM alertas_stock 
            WHERE id_producto = p_id_producto 
            AND tipo_alerta = 'stock_minimo' 
            AND resuelta = FALSE
        );
    END IF;
    
    COMMIT;
END //

-- Procedimiento: Obtener productos con stock bajo
CREATE PROCEDURE sp_productos_stock_bajo()
BEGIN
    SELECT 
        id_producto,
        codigo_producto,
        nombre_producto,
        stock_actual,
        stock_minimo,
        ubicacion_almacen,
        (stock_minimo - stock_actual) as cantidad_faltante
    FROM productos 
    WHERE stock_actual <= stock_minimo 
    AND activo = TRUE
    ORDER BY (stock_actual - stock_minimo) ASC;
END //

-- Procedimiento: Generar reporte de inventario
CREATE PROCEDURE sp_reporte_inventario(
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    IN p_id_categoria INT
)
BEGIN
    SELECT 
        p.codigo_producto,
        p.nombre_producto,
        c.nombre_categoria,
        pr.nombre_proveedor,
        p.stock_inicial,
        p.stock_actual,
        SUM(CASE WHEN m.tipo_movimiento = 'entrada' THEN m.cantidad ELSE 0 END) as total_entradas,
        SUM(CASE WHEN m.tipo_movimiento = 'salida' THEN m.cantidad ELSE 0 END) as total_salidas,
        p.precio_compra,
        p.precio_venta,
        (p.stock_actual * p.precio_compra) as valor_inventario
    FROM productos p
    JOIN categorias c ON p.id_categoria = c.id_categoria
    JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
    LEFT JOIN movimientos_inventario m ON p.id_producto = m.id_producto 
        AND m.fecha_movimiento BETWEEN p_fecha_inicio AND p_fecha_fin
    WHERE (p_id_categoria IS NULL OR p.id_categoria = p_id_categoria)
    AND p.activo = TRUE
    GROUP BY p.id_producto
    ORDER BY p.nombre_producto;
END //

DELIMITER ;

-- ===============================================
-- TRIGGERS
-- ===============================================

DELIMITER //

-- Trigger: Verificar stock mínimo después de actualización
CREATE TRIGGER tr_verificar_stock_minimo
AFTER UPDATE ON productos
FOR EACH ROW
BEGIN
    IF NEW.stock_actual <= NEW.stock_minimo AND OLD.stock_actual > OLD.stock_minimo THEN
        INSERT INTO alertas_stock (id_producto, tipo_alerta, mensaje, prioridad)
        SELECT 
            NEW.id_producto,
            'stock_minimo',
            CONCAT('El producto ', NEW.nombre_producto, ' ha alcanzado su stock mínimo'),
            'alta'
        WHERE NOT EXISTS (
            SELECT 1 FROM alertas_stock 
            WHERE id_producto = NEW.id_producto 
            AND tipo_alerta = 'stock_minimo' 
            AND resuelta = FALSE
        );
    END IF;
END //

DELIMITER ;

-- ===============================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ===============================================

-- Índices para mejorar el rendimiento de consultas frecuentes
CREATE INDEX idx_productos_stock_bajo ON productos(stock_actual, stock_minimo, activo);
CREATE INDEX idx_movimientos_fecha_producto ON movimientos_inventario(fecha_movimiento, id_producto);
CREATE INDEX idx_alertas_sin_resolver ON alertas_stock(resuelta, prioridad, fecha_creacion);

-- ===============================================
-- COMENTARIOS FINALES
-- ===============================================

/* 
CONFIGURACIÓN COMPLETADA:
- Base de datos 'stocktrack_db' creada
- 8 tablas principales definidas con relaciones
- 3 vistas útiles para consultas complejas
- 3 procedimientos almacenados para operaciones comunes
- 1 trigger para alertas automáticas
- Datos iniciales insertados
- Índices optimizados para rendimiento

PRÓXIMOS PASOS:
1. Ejecutar este script en MySQL
2. Configurar la conexión en config/database.py
3. Configurar PHPMyAdmin para gestionar la base de datos
4. Iniciar el servidor FastAPI
5. Acceder al sistema desde el navegador
*/