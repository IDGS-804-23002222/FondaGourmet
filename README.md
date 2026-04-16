# FondaGourmet

Sistema web para gestion operativa de una fonda/restaurante.

Incluye modulos de:
- autenticacion y cuentas
- clientes
- pedidos
- caja y ventas
- compras y proveedores
- ingredientes, recetas, inventario y mermas
- dashboard y alertas

## Stack
- Flask
- SQLAlchemy + Flask-Migrate (MySQL/MariaDB)
- PyMongo (logs/tickets/eventos en Mongo)
- Jinja2 + Bootstrap/Tailwind segun modulo

## Requisitos
- Python 3.11+ (recomendado)
- MySQL/MariaDB activo
- MongoDB activo (si se usa bitacora/tickets)
- Entorno virtual `.venv`

## Clonar y preparar

### Linux/macOS
```bash
git clone https://github.com/IDGS-804-23002222/FondaGourmet
cd FondaGourmet
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
git clone https://github.com/IDGS-804-23002222/FondaGourmet
cd FondaGourmet
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuracion
Este proyecto carga configuracion desde [config.py](config.py).

Asegura que `SQLALCHEMY_DATABASE_URI`, `SECRET_KEY` y `MONGO_URI` apunten a tu ambiente.

## Levantar la app

### Linux/macOS
```bash
source .venv/bin/activate
flask --app app.py run --debug --port 5000
```

### Windows
```bat
.venv\Scripts\flask --app app.py run --debug --port 5000
```

## Setup / actualizacion de base de datos

### Setup inicial en Windows
- Script: [scripts/setup_db_windows.bat](scripts/setup_db_windows.bat)
- Alternativa: [scripts/setup_db_windows.ps1](scripts/setup_db_windows.ps1)
- Guia: [scripts/README_DB_SETUP.md](scripts/README_DB_SETUP.md)

### Actualizar proyecto (deps + migraciones + schema sync + snapshot)
- Script recomendado: [scripts/update_project_windows.bat](scripts/update_project_windows.bat)

Este script hace:
1. Upgrade de `pip/setuptools/wheel`
2. Instalacion de `requirements.txt`
3. `flask db upgrade`
4. `scripts/sync_db_schema.py`
5. Export de snapshot SQL de la BD

## Exportar BD

### Snapshot completo (estructura + datos)
- Script: [scripts/export_db_snapshot.py](scripts/export_db_snapshot.py)
- Comando:
```bash
.venv/bin/python scripts/export_db_snapshot.py scripts/fonda_snapshot_visual.sql
```

### Solo esquema
- Script: [scripts/export_db_schema.py](scripts/export_db_schema.py)
- Comando:
```bash
.venv/bin/python scripts/export_db_schema.py scripts/fonda_schema_export.sql
```

### Archivo de snapshot ya generado
- [scripts/fonda_snapshot_visual.sql](scripts/fonda_snapshot_visual.sql)

## Datos demo para pruebas
- Script: [scripts/seed_demo_data.py](scripts/seed_demo_data.py)
- Wrapper: [scripts/run_demo_seed.sh](scripts/run_demo_seed.sh)

Comando:
```bash
.venv/bin/python scripts/seed_demo_data.py
```

## Migraciones
Las migraciones viven en [migrations/versions](migrations/versions).

Comandos comunes:
```bash
flask --app app.py db current
flask --app app.py db upgrade
```

## Checklist de regresion rapida
- [scripts/CHECKLIST_REGRESION_10_MIN.md](scripts/CHECKLIST_REGRESION_10_MIN.md)

## Estructura principal
- [app.py](app.py): app factory, blueprints, login/csrf/migrate
- [models.py](models.py): modelos SQLAlchemy
- [modules](modules): modulos funcionales por dominio
- [templates](templates): vistas Jinja
- [static](static): assets front
- [scripts](scripts): utilidades de setup/migracion/export

## Notas operativas
- No aplicar cambios de esquema en produccion sin respaldo previo.
- Probar primero en staging.
- Si usas scripts de sync, revisar diff de schema antes de release.

## Licencia
Definir licencia del proyecto (MIT, privada, etc.).
