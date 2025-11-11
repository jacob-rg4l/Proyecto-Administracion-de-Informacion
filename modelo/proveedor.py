"""
Modelo de Proveedor
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship

class Proveedor(Base):
    """
    Modelo para la gestión de proveedores
    """
    __tablename__ = "proveedores"
    
    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre_proveedor = Column(String(255), nullable=False, unique=True)
    contacto = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    direccion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=func.current_timestamp())
    
    # Relaciones
    productos = relationship("Producto", back_populates="proveedor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Proveedor(id={self.id_proveedor}, nombre='{self.nombre_proveedor}')>"
    
    def desactivar(self):
        """Desactiva el proveedor"""
        self.activo = False
    
    def activar(self):
        """Activa el proveedor"""
        self.activo = True
    
    def puede_eliminarse(self):
        """Verifica si el proveedor puede eliminarse (no tiene productos asociados)"""
        return len(self.productos) == 0
    
    def obtener_productos_activos(self):
        """Obtiene solo los productos activos de este proveedor"""
        return [p for p in self.productos if p.activo]
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas del proveedor"""
        productos_activos = self.obtener_productos_activos()
        return {
            "total_productos": len(self.productos),
            "productos_activos": len(productos_activos),
            "stock_total": sum(p.stock_actual for p in productos_activos),
            "valor_inventario": sum(p.stock_actual * p.precio_compra for p in productos_activos)
        }
    
    def obtener_ultimos_movimientos(self, limite=10):
        """Obtiene los últimos movimientos de productos de este proveedor"""
        from modelo.movimiento_inventario import MovimientoInventario
        from sqlalchemy import desc
        
        movimientos = []
        for producto in self.obtener_productos_activos():
            movimientos.extend(producto.movimientos)
        
        # Ordenar por fecha y devolver los más recientes
        movimientos.sort(key=lambda x: x.fecha_movimiento, reverse=True)
        return movimientos[:limite]

# Import necesario para evitar circular imports
from modelo.producto import Producto
