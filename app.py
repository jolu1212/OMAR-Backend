#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMAR Backend - IA Industrial
- Endpoints:
  /ping   : healthcheck
  /status : listado de endpoints y versión
  /ask    : chat con IA (memoria corta por sesión, ahorro de tokens, short-circuits)
  /reset  : reinicia memoria de sesión
"""

import os, re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import deque

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

from config import get_config

# === Cargar config ===
Conf = get_config()
TZ = ZoneInfo(os.environ.get("OMAR_TZ", "America/Santiago"))

# === Sistema y tono ===
SYSTEM_PROMPT = (
    "Eres un compañero de trabajo cercano, claro y práctico. "
    "Respondes en español de Chile, en 1–3 oraciones y directo al grano. "
    f"Habla solo de {Conf.OMAR_DOMINIO}. "
    "Si la pregunta no corresponde, responde: 'No tengo esa info.'"
)
SALUDO_INICIAL = "Hola, soy tu compañero de trabajo. ¿En qué puedo ayudarte?"

# === Inicialización Flask / OpenAI ===
app = Flask(__name__)
app.config.from_object(Conf)
CORS(app, resources={r"/*": {"origins": Conf.CORS_ORIGINS}})
client = OpenAI(api_key=Conf.OPENAI_API_KEY)

# === Memoria en RAM por sesión ===
# sessions[key] = {
#   "greet_until": datetime,
#   "summary": str,
#   "turns": [{"u": str, "a": str}],
#   "last_seen": datetime,
#   "rate": deque(datetime)
# }
sessions = {}

# === Utilidades ===
def ahora_str() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

def sanea(txt: str) -> str:
    if not txt:
        return ""
    t = txt.strip()
    t = re.sub(r"[\x00-\x1F\x7F]", " ", t)
    return t

def es_solo_saludo(p: str) -> bool:
    return re.fullmatch(r"\s*(hola+|buen[oa]s|qué tal|que tal|hey)\W*\s*", p, re.I) is not None

def es_fecha_hora(p: str) -> bool:
    return re.search(r"(fecha|qué\s*d[ií]a|que\s*d[ií]a|día\s*de\s*hoy|hora|qué\s*hora|que\s*hora)", p, re.I) is not None

def fuera_de_dominio(p: str) -> bool:
    prohibidos = [
        r"\b(clima|pel[ií]cula|celebridad|f[úu]tbol|pol[ií]tica|hor[óo]scopo|receta)\b",
        r"\b(chatgpt|openai api key|programaci[óo]n gen[ée]rica)\b"
    ]
    return any(re.search(pat, p, re.I) for pat in prohibidos)

def key_sesion(session_id: str | None) -> str:
    if session_id:
        return f"sid:{session_id}"
    ip = (request.headers.get("X-Forwarded-For", request.remote_addr) or "0.0.0.0").split(",")[0].strip()
    return f"ip:{ip}"

def get_or_create_session(k: str):
    now = datetime.now(TZ)
    s = sessions.get(k)
    if not s:
        s = {"greet_until": datetime.min.replace(tzinfo=TZ), "summary": "", "turns": [], "last_seen": now, "rate": deque()}
        sessions[k] = s
    else:
        s["last_seen"] = now
    return s

def apply_rate_limit(s) -> bool:
    # True si supera el rate y NO debe llamarse a OpenAI
    now = datetime.now(TZ)
    dq = s["rate"]
    dq.append(now)
    limite = now - timedelta(seconds=Conf.SESSION_RATE_LIMIT_SECONDS)
    while dq and dq[0] < limite:
        dq.popleft()
    return len(dq) > 1  # más de 1 petición dentro de la ventana = corta

def push_turn(s, user_text: str, assistant_text: str | None):
    s["turns"].append({"u": user_text, "a": assistant_text})
    if len(s["turns"]) > Conf.SESSION_MAX_TURNS:
        s["turns"] = s["turns"][-Conf.SESSION_MAX_TURNS:]

def build_messages(s, pregunta: str):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if s["turns"]:
        # Memoria corta: enviamos 2-4 turnos previos
        for t in s["turns"][-Conf.SESSION_MAX_TURNS:]:
            if t.get("u"): msgs.append({"role": "user", "content": t["u"]})
            if t.get("a"): msgs.append({"role": "assistant", "content": t["a"]})
    msgs.append({"role": "user", "content": pregunta})
    return msgs

# === Endpoints ===
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"ok": True, "mensaje": "Backend activo", "ahora": ahora_str()}), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "puntos_finales": [
            "/ask - Chat con IA",
            "/reset - Reinicia memoria de sesión",
            "/status - Estado del sistema",
            "/ping - Comprobación del estado"
        ],
        "mensaje": "OMAR Backend - IA Industrial",
        "marca_de_tiempo": ahora_str(),
        "version": "1.0.0"
    }), 200

@app.route("/reset", methods=["POST"])
def reset():
    data = request.get_json(silent=True) or {}
    session_id = sanea(data.get("sessionId") or "")
    k = key_sesion(session_id)
    sessions.pop(k, None)
    return jsonify({"ok": True, "mensaje": "Sesión reiniciada"}), 200

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(silent=True) or {}
        pregunta = sanea(data.get("pregunta") or "")
        session_id = sanea(data.get("sessionId") or "")

        if not pregunta:
            return jsonify({"error": "La pregunta está vacía"}), 400

        # Short-circuits (gratis, no gastan tokens)
        if es_solo_saludo(pregunta):
            return jsonify({"respuesta": SALUDO_INICIAL, "imagenes": []}), 200
        if es_fecha_hora(pregunta):
            return jsonify({"respuesta": f"Ahora es {ahora_str()} (America/Santiago).", "imagenes": []}), 200
        if fuera_de_dominio(pregunta):
            return jsonify({"respuesta": "No tengo esa info.", "imagenes": []}), 200

        # Sesión + rate-limit
        k = key_sesion(session_id)
        s = get_or_create_session(k)
        if apply_rate_limit(s):
            # Sugiere esperar sin “matar” al usuario
            return jsonify({"respuesta": "Estás consultando muy rápido. Prueba de nuevo en unos segundos.", "imagenes": []}), 429

        # Construir mensajes con memoria corta
        messages = build_messages(s, pregunta)

        # Llamada a OpenAI
        resp = client.chat.completions.create(
            model=Conf.OPENAI_MODEL,
            messages=messages,
            temperature=Conf.OPENAI_TEMPERATURE,
            max_tokens=Conf.OPENAI_MAX_TOKENS,
        )
        texto = (resp.choices[0].message.content or "").strip()

        # Saludo solo si no saludamos hace un rato
        now = datetime.now(TZ)
        if now > s["greet_until"]:
            if not texto.lower().startswith("hola, soy tu compañero de trabajo"):
                texto = f"{SALUDO_INICIAL}\n\n{texto}"
            s["greet_until"] = now + timedelta(minutes=Conf.SESSION_GREETING_TTL_MIN)

        # Guardar turno en memoria corta
        push_turn(s, pregunta, texto)

        # Recorte por seguridad de transferencia
        if len(texto) > 900:
            texto = texto[:900] + "…"

        return jsonify({"respuesta": texto, "imagenes": []}), 200

    except Exception as e:
        msg = str(e)
        if "insufficient_quota" in msg:
            return jsonify({"error": "Sin saldo de API. Revisa Billing de OpenAI."}), 502
        return jsonify({"error": msg}), 500


if __name__ == "__main__":
    app.run(host=Conf.HOST, port=Conf.PORT)
