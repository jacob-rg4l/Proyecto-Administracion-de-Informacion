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
