"""
Modelo de Configuración
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship
import json
import enum

class TipoConfiguracion(enum.Enum):
    """Enumeración para tipos de configuración"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"

class Configuracion(Base):
    """
    Modelo para la gestión de configuraciones del sistema
    """
    __tablename__ = "configuraciones"
    
    id_config = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False, index=True)
    valor = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(Enum(TipoConfiguracion), default=TipoConfiguracion.STRING)
    fecha_modificacion = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    modificado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    
    # Relaciones
    usuario_modificador = relationship("Usuario", foreign_keys=[modificado_por])
    
    def __repr__(self):
        return f"<Configuracion(clave='{self.clave}', valor='{self.valor[:50]}...', tipo='{self.tipo}')>"
    
    def obtener_valor_typed(self):
        """Obtiene el valor con el tipo correcto"""
        if self.tipo == TipoConfiguracion.STRING:
            return self.valor
        elif self.tipo == TipoConfiguracion.NUMBER:
            try:
                return float(self.valor)
            except ValueError:
                return 0
        elif self.tipo == TipoConfiguracion.BOOLEAN:
            return self.valor.lower() in ('true', '1', 'yes', 'on')
        elif self.tipo == TipoConfiguracion.JSON:
            try:
                return json.loads(self.valor)
            except json.JSONDecodeError:
                return None
        return self.valor
    
    def establecer_valor(self, valor, usuario_id=None):
        """
        Establece el valor de la configuración
        """
        if self.tipo == TipoConfiguracion.STRING:
            self.valor = str(valor)
        elif self.tipo == TipoConfiguracion.NUMBER:
            self.valor = str(float(valor))
        elif self.tipo == TipoConfiguracion.BOOLEAN:
            self.valor = "true" if valor else "false"
        elif self.tipo == TipoConfiguracion.JSON:
            self.valor = json.dumps(valor, ensure_ascii=False)
        
        self.modificado_por = usuario_id
        self.fecha_modificacion = func.current_timestamp()
    
    @staticmethod
    def obtener_configuracion(db, clave, valor_por_defecto=None):
        """
        Obtiene una configuración específica
        """
        config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
        if config:
            return config.obtener_valor_typed()
        return valor_por_defecto
    
    @staticmethod
    def establecer_configuracion(db, clave, valor, tipo=TipoConfiguracion.STRING, descripcion="", usuario_id=None):
        """
        Establece una configuración específica
        """
        config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
        
        if not config:
            config = Configuracion(
                clave=clave,
                valor="",
                tipo=tipo,
                descripcion=descripcion,
                modificado_por=usuario_id
            )
            db.add(config)
        
        config.establecer_valor(valor, usuario_id)
        db.commit()
        
        return config
    
    @staticmethod
    def obtener_configuraciones_empresa(db):
        """
        Obtiene todas las configuraciones relacionadas con la empresa
        """
        configs = db.query(Configuracion).filter(
            Configuracion.clave.like('empresa_%')
        ).all()
        
        empresa_config = {}
        for config in configs:
            clave_sin_prefijo = config.clave.replace('empresa_', '')
            empresa_config[clave_sin_prefijo] = config.obtener_valor_typed()
        
        return empresa_config
    
    @staticmethod
    def obtener_configuraciones_sistema(db):
        """
        Obtiene todas las configuraciones del sistema
        """
        configs = db.query(Configuracion).filter(
            Configuracion.clave.like('sistema_%')
        ).all()
        
        sistema_config = {}
        for config in configs:
            clave_sin_prefijo = config.clave.replace('sistema_', '')
            sistema_config[clave_sin_prefijo] = config.obtener_valor_typed()
        
        return sistema_config
    
    @staticmethod
    def obtener_configuraciones_notificacion(db):
        """
        Obtiene todas las configuraciones de notificación
        """
        configs = db.query(Configuracion).filter(
            Configuracion.clave.like('notificacion_%')
        ).all()
        
        notificacion_config = {}
        for config in configs:
            clave_sin_prefijo = config.clave.replace('notificacion_', '')
            notificacion_config[clave_sin_prefijo] = config.obtener_valor_typed()
        
        return notificacion_config

# Configuraciones predefinidas del sistema
CONFIGURACIONES_PREDEFINIDAS = {
    # Configuraciones de empresa
    "empresa_nombre": {
        "valor": "StockTrack",
        "tipo": TipoConfiguracion.STRING,
        "descripcion": "Nombre de la empresa"
    },
    "empresa_direccion": {
        "valor": "Dirección de la empresa",
        "tipo": TipoConfiguracion.STRING,
        "descripcion": "Dirección de la empresa"
    },
    "empresa_telefono": {
        "valor": "01-234-5678",
        "tipo": TipoConfiguracion.STRING,
        "descripcion": "Teléfono de la empresa"
    },
    "empresa_email": {
        "valor": "info@stocktrack.com",
        "tipo": TipoConfiguracion.STRING,
        "descripcion": "Email de la empresa"
    },
    
    # Configuraciones del sistema
    "sistema_alerta_stock_minimo": {
        "valor": True,
        "tipo": TipoConfiguracion.BOOLEAN,
        "descripcion": "Activar alertas de stock mínimo"
    },
    "sistema_notificaciones_email": {
        "valor": True,
        "tipo": TipoConfiguracion.BOOLEAN,
        "descripcion": "Activar notificaciones por email"
    },
    "sistema_backup_automatico": {
        "valor": True,
        "tipo": TipoConfiguracion.BOOLEAN,
        "descripcion": "Activar backup automático"
    },
    "sistema_idioma": {
        "valor": "es",
        "tipo": TipoConfiguracion.STRING,
        "descripcion": "Idioma del sistema"
    },
    "sistema_formato_fecha": {
        "valor": "dd/mm/yyyy",
        "tipo": TipoConfiguracion.STRING,
        "descripcion": "Formato de fecha"
    },
    "sistema_zona_horaria": {
        "valor": "America/Lima",
        "tipo": TipoConfiguracion.STRING,
        "descripcion": "Zona horaria del sistema"
    },
    
    # Configuraciones de QR
    "qr_base_url": {
        "valor": "https://stocktrack.app",
        "tipo": TipoConfiguracion.STRING,
        "descripcion": "URL base para códigos QR"
    },
    
    # Configuraciones de inventario
    "inventario_limite_exceso": {
        "valor": 1000,
        "tipo": TipoConfiguracion.NUMBER,
        "descripcion": "Límite para alertas de exceso de stock"
    },
    "inventario_dias_alerta_vencida": {
        "valor": 7,
        "tipo": TipoConfiguracion.NUMBER,
        "descripcion": "Días para considerar una alerta como vencida"
    }
}

# Import necesario para evitar circular imports
from modelo.usuario import Usuario
