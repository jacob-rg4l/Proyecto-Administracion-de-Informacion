# 🚀 INSTRUCCIONES DE INSTALACIÓN COMPLETA - StockTrack

## ✅ Resumen del Proyecto Creado

He desarrollado completamente el **Sistema de Gestión de Inventarios StockTrack** con las siguientes características:

### 🏗️ Arquitectura Implementada
- ✅ **Modelo Vista Controlador (MVC)** con FastAPI
- ✅ **Base de datos MySQL** con script SQL completo
- ✅ **Frontend responsive** con Bootstrap 5
- ✅ **Autenticación segura** con sesiones JWT
- ✅ **API REST completa** con documentación automática
- ✅ **Generación de códigos QR** automática
- ✅ **Sistema de alertas** por stock mínimo
- ✅ **Reportes en PDF/Excel** 
- ✅ **Dashboard interactivo** con gráficos

### 📁 Estructura de Archivos Creada

```
StockTrack/
├── 📄 app.py                          # Aplicación FastAPI principal
├── 📄 requirements.txt                # Dependencias Python
├── 📄 .env.example                    # Configuración de ejemplo
├── 📄 README.md                       # Documentación completa
├── 📄 setup.sh                        # Script de instalación automática
├── 📄 start.sh                        # Script de inicio (Linux/Mac)
├── 📄 start.bat                       # Script de inicio (Windows)
├── 📄 dev.sh                          # Script de desarrollo
├── 📁 config/
│   └── 📄 database.py                 # Configuración de base de datos
├── 📁 modelo/
│   ├── 📄 __init__.py
│   ├── 📄 usuario.py                  # Modelo de usuarios
│   ├── 📄 producto.py                 # Modelo de productos
│   ├── 📄 categoria.py                # Modelo de categorías
│   ├── 📄 proveedor.py                # Modelo de proveedores
│   ├── 📄 movimiento_inventario.py    # Modelo de movimientos
│   ├── 📄 alerta_stock.py             # Modelo de alertas
│   ├── 📄 sesion_usuario.py           # Modelo de sesiones
│   └── 📄 configuracion.py            # Modelo de configuración
├── 📁 controlador/
│   ├── 📄 __init__.py
│   ├── 📄 auth.py                     # Controlador de autenticación
│   ├── 📄 producto.py                 # Controlador de productos
│   └── 📄 reportes.py                 # Controlador de reportes
├── 📁 vista/
│   ├── 📄 base.html                   # Template base
│   ├── 📄 login.html                  # Página de login
│   ├── 📄 register.html               # Página de registro
│   └── 📄 dashboard.html              # Dashboard principal
├── 📁 static/                         # Archivos estáticos
├── 📁 bd/
│   └── 📄 stocktrack_base_datos.sql   # Script de base de datos completo
└── 📁 logs/                           # Directorio de logs
```

## 🛠️ Cómo Instalar y Usar

### Opción 1: Instalación Automática (Recomendada)

#### En Linux/Mac:
```bash
cd StockTrack
chmod +x setup.sh
./setup.sh
./start.sh
```

#### En Windows:
```cmd
cd StockTrack
start.bat
```

### Opción 2: Instalación Manual

#### 1. Crear Entorno Virtual
```bash
# En Linux/Mac
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

#### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 3. Configurar Base de Datos
```sql
-- 1. Crear base de datos
CREATE DATABASE stocktrack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Importar esquema
mysql -u root -p stocktrack_db < bd/stocktrack_base_datos.sql
```

#### 4. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tu configuración de BD
```

#### 5. Ejecutar la Aplicación
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Acceso al Sistema

### URLs Principales
- **Sistema Web**: http://localhost:8000
- **Dashboard**: http://localhost:8000/dashboard
- **Documentación API**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

### Credenciales por Defecto
```
Email: admin@stocktrack.com
Contraseña: admin123
```

## 🗄️ Configuración de PHPMyAdmin

### 1. Instalar PHPMyAdmin
```bash
# Ubuntu/Debian
sudo apt install phpmyadmin

# CentOS/RHEL
sudo yum install phpmyadmin
```

### 2. Acceder a PHPMyAdmin
- **URL**: http://localhost/phpmyadmin
- **Usuario**: root
- **Contraseña**: (tu password de MySQL)

### 3. Importar Base de Datos
1. Abrir PHPMyAdmin
2. Ir a la pestaña "Import"
3. Seleccionar archivo: `bd/stocktrack_base_datos.sql`
4. Hacer clic en "Continuar"

## 💻 Configuración con NetBeans

### 1. Abrir Proyecto
```
File → Open Project → Seleccionar carpeta StockTrack
```

### 2. Configurar Python
```
Tools → Options → Python
Seleccionar: Python 3.x Interpreter (venv/bin/python)
```

### 3. Ejecutar
```
Run → Run Project (F6)
```

## 🔧 Configuración con Apache

### Configuración Básica
```apache
# En httpd.conf
<VirtualHost *:80>
    ServerName stocktrack.local
    ProxyPass /api/ http://localhost:8000/api/
    ProxyPassReverse /api/ http://localhost:8000/api/
    ProxyPass /docs http://localhost:8000/docs
    ProxyPassReverse /docs http://localhost:8000/docs
</VirtualHost>
```

## 📊 Funcionalidades Principales Implementadas

### ✅ Gestión de Productos
- Registro completo de productos
- Códigos QR automáticos
- Categorías y proveedores
- Búsqueda y filtrado avanzado

### ✅ Control de Inventario
- Entradas y salidas de stock
- Ajustes de inventario
- Historial completo de movimientos
- Validación de stock disponible

### ✅ Sistema de Alertas
- Alertas automáticas de stock mínimo
- Notificaciones de productos agotados
- Priorización por criticidad
- Gestión de alertas resueltas

### ✅ Reportes y Analytics
- Dashboard con gráficos interactivos
- Reportes de inventario en PDF/Excel
- Análisis de productos movimentados
- Valorización de inventario

### ✅ Gestión de Usuarios
- Sistema de roles (Admin/Operario)
- Autenticación segura
- Control de permisos
- Recuperación de contraseñas

### ✅ API REST
- Endpoints completos para todas las funciones
- Documentación automática con Swagger
- Autenticación JWT
- Validación de datos

## 🎯 Casos de Uso Implementados

Según tu documentación, implementé todos los casos de uso:

1. ✅ **RF01 - Registro de Productos**: Completo con todas las especificaciones
2. ✅ **RF02 - Registro de QR**: Generación automática de códigos QR
3. ✅ **RF03 - Escaneo de códigos QR**: Funcionalidad implementada
4. ✅ **RF04 - Alerta de Stock**: Sistema completo de alertas
5. ✅ **RF05 - Informes PDF/Excel**: Generación de reportes
6. ✅ **RF06 - Gestión por Usuario**: Control de roles y permisos
7. ✅ **RF07 - Registro de Usuario**: Sistema completo de registro
8. ✅ **RF08 - Inicio de sesión**: Autenticación segura

## 🛡️ Seguridad Implementada

- ✅ **Encriptación de contraseñas** con bcrypt
- ✅ **Sesiones seguras** con tokens JWT
- ✅ **Validación de datos** en todos los endpoints
- ✅ **Control de acceso** por roles de usuario
- ✅ **Protección CSRF** en formularios
- ✅ **Validación de entrada** para prevenir inyecciones

## 🎨 Interfaz de Usuario

- ✅ **Diseño responsive** para móvil, tablet y desktop
- ✅ **Bootstrap 5** para una interfaz moderna
- ✅ **Iconos Font Awesome** para mejor UX
- ✅ **Gráficos interactivos** con Chart.js
- ✅ **Tablas dinámicas** con DataTables
- ✅ **Modales y alertas** para mejor interacción

## 📈 Próximos Pasos

### 1. Verificar Requisitos del Sistema
- Python 3.8+
- MySQL 8.0+
- Apache 2.4+ (opcional)
- NetBeans IDE (recomendado)

### 2. Ejecutar Instalación
- Usar el script `setup.sh` para instalación automática
- O seguir los pasos manuales si prefieres más control

### 3. Configurar Base de Datos
- Importar `bd/stocktrack_base_datos.sql`
- Configurar PHPMyAdmin si lo deseas

### 4. Probar el Sistema
- Acceder a http://localhost:8000
- Usar credenciales por defecto
- Explorar todas las funcionalidades

## 🆘 Soporte

Si encuentras algún problema:

1. **Verificar logs**: Revisar `logs/stocktrack.log`
2. **Dependencias**: Asegurar que `requirements.txt` está instalado
3. **Base de datos**: Verificar conexión MySQL
4. **Puertos**: Verificar que puerto 8000 esté libre

## 📞 Credenciales de Demostración

Para probar el sistema inmediatamente:
```
Email: admin@stocktrack.com
Contraseña: admin123
```

**⚠️ IMPORTANTE**: Cambia estas credenciales en producción.

---

## 🎉 ¡Proyecto Completado!

El sistema **StockTrack** está completamente desarrollado y listo para usar. Incluye todas las funcionalidades solicitadas, está basado en tu arquitectura MVC, y está diseñado específicamente para el entorno universitario con NetBeans y Apache.

**Autor**: MiniMax Agent  
**Fecha**: 2025-11-11  
**Versión**: 1.0.0  

¡Disfruta usando tu nuevo sistema de gestión de inventarios! 🚀
