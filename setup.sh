#!/bin/bash
# Script de Instalación Automática - StockTrack
# Autor: MiniMax Agent

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[ÉXITO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ADVERTENCIA]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   StockTrack Installation                    ║"
echo "║              Sistema de Gestión de Inventarios               ║"
echo "║                        v1.0.0                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar si estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    print_error "app.py no encontrado. Asegúrate de ejecutar este script en el directorio del proyecto."
    exit 1
fi

print_status "Iniciando instalación de StockTrack..."

# 1. Verificar Python
print_status "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION encontrado"
else
    print_error "Python 3 no está instalado. Instala Python 3.8+ e intenta de nuevo."
    exit 1
fi

# 2. Crear entorno virtual
print_status "Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Entorno virtual creado"
else
    print_warning "Entorno virtual ya existe"
fi

# 3. Activar entorno virtual
print_status "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"

# 4. Actualizar pip
print_status "Actualizando pip..."
pip install --upgrade pip
print_success "pip actualizado"

# 5. Instalar dependencias
print_status "Instalando dependencias..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencias instaladas"
else
    print_error "requirements.txt no encontrado"
    exit 1
fi

# 6. Configurar archivo de entorno
print_status "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Archivo .env creado desde .env.example"
    print_warning "¡IMPORTANTE! Edita el archivo .env con tu configuración de base de datos"
else
    print_warning "Archivo .env ya existe"
fi

# 7. Verificar MySQL
print_status "Verificando MySQL..."
if command -v mysql &> /dev/null; then
    print_success "MySQL encontrado"
else
    print_warning "MySQL no encontrado en PATH. Asegúrate de que esté instalado y en PATH"
fi

# 8. Crear base de datos
print_status "Creando base de datos..."
read -p "¿Quieres crear la base de datos automáticamente? (y/n): " CREATE_DB
if [ "$CREATE_DB" = "y" ] || [ "$CREATE_DB" = "Y" ]; then
    read -p "Host de MySQL [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    read -p "Puerto de MySQL [3306]: " DB_PORT
    DB_PORT=${DB_PORT:-3306}
    read -p "Usuario de MySQL [root]: " DB_USER
    DB_USER=${DB_USER:-root}
    read -s -p "Password de MySQL: " DB_PASSWORD
    echo
    read -p "Nombre de la base de datos [stocktrack_db]: " DB_NAME
    DB_NAME=${DB_NAME:-stocktrack_db}
    
    # Crear base de datos
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Base de datos $DB_NAME creada"
        
        # Importar esquema
        if [ -f "bd/stocktrack_base_datos.sql" ]; then
            mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < bd/stocktrack_base_datos.sql 2>/dev/null
            if [ $? -eq 0 ]; then
                print_success "Esquema de base de datos importado"
            else
                print_warning "No se pudo importar el esquema automáticamente. Importa manualmente bd/stocktrack_base_datos.sql"
            fi
        fi
        
        # Actualizar .env
        sed -i "s/DB_HOST=.*/DB_HOST=$DB_HOST/" .env
        sed -i "s/DB_PORT=.*/DB_PORT=$DB_PORT/" .env
        sed -i "s/DB_USER=.*/DB_USER=$DB_USER/" .env
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
        sed -i "s/DB_NAME=.*/DB_NAME=$DB_NAME/" .env
        print_success "Configuración de base de datos guardada en .env"
    else
        print_error "No se pudo crear la base de datos. Verifica tus credenciales"
    fi
else
    print_warning "Saltando creación automática de base de datos"
fi

# 9. Crear directorios necesarios
print_status "Creando directorios necesarios..."
mkdir -p logs
mkdir -p backups
mkdir -p temp
print_success "Directorios creados"

# 10. Configurar permisos (Linux/Mac)
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    chmod +x venv/bin/activate
    print_success "Permisos configurados"
fi

# 11. Crear script de inicio
print_status "Creando script de inicio..."
cat > start.sh << 'EOF'
#!/bin/bash
# Script de inicio de StockTrack

echo "Iniciando StockTrack..."

# Activar entorno virtual
source venv/bin/activate

# Verificar que existe .env
if [ ! -f ".env" ]; then
    echo "Error: Archivo .env no encontrado. Ejecuta setup.sh primero."
    exit 1
fi

# Iniciar aplicación
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
EOF

chmod +x start.sh
print_success "Script start.sh creado"

# 12. Crear script de desarrollo
cat > dev.sh << 'EOF'
#!/bin/bash
# Script de desarrollo para StockTrack

echo "Iniciando StockTrack en modo desarrollo..."

# Activar entorno virtual
source venv/bin/activate

# Verificar que existe .env
if [ ! -f ".env" ]; then
    echo "Error: Archivo .env no encontrado. Ejecuta setup.sh primero."
    exit 1
fi

# Verificar que la base de datos existe
echo "Verificando base de datos..."
python -c "
from config.database import crear_tablas
crear_tablas()
print('✓ Base de datos verificada')
"

# Iniciar aplicación con auto-reload
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level debug
EOF

chmod +x dev.sh
print_success "Script dev.sh creado"

# 13. Verificar instalación
print_status "Verificando instalación..."
python -c "
try:
    import fastapi
    import sqlalchemy
    import pymysql
    print('✓ FastAPI:', fastapi.__version__)
    print('✓ SQLAlchemy:', sqlalchemy.__version__)
    print('✓ PyMySQL instalado')
    print('✓ Todas las dependencias verificadas')
except ImportError as e:
    print('✗ Error:', e)
    exit(1)
"

# 14. Información final
echo
print_success "¡Instalación completada!"
echo
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                     PRÓXIMOS PASOS                       ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo
echo "1. Edita el archivo .env con tu configuración:"
echo "   nano .env"
echo
echo "2. Inicia el servidor:"
echo "   ./start.sh"
echo
echo "3. Accede al sistema:"
echo "   🌐 Web: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo
echo "4. Credenciales por defecto:"
echo "   📧 Email: admin@stocktrack.com"
echo "   🔑 Password: admin123"
echo
echo "5. Para desarrollo:"
echo "   ./dev.sh"
echo
echo "6. Para crear base de datos (si no se hizo automáticamente):"
echo "   mysql -u root -p < bd/stocktrack_base_datos.sql"
echo
echo -e "${YELLOW}¡IMPORTANTE!${NC} Cambia la contraseña del administrador en producción."
echo
print_success "¡StockTrack está listo para usar!"
