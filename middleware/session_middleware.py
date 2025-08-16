# Middleware para validación automática de sesiones en requests
from functools import wraps
from flask import request, jsonify, g
import logging

from services.session_manager import GestorSesiones

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

# Instancia global del gestor de sesiones
gestor_sesiones = GestorSesiones()

def requiere_sesion_valida(f):
    """
    Decorador que valida la sesión antes de ejecutar el endpoint
    Verifica que el request tenga una sesión válida y activa
    """
    @wraps(f)
    def funcion_decorada(*args, **kwargs):
        # Obtener ID de sesión desde headers o parámetros
        id_sesion = request.headers.get('X-Session-ID') or request.json.get('sessionId') if request.json else None
        
        if not id_sesion:
            logger.warning("Request sin ID de sesión")
            return jsonify({
                'error': 'sesion_requerida',
                'mensaje': 'Se requiere un ID de sesión válido',
                'codigo': 'SESSION_REQUIRED'
            }), 401
        
        # Validar la sesión
        sesion = gestor_sesiones.validar_sesion(id_sesion)
        if not sesion:
            logger.warning(f"Sesión inválida: {id_sesion}")
            return jsonify({
                'error': 'sesion_invalida',
                'mensaje': 'La sesión no existe o ha expirado',
                'codigo': 'INVALID_SESSION'
            }), 401
        
        # Verificar límites de velocidad
        resultado_limite = gestor_sesiones.aplicar_limitacion_velocidad(id_sesion)
        if not resultado_limite['permitido']:
            logger.warning(f"Límite de velocidad excedido para sesión: {id_sesion}")
            return jsonify({
                'error': 'limite_velocidad',
                'mensaje': 'Demasiadas solicitudes. Intente más tarde.',
                'codigo': 'RATE_LIMIT_EXCEEDED',
                'reintentar_despues': resultado_limite.get('reintentar_despues')
            }), 429
        
        # Almacenar sesión en contexto global de Flask
        g.sesion_actual = sesion
        g.id_sesion = id_sesion
        
        # Ejecutar la función original
        return f(*args, **kwargs)
    
    return funcion_decorada

def registrar_interaccion(tipo_interaccion: str = 'general'):
    """
    Decorador para registrar automáticamente interacciones en la sesión
    Args:
        tipo_interaccion: Tipo de interacción a registrar (chat, upload, etc.)
    """
    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            # Verificar que hay una sesión en el contexto
            if not hasattr(g, 'id_sesion'):
                logger.error("Intento de registrar interacción sin sesión válida")
                return jsonify({
                    'error': 'sesion_requerida',
                    'mensaje': 'No hay sesión activa para registrar interacción'
                }), 401
            
            # Registrar la interacción
            if not gestor_sesiones.rastrear_interaccion(g.id_sesion, tipo_interaccion):
                logger.warning(f"Límite de interacciones excedido para sesión: {g.id_sesion}")
                return jsonify({
                    'error': 'limite_interacciones',
                    'mensaje': 'Se ha alcanzado el límite de interacciones para esta sesión',
                    'codigo': 'INTERACTION_LIMIT_EXCEEDED'
                }), 429
            
            # Ejecutar la función original
            return f(*args, **kwargs)
        
        return funcion_decorada
    return decorador

def limpiar_sesiones_expiradas():
    """
    Función utilitaria para limpiar sesiones expiradas
    Debe ser llamada periódicamente por un scheduler
    """
    sesiones_limpiadas = gestor_sesiones.limpiar_sesiones_expiradas()
    if sesiones_limpiadas > 0:
        logger.info(f"Limpiadas {sesiones_limpiadas} sesiones expiradas")
    return sesiones_limpiadas

def obtener_estadisticas_sesiones():
    """
    Obtiene estadísticas actuales del sistema de sesiones
    Returns:
        Dict con estadísticas de sesiones
    """
    return gestor_sesiones.obtener_estadisticas_sesion()