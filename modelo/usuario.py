"""
Modelo de Usuario
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from config.database import Base
import enum
from datetime import datetime

class RolUsuario(enum.Enum):
    """Enumeración para roles de usuario"""
    ADMINISTRADOR = "administrador"
    OPERARIO = "operario"

class Usuario(Base):
    """
    Modelo para la gestión de usuarios del sistema
    """
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.OPERARIO)
    fecha_registro = Column(DateTime, default=func.current_timestamp())
    ultimo_acceso = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)
    token_recuperacion = Column(String(255), nullable=True)
    token_expiracion = Column(DateTime, nullable=True)
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime, nullable=True)
    
    # Relaciones
    movimientos = relationship("MovimientoInventario", back_populates="usuario", cascade="all, delete-orphan")
    sesiones = relationship("SesionUsuario", back_populates="usuario", cascade="all, delete-orphan")
    alertas_asignadas = relationship("AlertaStock", foreign_keys="AlertaStock.id_usuario_responsable")
    
    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, email='{self.email}', rol='{self.rol}')>"
    
    def esta_bloqueado(self):
        """Verifica si el usuario está bloqueado"""
        if self.bloqueado_hasta:
            return datetime.now() < self.bloqueado_hasta
        return False
    
    def puede_acceder(self):
        """Verifica si el usuario puede acceder al sistema"""
        return self.activo and not self.esta_bloqueado()
    
    def aumentar_intentos_fallidos(self):
        """Aumenta el contador de intentos fallidos"""
        self.intentos_fallidos += 1
        
        # Bloquear después de 5 intentos fallidos
        if self.intentos_fallidos >= 5:
            from datetime import timedelta
            self.bloqueado_hasta = datetime.now() + timedelta(minutes=30)
    
    def reiniciar_intentos_fallidos(self):
        """Reinicia el contador de intentos fallidos"""
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.ultimo_acceso = datetime.now()
    
    def cambiar_password(self, password_actual, password_nuevo, verificar_password):
        """
        Cambia la contraseña del usuario
        """
        from controlador.auth import verify_password, hash_password
        
        if not verify_password(password_actual, self.password_hash):
            return False, "La contraseña actual es incorrecta"
        
        if password_nuevo != verificar_password:
            return False, "Las contraseñas nuevas no coinciden"
        
        self.password_hash = hash_password(password_nuevo)
        return True, "Contraseña cambiada exitosamente"
    
    def generar_token_recuperacion(self):
        """Genera un token para recuperación de contraseña"""
        import secrets
        self.token_recuperacion = secrets.token_urlsafe(32)
        from datetime import timedelta
        self.token_expiracion = datetime.now() + timedelta(hours=24)
        return self.token_recuperacion
    
    def es_administrador(self):
        """Verifica si el usuario es administrador"""
        return self.rol == RolUsuario.ADMINISTRADOR
    
    def puede_crear_usuarios(self):
        """Verifica si el usuario puede crear otros usuarios"""
        return self.es_administrador()
    
    def puede_gestionar_productos(self):
        """Verifica si el usuario puede gestionar productos"""
        return self.es_administrador()
    
    def puede_ver_reportes(self):
        """Verifica si el usuario puede ver reportes"""
        return self.es_administrador()

# Import necesario para evitar circular imports
from sqlalchemy.orm import relationship
from modelo.movimiento_inventario import MovimientoInventario
from modelo.sesion_usuario import SesionUsuario
from modelo.alerta_stock import AlertaStock
