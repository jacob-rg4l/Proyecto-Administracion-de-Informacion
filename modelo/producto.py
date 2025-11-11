"""
Modelo de Producto
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Decimal, ForeignKey
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship
import qrcode
from io import BytesIO
import base64
import uuid

class Producto(Base):
    """
    Modelo para la gestión de productos del inventario
    """
    __tablename__ = "productos"
    
    id_producto = Column(Integer, primary_key=True, index=True)
    codigo_producto = Column(String(100), unique=True, nullable=False, index=True)
    nombre_producto = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=False)
    precio_compra = Column(Decimal(10,2), default=0.00)
    precio_venta = Column(Decimal(10,2), default=0.00)
    stock_minimo = Column(Integer, default=5)
    stock_actual = Column(Integer, default=0)
    ubicacion_almacen = Column(String(255), nullable=True)
    unidad_medida = Column(String(50), default="unidad")
    peso = Column(Decimal(8,3), nullable=True)
    dimensiones = Column(String(100), nullable=True)
    fecha_creacion = Column(DateTime, default=func.current_timestamp())
    fecha_modificacion = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    activo = Column(Boolean, default=True)
    qr_code = Column(Text, nullable=True)  # Texto del código QR
    qr_data_url = Column(Text, nullable=True)  # Data URL de la imagen QR
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    proveedor = relationship("Proveedor", back_populates="productos")
    movimientos = relationship("MovimientoInventario", back_populates="producto", cascade="all, delete-orphan")
    alertas = relationship("AlertaStock", back_populates="producto", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Producto(id={self.id_producto}, codigo='{self.codigo_producto}', nombre='{self.nombre_producto}')>"
    
    def obtener_estado_stock(self):
        """Obtiene el estado actual del stock"""
        if self.stock_actual <= self.stock_minimo // 2:
            return "crítico"
        elif self.stock_actual <= self.stock_minimo:
            return "bajo"
        elif self.stock_actual <= self.stock_minimo * 2:
            return "normal"
        else:
            return "alto"
    
    def necesita_alerta_stock(self):
        """Verifica si el producto necesita alerta de stock"""
        return self.stock_actual <= self.stock_minimo
    
    def generar_codigo_qr(self, base_url="https://stocktrack.app"):
        """
        Genera el código QR para el producto
        """
        # Crear datos del QR
        qr_data = f"{base_url}/producto/{self.codigo_producto}"
        
        # Generar código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Crear imagen QR
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"
        
        # Guardar en el producto
        self.qr_code = qr_data
        self.qr_data_url = data_url
        
        return data_url
    
    def registrar_entrada(self, cantidad, motivo="", costo_unitario=None, usuario_id=None):
        """
        Registra una entrada de productos
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        
        self.stock_actual += cantidad
        if costo_unitario and costo_unitario > 0:
            self.precio_compra = costo_unitario
        
        # Crear movimiento
        from modelo.movimiento_inventario import MovimientoInventario
        return MovimientoInventario(
            id_producto=self.id_producto,
            id_usuario=usuario_id,
            tipo_movimiento="entrada",
            cantidad=cantidad,
            cantidad_anterior=self.stock_actual - cantidad,
            cantidad_nueva=self.stock_actual,
            motivo=motivo,
            costo_unitario=costo_unitario
        )
    
    def registrar_salida(self, cantidad, motivo="", usuario_id=None):
        """
        Registra una salida de productos
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        
        if self.stock_actual < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {self.stock_actual}")
        
        stock_anterior = self.stock_actual
        self.stock_actual -= cantidad
        
        # Crear movimiento
        from modelo.movimiento_inventario import MovimientoInventario
        return MovimientoInventario(
            id_producto=self.id_producto,
            id_usuario=usuario_id,
            tipo_movimiento="salida",
            cantidad=cantidad,
            cantidad_anterior=stock_anterior,
            cantidad_nueva=self.stock_actual,
            motivo=motivo
        )
    
    def ajustar_stock(self, nuevo_stock, motivo="", usuario_id=None):
        """
        Ajusta el stock a un valor específico
        """
        if nuevo_stock < 0:
            raise ValueError("El stock no puede ser negativo")
        
        stock_anterior = self.stock_actual
        self.stock_actual = nuevo_stock
        
        # Crear movimiento
        from modelo.movimiento_inventario import MovimientoInventario
        return MovimientoInventario(
            id_producto=self.id_producto,
            id_usuario=usuario_id,
            tipo_movimiento="ajuste",
            cantidad=abs(nuevo_stock - stock_anterior),
            cantidad_anterior=stock_anterior,
            cantidad_nueva=self.stock_actual,
            motivo=motivo
        )
    
    def obtener_ultimos_movimientos(self, limite=10):
        """Obtiene los últimos movimientos del producto"""
        movimientos = sorted(self.movimientos, key=lambda x: x.fecha_movimiento, reverse=True)
        return movimientos[:limite]
    
    def obtener_valor_inventario(self):
        """Calcula el valor total del inventario de este producto"""
        return self.stock_actual * float(self.precio_compra)
    
    def obtener_estadisticas_periodo(self, fecha_inicio, fecha_fin):
        """Obtiene estadísticas del producto en un período específico"""
        movimientos_periodo = [m for m in self.movimientos 
                             if fecha_inicio <= m.fecha_movimiento <= fecha_fin]
        
        entradas = sum(m.cantidad for m in movimientos_periodo if m.tipo_movimiento == "entrada")
        salidas = sum(m.cantidad for m in movimientos_periodo if m.tipo_movimiento == "salida")
        
        return {
            "entradas": entradas,
            "salidas": salidas,
            "movimiento_neto": entradas - salidas,
            "total_movimientos": len(movimientos_periodo)
        }
    
    def generar_codigo_producto_automatico(self):
        """Genera un código de producto automático basado en categoría y nombre"""
        if not self.categoria or not self.nombre_producto:
            return None
        
        # Obtener iniciales de la categoría (máximo 3 caracteres)
        categoria_codigo = ''.join([c[0].upper() for c in self.categoria.nombre_categoria.split()[:2]])
        if len(categoria_codigo) > 3:
            categoria_codigo = categoria_codigo[:3]
        
        # Obtener iniciales del nombre del producto (máximo 4 caracteres)
        nombre_codigo = ''.join([c[0].upper() for c in self.nombre_producto.split()[:2]])
        if len(nombre_codigo) > 4:
            nombre_codigo = nombre_codigo[:4]
        
        # Generar número aleatorio de 4 dígitos
        numero_aleatorio = str(uuid.uuid4().int)[:4]
        
        return f"{categoria_codigo}-{nombre_codigo}-{numero_aleatorio}"

# Import necesario para evitar circular imports
from modelo.categoria import Categoria
from modelo.proveedor import Proveedor
from modelo.movimiento_inventario import MovimientoInventario
from modelo.alerta_stock import AlertaStock
