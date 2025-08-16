# Rutas de API para funcionalidad de chat
from flask import Blueprint, request, jsonify, g
import logging
from datetime import datetime
import time

from services.motor_chat import MotorChat
from middleware.session_middleware import requiere_sesion_valida, registrar_interaccion
from config import Config

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

# Crear blueprint para rutas de chat
bp_chat = Blueprint('chat', __name__, url_prefix='/api/chat')

# Inicializar motor de chat con configuración
motor_chat = MotorChat(Config.OPENAI_API_KEY)

@bp_chat.route('/ask', methods=['POST'])
@requiere_sesion_valida
@registrar_interaccion('chat')
def procesar_consulta_chat():
    """
    Endpoint principal para procesar consultas de chat
    Recibe una consulta del usuario y retorna respuesta del asistente técnico
    """
    inicio_tiempo = time.time()
    
    try:
        # Validar que el request tenga contenido JSON
        if not request.json:
            logger.warning("Request sin contenido JSON")
            return jsonify({
                'error': 'datos_invalidos',
                'mensaje': 'Se requiere contenido JSON en el request',
                'codigo': 'INVALID_JSON'
            }), 400
        
        # Extraer datos del request
        datos_request = request.json
        mensaje_usuario = datos_request.get('message', '').strip()
        contexto_adicional = datos_request.get('context', {})
        
        # Validar que hay un mensaje
        if not mensaje_usuario:
            logger.warning("Request sin mensaje de usuario")
            return jsonify({
                'error': 'mensaje_requerido',
                'mensaje': 'Se requiere un mensaje para procesar',
                'codigo': 'MESSAGE_REQUIRED'
            }), 400
        
        # Validar longitud del mensaje
        if len(mensaje_usuario) > 1000:
            logger.warning(f"Mensaje demasiado largo: {len(mensaje_usuario)} caracteres")
            return jsonify({
                'error': 'mensaje_muy_largo',
                'mensaje': 'El mensaje no puede exceder 1000 caracteres',
                'codigo': 'MESSAGE_TOO_LONG'
            }), 400
        
        # Obtener información de la sesión desde el contexto de Flask
        id_sesion = g.id_sesion
        sesion_actual = g.sesion_actual
        
        # Preparar contexto para el motor de chat
        contexto_completo = {
            'id_usuario': sesion_actual.id_usuario,
            'contador_interacciones': sesion_actual.contador_interacciones,
            'timestamp_sesion': sesion_actual.creada_en.isoformat(),
            **contexto_adicional
        }
        
        logger.info(f"Procesando consulta de chat para sesión {id_sesion}: {mensaje_usuario[:50]}...")
        
        # Procesar consulta con el motor de chat
        respuesta_chat = motor_chat.procesar_consulta(
            consulta=mensaje_usuario,
            id_sesion=id_sesion,
            contexto=contexto_completo
        )
        
        # Calcular tiempo de respuesta
        tiempo_respuesta = time.time() - inicio_tiempo
        
        # Preparar respuesta final
        respuesta_final = {
            'respuesta': respuesta_chat['mensaje'],
            'confianza': respuesta_chat['puntuacion_confianza'],
            'contenido_visual': respuesta_chat['contenido_visual'],
            'acciones_sugeridas': respuesta_chat['acciones_sugeridas'],
            'requiere_clarificacion': respuesta_chat['requiere_clarificacion'],
            'tipo_consulta': respuesta_chat['tipo_consulta'],
            'metadata': {
                'tiempo_respuesta_segundos': round(tiempo_respuesta, 2),
                'timestamp': datetime.now().isoformat(),
                'id_sesion': id_sesion,
                'contador_interacciones': sesion_actual.contador_interacciones
            }
        }
        
        # Log de éxito
        logger.info(f"Consulta procesada exitosamente en {tiempo_respuesta:.2f}s para sesión {id_sesion}")
        
        return jsonify(respuesta_final), 200
        
    except Exception as e:
        # Log del error
        logger.error(f"Error procesando consulta de chat: {str(e)}")
        
        # Respuesta de error
        return jsonify({
            'error': 'error_interno',
            'mensaje': 'Ocurrió un error interno procesando tu consulta. Intenta nuevamente.',
            'codigo': 'INTERNAL_ERROR',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp_chat.route('/clarify', methods=['POST'])
@requiere_sesion_valida
@registrar_interaccion('clarificacion')
def manejar_clarificacion():
    """
    Endpoint para manejar clarificaciones de consultas ambiguas
    Procesa clarificaciones adicionales del usuario
    """
    try:
        # Validar contenido JSON
        if not request.json:
            return jsonify({
                'error': 'datos_invalidos',
                'mensaje': 'Se requiere contenido JSON'
            }), 400
        
        datos_request = request.json
        consulta_original = datos_request.get('original_query', '')
        clarificacion = datos_request.get('clarification', '')
        
        # Validar datos requeridos
        if not consulta_original or not clarificacion:
            return jsonify({
                'error': 'datos_incompletos',
                'mensaje': 'Se requiere consulta original y clarificación'
            }), 400
        
        # Combinar consulta original con clarificación
        consulta_completa = f"Consulta original: {consulta_original}\nClarificación: {clarificacion}"
        
        # Procesar con el motor de chat
        respuesta_chat = motor_chat.procesar_consulta(
            consulta=consulta_completa,
            id_sesion=g.id_sesion,
            contexto={'tipo': 'clarificacion'}
        )
        
        # Preparar respuesta
        respuesta_final = {
            'respuesta': respuesta_chat['mensaje'],
            'confianza': respuesta_chat['puntuacion_confianza'],
            'contenido_visual': respuesta_chat['contenido_visual'],
            'acciones_sugeridas': respuesta_chat['acciones_sugeridas'],
            'metadata': {
                'tipo': 'clarificacion',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        logger.info(f"Clarificación procesada para sesión {g.id_sesion}")
        return jsonify(respuesta_final), 200
        
    except Exception as e:
        logger.error(f"Error procesando clarificación: {str(e)}")
        return jsonify({
            'error': 'error_interno',
            'mensaje': 'Error procesando clarificación'
        }), 500

@bp_chat.route('/history', methods=['GET'])
@requiere_sesion_valida
def obtener_historial_chat():
    """
    Endpoint para obtener historial de chat de la sesión actual
    Retorna las últimas interacciones de la sesión
    """
    try:
        # Obtener parámetros de consulta
        limite = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validar límites
        if limite > 100:
            limite = 100
        if limite < 1:
            limite = 20
            
        # En una implementación real, aquí se consultaría la base de datos
        # Por ahora, retornamos un historial simulado
        historial_simulado = {
            'mensajes': [
                {
                    'id': 'msg_001',
                    'tipo': 'usuario',
                    'contenido': 'Ejemplo de consulta anterior',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'total': 1,
            'limite': limite,
            'offset': offset,
            'sesion_id': g.id_sesion
        }
        
        logger.info(f"Historial de chat solicitado para sesión {g.id_sesion}")
        return jsonify(historial_simulado), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        return jsonify({
            'error': 'error_interno',
            'mensaje': 'Error obteniendo historial de chat'
        }), 500

@bp_chat.route('/feedback', methods=['POST'])
@requiere_sesion_valida
def enviar_feedback():
    """
    Endpoint para recibir feedback sobre respuestas del chat
    Permite a los usuarios calificar la utilidad de las respuestas
    """
    try:
        if not request.json:
            return jsonify({
                'error': 'datos_invalidos',
                'mensaje': 'Se requiere contenido JSON'
            }), 400
        
        datos_feedback = request.json
        id_mensaje = datos_feedback.get('message_id')
        calificacion = datos_feedback.get('rating')  # 1-5 estrellas
        comentario = datos_feedback.get('comment', '')
        
        # Validar datos
        if not id_mensaje or not calificacion:
            return jsonify({
                'error': 'datos_incompletos',
                'mensaje': 'Se requiere ID de mensaje y calificación'
            }), 400
        
        if not isinstance(calificacion, int) or calificacion < 1 or calificacion > 5:
            return jsonify({
                'error': 'calificacion_invalida',
                'mensaje': 'La calificación debe ser un número entre 1 y 5'
            }), 400
        
        # Registrar feedback (en implementación real se guardaría en BD)
        feedback_data = {
            'id_mensaje': id_mensaje,
            'calificacion': calificacion,
            'comentario': comentario,
            'id_sesion': g.id_sesion,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Feedback recibido para mensaje {id_mensaje}: {calificacion} estrellas")
        
        return jsonify({
            'mensaje': 'Feedback recibido correctamente',
            'feedback_id': f"fb_{datetime.now().timestamp()}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error procesando feedback: {str(e)}")
        return jsonify({
            'error': 'error_interno',
            'mensaje': 'Error procesando feedback'
        }), 500

@bp_chat.route('/stats', methods=['GET'])
@requiere_sesion_valida
def obtener_estadisticas_chat():
    """
    Endpoint para obtener estadísticas de uso del chat
    Retorna métricas de la sesión actual
    """
    try:
        sesion_actual = g.sesion_actual
        
        # Calcular estadísticas de la sesión
        tiempo_activo = datetime.now() - sesion_actual.creada_en
        
        estadisticas = {
            'sesion': {
                'id': sesion_actual.id,
                'tiempo_activo_minutos': int(tiempo_activo.total_seconds() / 60),
                'interacciones_realizadas': sesion_actual.contador_interacciones,
                'interacciones_restantes': 50 - sesion_actual.contador_interacciones,
                'estado': sesion_actual.estado
            },
            'chat': {
                'consultas_procesadas': sesion_actual.contador_interacciones,
                'tiempo_promedio_respuesta': '2.3 segundos',  # Simulado
                'tipos_consulta_frecuentes': ['codigo_error', 'parametro', 'instalacion']
            }
        }
        
        return jsonify(estadisticas), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({
            'error': 'error_interno',
            'mensaje': 'Error obteniendo estadísticas'
        }), 500