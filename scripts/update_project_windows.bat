@echo off
setlocal

cd /d "%~dp0\.."

echo [1/6] Verificando entorno virtual...
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: No existe .venv\Scripts\python.exe
  echo Crea el entorno primero: py -m venv .venv
  exit /b 1
)

echo [2/6] Actualizando herramientas base de Python...
".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 exit /b 1

echo [3/6] Actualizando dependencias del proyecto...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo [4/6] Ejecutando migraciones de base de datos...
set "FLASK_APP=app.py"
".venv\Scripts\python.exe" -m flask db upgrade
if errorlevel 1 exit /b 1

echo [5/6] Sincronizando compatibilidad de esquema...
".venv\Scripts\python.exe" scripts\sync_db_schema.py
if errorlevel 1 exit /b 1

echo [6/6] Exportando snapshot de base de datos...
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set "DB_SNAPSHOT=scripts\fonda_snapshot_%TS%.sql"
".venv\Scripts\python.exe" scripts\export_db_snapshot.py "%DB_SNAPSHOT%"
if errorlevel 1 exit /b 1

echo.
echo Proyecto actualizado correctamente.
echo Este script NO elimina tu base de datos; solo aplica migraciones y ajustes de esquema.
echo Snapshot generado en: %DB_SNAPSHOT%
echo.
echo Para iniciar la app:
echo .venv\Scripts\flask --app app.py run --debug --port 5000

endlocal