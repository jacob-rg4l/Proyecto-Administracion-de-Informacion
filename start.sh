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
