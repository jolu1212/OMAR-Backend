#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List

# --- OpenAI ---
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no está configurada")

_openai_client = None
_use_openai_legacy = False
try:
    from openai import OpenAI, APIConnectionError, APITimeoutError, RateLimitError
    _openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception:
    import openai
    from openai.error import APIConnectionError, Timeout as APITimeoutError, RateLimitError
    openai.api_key = OPENAI_API_KEY
    _use_openai_legacy = True

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OMAR-Backend")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'omar_industrial_ai_2024')
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración
MODEL = "gpt-4o-mini"
MAX_TOKENS_OUT = 500
TEMPERATURE = 0.3
OPENAI_TIMEOUT = float(os.environ.get("OPENAI_TIMEOUT", "30.0"))
GREETING_TTL_MIN = 30
MAX_SESSION_TURNS = 10

SALUDO_INICIAL = """Hola, soy OMAR, tu compañero de trabajo inteligente. 

He sido entrenado con la experiencia de operadores y mantenedores expertos de esta planta. Puedo ayudarte con:

🔧 Diagnóstico de fallas comunes
📚 Procedimientos operativos
⚡ Soluciones rápidas basadas en casos anteriores
🎯 Mantenimiento preventivo

¿En qué puedo ayudarte hoy?"""

sessions: Dict[str, Dict] = {}

def get_or_create_session(session_id: str) -> Dict:
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
    messages = [{
        "role": "system",
        "content": f"""Eres OMAR, un asistente de IA industrial especializado en ayudar operadores y mantenedores.
Contexto de la sesión: {session_data.get('machine_context', 'No especificado')}"""
    }]
    if session_data.get('summary'):
        messages.append({"role": "system", "content": f"Resumen: {session_data['summary']}"})
    for turn in session_data['turns']:
        messages.append({"role": "user", "content": turn['question']})
        messages.append({"role": "assistant", "content": turn['answer']})
    messages.append({"role": "user", "content": user_question})
    return messages

def push_turn(session_data: Dict, question: str, answer: str):
    session_data['turns'].append({
        'question': question,
        'answer': answer,
        'timestamp': datetime.now()
    })
    session_data['last_interaction'] = datetime.now()

def apply_rate_limit(session_data: Dict) -> bool:
    now = datetime.now()
    return (now - session_data['last_interaction']).seconds < 2

@app.before_request
def _log_request_meta():
    logger.info("REQ %s %s Ctype=%s", request.method, request.path, request.headers.get("Content-Type"))

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route("/ask", methods=["POST", "OPTIONS"])
def ask():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        data = request.get_json(silent=True) or {}
        pregunta = (data.get("pregunta") or "").strip()
        session_id = (data.get("sessionId") or "").strip()
        if not pregunta:
            return jsonify({"respuesta": "", "imagenes": [], "error": "La pregunta está vacía"}), 400
        if not session_id:
            return jsonify({"respuesta": "", "imagenes": [], "error": "SessionId requerido"}), 400

        session_data = get_or_create_session(session_id)
        if apply_rate_limit(session_data):
            return jsonify({"respuesta": "", "imagenes": [], "error": "Consulta muy rápida"}), 429

        messages = build_messages(session_data, pregunta)

        try:
            if not _use_openai_legacy:
                resp = _openai_client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS_OUT,
                    timeout=OPENAI_TIMEOUT
                )
                answer = (resp.choices[0].message.content or "").strip()
            else:
                resp = openai.ChatCompletion.create(
                    model=MODEL,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS_OUT,
                    request_timeout=OPENAI_TIMEOUT
                )
                answer = (resp["choices"][0]["message"]["content"] or "").strip()
        except (APITimeoutError, APIConnectionError) as e:
            logger.warning(f"Timeout/Conn OpenAI: {e}")
            return jsonify({"respuesta": "", "imagenes": [], "error": "La IA tardó demasiado en responder"}), 504
        except RateLimitError as e:
            logger.warning(f"RateLimit: {e}")
            return jsonify({"respuesta": "", "imagenes": [], "error": "La IA está ocupada"}), 429

        now = datetime.now()
        if now > session_data['greet_until']:
            if not answer.lower().startswith("hola, soy omar"):
                answer = f"{SALUDO_INICIAL}\n\n{answer}"
            session_data['greet_until'] = now + timedelta(minutes=GREETING_TTL_MIN)

        push_turn(session_data, pregunta, answer)

        return jsonify({"respuesta": answer, "imagenes": [], "error": None})
    except Exception as e:
        logger.exception("Error /ask")
        return jsonify({"respuesta": "", "imagenes": [], "error": str(e)}), 500

# Endpoint de entrenamiento de texto
@app.route("/train/text", methods=["POST", "OPTIONS"])
def train_text():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        data = request.get_json(silent=True) or {}
        nota = (data.get("nota") or "").strip()
        
        if not nota:
            return jsonify({"status": "error", "message": "Nota requerida"}), 400
        
        # Aquí procesarías la nota para entrenar el modelo
        # Por ahora solo confirmamos recepción
        logger.info(f"Entrenamiento de texto recibido: {nota[:100]}...")
        
        return jsonify({
            "status": "success", 
            "message": "Texto recibido para entrenamiento",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error /train/text")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint de entrenamiento de imagen
@app.route("/train/image", methods=["POST", "OPTIONS"])
def train_image():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        # Verificar si hay archivo
        if 'imagen' not in request.files:
            return jsonify({"status": "error", "message": "No se recibió imagen"}), 400
        
        file = request.files['imagen']
        if file.filename == '':
            return jsonify({"status": "error", "message": "Nombre de archivo vacío"}), 400
        
        # Aquí procesarías la imagen para entrenar el modelo
        # Por ahora solo confirmamos recepción
        logger.info(f"Entrenamiento de imagen recibido: {file.filename}")
        
        return jsonify({
            "status": "success", 
            "message": "Imagen recibida para entrenamiento",
            "filename": file.filename,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error /train/image")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint de entrenamiento de audio
@app.route("/train/audio", methods=["POST", "OPTIONS"])
def train_audio():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        # Verificar si hay archivo
        if 'audio' not in request.files:
            return jsonify({"status": "error", "message": "No se recibió audio"}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({"status": "error", "message": "Nombre de archivo vacío"}), 400
        
        # Aquí procesarías el audio para entrenar el modelo
        # Por ahora solo confirmamos recepción
        logger.info(f"Entrenamiento de audio recibido: {file.filename}")
        
        return jsonify({
            "status": "success", 
            "message": "Audio recibido para entrenamiento",
            "filename": file.filename,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error /train/audio")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint de feedback
@app.route("/feedback", methods=["POST", "OPTIONS"])
def feedback():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        data = request.get_json(silent=True) or {}
        session_id = (data.get("sessionId") or "").strip()
        feedback_text = (data.get("feedback") or "").strip()
        rating = data.get("rating", 0)
        
        if not session_id:
            return jsonify({"status": "error", "message": "SessionId requerido"}), 400
        
        # Aquí procesarías el feedback
        logger.info(f"Feedback recibido - Session: {session_id}, Rating: {rating}, Text: {feedback_text[:100]}...")
        
        return jsonify({
            "status": "success", 
            "message": "Feedback recibido",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error /feedback")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint de estado del sistema
@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "sessions_active": len(sessions),
        "model": MODEL,
        "openai_configured": bool(OPENAI_API_KEY)
    })

# Endpoint raíz
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "OMAR Backend - IA Industrial",
        "version": "1.0.0",
        "endpoints": [
            "/ask - Chat con IA",
            "/train/text - Entrenamiento de texto",
            "/train/image - Entrenamiento de imagen", 
            "/train/audio - Entrenamiento de audio",
            "/feedback - Feedback del usuario",
            "/status - Estado del sistema",
            "/ping - Health check"
        ],
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
