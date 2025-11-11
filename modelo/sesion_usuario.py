"""
Modelo de Sesión de Usuario
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship
import secrets
import hashlib
from datetime import datetime, timedelta

class SesionUsuario(Base):
    """
    Modelo para la gestión de sesiones de usuario
    """
    __tablename__ = "sesiones_usuario"
    
    id_sesion = Column(String(128), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_creacion = Column(DateTime, default=func.current_timestamp())
    fecha_expiracion = Column(DateTime, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    activa = Column(Boolean, default=True, index=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones")
    
    def __repr__(self):
        return f"<SesionUsuario(id='{self.id_sesion[:8]}...', usuario={self.usuario.email if self.usuario else 'N/A'})>"
    
    @staticmethod
    def generar_id_sesion():
        """Genera un ID único para la sesión"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def crear_sesion(usuario_id, ip_address=None, user_agent=None, duracion_horas=24):
        """
        Crea una nueva sesión para un usuario
        """
        sesion = SesionUsuario(
            id_sesion=SesionUsuario.generar_id_sesion(),
            id_usuario=usuario_id,
            fecha_expiracion=datetime.now() + timedelta(hours=duracion_horas),
            ip_address=ip_address,
            user_agent=user_agent
        )
        return sesion
    
    def esta_expirada(self):
        """Verifica si la sesión ha expirado"""
        return datetime.now() > self.fecha_expiracion
    
    def es_valida(self):
        """Verifica si la sesión es válida (activa y no expirada)"""
        return self.activa and not self.esta_expirada()
    
    def renovar_sesion(self, duracion_horas=24):
        """Renueva la sesión extendiendo su tiempo de expiración"""
        if self.es_valida():
            self.fecha_expiracion = datetime.now() + timedelta(hours=duracion_horas)
            return True
        return False
    
    def terminar_sesion(self):
        """Termina la sesión (la marca como inactiva)"""
        self.activa = False
    
    def obtener_duracion_total(self):
        """Obtiene la duración total de la sesión en horas"""
        duracion = self.fecha_expiracion - self.fecha_creacion
        return duracion.total_seconds() / 3600
    
    def obtener_tiempo_restante(self):
        """Obtiene el tiempo restante de la sesión en horas"""
        if self.esta_expirada():
            return 0
        tiempo_restante = self.fecha_expiracion - datetime.now()
        return tiempo_restante.total_seconds() / 3600
    
    def obtener_ubicacion_origen(self):
        """Intenta obtener información de ubicación basada en IP (implementación básica)"""
        # Esta es una implementación básica. En producción, usar un servicio como MaxMind
        if self.ip_address:
            if self.ip_address.startswith('192.168.') or self.ip_address.startswith('10.') or self.ip_address.startswith('172.'):
                return "Red Local"
            elif self.ip_address.startswith('127.'):
                return "Localhost"
            else:
                return "Red Externa"
        return "Desconocida"
    
    def verificar_dispositivo(self, user_agent_actual):
        """Verifica si el dispositivo (user agent) ha cambiado"""
        if not self.user_agent or not user_agent_actual:
            return True  # No podemos verificar, asumimos que es válido
        
        # Comparación básica del user agent
        return self.user_agent == user_agent_actual
    
    def obtener_info_dispositivo(self):
        """Analiza el user agent para obtener información del dispositivo"""
        if not self.user_agent:
            return "Desconocido"
        
        info = {
            "tipo": "Desconocido",
            "navegador": "Desconocido",
            "sistema_operativo": "Desconocido"
        }
        
        user_agent_lower = self.user_agent.lower()
        
        # Detectar tipo de dispositivo
        if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
            info["tipo"] = "Móvil"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            info["tipo"] = "Tablet"
        else:
            info["tipo"] = "Escritorio"
        
        # Detectar navegador
        if "chrome" in user_agent_lower:
            info["navegador"] = "Chrome"
        elif "firefox" in user_agent_lower:
            info["navegador"] = "Firefox"
        elif "safari" in user_agent_lower and "chrome" not in user_agent_lower:
            info["navegador"] = "Safari"
        elif "edge" in user_agent_lower:
            info["navegador"] = "Edge"
        elif "opera" in user_agent_lower:
            info["navegador"] = "Opera"
        
        # Detectar sistema operativo
        if "windows" in user_agent_lower:
            info["sistema_operativo"] = "Windows"
        elif "mac" in user_agent_lower:
            info["sistema_operativo"] = "macOS"
        elif "linux" in user_agent_lower:
            info["sistema_operativo"] = "Linux"
        elif "android" in user_agent_lower:
            info["sistema_operativo"] = "Android"
        elif "ios" in user_agent_lower or "iphone" in user_agent_lower or "ipad" in user_agent_lower:
            info["sistema_operativo"] = "iOS"
        
        return f"{info['tipo']} - {info['navegador']} - {info['sistema_operativo']}"
    
    def generar_token_csrf(self):
        """Genera un token CSRF para la sesión"""
        import secrets
        token = secrets.token_urlsafe(32)
        # En una implementación completa, almacenarías este token en la base de datos
        return token
    
    def es_sesion_sospechosa(self, ip_actual, user_agent_actual):
        """
        Determina si la sesión puede ser sospechosa (cambios de IP o dispositivo)
        """
        razones = []
        
        # Verificar cambio de IP
        if self.ip_address and ip_actual and self.ip_address != ip_actual:
            # Permitir cambios dentro de la misma red
            if not (self.ip_address.startswith('192.168.') and ip_actual.startswith('192.168.')):
                razones.append("Cambio de IP detected")
        
        # Verificar cambio de dispositivo
        if not self.verificar_dispositivo(user_agent_actual):
            razones.append("Cambio de dispositivo detectado")
        
        return len(razones) > 0, razones

# Import necesario para evitar circular imports
from modelo.usuario import Usuario
