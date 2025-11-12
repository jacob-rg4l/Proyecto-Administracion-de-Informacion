@echo off
REM Script de Inicio para Windows - StockTrack
REM Autor: MiniMax Agent

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                   StockTrack Startup                         ║
echo ║              Sistema de Gestión de Inventarios               ║
echo ║                        v1.0.0                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Verificar si estamos en el directorio correcto
if not exist "app.py" (
    echo [ERROR] app.py no encontrado. Asegúrate de ejecutar este script en el directorio del proyecto.
    pause
    exit /b 1
)

echo [INFO] Iniciando StockTrack...

REM Verificar que existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado. Ejecuta setup.sh primero o crea el venv manualmente.
    echo [INFO] Para crear el venv: python -m venv venv
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar que existe .env
if not exist ".env" (
    echo [ERROR] Archivo .env no encontrado. Ejecuta setup.sh primero o copia .env.example a .env
    pause
    exit /b 1
)

REM Verificar dependencias
echo [INFO] Verificando dependencias...
python -c "import fastapi, sqlalchemy, pymysql" 2>nul
if errorlevel 1 (
    echo [ERROR] Dependencias no instaladas. Ejecuta: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Iniciar aplicación
echo [INFO] Iniciando servidor StockTrack...
echo.
echo [INFO] El sistema estará disponible en:
echo [INFO]   Web: http://localhost:8000
echo [INFO]   API Docs: http://localhost:8000/docs
echo.
echo [INFO] Para detener el servidor: Ctrl+C
echo.

REM Iniciar con uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

pause
