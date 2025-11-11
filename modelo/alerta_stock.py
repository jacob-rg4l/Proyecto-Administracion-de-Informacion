"""
Modelo de Alerta de Stock
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship
import enum

class TipoAlerta(enum.Enum):
    """Enumeración para tipos de alerta"""
    STOCK_MINIMO = "stock_minimo"
    AGOTAMIENTO = "agotamiento"
    EXCESO = "exceso"

class PrioridadAlerta(enum.Enum):
    """Enumeración para prioridades de alerta"""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class AlertaStock(Base):
    """
    Modelo para la gestión de alertas de stock
    """
    __tablename__ = "alertas_stock"
    
    id_alerta = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    tipo_alerta = Column(Enum(TipoAlerta), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime, default=func.current_timestamp())
    fecha_resolucion = Column(DateTime, nullable=True)
    resuelta = Column(Boolean, default=False, index=True)
    prioridad = Column(Enum(PrioridadAlerta), default=PrioridadAlerta.MEDIA)
    id_usuario_responsable = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    
    # Relaciones
    producto = relationship("Producto", back_populates="alertas")
    usuario_responsable = relationship("Usuario", foreign_keys=[id_usuario_responsable])
    
    def __repr__(self):
        return f"<AlertaStock(id={self.id_alerta}, producto={self.producto.nombre_producto if self.producto else 'N/A'}, tipo='{self.tipo_alerta}')>"
    
    def obtener_descripcion_completa(self):
        """Obtiene una descripción completa de la alerta"""
        if self.producto:
            return f"{self.tipo_alerta.replace('_', ' ').title()}: {self.producto.nombre_producto} - {self.mensaje}"
        return f"{self.tipo_alerta.replace('_', ' ').title()}: {self.mensaje}"
    
    def obtener_tiempo_transcurrido(self):
        """Obtiene el tiempo transcurrido desde la creación de la alerta"""
        from datetime import datetime
        return datetime.now() - self.fecha_creacion
    
    def obtener_tiempo_transcurrido_texto(self):
        """Obtiene el tiempo transcurrido en formato de texto legible"""
        tiempo = self.obtener_tiempo_transcurrido()
        segundos = int(tiempo.total_seconds())
        
        if segundos < 60:
            return f"{segundos} segundos"
        elif segundos < 3600:
            minutos = segundos // 60
            return f"{minutos} minutos"
        elif segundos < 86400:
            horas = segundos // 3600
            return f"{horas} horas"
        else:
            dias = segundos // 86400
            return f"{dias} días"
    
    def es_critica(self):
        """Verifica si la alerta es crítica"""
        return self.prioridad == PrioridadAlerta.CRITICA
    
    def es_alta_prioridad(self):
        """Verifica si la alerta es de alta prioridad"""
        return self.prioridad in [PrioridadAlerta.ALTA, PrioridadAlerta.CRITICA]
    
    def esta_vencida(self):
        """Verifica si la alerta está vencida (más de 7 días sin resolver)"""
        from datetime import datetime, timedelta
        return datetime.now() - self.fecha_creacion > timedelta(days=7)
    
    def asignar_responsable(self, usuario_id):
        """Asigna un responsable a la alerta"""
        self.id_usuario_responsable = usuario_id
    
    def resolver(self, usuario_id=None, comentario=""):
        """
        Marca la alerta como resuelta
        """
        self.resuelta = True
        self.fecha_resolucion = func.current_timestamp()
        if usuario_id:
            self.id_usuario_responsable = usuario_id
        if comentario:
            self.mensaje += f"\n[RESUELTO] {comentario}"
    
    def reabrir(self, motivo=""):
        """
        Reabre una alerta previamente resuelta
        """
        self.resuelta = False
        self.fecha_resolucion = None
        if motivo:
            self.mensaje += f"\n[REABIERTA] {motivo}"
    
    def obtener_nivel_urgencia(self):
        """Obtiene el nivel de urgencia basado en tiempo transcurrido y prioridad"""
        if self.es_critica():
            return 4
        elif self.es_alta_prioridad():
            return 3
        elif self.esta_vencida():
            return 2
        else:
            return 1
    
    @staticmethod
    def crear_alerta_stock_minimo(producto, usuario_responsable=None):
        """Crea una alerta de stock mínimo para un producto"""
        if producto.stock_actual <= producto.stock_minimo:
            mensaje = f"El producto {producto.nombre_producto} ha alcanzado su stock mínimo. Stock actual: {producto.stock_actual}, Stock mínimo: {producto.stock_minimo}"
            
            # Determinar prioridad
            if producto.stock_actual == 0:
                prioridad = PrioridadAlerta.CRITICA
            elif producto.stock_actual <= producto.stock_minimo // 2:
                prioridad = PrioridadAlerta.ALTA
            else:
                prioridad = PrioridadAlerta.MEDIA
            
            alerta = AlertaStock(
                id_producto=producto.id_producto,
                tipo_alerta=TipoAlerta.STOCK_MINIMO,
                mensaje=mensaje,
                prioridad=prioridad,
                id_usuario_responsable=usuario_responsable.id_usuario if usuario_responsable else None
            )
            
            return alerta
        
        return None
    
    @staticmethod
    def crear_alerta_agotamiento(producto, usuario_responsable=None):
        """Crea una alerta de agotamiento cuando el stock llega a cero"""
        if producto.stock_actual == 0:
            mensaje = f"¡AGOTADO! El producto {producto.nombre_producto} se ha agotado completamente. Se requiere reposición inmediata."
            
            alerta = AlertaStock(
                id_producto=producto.id_producto,
                tipo_alerta=TipoAlerta.AGOTAMIENTO,
                mensaje=mensaje,
                prioridad=PrioridadAlerta.CRITICA,
                id_usuario_responsable=usuario_responsable.id_usuario if usuario_responsable else None
            )
            
            return alerta
        
        return None
    
    @staticmethod
    def crear_alerta_exceso(producto, limite_exceso=1000, usuario_responsable=None):
        """Crea una alerta de exceso de stock"""
        if producto.stock_actual > limite_exceso:
            mensaje = f"Exceso de stock detectado en {producto.nombre_producto}. Stock actual: {producto.stock_actual}, Límite sugerido: {limite_exceso}"
            
            alerta = AlertaStock(
                id_producto=producto.id_producto,
                tipo_alerta=TipoAlerta.EXCESO,
                mensaje=mensaje,
                prioridad=PrioridadAlerta.BAJA,
                id_usuario_responsable=usuario_responsable.id_usuario if usuario_responsable else None
            )
            
            return alerta
        
        return None
    
    def obtener_notificacion_email(self):
        """Genera el contenido para notificación por email"""
        return f"""
        <h3>Alerta de Inventario - StockTrack</h3>
        <p><strong>Tipo de Alerta:</strong> {self.tipo_alerta.replace('_', ' ').title()}</p>
        <p><strong>Producto:</strong> {self.producto.nombre_producto if self.producto else 'N/A'}</p>
        <p><strong>Código:</strong> {self.producto.codigo_producto if self.producto else 'N/A'}</p>
        <p><strong>Prioridad:</strong> {self.prioridad.title()}</p>
        <p><strong>Mensaje:</strong> {self.mensaje}</p>
        <p><strong>Fecha:</strong> {self.fecha_creacion.strftime('%d/%m/%Y %H:%M:%S')}</p>
        <p><strong>Tiempo transcurrido:</strong> {self.obtener_tiempo_transcurrido_texto()}</p>
        
        <p>Acceda al sistema para más detalles: <a href="https://stocktrack.app/alertas">Ver Alertas</a></p>
        """

# Import necesario para evitar circular imports
from modelo.producto import Producto
from modelo.usuario import Usuario
