from sqlalchemy import text

def obtener_estadisticas_ventas(mongo_db):
    try:
        stats = mongo_db.dashboard_cache.find_one(sort=[("fecha", -1)])
        return stats, None
    except Exception as e:
        return None, str(e)
    
def obtener_resumen_ventas(mongo_db):
    try:
        resumen = mongo_db.resumen_ventas.find_one(sort=[("fecha", -1)])
        return resumen, None    
    except Exception as e:
        return None, str(e)

def obtener_ventas_por_producto(mongo_db):
    try:
        ventas_producto = list(mongo_db.ventas_por_producto.find().sort("fecha", -1).limit(10))
        return ventas_producto, None
    except Exception as e:
        return None, str(e)     