#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask para IA Industrial OMAR
Mantiene 100% compatibilidad con la app Android existente
"""

import os
import json
import logging
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Any
import openai
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'omar_industrial_ai_2024')
CORS(app)

# Configuración OpenAI
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no está configurada")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Configuración del modelo
MODEL = "gpt-4o-mini"  # Modelo más económico
MAX_TOKENS_OUT = 500
TEMPERATURE = 0.3  # Más determinístico para respuestas técnicas

# Configuración de sesiones
GREETING_TTL_MIN = 30  # Saludo cada 30 minutos
MAX_SESSION_TURNS = 10  # Máximo 10 turnos por sesión

# Saludo inicial personalizado para industria
SALUDO_INICIAL = """Hola, soy OMAR, tu compañero de trabajo inteligente. 

He sido entrenado con la experiencia de operadores y mantenedores expertos de esta planta. Puedo ayudarte con:

🔧 Diagnóstico de fallas comunes
📚 Procedimientos operativos
⚡ Soluciones rápidas basadas en casos anteriores
🎯 Mantenimiento preventivo

¿En qué puedo ayudarte hoy?"""

# Almacenamiento de sesiones (en producción usar Redis o base de datos)
sessions = {}

def get_or_create_session(session_id: str) -> Dict:
    """Obtiene o crea una sesión para el usuario"""
    if session_id not in sessions:
        sessions[session_id] = {
            'turns': deque(maxlen=MAX_SESSION_TURNS),
            'summary': '',
            'greet_until': datetime.now() + timedelta(minutes=GREETING_TTL_MIN),
            'machine_context': None,
            'last_interaction': datetime.now()
        }
    return sessions[session_id]

def build_messages(session_data: Dict, user_question: str) -> List[Dict]:
    """Construye el contexto de mensajes para OpenAI"""
    messages = [
        {
            "role": "system",
            "content": f"""Eres OMAR, un asistente de IA industrial especializado en ayudar operadores y mantenedores.

Tu conocimiento incluye:
- Diagnóstico de fallas comunes en maquinaria industrial
- Procedimientos de operación y mantenimiento
- Soluciones basadas en experiencia de expertos
- Mejores prácticas de seguridad industrial

Responde de forma clara, práctica y orientada a la acción. Si no tienes información específica sobre algo, dilo claramente.

Contexto de la sesión: {session_data.get('machine_context', 'No especificado')}"""
        }
    ]
    
    # Agregar resumen de conversación anterior
    if session_data.get('summary'):
        messages.append({
            "role": "system",
            "content": f"Resumen de conversación anterior: {session_data['summary']}"
        })
    
    # Agregar turnos recientes
    for turn in session_data['turns']:
        messages.append({"role": "user", "content": turn['question']})
        messages.append({"role": "assistant", "content": turn['answer']})
    
    # Agregar pregunta actual
    messages.append({"role": "user", "content": user_question})
    
    return messages

def push_turn(session_data: Dict, question: str, answer: str):
    """Agrega un turno a la conversación"""
    session_data['turns'].append({
        'question': question,
        'answer': answer,
        'timestamp': datetime.now()
    })
    session_data['last_interaction'] = datetime.now()

def apply_rate_limit(session_data: Dict) -> bool:
    """Aplica rate limiting básico"""
    now = datetime.now()
    if session_data['last_interaction'] and (now - session_data['last_interaction']).seconds < 2:
        return True  # Muy rápido
    return False

@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint de salud del servidor"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "ai_system": "Industrial OMAR"
    })

@app.route("/ask", methods=["POST"])
def ask():
    """Endpoint principal para consultas de IA - MANTIENE COMPATIBILIDAD 100%"""
    try:
        data = request.get_json(silent=True) or {}
        pregunta = data.get("pregunta", "").strip()
        session_id = data.get("sessionId", "")
        
        if not pregunta:
            return jsonify({"error": "La pregunta está vacía"}), 400
        
        # Validar sesión
        if not session_id:
            return jsonify({"error": "SessionId requerido"}), 400
        
        # Obtener o crear sesión
        session_data = get_or_create_session(session_id)
        
        # Rate limiting
        if apply_rate_limit(session_data):
            return jsonify({
                "respuesta": "Estás consultando muy rápido. Intenta de nuevo en un momento.",
                "imagenes": [],
                "error": None
            }), 429
        
        # Construir mensajes para OpenAI
        messages = build_messages(session_data, pregunta)
        
        # Llamada a OpenAI
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS_OUT,
        )
        
        answer = (response.choices[0].message.content or "").strip()
        
        # Agregar saludo si es necesario
        now = datetime.now()
        if now > session_data['greet_until']:
            if not answer.lower().startswith("hola, soy tu compañero"):
                answer = f"{SALUDO_INICIAL}\n\n{answer}"
            session_data['greet_until'] = now + timedelta(minutes=GREETING_TTL_MIN)
        
        # Guardar turno en la conversación
        push_turn(session_data, pregunta, answer)
        
        # MANTIENE ESTRUCTURA EXACTA que espera la app Android
        return jsonify({
            "respuesta": answer,
            "imagenes": [],
            "error": None
        }), 200
        
    except Exception as e:
        logger.error(f"Error en endpoint /ask: {e}")
        return jsonify({
            "respuesta": "",
            "imagenes": [],
            "error": str(e)
        }), 500

@app.route("/train/text", methods=["POST"])
def train_text():
    """Endpoint para entrenamiento de texto - MANTIENE COMPATIBILIDAD 100%"""
    try:
        data = request.get_json(silent=True) or {}
        nota = data.get("nota", "").strip()
        
        if not nota:
            return jsonify({"error": "La nota está vacía"}), 400
        
        # Aquí se procesaría el texto para entrenamiento
        # Por ahora solo simulamos el procesamiento
        logger.info(f"Texto recibido para entrenamiento: {nota[:100]}...")
        
        # MANTIENE COMPATIBILIDAD con la app Android
        return jsonify({
            "message": "Texto recibido para entrenamiento exitosamente",
            "status": "success"
        }), 200
        
    except Exception as e:
        logger.error(f"Error en entrenamiento de texto: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/train/image", methods=["POST"])
def train_image():
    """Endpoint para subir imagen - MANTIENE COMPATIBILIDAD 100%"""
    try:
        if 'imagen' not in request.files:
            return jsonify({"error": "No se recibió imagen"}), 400
        
        imagen = request.files['imagen']
        if imagen.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400
        
        # Aquí se procesaría la imagen para entrenamiento
        logger.info(f"Imagen recibida: {imagen.filename}")
        
        # MANTIENE COMPATIBILIDAD con la app Android
        return jsonify({
            "message": "Imagen recibida para entrenamiento exitosamente",
            "filename": imagen.filename,
            "status": "success"
        }), 200
        
    except Exception as e:
        logger.error(f"Error en entrenamiento de imagen: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/train/audio", methods=["POST"])
def train_audio():
    """Endpoint para subir audio - MANTIENE COMPATIBILIDAD 100%"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No se recibió audio"}), 400
        
        audio = request.files['audio']
        if audio.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400
        
        # Aquí se procesaría el audio para entrenamiento
        logger.info(f"Audio recibido: {audio.filename}")
        
        # MANTIENE COMPATIBILIDAD con la app Android
        return jsonify({
            "message": "Audio recibido para entrenamiento exitosamente",
            "filename": audio.filename,
            "status": "success"
        }), 200
        
    except Exception as e:
        logger.error(f"Error en entrenamiento de audio: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """Endpoint para recibir feedback de operadores"""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get("sessionId", "")
        machine_id = data.get("machineId", "")
        question = data.get("question", "")
        answer = data.get("answer", "")
        was_helpful = data.get("wasHelpful", True)
        feedback_text = data.get("feedbackText", "")
        
        if not session_id:
            return jsonify({"error": "SessionId requerido"}), 400
        
        # Guardar feedback (en producción se guardaría en base de datos)
        logger.info(f"Feedback recibido: {session_id} - {machine_id} - Útil: {was_helpful}")
        
        return jsonify({
            "message": "Feedback recibido exitosamente",
            "feedback_id": f"{session_id}_{datetime.now().timestamp()}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error recibiendo feedback: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset_session():
    """Endpoint para resetear sesión"""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get("sessionId", "")
        
        if session_id in sessions:
            del sessions[session_id]
            logger.info(f"Sesión {session_id} reseteada")
        
        return jsonify({"message": "Sesión reseteada"}), 200
        
    except Exception as e:
        logger.error(f"Error reseteando sesión: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Maneja errores HTTP"""
    return jsonify({
        "respuesta": "",
        "imagenes": [],
        "error": e.description
    }), e.code

@app.errorhandler(Exception)
def handle_general_exception(e):
    """Maneja errores generales"""
    logger.error(f"Error no manejado: {e}")
    return jsonify({
        "respuesta": "",
        "imagenes": [],
        "error": "Error interno del servidor"
    }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    logger.info(f"Iniciando servidor OMAR Industrial AI en puerto {port}")
    logger.info(f"Modelo OpenAI: {MODEL}")
    logger.info(f"Modo debug: {debug}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
