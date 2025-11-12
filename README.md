# StockTrack - Sistema de Gestión de Inventarios

![StockTrack Logo](https://img.shields.io/badge/StockTrack-v1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

StockTrack es un sistema web moderno para la gestión eficiente de inventarios diseñado específicamente para pequeñas y medianas empresas. Desarrollado con FastAPI, SQLAlchemy, Bootstrap 5 y MySQL, ofrece una interfaz intuitiva, funcionalidades avanzadas de gestión de stock, generación de códigos QR, alertas automáticas y reportes detallados.

## 🚀 Características Principales

### 📦 Gestión de Productos
- ✅ Registro completo de productos con categorías y proveedores
- ✅ Generación automática de códigos QR únicos
- ✅ Gestión de stock con control de mínimos
- ✅ Búsqueda y filtrado avanzado
- ✅ Importación/exportación de datos

### 📊 Movimientos de Inventario
- ✅ Registro de entradas y salidas
- ✅ Ajustes de stock con trazabilidad
- ✅ Historial completo de movimientos
- ✅ Validación automática de stock disponible

### 🚨 Sistema de Alertas
- ✅ Alertas automáticas de stock mínimo
- ✅ Notificaciones de productos agotados
- ✅ Alertas de exceso de inventario
- ✅ Priorización por criticidad

### 📈 Reportes y Analytics
- ✅ Reportes de inventario en Excel/PDF
- ✅ Dashboard interactivo con gráficos
- ✅ Análisis de productos más movimentados
- ✅ Valorización de inventario

### 👥 Gestión de Usuarios
- ✅ Sistema de roles (Administrador/Operario)
- ✅ Autenticación segura con sesiones
- ✅ Control de permisos granulares
- ✅ Recuperación de contraseñas

### 🔍 Funcionalidades Adicionales
- ✅ Interfaz responsive (móvil, tablet, desktop)
- ✅ Códigos QR para consulta rápida
- ✅ Integración con PHPMyAdmin
- ✅ Backup automático de datos
- ✅ API REST completa

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Backend | FastAPI | Latest |
| Base de Datos | MySQL | 8.0+ |
| ORM | SQLAlchemy | 2.0+ |
| Frontend | Bootstrap 5, jQuery | 5.3, 3.6+ |
| Autenticación | JWT, Bcrypt | - |
| QR Codes | qrcode, Pillow | 7.4+ |
| Gráficos | Chart.js, Matplotlib | 4.0+, 3.8+ |
| Reportes | Pandas, ReportLab, OpenPyXL | 2.1+ |

## 📋 Requisitos del Sistema

### Software Necesario
- **Python 3.8+**
- **MySQL 8.0+**
- **Apache 2.4+** (para integración web)
- **NetBeans IDE 20+** (recomendado)
- **PHPMyAdmin** (opcional, para gestión de BD)

### Requisitos de Hardware
- **RAM**: Mínimo 2GB, Recomendado 4GB+
- **Espacio en disco**: Mínimo 1GB
- **Procesador**: Cualquier CPU moderna
- **Conexión**: Internet para dependencias

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
# Crear directorio del proyecto
mkdir StockTrack
cd StockTrack

# Copiar todos los archivos del proyecto aquí
# (Los archivos ya están en la carpeta StockTrack)
```

### 2. Configurar Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Actualizar pip
python -m pip install --upgrade pip
```

### 3. Instalar Dependencias
```bash
# Instalar todas las dependencias
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

#### 4.1 Crear Base de Datos MySQL
```sql
-- Abrir MySQL o PHPMyAdmin
-- Ejecutar el script de creación de BD
SOURCE bd/stocktrack_base_datos.sql;
```

#### 4.2 Configurar Conexión
```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuración de BD en .env
nano .env
```

**Configuración mínima en .env:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password_mysql
DB_NAME=stocktrack_db
SECRET_KEY=tu-clave-secreta-muy-larga-aqui
```

### 5. Ejecutar la Aplicación
```bash
# Ejecutar servidor de desarrollo
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# O usar el archivo Python directamente
python app.py
```

### 6. Acceder al Sistema
- **URL del Sistema**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## 🔐 Credenciales por Defecto

### Usuario Administrador
```
Email: admin@stocktrack.com
Contraseña: admin123
```

**⚠️ IMPORTANTE**: Cambiar la contraseña del administrador en producción.

## 🌐 Configuración con NetBeans y Apache

### 1. Abrir Proyecto en NetBeans
```
File → Open Project → Seleccionar carpeta StockTrack
```

### 2. Configurar Interpretador Python
```
Tools → Options → Python
Select: Python 3.x Interpreter (venv/bin/python)
```

### 3. Ejecutar con NetBeans
```
Run → Run Project (F6)
O usar el panel de servicios para administrar
```

### 4. Configurar Apache (Opcional)
```apache
# En httpd.conf o sitios disponibles
<VirtualHost *:80>
    ServerName stocktrack.local
    ProxyPass /api/ http://localhost:8000/api/
    ProxyPassReverse /api/ http://localhost:8000/api/
    ProxyPass /docs http://localhost:8000/docs
    ProxyPassReverse /docs http://localhost:8000/docs
</VirtualHost>
```

## 📊 Gestión de Base de Datos con PHPMyAdmin

### 1. Instalar PHPMyAdmin
```bash
# En Ubuntu/Debian
sudo apt install phpmyadmin

# En CentOS/RHEL
sudo yum install phpmyadmin
```

### 2. Configurar Acceso
- **URL**: http://localhost/phpmyadmin
- **Usuario**: root
- **Contraseña**: (tu password de MySQL)

### 3. Importar Script SQL
```sql
-- En PHPMyAdmin, pestaña "Import"
-- Seleccionar archivo: bd/stocktrack_base_datos.sql
-- Hacer clic en "Continuar"
```

### 4. Verificar Tablas Creadas
```
stocktrack_db
├── usuarios
├── categorias
├── proveedores
├── productos
├── movimientos_inventario
├── alertas_stock
├── sesiones_usuario
└── configuraciones
```

## 🚀 Despliegue en Producción

### 1. Configurar Variables de Entorno
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
SECRET_KEY=clave-super-secreta-de-produccion
DB_PASSWORD=password-seguro-produccion
```

### 2. Usar Gunicorn para Producción
```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar con Gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. Configurar Proxy Reverso con Nginx
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/StockTrack/static/;
    }
}
```

### 4. Configurar SSL con Let's Encrypt
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com
```

## 📱 Uso del Sistema

### Dashboard Principal
- **Acceso**: http://localhost:8000/dashboard
- **Funciones**: Vista general del inventario, alertas activas, estadísticas
- **Características**: Gráficos interactivos, actualización automática

### Gestión de Productos
- **Acceso**: http://localhost:8000/productos
- **Funciones**: Crear, editar, eliminar productos
- **Características**: Códigos QR, búsqueda, filtros

### Movimientos de Inventario
- **Acceso**: http://localhost:8000/inventario
- **Funciones**: Registrar entradas, salidas, ajustes
- **Características**: Validación de stock, trazabilidad completa

### Alertas
- **Acceso**: http://localhost:8000/alertas
- **Funciones**: Ver y resolver alertas de stock
- **Características**: Priorización, asignaciones

### Reportes
- **Acceso**: http://localhost:8000/reportes
- **Funciones**: Generar reportes de inventario y movimientos
- **Formatos**: PDF, Excel, CSV

## 🔧 API REST

### Autenticación
```http
POST /login
Content-Type: application/x-www-form-urlencoded

email=admin@stocktrack.com&password=admin123
```

### Productos
```http
GET /api/productos
Authorization: Bearer <token>

POST /api/productos
Authorization: Bearer <token>
Content-Type: application/json

{
  "codigo_producto": "PROD-001",
  "nombre_producto": "Producto de Ejemplo",
  "id_categoria": 1,
  "id_proveedor": 1,
  "precio_compra": 10.50,
  "precio_venta": 15.00,
  "stock_minimo": 5
}
```

### Movimientos
```http
POST /api/productos/1/entrada
Authorization: Bearer <token>
Content-Type: application/json

{
  "cantidad": 10,
  "motivo": "Compra a proveedor",
  "costo_unitario": 10.50
}
```

## 🧪 Testing

### Ejecutar Pruebas
```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar todas las pruebas
pytest

# Ejecutar con coverage
pytest --cov=controlador --cov=modelo
```

### Estructura de Pruebas
```
tests/
├── test_auth.py
├── test_productos.py
├── test_movimientos.py
├── test_reportes.py
└── conftest.py
```

## 🐛 Solución de Problemas

### Errores Comunes

#### 1. Error de Conexión a Base de Datos
```bash
# Verificar MySQL
sudo systemctl status mysql
sudo systemctl start mysql

# Verificar credenciales
mysql -u root -p
```

#### 2. Error de Dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

#### 3. Puerto en Uso
```bash
# Verificar procesos en puerto 8000
lsof -i :8000

# Matar proceso si es necesario
kill -9 <PID>
```

#### 4. Problemas con QR
```bash
# Instalar Pillow si faltan fuentes
pip install --upgrade pillow
```

### Logs del Sistema
```bash
# Ver logs de la aplicación
tail -f logs/stocktrack.log

# Logs de Apache
sudo tail -f /var/log/apache2/error.log

# Logs de MySQL
sudo tail -f /var/log/mysql/error.log
```

## 📚 Documentación Adicional

### Estructura del Proyecto
```
StockTrack/
├── app.py                 # Aplicación principal FastAPI
├── requirements.txt       # Dependencias Python
├── .env.example          # Configuración de ejemplo
├── config/               # Configuraciones
│   └── database.py
├── modelo/               # Modelos SQLAlchemy
│   ├── __init__.py
│   ├── usuario.py
│   ├── producto.py
│   ├── categoria.py
│   ├── proveedor.py
│   ├── movimiento_inventario.py
│   ├── alerta_stock.py
│   ├── sesion_usuario.py
│   └── configuracion.py
├── controlador/          # Lógica de negocio
│   ├── __init__.py
│   ├── auth.py
│   ├── producto.py
│   └── reportes.py
├── vista/               # Interfaz de usuario
│   └── (templates HTML)
├── static/              # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── imagenes/
├── bd/                  # Base de datos
│   └── stocktrack_base_datos.sql
└── logs/                # Logs del sistema
```

### Patrones de Diseño Utilizados
- **MVC (Modelo-Vista-Controlador)**
- **Repository Pattern** (para acceso a datos)
- **Factory Pattern** (para creación de objetos)
- **Singleton** (para conexiones de BD)

## 🤝 Contribuciones

Este es un proyecto de universidad. Para mejoras o contribuciones:

1. Fork el proyecto
2. Crear branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autores

- **MiniMax Agent** - *Desarrollo Completo* - Sistema de Gestión de Inventarios para Universidad

## 🙏 Agradecimientos

- **Bootstrap Team** - Framework CSS
- **FastAPI Team** - Framework web
- **SQLAlchemy Team** - ORM
- **MySQL Team** - Base de datos
- **Comunidad Python** - Librerías y herramientas

## 📞 Soporte

Para soporte técnico o consultas:

- **Email**: soporte@stocktrack.com
- **Documentación**: http://localhost:8000/docs
- **Issues**: Crear issue en el repositorio

---

**⭐ Si este proyecto te es útil, no olvides darle una estrella!**

*Desarrollado con ❤️ para facilitar la gestión de inventarios en pequeñas y medianas empresas.*
# Proyecto-Administracion-de-Informacion
