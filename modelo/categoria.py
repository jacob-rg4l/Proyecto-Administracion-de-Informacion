"""
Modelo de Categoría
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship

class Categoria(Base):
    """
    Modelo para la gestión de categorías de productos
    """
    __tablename__ = "categorias"
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre_categoria = Column(String(255), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    color_hex = Column(String(7), default="#007bff")
    fecha_creacion = Column(DateTime, default=func.current_timestamp())
    activa = Column(Boolean, default=True)
    
    # Relaciones
    productos = relationship("Producto", back_populates="categoria", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Categoria(id={self.id_categoria}, nombre='{self.nombre_categoria}')>"
    
    def desactivar(self):
        """Desactiva la categoría (no elimina, solo marca como inactiva)"""
        self.activa = False
    
    def activar(self):
        """Activa la categoría"""
        self.activa = True
    
    def puede_eliminarse(self):
        """Verifica si la categoría puede eliminarse (no tiene productos asociados)"""
        return len(self.productos) == 0
    
    def obtener_productos_activos(self):
        """Obtiene solo los productos activos de esta categoría"""
        return [p for p in self.productos if p.activo]
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas de la categoría"""
        productos_activos = self.obtener_productos_activos()
        return {
            "total_productos": len(self.productos),
            "productos_activos": len(productos_activos),
            "stock_total": sum(p.stock_actual for p in productos_activos),
            "valor_inventario": sum(p.stock_actual * p.precio_compra for p in productos_activos)
        }

# Import necesario para evitar circular imports
from modelo.producto import Producto
