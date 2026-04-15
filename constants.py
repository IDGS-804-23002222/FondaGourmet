from enum import Enum


class EstadoCompra(str, Enum):
    PENDIENTE = 'Pendiente'
    EN_CAMINO = 'En Camino'
    COMPLETADA = 'Completada'
    CANCELADA = 'Cancelada'


class MotivoMerma(str, Enum):
    CADUCIDAD = 'Caducidad'
    DANO = 'Daño'
    ERROR_PRODUCCION = 'Error de Producción'
    ROBO = 'Robo'
    OTRO = 'Otro'


class EstadoPedido(str, Enum):
    PENDIENTE = 'Pendiente'
    PAGADO = 'Pagado'
    COMPLETADO = 'Completado'
    CANCELADO = 'Cancelado'