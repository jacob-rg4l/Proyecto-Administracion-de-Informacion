"""
Aplicación Principal FastAPI
Sistema de Gestión de Inventarios StockTrack
Autor: MiniMax Agent
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import uvicorn
import os
from datetime import datetime

# Importar configuración y modelos
from config.database import obtener_sesion, crear_tablas
from modelo import *
from controlador import *

# Configurar la aplicación
app = FastAPI(
    title="StockTrack - Sistema de Gestión de Inventarios",
    description="Sistema web para la gestión eficiente de inventarios de pequeñas y medianas empresas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configurar templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)

# Seguridad
security = HTTPBearer()

# Dependencias
async def obtener_usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(security), 
                                db: Session = Depends(obtener_sesion)):
    """
    Obtiene el usuario actual basado en el token de sesión
    """
    try:
        token = credentials.credentials
        auth_controller = ControladorAutenticacion(db)
        valido, mensaje, usuario = auth_controller.validar_sesion(token)
        
        if not valido:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=mensaje,
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return usuario
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def verificar_administrador(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Verifica que el usuario actual sea administrador
    """
    if not usuario_actual.es_administrador():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return usuario_actual

# ===============================
# RUTAS DE AUTENTICACIÓN
# ===============================

@app.get("/login", response_class=HTMLResponse)
async def mostrar_login(request: Request):
    """Muestra la página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def iniciar_sesion(request: Request, db: Session = Depends(obtener_sesion)):
    """Procesa el login de usuario"""
    try:
        form_data = await request.form()
        email = form_data.get("email", "").lower().strip()
        password = form_data.get("password", "")
        remember_me = form_data.get("remember_me") == "on"
        
        # Obtener información adicional
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        auth_controller = ControladorAutenticacion(db)
        valido, mensaje, info_sesion = auth_controller.autenticar_usuario(
            email=email,
            password=password,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        if valido:
            # Redirigir al dashboard
            response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
            response.set_cookie(
                key="session_token",
                value=info_sesion["sesion"]["id"],
                httponly=True,
                secure=False,  # Cambiar a True en producción
                samesite="lax",
                max_age=86400 if remember_me else 3600
            )
            return response
        else:
            return templates.TemplateResponse(
                "login.html", 
                {
                    "request": request,
                    "error": mensaje,
                    "email": email
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Error interno del servidor"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.post("/logout")
async def cerrar_sesion(request: Request, db: Session = Depends(obtener_sesion)):
    """Cierra la sesión del usuario"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        auth_controller = ControladorAutenticacion(db)
        auth_controller.cerrar_sesion(session_token)
    
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session_token")
    return response

@app.get("/register", response_class=HTMLResponse)
async def mostrar_registro(request: Request):
    """Muestra la página de registro"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def registrar_usuario(request: Request, db: Session = Depends(obtener_sesion)):
    """Procesa el registro de nuevo usuario"""
    try:
        form_data = await request.form()
        email = form_data.get("email", "").lower().strip()
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")
        nombre_completo = form_data.get("nombre_completo", "").strip()
        rol = form_data.get("rol", "operario")
        
        if password != confirm_password:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Las contraseñas no coinciden"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 6:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "La contraseña debe tener al menos 6 caracteres"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        auth_controller = ControladorAutenticacion(db)
        exito, mensaje, usuario = auth_controller.registrar_usuario(
            email=email,
            password=password,
            nombre_completo=nombre_completo,
            rol=rol
        )
        
        if exito:
            return RedirectResponse(url="/login?registered=1", status_code=status.HTTP_302_FOUND)
        else:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": mensaje},
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Error interno del servidor"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ===============================
# RUTAS PROTEGIDAS (DASHBOARD)
# ===============================

@app.get("/", response_class=HTMLResponse)
async def pagina_inicio(request: Request):
    """Página de inicio - redirige al dashboard o login"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Verificar sesión válida
        try:
            db = next(obtener_sesion())
            auth_controller = ControladorAutenticacion(db)
            valido, mensaje, usuario = auth_controller.validar_sesion(session_token)
            if valido:
                return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        except:
            pass
    
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, usuario_actual: Usuario = Depends(obtener_usuario_actual), 
                   db: Session = Depends(obtener_sesion)):
    """Dashboard principal del sistema"""
    try:
        # Obtener datos del dashboard
        reportes_controller = ControladorReportes(db)
        dashboard_data = reportes_controller.generar_dashboard_datos()
        
        # Obtener alertas recientes
        alertas_controller = ControladorAlertas(db)
        alertas_data = alertas_controller.listar_alertas(solo_activas=True, elementos_por_pagina=5)
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "usuario": usuario_actual,
                "dashboard_data": dashboard_data,
                "alertas": alertas_data["alertas"]
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Error al cargar el dashboard: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ===============================
# API ENDPOINTS PARA PRODUCTOS
# ===============================

@app.get("/api/productos")
async def listar_productos(
    busqueda: str = "",
    categoria_id: Optional[int] = None,
    solo_stock_bajo: bool = False,
    pagina: int = 1,
    elementos_por_pagina: int = 20,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para listar productos"""
    try:
        productos_controller = ControladorProductos(db)
        return productos_controller.listar_productos(
            busqueda=busqueda,
            categoria_id=categoria_id,
            solo_stock_bajo=solo_stock_bajo,
            pagina=pagina,
            elementos_por_pagina=elementos_por_pagina
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/productos/{producto_id}")
async def obtener_producto(
    producto_id: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para obtener un producto específico"""
    try:
        productos_controller = ControladorProductos(db)
        producto = productos_controller.obtener_producto(producto_id=producto_id)
        
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Obtener movimientos del producto
        movimientos = productos_controller.obtener_movimientos_producto(producto_id)
        
        return {
            "producto": {
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
                "qr_data_url": producto.qr_data_url
            },
            "movimientos": movimientos
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/productos")
async def crear_producto(
    producto_data: dict,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para crear un nuevo producto"""
    try:
        productos_controller = ControladorProductos(db)
        exito, mensaje, producto = productos_controller.crear_producto(
            codigo_producto=producto_data["codigo_producto"],
            nombre_producto=producto_data["nombre_producto"],
            descripcion=producto_data.get("descripcion", ""),
            id_categoria=producto_data["id_categoria"],
            id_proveedor=producto_data["id_proveedor"],
            precio_compra=producto_data.get("precio_compra", 0.0),
            precio_venta=producto_data.get("precio_venta", 0.0),
            stock_minimo=producto_data.get("stock_minimo", 5),
            stock_inicial=producto_data.get("stock_inicial", 0),
            ubicacion_almacen=producto_data.get("ubicacion_almacen", ""),
            usuario_id=usuario_actual.id_usuario
        )
        
        if exito:
            return {"success": True, "message": mensaje, "producto_id": producto.id_producto}
        else:
            raise HTTPException(status_code=400, detail=mensaje)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/productos/{producto_id}")
async def actualizar_producto(
    producto_id: int,
    producto_data: dict,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para actualizar un producto"""
    try:
        productos_controller = ControladorProductos(db)
        exito, mensaje = productos_controller.actualizar_producto(producto_id, **producto_data)
        
        if exito:
            return {"success": True, "message": mensaje}
        else:
            raise HTTPException(status_code=400, detail=mensaje)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/productos/{producto_id}")
async def eliminar_producto(
    producto_id: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para eliminar un producto"""
    try:
        productos_controller = ControladorProductos(db)
        exito, mensaje = productos_controller.eliminar_producto(producto_id)
        
        if exito:
            return {"success": True, "message": mensaje}
        else:
            raise HTTPException(status_code=400, detail=mensaje)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# API ENDPOINTS PARA MOVIMIENTOS
# ===============================

@app.post("/api/productos/{producto_id}/entrada")
async def registrar_entrada(
    producto_id: int,
    movimiento_data: dict,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para registrar entrada de productos"""
    try:
        productos_controller = ControladorProductos(db)
        exito, mensaje = productos_controller.registrar_entrada(
            producto_id=producto_id,
            cantidad=movimiento_data["cantidad"],
            motivo=movimiento_data.get("motivo", ""),
            costo_unitario=movimiento_data.get("costo_unitario"),
            usuario_id=usuario_actual.id_usuario
        )
        
        if exito:
            return {"success": True, "message": mensaje}
        else:
            raise HTTPException(status_code=400, detail=mensaje)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/productos/{producto_id}/salida")
async def registrar_salida(
    producto_id: int,
    movimiento_data: dict,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para registrar salida de productos"""
    try:
        productos_controller = ControladorProductos(db)
        exito, mensaje = productos_controller.registrar_salida(
            producto_id=producto_id,
            cantidad=movimiento_data["cantidad"],
            motivo=movimiento_data.get("motivo", ""),
            usuario_id=usuario_actual.id_usuario
        )
        
        if exito:
            return {"success": True, "message": mensaje}
        else:
            raise HTTPException(status_code=400, detail=mensaje)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/productos/{producto_id}/ajuste")
async def ajustar_stock(
    producto_id: int,
    movimiento_data: dict,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para ajustar stock de productos"""
    try:
        productos_controller = ControladorProductos(db)
        exito, mensaje = productos_controller.ajustar_stock(
            producto_id=producto_id,
            nuevo_stock=movimiento_data["nuevo_stock"],
            motivo=movimiento_data.get("motivo", ""),
            usuario_id=usuario_actual.id_usuario
        )
        
        if exito:
            return {"success": True, "message": mensaje}
        else:
            raise HTTPException(status_code=400, detail=mensaje)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# API ENDPOINTS PARA REPORTES
# ===============================

@app.get("/api/reportes/dashboard")
async def obtener_datos_dashboard(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para obtener datos del dashboard"""
    try:
        reportes_controller = ControladorReportes(db)
        return reportes_controller.generar_dashboard_datos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reportes/inventario")
async def generar_reporte_inventario(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    categoria_id: Optional[int] = None,
    formato: str = "json",
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_sesion)
):
    """API para generar reporte de inventario"""
    try:
        reportes_controller = ControladorReportes(db)
        
        # Parsear fechas
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio) if fecha_inicio else None
        fecha_fin_dt = datetime.fromisoformat(fecha_fin) if fecha_fin else None
        
        return reportes_controller.generar_reporte_inventario(
            fecha_inicio=fecha_inicio_dt,
            fecha_fin=fecha_fin_dt,
            categoria_id=categoria_id,
            formato=formato
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# PÁGINAS HTML
# ===============================

@app.get("/productos", response_class=HTMLResponse)
async def pagina_productos(request: Request, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """Página de gestión de productos"""
    return templates.TemplateResponse("productos.html", {"request": request, "usuario": usuario_actual})

@app.get("/reportes", response_class=HTMLResponse)
async def pagina_reportes(request: Request, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """Página de reportes"""
    return templates.TemplateResponse("reportes.html", {"request": request, "usuario": usuario_actual})

@app.get("/alertas", response_class=HTMLResponse)
async def pagina_alertas(request: Request, usuario_actual: Usuario = Depends(obtener_usuario_actual), 
                        db: Session = Depends(obtener_sesion)):
    """Página de alertas"""
    alertas_controller = ControladorAlertas(db)
    alertas_data = alertas_controller.listar_alertas()
    
    return templates.TemplateResponse(
        "alertas.html", 
        {
            "request": request, 
            "usuario": usuario_actual,
            "alertas": alertas_data["alertas"],
            "total_alertas": alertas_data["total_alertas"]
        }
    )

# ===============================
# EVENTOS DE INICIO
# ===============================

@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    try:
        # Crear tablas si no existen
        crear_tablas()
        
        # Inicializar base de datos con datos por defecto
        from config.database import inicializar_base_datos
        inicializar_base_datos()
        
        print("✅ StockTrack iniciado exitosamente")
        print("🌐 Accede a http://localhost:8000 para usar el sistema")
        print("📚 Documentación API: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error al iniciar StockTrack: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    print("🔄 StockTrack cerrando...")

# ===============================
# PUNTO DE ENTRADA
# ===============================

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
