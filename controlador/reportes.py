"""
Controlador de Alertas y Reportes
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from modelo.alerta_stock import AlertaStock, TipoAlerta, PrioridadAlerta
from modelo.producto import Producto
from modelo.movimiento_inventario import MovimientoInventario
from modelo.configuracion import Configuracion
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import csv
from io import StringIO, BytesIO
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import seaborn as sns

class ControladorAlertas:
    """
    Controlador para la gestión de alertas
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def listar_alertas(self, solo_activas: bool = True, prioridad: str = None, 
                      tipo_alerta: str = None, pagina: int = 1, elementos_por_pagina: int = 20) -> Dict[str, Any]:
        """
        Lista alertas con filtros y paginación
        """
        try:
            query = self.db.query(AlertaStock).join(Producto)
            
            if solo_activas:
                query = query.filter(AlertaStock.resuelta == False)
            
            if prioridad:
                query = query.filter(AlertaStock.prioridad == prioridad)
            
            if tipo_alerta:
                query = query.filter(AlertaStock.tipo_alerta == tipo_alerta)
            
            # Contar total
            total_alertas = query.count()
            
            # Paginación
            offset = (pagina - 1) * elementos_por_pagina
            alertas = query.order_by(
                desc(AlertaStock.prioridad), 
                desc(AlertaStock.fecha_creacion)
            ).offset(offset).limit(elementos_por_pagina).all()
            
            # Preparar respuesta
            alertas_data = []
            for alerta in alertas:
                alertas_data.append({
                    "id": alerta.id_alerta,
                    "producto_id": alerta.id_producto,
                    "codigo_producto": alerta.producto.codigo_producto,
                    "nombre_producto": alerta.producto.nombre_producto,
                    "tipo_alerta": alerta.tipo_alerta.value,
                    "mensaje": alerta.mensaje,
                    "prioridad": alerta.prioridad.value,
                    "fecha_creacion": alerta.fecha_creacion,
                    "tiempo_transcurrido": alerta.obtener_tiempo_transcurrido_texto(),
                    "es_critica": alerta.es_critica(),
                    "esta_vencida": alerta.esta_vencida(),
                    "responsable": alerta.usuario_responsable.nombre_completo if alerta.usuario_responsable else None
                })
            
            return {
                "alertas": alertas_data,
                "total_alertas": total_alertas,
                "pagina_actual": pagina,
                "total_paginas": (total_alertas + elementos_por_pagina - 1) // elementos_por_pagina
            }
            
        except Exception as e:
            return {"alertas": [], "error": str(e), "total_alertas": 0}
    
    def resolver_alerta(self, alerta_id: int, usuario_id: int, comentario: str = "") -> tuple[bool, str]:
        """
        Marca una alerta como resuelta
        """
        try:
            alerta = self.db.query(AlertaStock).filter(AlertaStock.id_alerta == alerta_id).first()
            
            if not alerta:
                return False, "Alerta no encontrada"
            
            if alerta.resuelta:
                return False, "La alerta ya está resuelta"
            
            alerta.resolver(usuario_id, comentario)
            self.db.commit()
            
            return True, "Alerta resuelta exitosamente"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al resolver alerta: {str(e)}"
    
    def crear_alerta_manual(self, producto_id: int, tipo_alerta: str, mensaje: str, 
                           prioridad: str = "media", usuario_responsable: int = None) -> tuple[bool, str]:
        """
        Crea una alerta manual
        """
        try:
            producto = self.db.query(Producto).filter(
                Producto.id_producto == producto_id,
                Producto.activo == True
            ).first()
            
            if not producto:
                return False, "Producto no encontrado"
            
            # Verificar que no exista una alerta activa similar
            alerta_existente = self.db.query(AlertaStock).filter(
                AlertaStock.id_producto == producto_id,
                AlertaStock.tipo_alerta == tipo_alerta,
                AlertaStock.resuelta == False
            ).first()
            
            if alerta_existente:
                return False, "Ya existe una alerta activa para este producto y tipo"
            
            alerta = AlertaStock(
                id_producto=producto_id,
                tipo_alerta=tipo_alerta,
                mensaje=mensaje,
                prioridad=prioridad,
                id_usuario_responsable=usuario_responsable
            )
            
            self.db.add(alerta)
            self.db.commit()
            
            return True, "Alerta creada exitosamente"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al crear alerta: {str(e)}"
    
    def obtener_estadisticas_alertas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de alertas
        """
        try:
            total_alertas = self.db.query(AlertaStock).count()
            alertas_activas = self.db.query(AlertaStock).filter(AlertaStock.resuelta == False).count()
            alertas_criticas = self.db.query(AlertaStock).filter(
                AlertaStock.resuelta == False,
                AlertaStock.prioridad == PrioridadAlerta.CRITICA
            ).count()
            alertas_vencidas = self.db.query(AlertaStock).filter(
                AlertaStock.resuelta == False
            ).all()
            
            # Contar alertas vencidas (más de 7 días)
            dias_limite = Configuracion.obtener_configuracion(self.db, "inventario_dias_alerta_vencida", 7)
            alertas_vencidas_count = sum(1 for a in alertas_vencidas if a.esta_vencida())
            
            # Alertas por tipo
            alertas_por_tipo = self.db.query(
                AlertaStock.tipo_alerta,
                func.count(AlertaStock.id_alerta)
            ).filter(AlertaStock.resuelta == False).group_by(AlertaStock.tipo_alerta).all()
            
            return {
                "total_alertas": total_alertas,
                "alertas_activas": alertas_activas,
                "alertas_criticas": alertas_criticas,
                "alertas_vencidas": alertas_vencidas_count,
                "alertas_resueltas": total_alertas - alertas_activas,
                "por_tipo": {
                    tipo: count for tipo, count in alertas_por_tipo
                }
            }
            
        except Exception as e:
            return {"error": str(e)}

class ControladorReportes:
    """
    Controlador para la generación de reportes
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generar_reporte_inventario(self, fecha_inicio: datetime = None, fecha_fin: datetime = None,
                                  categoria_id: int = None, formato: str = "json") -> Dict[str, Any]:
        """
        Genera reporte de inventario
        """
        try:
            if not fecha_inicio:
                fecha_inicio = datetime.now() - timedelta(days=30)
            if not fecha_fin:
                fecha_fin = datetime.now()
            
            query = self.db.query(Producto).filter(Producto.activo == True)
            
            if categoria_id:
                query = query.filter(Producto.id_categoria == categoria_id)
            
            productos = query.all()
            
            datos_reporte = []
            for producto in productos:
                # Obtener movimientos del período
                movimientos = self.db.query(MovimientoInventario).filter(
                    MovimientoInventario.id_producto == producto.id_producto,
                    and_(
                        MovimientoInventario.fecha_movimiento >= fecha_inicio,
                        MovimientoInventario.fecha_movimiento <= fecha_fin
                    )
                ).all()
                
                entradas = sum(m.cantidad for m in movimientos if m.tipo_movimiento.value in ['entrada', 'devolucion'])
                salidas = sum(m.cantidad for m in movimientos if m.tipo_movimiento.value in ['salida', 'perdida'])
                
                datos_reporte.append({
                    "codigo": producto.codigo_producto,
                    "nombre": producto.nombre_producto,
                    "categoria": producto.categoria.nombre_categoria if producto.categoria else "",
                    "proveedor": producto.proveedor.nombre_proveedor if producto.proveedor else "",
                    "stock_actual": producto.stock_actual,
                    "stock_minimo": producto.stock_minimo,
                    "precio_compra": float(producto.precio_compra),
                    "precio_venta": float(producto.precio_venta),
                    "entradas": entradas,
                    "salidas": salidas,
                    "valor_inventario": producto.obtener_valor_inventario(),
                    "estado_stock": producto.obtener_estado_stock(),
                    "ubicacion": producto.ubicacion_almacen
                })
            
            if formato.lower() == "excel":
                return self._generar_excel(datos_reporte, f"reporte_inventario_{datetime.now().strftime('%Y%m%d')}")
            elif formato.lower() == "csv":
                return self._generar_csv(datos_reporte, f"reporte_inventario_{datetime.now().strftime('%Y%m%d')}")
            else:
                return {
                    "datos": datos_reporte,
                    "resumen": {
                        "total_productos": len(datos_reporte),
                        "valor_total": sum(item["valor_inventario"] for item in datos_reporte),
                        "productos_stock_bajo": len([p for p in datos_reporte if p["estado_stock"] in ["bajo", "crítico"]]),
                        "periodo": {
                            "inicio": fecha_inicio.strftime("%Y-%m-%d"),
                            "fin": fecha_fin.strftime("%Y-%m-%d")
                        }
                    }
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def generar_reporte_movimientos(self, producto_id: int = None, fecha_inicio: datetime = None,
                                   fecha_fin: datetime = None, tipo_movimiento: str = None,
                                   formato: str = "json") -> Dict[str, Any]:
        """
        Genera reporte de movimientos de inventario
        """
        try:
            if not fecha_inicio:
                fecha_inicio = datetime.now() - timedelta(days=30)
            if not fecha_fin:
                fecha_fin = datetime.now()
            
            query = self.db.query(MovimientoInventario).filter(
                and_(
                    MovimientoInventario.fecha_movimiento >= fecha_inicio,
                    MovimientoInventario.fecha_movimiento <= fecha_fin
                )
            )
            
            if producto_id:
                query = query.filter(MovimientoInventario.id_producto == producto_id)
            
            if tipo_movimiento:
                query = query.filter(MovimientoInventario.tipo_movimiento == tipo_movimiento)
            
            movimientos = query.order_by(desc(MovimientoInventario.fecha_movimiento)).all()
            
            datos_reporte = []
            for movimiento in movimientos:
                datos_reporte.append({
                    "fecha": movimiento.fecha_movimiento,
                    "producto_codigo": movimiento.producto.codigo_producto,
                    "producto_nombre": movimiento.producto.nombre_producto,
                    "tipo_movimiento": movimiento.tipo_movimiento.value,
                    "cantidad": movimiento.cantidad,
                    "stock_anterior": movimiento.cantidad_anterior,
                    "stock_nuevo": movimiento.cantidad_nueva,
                    "motivo": movimiento.motivo,
                    "usuario": movimiento.usuario.nombre_completo if movimiento.usuario else "Sistema",
                    "valor_movimiento": movimiento.calcular_valor_movimiento()
                })
            
            if formato.lower() == "excel":
                return self._generar_excel(datos_reporte, f"reporte_movimientos_{datetime.now().strftime('%Y%m%d')}")
            elif formato.lower() == "csv":
                return self._generar_csv(datos_reporte, f"reporte_movimientos_{datetime.now().strftime('%Y%m%d')}")
            else:
                return {
                    "datos": datos_reporte,
                    "resumen": {
                        "total_movimientos": len(datos_reporte),
                        "entradas": len([m for m in datos_reporte if m["tipo_movimiento"] in ["entrada", "devolucion"]]),
                        "salidas": len([m for m in datos_reporte if m["tipo_movimiento"] in ["salida", "perdida"]]),
                        "ajustes": len([m for m in datos_reporte if m["tipo_movimiento"] == "ajuste"]),
                        "periodo": {
                            "inicio": fecha_inicio.strftime("%Y-%m-%d"),
                            "fin": fecha_fin.strftime("%Y-%m-%d")
                        }
                    }
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def generar_dashboard_datos(self) -> Dict[str, Any]:
        """
        Genera datos para el dashboard principal
        """
        try:
            # Estadísticas generales
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
            
            # Movimientos recientes (últimos 7 días)
            fecha_limite = datetime.now() - timedelta(days=7)
            movimientos_recientes = self.db.query(MovimientoInventario).filter(
                MovimientoInventario.fecha_movimiento >= fecha_limite
            ).count()
            
            # Alertas activas
            alertas_activas = self.db.query(AlertaStock).filter(AlertaStock.resuelta == False).count()
            alertas_criticas = self.db.query(AlertaStock).filter(
                AlertaStock.resuelta == False,
                AlertaStock.prioridad == PrioridadAlerta.CRITICA
            ).count()
            
            # Productos más movimentados (últimos 30 días)
            fecha_movimientos = datetime.now() - timedelta(days=30)
            productos_movimentados = self.db.query(
                Producto.codigo_producto,
                Producto.nombre_producto,
                func.count(MovimientoInventario.id_movimiento).label('total_movimientos'),
                func.sum(MovimientoInventario.cantidad).label('cantidad_total')
            ).join(
                MovimientoInventario, Producto.id_producto == MovimientoInventario.id_producto
            ).filter(
                MovimientoInventario.fecha_movimiento >= fecha_movimientos,
                Producto.activo == True
            ).group_by(
                Producto.id_producto
            ).order_by(
                desc('total_movimientos')
            ).limit(10).all()
            
            # Productos con stock crítico
            productos_criticos = self.db.query(Producto).filter(
                Producto.activo == True,
                Producto.stock_actual <= Producto.stock_minimo
            ).order_by(Producto.stock_actual).limit(5).all()
            
            return {
                "estadisticas_generales": {
                    "total_productos": total_productos,
                    "productos_stock_bajo": productos_stock_bajo,
                    "productos_agotados": productos_agotados,
                    "valor_total_inventario": valor_total_inventario,
                    "movimientos_recientes": movimientos_recientes,
                    "alertas_activas": alertas_activas,
                    "alertas_criticas": alertas_criticas
                },
                "productos_movimentados": [
                    {
                        "codigo": p[0],
                        "nombre": p[1],
                        "total_movimientos": p[2],
                        "cantidad_total": p[3]
                    }
                    for p in productos_movimentados
                ],
                "productos_criticos": [
                    {
                        "codigo": p.codigo_producto,
                        "nombre": p.nombre_producto,
                        "stock_actual": p.stock_actual,
                        "stock_minimo": p.stock_minimo
                    }
                    for p in productos_criticos
                ]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generar_excel(self, datos: List[Dict], nombre_archivo: str) -> Dict[str, Any]:
        """
        Genera archivo Excel con los datos
        """
        try:
            df = pd.DataFrame(datos)
            
            # Crear archivo en memoria
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Datos')
            
            buffer.seek(0)
            
            return {
                "archivo": buffer.getvalue(),
                "nombre": f"{nombre_archivo}.xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
            
        except Exception as e:
            return {"error": f"Error al generar Excel: {str(e)}"}
    
    def _generar_csv(self, datos: List[Dict], nombre_archivo: str) -> Dict[str, Any]:
        """
        Genera archivo CSV con los datos
        """
        try:
            if not datos:
                return {"error": "No hay datos para generar el CSV"}
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=datos[0].keys())
            writer.writeheader()
            writer.writerows(datos)
            
            csv_data = output.getvalue()
            output.close()
            
            return {
                "archivo": csv_data.encode('utf-8'),
                "nombre": f"{nombre_archivo}.csv",
                "mime_type": "text/csv"
            }
            
        except Exception as e:
            return {"error": f"Error al generar CSV: {str(e)}"}
    
    def generar_grafico_inventario(self) -> Dict[str, Any]:
        """
        Genera gráfico de estado del inventario
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Configurar matplotlib para evitar problemas de renderizado
            plt.switch_backend("Agg")
            plt.style.use("seaborn-v0_8")
            sns.set_palette("husl")
            plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
            plt.rcParams["axes.unicode_minus"] = False
            
            # Obtener datos
            productos = self.db.query(Producto).filter(Producto.activo == True).all()
            
            estados_stock = {}
            for producto in productos:
                estado = producto.obtener_estado_stock()
                estados_stock[estado] = estados_stock.get(estado, 0) + 1
            
            # Crear gráfico
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Gráfico de torta
            colores = ['#ff9999', '#ffcc99', '#99ff99', '#99ccff']
            ax1.pie(estados_stock.values(), labels=estados_stock.keys(), autopct='%1.1f%%', 
                   colors=colores[:len(estados_stock)])
            ax1.set_title('Distribución de Estados de Stock')
            
            # Gráfico de barras por categoría
            categorias = self.db.query(
                Producto.categoria,
                func.count(Producto.id_producto),
                func.sum(Producto.stock_actual)
            ).join(
                Producto, Producto.id_categoria == Producto.categoria
            ).filter(
                Producto.activo == True
            ).group_by(Producto.categoria).all()
            
            if categorias:
                cat_nombres = [cat[0].nombre_categoria for cat in categorias if cat[0]]
                cat_productos = [cat[1] for cat in categorias if cat[0]]
                
                ax2.bar(cat_nombres, cat_productos)
                ax2.set_title('Productos por Categoría')
                ax2.set_xlabel('Categoría')
                ax2.set_ylabel('Número de Productos')
                plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            plt.tight_layout()
            
            # Guardar gráfico
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            return {
                "imagen": buffer.getvalue(),
                "formato": "image/png"
            }
            
        except Exception as e:
            return {"error": f"Error al generar gráfico: {str(e)}"}
