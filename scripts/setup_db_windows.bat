@echo off
setlocal

cd /d "%~dp0\.."

echo [1/3] Verificando entorno virtual...
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: No existe .venv\Scripts\python.exe
  echo Crea el entorno primero: py -m venv .venv
  exit /b 1
)

echo [2/3] Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo [3/3] Sincronizando esquema de base de datos...
".venv\Scripts\python.exe" scripts\sync_db_schema.py
if errorlevel 1 exit /b 1

echo.
echo DB lista. Puedes iniciar con:
echo .venv\Scripts\flask --app app.py run --debug --port 5000

endlocal
