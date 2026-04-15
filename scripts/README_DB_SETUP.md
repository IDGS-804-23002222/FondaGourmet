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
   - aplica `scripts/schema_compras_proveedores_robusto.sql` (compras/detalle robustos: contado/credito, tarjeta, recepcion por linea)
   - aplica `scripts/schema_mermas_ajustes.sql` (tabla `mermas`, indices y reglas de motivos/costos)
   - evita conflicto con entornos legacy que ya tengan tablas `caja`/`movimientos_caja`
   - crea tablas nuevas de categorias separadas si faltan
   - agrega columnas FK nuevas si faltan
   - agrega/normaliza `recetas.porciones` (default 1, no nulo)
   - hace nullable las columnas legacy `id_categoria` en `productos` y `materias_primas`
   - rellena datos iniciales de categorias
   - agrega constraints FK faltantes

## Catalogo de scripts (referencia)
- `scripts/sync_db_schema.py`: script recomendado para entornos nuevos o locales. Aplica cambios de forma idempotente.
- `scripts/schema_caja_sesiones_movimientos.sql`: esquema de caja extendido + vistas de compatibilidad.
- `scripts/schema_recetas_inventario_terminado.sql`: rendimiento por porciones + inventario terminado.
- `scripts/schema_compras_proveedores_robusto.sql`: refuerzo de compras/detalle con recepcion por linea.
- `scripts/schema_mermas_ajustes.sql`: estructura de mermas y validaciones.
- `scripts/schema_clientes.sql`: ajustes de clientes.

## Produccion (importante)
- Respeta la base actual de produccion: no apliques scripts sueltos sin respaldo previo.
- Haz backup antes de cualquier cambio de esquema.
- Primero prueba en staging/copia de produccion.
- Para despliegue controlado, prioriza migraciones Alembic versionadas.
- Usa `scripts/sync_db_schema.py` solo cuando el equipo valide que su alcance coincide con el release.
- Verifica despues del despliegue: tablas, columnas, constraints e integridad de datos.

## Iniciar app

.venv\Scripts\flask --app app.py run --debug --port 5000
