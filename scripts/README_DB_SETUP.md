# DB setup para Windows (FondaGourmet)

Este paquete deja la base lista para trabajar con la version actual del proyecto.

## Requisitos
- Python instalado
- MySQL levantado
- DB/config accesible con la configuracion del proyecto (`config.py`)
- Entorno virtual `.venv`

## Opcion 1: BAT (doble click o CMD)
Ejecuta:

scripts\setup_db_windows.bat

## Opcion 2: PowerShell
Ejecuta:

powershell -ExecutionPolicy Bypass -File scripts\setup_db_windows.ps1

## Que hace
1. Instala dependencias de `requirements.txt`
2. Sincroniza esquema con `scripts/sync_db_schema.py`
   - aplica `scripts/schema_caja_sesiones_movimientos.sql` (tablas `caja_sesiones` y `caja_movimientos`)
   - aplica `scripts/schema_recetas_inventario_terminado.sql` (columna `recetas.rendimiento_porciones` + tabla `inventario_terminado`)
   - evita conflicto con entornos legacy que ya tengan tablas `caja`/`movimientos_caja`
   - crea tablas nuevas de categorias separadas si faltan
   - agrega columnas FK nuevas si faltan
   - agrega/normaliza `recetas.porciones` (default 1, no nulo)
   - hace nullable las columnas legacy `id_categoria` en `productos` y `materias_primas`
   - rellena datos iniciales de categorias
   - agrega constraints FK faltantes

## Iniciar app

.venv\Scripts\flask --app app.py run --debug --port 5000
