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

# --- OpenAI: compatibilidad con SDK nuevo y antiguo ---
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no está configurada")

_openai_client = None
_use_openai_legacy = False
try:
    # SDK nuevo (openai>=1.0.0)
    from openai import OpenAI
    _openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception:
    # SDK antiguo (openai==0.x)
    import openai  # type: ignore
    openai.api_key = OPENAI_API_KEY
    _use_openai_legacy = True

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OMAR-Backend")

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'omar_industrial_ai_2024')

# Aceptar /ruta y /ruta/ (evita 301/405 por slash)
app.url_map.strict_slashes = False

# CORS amplio (permite llamadas desde tu app Android o web)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# Configuración del modelo
MODEL = os.environ.get("OMAR_OPENAI_MODEL", "gpt-4o-mini")  # Modelo por defecto económico
MAX_TOKENS_OUT = int(os.environ.get("OMAR_MAX_TOKENS", "500"))
TEMPERATURE = float(os.environ.get("OMAR_TEMPERATURE", "0.3"))  # Determinístico para técnico

# Configuración de sesiones
GREETING_TTL_MIN = int(os.environ.get("OMAR_GREETING_TTL_MIN", "30"))  # Saludo cada 30 minutos
MAX_SESSION_TURNS = int(os.environ.get("OMAR_MAX_SESSION_TURNS", "10"))  # 10 turnos

# Saludo inicial personalizado para industria
SALUDO_INICIAL = """Hola, soy OMAR, tu compañero de trabajo. 

He sido entrenado con la experiencia de operadores y mantenedores expertos de esta planta. Puedo ayudarte con:

🔧 Diagnóstico de fallas comunes
📚 Procedimientos operativos
⚡ Soluciones rápidas basadas en casos anteriores
🎯 Mantenimiento preventivo

¿En qué puedo ayudarte hoy?"""

# Almacenamiento de sesiones (en producción usar Redis o base de datos)
sessions: Dict[str, Dict[str, Any]] = {}

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
    messages: List[Dict[str, str]] = [
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
