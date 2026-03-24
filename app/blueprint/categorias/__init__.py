# nombre para generar un modulo
from flask import Blueprint

maestros =  Blueprint(
    'categorias',
    __name__,
    template_folder = 'templates',
    static_folder = 'static'
)

from . import routes