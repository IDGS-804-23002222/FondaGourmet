# Checklist de Regresion (10 minutos)

Objetivo: detectar rapido si un cambio rompio funcionalidades criticas antes de subir a produccion.

## 0) Preparacion (1 minuto)

- Activar entorno virtual.
- Confirmar que la DB apunta al ambiente correcto (staging o local de pruebas).
- Verificar que el servidor Mongo este arriba si se usa bitacora/tickets.

Comandos sugeridos:

```bash
/home/paulobot/FondaGourmet/.venv/bin/python -m flask --app app.py db current
/home/paulobot/FondaGourmet/.venv/bin/python - <<'PY'
from app import create_app
app = create_app()
print('MONGO_URI:', app.config.get('MONGO_URI'))
PY
```

## 1) Arranque y smoke general (2 minutos)

- Crear app sin errores.
- Revisar que no existan errores de analisis.
- Hacer smoke rapido de rutas GET/POST sin payload (esperar 2xx/3xx/4xx, nunca 5xx).

Comandos:

```bash
/home/paulobot/FondaGourmet/.venv/bin/python - <<'PY'
from app import create_app
app = create_app()
print('app_ok', bool(app), 'rules', len(list(app.url_map.iter_rules())))
PY
```

## 2) Base de datos critica (2 minutos)

Validar nulos/huertanos en tablas sensibles.

```sql
SELECT COUNT(*) FROM mermas WHERE tipo_articulo IS NULL OR articulo_id IS NULL OR usuario_id IS NULL OR fecha_registro IS NULL;
SELECT COUNT(*) FROM mermas m
LEFT JOIN inventario_terminado it ON it.id_inventario = m.articulo_id
WHERE m.tipo_articulo='InventarioTerminado' AND it.id_inventario IS NULL;
SELECT COUNT(*) FROM mermas m
LEFT JOIN materias_primas mp ON mp.id_materia = m.articulo_id
WHERE m.tipo_articulo='MateriaPrima' AND mp.id_materia IS NULL;
```

Criterio: todos en 0.

## 3) Flujo de mermas (2 minutos)

- Probar registro de merma de InventarioTerminado con cantidad decimal (debe rechazar).
- Probar registro de merma con cantidad entera (debe registrar).
- Confirmar que historial muestra observaciones cuando hay payload en Mongo.

Checks visuales:
- Mensaje esperado con decimal: "Para inventario terminado la cantidad debe ser un numero entero".
- En historial, columna "Observaciones" visible y con valor cuando exista.

## 4) Modulos Parcial (2 minutos)

Rutas dinamicas de bajo riesgo para smoke manual:

- /clientes/api/<id_cliente>
- /compras/ver/<id_compra>
- /ingredientes/detalle/<id>
- /ingredientes/editar/<id>
- /pedidos/detalles/<id_pedido>
- /produccion/ver/<id>
- /proveedores/<id_proveedor>
- /recetas/ver/<id_receta>

Criterio: 200 o 302 controlado; nunca 500.

## 5) Auth y sesion (1 minuto)

- Login valido.
- OTP correcto (si aplica en ambiente).
- Logout.

Criterio: sin errores de servidor y redireccion por rol correcta.

## Endpoints de riesgo (no correr sin plan)

Estos pueden mutar estado o inventario. Ejecutarlos solo en staging con plan de rollback:

- /produccion/iniciar/<id>
- /produccion/completar/<id>
- /produccion/cancelar/<id>
- /caja/anular/<id_venta>
- /tienda/agregar/<id>
- /tienda/aumentar/<id>
- /tienda/reducir/<id>

## Criterio final de Go/No-Go

Go:
- 0 errores 5xx
- Integridad DB critica en 0 incidencias
- Merma decimal rechazada y merma entera funcional
- Historial de mermas mostrando observaciones cuando existe payload

No-Go:
- Cualquier 5xx
- Cualquier huertano/nulo critico en mermas
- Cambios en inventario no explicados
