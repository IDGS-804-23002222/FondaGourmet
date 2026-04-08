$ErrorActionPreference = 'Stop'

Set-Location (Join-Path $PSScriptRoot '..')

Write-Host '[1/3] Verificando entorno virtual...'
if (-not (Test-Path '.venv/Scripts/python.exe')) {
    throw 'No existe .venv/Scripts/python.exe. Crea el entorno primero: py -m venv .venv'
}

Write-Host '[2/3] Instalando dependencias...'
& '.venv/Scripts/python.exe' -m pip install -r requirements.txt

Write-Host '[3/3] Sincronizando esquema de base de datos...'
& '.venv/Scripts/python.exe' 'scripts/sync_db_schema.py'

Write-Host ''
Write-Host 'DB lista. Puedes iniciar con:'
Write-Host '.venv/Scripts/flask --app app.py run --debug --port 5000'
