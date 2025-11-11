"""
Configuración de Base de Datos
Sistema de Gestión de Inventarios StockTrack
Autor: MiniMax Agent
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/stocktrack_db"

# Configuración para desarrollo
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",  # Cambiar en producción
    "database": "stocktrack_db",
    "charset": "utf8mb4"
}

# Motor de base de datos
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

# Sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

def obtener_sesion():
    """
    Obtiene una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def crear_tablas():
    """
    Crea todas las tablas en la base de datos
    """
    Base.metadata.create_all(bind=engine)

def inicializar_base_datos():
    """
    Inicializa la base de datos con datos por defecto
    """
    db = SessionLocal()
    try:
        # Verificar si ya existen datos
        from modelo.usuario import Usuario
        if db.query(Usuario).count() == 0:
            # Crear usuario administrador por defecto
            from controlador.auth import hash_password
            usuario_admin = Usuario(
                email="admin@stocktrack.com",
                password_hash=hash_password("admin123"),
                nombre_completo="Administrador del Sistema",
                rol="administrador"
            )
            db.add(usuario_admin)
            db.commit()
            print("Usuario administrador creado: admin@stocktrack.com / admin123")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        db.close()
