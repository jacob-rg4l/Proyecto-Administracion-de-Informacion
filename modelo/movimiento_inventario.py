"""
Modelo de Movimiento de Inventario
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Decimal, ForeignKey, Enum
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship
import enum

class TipoMovimiento(enum.Enum):
    """Enumeración para tipos de movimiento de inventario"""
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"
    DEVOLUCION = "devolucion"
    PERDIDA = "perdida"

class MovimientoInventario(Base):
    """
    Modelo para el registro de movimientos de inventario
    """
    __tablename__ = "movimientos_inventario"
    
    id_movimiento = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo_movimiento = Column(Enum(TipoMovimiento), nullable=False)
    cantidad = Column(Integer, nullable=False)
    cantidad_anterior = Column(Integer, nullable=False)
    cantidad_nueva = Column(Integer, nullable=False)
    motivo = Column(Text, nullable=True)
    costo_unitario = Column(Decimal(10,2), default=0.00)
    fecha_movimiento = Column(DateTime, default=func.current_timestamp(), index=True)
    ubicacion_origen = Column(String(255), nullable=True)
    ubicacion_destino = Column(String(255), nullable=True)
    referencia_externa = Column(String(255), nullable=True)  # Facturas, guías, etc.
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    producto = relationship("Producto", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")
    
    def __repr__(self):
        return f"<MovimientoInventario(id={self.id_movimiento}, producto={self.producto.nombre_producto if self.producto else 'N/A'}, tipo='{self.tipo_movimiento}')>"
    
    def obtener_descripcion_movimiento(self):
        """Obtiene una descripción legible del movimiento"""
        if self.tipo_movimiento == TipoMovimiento.ENTRADA:
            return f"Entrada de {self.cantidad} {self.producto.unidad_medida if self.producto else 'unidades'}"
        elif self.tipo_movimiento == TipoMovimiento.SALIDA:
            return f"Salida de {self.cantidad} {self.producto.unidad_medida if self.producto else 'unidades'}"
        elif self.tipo_movimiento == TipoMovimiento.AJUSTE:
            return f"Ajuste de stock: {self.cantidad_anterior} → {self.cantidad_nueva}"
        elif self.tipo_movimiento == TipoMovimiento.DEVOLUCION:
            return f"Devolución de {self.cantidad} {self.producto.unidad_medida if self.producto else 'unidades'}"
        elif self.tipo_movimiento == TipoMovimiento.PERDIDA:
            return f"Pérdida de {self.cantidad} {self.producto.unidad_medida if self.producto else 'unidades'}"
        return "Movimiento desconocido"
    
    def calcular_valor_movimiento(self):
        """Calcula el valor monetario del movimiento"""
        if self.costo_unitario:
            return float(self.cantidad * self.costo_unitario)
        elif self.producto:
            return float(self.cantidad * self.producto.precio_compra)
        return 0.0
    
    def es_entrada(self):
        """Verifica si es un movimiento de entrada"""
        return self.tipo_movimiento in [TipoMovimiento.ENTRADA, TipoMovimiento.DEVOLUCION]
    
    def es_salida(self):
        """Verifica si es un movimiento de salida"""
        return self.tipo_movimiento in [TipoMovimiento.SALIDA, TipoMovimiento.PERDIDA]
    
    def obtener_impacto_stock(self):
        """Obtiene el impacto del movimiento en el stock"""
        if self.tipo_movimiento == TipoMovimiento.AJUSTE:
            return self.cantidad_nueva - self.cantidad_anterior
        elif self.tipo_movimiento in [TipoMovimiento.ENTRADA, TipoMovimiento.DEVOLUCION]:
            return self.cantidad
        elif self.tipo_movimiento in [TipoMovimiento.SALIDA, TipoMovimiento.PERDIDA]:
            return -self.cantidad
        return 0
    
    def puede_anularse(self, usuario_actual):
        """
        Verifica si el movimiento puede ser anulado
        """
        # Solo administradores pueden anular movimientos
        if not usuario_actual.es_administrador():
            return False, "Solo los administradores pueden anular movimientos"
        
        # No se pueden anular movimientos antiguos (más de 24 horas)
        from datetime import datetime, timedelta
        if datetime.now() - self.fecha_movimiento > timedelta(hours=24):
            return False, "No se pueden anular movimientos de más de 24 horas"
        
        # Verificar que el stock actual sea suficiente para la anulación
        if self.es_entrada() and self.producto.stock_actual < self.cantidad:
            return False, f"No hay suficiente stock para anular esta entrada. Disponible: {self.producto.stock_actual}"
        
        return True, "Movimiento puede ser anulado"
    
    def anular_movimiento(self, usuario_actual, motivo_anulacion):
        """
        Anula el movimiento creando un movimiento compensatorio
        """
        puede_anular, mensaje = self.puede_anularse(usuario_actual)
        if not puede_anular:
            raise ValueError(mensaje)
        
        # Crear movimiento compensatorio
        from modelo.movimiento_inventario import MovimientoInventario
        
        if self.tipo_movimiento == TipoMovimiento.ENTRADA:
            # Anular entrada = crear salida
            tipo_compensatorio = TipoMovimiento.SALIDA
        elif self.tipo_movimiento == TipoMovimiento.SALIDA:
            # Anular salida = crear entrada
            tipo_compensatorio = TipoMovimiento.ENTRADA
        elif self.tipo_movimiento == TipoMovimiento.DEVOLUCION:
            # Anular devolución = crear salida
            tipo_compensatorio = TipoMovimiento.SALIDA
        elif self.tipo_movimiento == TipoMovimiento.PERDIDA:
            # Anular pérdida = crear entrada
            tipo_compensatorio = TipoMovimiento.ENTRADA
        else:
            # Para ajustes, restaurar stock anterior
            stock_actual = self.producto.stock_actual
            diferencia = self.cantidad_anterior - stock_actual
            
            if diferencia > 0:
                tipo_compensatorio = TipoMovimiento.ENTRADA
            elif diferencia < 0:
                tipo_compensatorio = TipoMovimiento.SALIDA
            else:
                raise ValueError("No hay diferencia de stock que anular")
        
        movimiento_compensatorio = MovimientoInventario(
            id_producto=self.id_producto,
            id_usuario=usuario_actual.id_usuario,
            tipo_movimiento=tipo_compensatorio,
            cantidad=abs(self.obtener_impacto_stock()),
            cantidad_anterior=self.producto.stock_actual,
            cantidad_nueva=self.producto.stock_actual + self.obtener_impacto_stock(),
            motivo=f"Anulación de movimiento #{self.id_movimiento}: {motivo_anulacion}"
        )
        
        return movimiento_compensatorio

# Import necesario para evitar circular imports
from modelo.producto import Producto
from modelo.usuario import Usuario
