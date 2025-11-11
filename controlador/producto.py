"""
Controlador de Productos
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from modelo.producto import Producto
from modelo.categoria import Categoria
from modelo.proveedor import Proveedor
from modelo.movimiento_inventario import MovimientoInventario
from modelo.alerta_stock import AlertaStock, TipoAlerta, PrioridadAlerta
from modelo.configuracion import Configuracion
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import qrcode
from io import BytesIO
import base64

class ControladorProductos:
    """
    Controlador para la gestión de productos
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear_producto(self, codigo_producto: str, nombre_producto: str, descripcion: str,
                      id_categoria: int, id_proveedor: int, precio_compra: float = 0.0,
                      precio_venta: float = 0.0, stock_minimo: int = 5, stock_inicial: int = 0,
                      ubicacion_almacen: str = "", unidad_medida: str = "unidad",
                      peso: float = None, dimensiones: str = None, usuario_id: int = None) -> tuple[bool, str, Optional[Producto]]:
        """
        Crea un nuevo producto en el inventario
        """
        try:
            # Validar que el código no exista
            if self.db.query(Producto).filter(Producto.codigo_producto == codigo_producto).first():
                return False, "El código de producto ya existe", None
            
            # Validar categoría y proveedor
            categoria = self.db.query(Categoria).filter(Categoria.id_categoria == id_categoria).first()
            if not categoria or not categoria.activa:
                return False, "Categoría no válida", None
            
            proveedor = self.db.query(Proveedor).filter(Proveedor.id_proveedor == id_proveedor).first()
            if not proveedor or not proveedor.activo:
                return False, "Proveedor no válido", None
            
            # Crear producto
            producto = Producto(
                codigo_producto=codigo_producto.strip().upper(),
                nombre_producto=nombre_producto.strip(),
                descripcion=descripcion.strip() if descripcion else None,
                id_categoria=id_categoria,
                id_proveedor=id_proveedor,
                precio_compra=precio_compra,
                precio_venta=precio_venta,
                stock_minimo=max(0, stock_minimo),
                stock_actual=max(0, stock_inicial),
                ubicacion_almacen=ubicacion_almacen.strip() if ubicacion_almacen else None,
                unidad_medida=unidad_medida.strip(),
                peso=peso,
                dimensiones=dimensiones.strip() if dimensiones else None
            )
            
            # Generar código QR
            producto.generar_codigo_qr()
            
            self.db.add(producto)
            self.db.commit()
            self.db.refresh(producto)
            
            # Registrar movimiento inicial si hay stock
            if stock_inicial > 0:
                self.registrar_entrada(
                    producto_id=producto.id_producto,
                    cantidad=stock_inicial,
                    motivo="Stock inicial",
                    usuario_id=usuario_id
                )
            
            return True, "Producto creado exitosamente", producto
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al crear producto: {str(e)}", None
    
    def obtener_producto(self, producto_id: int = None, codigo_producto: str = None) -> Optional[Producto]:
        """
        Obtiene un producto por ID o código
        """
        query = self.db.query(Producto).filter(Producto.activo == True)
        
        if producto_id:
            return query.filter(Producto.id_producto == producto_id).first()
        elif codigo_producto:
            return query.filter(Producto.codigo_producto == codigo_producto.upper().strip()).first()
        
        return None
    
    def listar_productos(self, busqueda: str = "", categoria_id: int = None, 
                        proveedor_id: int = None, solo_stock_bajo: bool = False,
                        pagina: int = 1, elementos_por_pagina: int = 20) -> Dict[str, Any]:
        """
        Lista productos con filtros y paginación
        """
        try:
            query = self.db.query(Producto).filter(Producto.activo == True)
            
            # Filtros
            if busqueda:
                busqueda = f"%{busqueda.lower().strip()}%"
                query = query.filter(
                    or_(
                        Producto.nombre_producto.ilike(busqueda),
                        Producto.codigo_producto.ilike(busqueda),
                        Producto.descripcion.ilike(busqueda)
                    )
                )
            
            if categoria_id:
                query = query.filter(Producto.id_categoria == categoria_id)
            
            if proveedor_id:
                query = query.filter(Producto.id_proveedor == proveedor_id)
            
            if solo_stock_bajo:
                query = query.filter(Producto.stock_actual <= Producto.stock_minimo)
            
            # Contar total
            total_productos = query.count()
            
            # Paginación
            offset = (pagina - 1) * elementos_por_pagina
            productos = query.order_by(Producto.nombre_producto).offset(offset).limit(elementos_por_pagina).all()
            
            # Preparar respuesta
            productos_data = []
            for producto in productos:
                productos_data.append({
                    "id": producto.id_producto,
                    "codigo_producto": producto.codigo_producto,
                    "nombre_producto": producto.nombre_producto,
                    "descripcion": producto.descripcion,
                    "categoria": producto.categoria.nombre_categoria if producto.categoria else "",
                    "proveedor": producto.proveedor.nombre_proveedor if producto.proveedor else "",
                    "precio_compra": float(producto.precio_compra),
                    "precio_venta": float(producto.precio_venta),
                    "stock_minimo": producto.stock_minimo,
                    "stock_actual": producto.stock_actual,
                    "ubicacion_almacen": producto.ubicacion_almacen,
                    "unidad_medida": producto.unidad_medida,
                    "estado_stock": producto.obtener_estado_stock(),
                    "necesita_alerta": producto.necesita_alerta_stock(),
                    "valor_inventario": producto.obtener_valor_inventario(),
                    "qr_data_url": producto.qr_data_url,
                    "fecha_creacion": producto.fecha_creacion
                })
            
            return {
                "productos": productos_data,
                "total_productos": total_productos,
                "pagina_actual": pagina,
                "total_paginas": (total_productos + elementos_por_pagina - 1) // elementos_por_pagina,
                "elementos_por_pagina": elementos_por_pagina
            }
            
        except Exception as e:
            return {"productos": [], "error": str(e), "total_productos": 0}
    
    def actualizar_producto(self, producto_id: int, **kwargs) -> tuple[bool, str]:
        """
        Actualiza un producto existente
        """
        try:
            producto = self.db.query(Producto).filter(
                Producto.id_producto == producto_id,
                Producto.activo == True
            ).first()
            
            if not producto:
                return False, "Producto no encontrado"
            
            # Campos actualizables
            campos_actualizables = [
                'nombre_producto', 'descripcion', 'id_categoria', 'id_proveedor',
                'precio_compra', 'precio_venta', 'stock_minimo', 'ubicacion_almacen',
                'unidad_medida', 'peso', 'dimensiones'
            ]
            
            for campo, valor in kwargs.items():
                if campo in campos_actualizables and valor is not None:
                    setattr(producto, campo, valor)
            
            self.db.commit()
            return True, "Producto actualizado exitosamente"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al actualizar producto: {str(e)}"
    
    def eliminar_producto(self, producto_id: int) -> tuple[bool, str]:
        """
        Elimina (desactiva) un producto
        """
        try:
            producto = self.db.query(Producto).filter(Producto.id_producto == producto_id).first()
            
            if not producto:
                return False, "Producto no encontrado"
            
            # Verificar si tiene movimientos
            movimientos_count = self.db.query(MovimientoInventario).filter(
                MovimientoInventario.id_producto == producto_id
            ).count()
            
            if movimientos_count > 0:
                # Si tiene movimientos, solo desactivar
                producto.activo = False
                mensaje = "Producto desactivado (tiene historial de movimientos)"
            else:
                # Si no tiene movimientos, se puede eliminar
                self.db.delete(producto)
                mensaje = "Producto eliminado exitosamente"
            
            self.db.commit()
            return True, mensaje
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al eliminar producto: {str(e)}"
    
    def registrar_entrada(self, producto_id: int, cantidad: int, motivo: str = "",
                         costo_unitario: float = None, usuario_id: int = None) -> tuple[bool, str]:
        """
        Registra una entrada de productos
        """
        try:
            producto = self.db.query(Producto).filter(
                Producto.id_producto == producto_id,
                Producto.activo == True
            ).first()
            
            if not producto:
                return False, "Producto no encontrado"
            
            if cantidad <= 0:
                return False, "La cantidad debe ser mayor a cero"
            
            # Registrar entrada
            movimiento = producto.registrar_entrada(
                cantidad=cantidad,
                motivo=motivo,
                costo_unitario=costo_unitario,
                usuario_id=usuario_id
            )
            
            self.db.add(movimiento)
            self.db.commit()
            
            # Crear alerta si es necesario
            if producto.necesita_alerta_stock():
                alerta = AlertaStock.crear_alerta_stock_minimo(producto)
                if alerta:
                    self.db.add(alerta)
                    self.db.commit()
            
            return True, f"Entrada registrada exitosamente. Nuevo stock: {producto.stock_actual}"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al registrar entrada: {str(e)}"
    
    def registrar_salida(self, producto_id: int, cantidad: int, motivo: str = "", 
                        usuario_id: int = None) -> tuple[bool, str]:
        """
        Registra una salida de productos
        """
        try:
            producto = self.db.query(Producto).filter(
                Producto.id_producto == producto_id,
                Producto.activo == True
            ).first()
            
            if not producto:
                return False, "Producto no encontrado"
            
            if cantidad <= 0:
                return False, "La cantidad debe ser mayor a cero"
            
            if producto.stock_actual < cantidad:
                return False, f"Stock insuficiente. Disponible: {producto.stock_actual}"
            
            # Registrar salida
            movimiento = producto.registrar_salida(
                cantidad=cantidad,
                motivo=motivo,
                usuario_id=usuario_id
            )
            
            self.db.add(movimiento)
            self.db.commit()
            
            # Verificar alertas
            if producto.stock_actual == 0:
                alerta = AlertaStock.crear_alerta_agotamiento(producto)
                if alerta:
                    self.db.add(alerta)
            elif producto.necesita_alerta_stock():
                alerta = AlertaStock.crear_alerta_stock_minimo(producto)
                if alerta:
                    self.db.add(alerta)
            
            self.db.commit()
            
            return True, f"Salida registrada exitosamente. Nuevo stock: {producto.stock_actual}"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al registrar salida: {str(e)}"
    
    def ajustar_stock(self, producto_id: int, nuevo_stock: int, motivo: str = "",
                     usuario_id: int = None) -> tuple[bool, str]:
        """
        Ajusta el stock de un producto
        """
        try:
            producto = self.db.query(Producto).filter(
                Producto.id_producto == producto_id,
                Producto.activo == True
            ).first()
            
            if not producto:
                return False, "Producto no encontrado"
            
            if nuevo_stock < 0:
                return False, "El stock no puede ser negativo"
            
            # Registrar ajuste
            movimiento = producto.ajustar_stock(
                nuevo_stock=nuevo_stock,
                motivo=motivo,
                usuario_id=usuario_id
            )
            
            self.db.add(movimiento)
            self.db.commit()
            
            # Verificar alertas
            if producto.necesita_alerta_stock():
                alerta = AlertaStock.crear_alerta_stock_minimo(producto)
                if alerta:
                    self.db.add(alerta)
            elif producto.stock_actual == 0:
                alerta = AlertaStock.crear_alerta_agotamiento(producto)
                if alerta:
                    self.db.add(alerta)
            
            self.db.commit()
            
            return True, f"Stock ajustado exitosamente. Nuevo stock: {producto.stock_actual}"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al ajustar stock: {str(e)}"
    
    def obtener_productos_stock_bajo(self) -> List[Dict[str, Any]]:
        """
        Obtiene productos con stock bajo
        """
        try:
            productos = self.db.query(Producto).filter(
                Producto.activo == True,
                Producto.stock_actual <= Producto.stock_minimo
            ).order_by(Producto.stock_actual).all()
            
            return [
                {
                    "id": p.id_producto,
                    "codigo_producto": p.codigo_producto,
                    "nombre_producto": p.nombre_producto,
                    "stock_actual": p.stock_actual,
                    "stock_minimo": p.stock_minimo,
                    "cantidad_faltante": p.stock_minimo - p.stock_actual,
                    "ubicacion_almacen": p.ubicacion_almacen,
                    "proveedor": p.proveedor.nombre_proveedor if p.proveedor else "",
                    "categoria": p.categoria.nombre_categoria if p.categoria else ""
                }
                for p in productos
            ]
            
        except Exception as e:
            return []
    
    def obtener_estadisticas_productos(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de productos
        """
        try:
            total_productos = self.db.query(Producto).filter(Producto.activo == True).count()
            productos_stock_bajo = self.db.query(Producto).filter(
                Producto.activo == True,
                Producto.stock_actual <= Producto.stock_minimo
            ).count()
            productos_agotados = self.db.query(Producto).filter(
                Producto.activo == True,
                Producto.stock_actual == 0
            ).count()
            
            # Valor total del inventario
            resultado_valor = self.db.query(
                func.sum(Producto.stock_actual * Producto.precio_compra)
            ).filter(Producto.activo == True).first()
            valor_total_inventario = float(resultado_valor[0] or 0)
            
            # Productos por categoría
            categorias_stats = self.db.query(
                Categoria.nombre_categoria,
                func.count(Producto.id_producto).label('total_productos'),
                func.sum(Producto.stock_actual).label('stock_total')
            ).join(
                Producto, Categoria.id_categoria == Producto.id_categoria
            ).filter(
                Producto.activo == True
            ).group_by(Categoria.id_categoria).all()
            
            return {
                "total_productos": total_productos,
                "productos_stock_bajo": productos_stock_bajo,
                "productos_agotados": productos_agotados,
                "productos_normales": total_productos - productos_stock_bajo,
                "valor_total_inventario": valor_total_inventario,
                "categorias": [
                    {
                        "categoria": cat[0],
                        "total_productos": cat[1],
                        "stock_total": cat[2] or 0
                    }
                    for cat in categorias_stats
                ]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def buscar_por_codigo_qr(self, qr_data: str) -> Optional[Producto]:
        """
        Busca un producto por código QR
        """
        try:
            # Extraer código del QR (formato: URL/producto/CODIGO)
            if "/producto/" in qr_data:
                codigo = qr_data.split("/producto/")[-1]
                return self.obtener_producto(codigo_producto=codigo)
            
            # Buscar por código directo
            return self.obtener_producto(codigo_producto=qr_data)
            
        except Exception as e:
            return None
    
    def generar_codigo_qr_actualizado(self, producto_id: int, base_url: str = None) -> tuple[bool, str, Optional[str]]:
        """
        Regenera el código QR de un producto
        """
        try:
            if not base_url:
                base_url = Configuracion.obtener_configuracion(self.db, "qr_base_url", "https://stocktrack.app")
            
            producto = self.db.query(Producto).filter(Producto.id_producto == producto_id).first()
            
            if not producto:
                return False, "Producto no encontrado", None
            
            qr_data_url = producto.generar_codigo_qr(base_url)
            self.db.commit()
            
            return True, "Código QR actualizado", qr_data_url
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al generar QR: {str(e)}", None
    
    def obtener_movimientos_producto(self, producto_id: int, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de movimientos de un producto
        """
        try:
            movimientos = self.db.query(MovimientoInventario).filter(
                MovimientoInventario.id_producto == producto_id
            ).order_by(desc(MovimientoInventario.fecha_movimiento)).limit(limite).all()
            
            return [
                {
                    "id": m.id_movimiento,
                    "tipo_movimiento": m.tipo_movimiento.value,
                    "cantidad": m.cantidad,
                    "cantidad_anterior": m.cantidad_anterior,
                    "cantidad_nueva": m.cantidad_nueva,
                    "motivo": m.motivo,
                    "fecha_movimiento": m.fecha_movimiento,
                    "usuario": m.usuario.nombre_completo if m.usuario else "Sistema",
                    "valor_movimiento": m.calcular_valor_movimiento()
                }
                for m in movimientos
            ]
            
        except Exception as e:
            return []
