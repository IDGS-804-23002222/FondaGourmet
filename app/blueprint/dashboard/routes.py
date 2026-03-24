from flask import Blueprint, request, jsonify
from app.extensions import db, app
from app.models import Venta, DetalleVenta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    stats = list(app.mongo.dashboard_cache.find().sort("fecha", -1).limit(1))[0]
    return render_template('dashboard.html', stats=stats)

@dashboard_bp.route('/resumen-ventas', methods=['GET'])
def resumen_ventas():
    resumen = app.mongo.resumen_ventas.find_one(sort=[("fecha", -1)])
    return jsonify(resumen)

