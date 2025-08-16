#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración para OMAR Industrial AI (Railway).
Lee variables de entorno y valida presencia de la API key de OpenAI.
"""

import os


class Config:
    # --- Servidor / Flask ---
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = FLASK_ENV == "development"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    SECRET_KEY = os.environ.get("SECRET_KEY")  # define esto en Railway

    # --- OpenAI ---
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # OBLIGATORIA
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE = float(os.environ.get("OPENAI_TEMPERATURE", 0.2))
    OPENAI_MAX_TOKENS = int(os.environ.get("OPENAI_MAX_TOKENS", 220))

    # --- Sesiones / Rate limit (backend) ---
    SESSION_GREETING_TTL_MIN = int(os.environ.get("SESSION_GREETING_TTL_MIN", 120))
    SESSION_MAX_TURNS = int(os.environ.get("SESSION_MAX_TURNS", 4))  # memoria corta
    SESSION_RATE_LIMIT_SECONDS = int(os.environ.get("SESSION_RATE_LIMIT_SECONDS", 2))

    # --- Dominio temático (para acotar respuestas) ---
    OMAR_DOMINIO = os.environ.get(
        "OMAR_DOMINIO",
        "variadores de frecuencia, empaques y operación/mantenimiento básico de planta",
    )

    # --- CORS ---
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")]

    @classmethod
    def validate(cls) -> None:
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY no está configurada. "
                "En Railway → Variables: agrega OPENAI_API_KEY con tu clave 'sk-...'."
            )
        if not (0.0 <= cls.OPENAI_TEMPERATURE <= 2.0):
            raise ValueError("OPENAI_TEMPERATURE debe estar entre 0.0 y 2.0.")
        if not (1 <= cls.OPENAI_MAX_TOKENS <= 4096):
            raise ValueError("OPENAI_MAX_TOKENS debe estar entre 1 y 4096.")

    @classmethod
    def debug_print(cls) -> None:
        mk = (cls.OPENAI_API_KEY[:4] + "..." + cls.OPENAI_API_KEY[-4:]) if cls.OPENAI_API_KEY else "NONE"
        print("[CONFIG] ENV:", cls.FLASK_ENV)
        print("[CONFIG] DEBUG:", cls.DEBUG)
        print("[CONFIG] HOST:PORT ->", cls.HOST, cls.PORT)
        print("[CONFIG] OPENAI_MODEL:", cls.OPENAI_MODEL)
        print("[CONFIG] OPENAI_API_KEY:", mk)
        print("[CONFIG] CORS_ORIGINS:", cls.CORS_ORIGINS)
        print("[CONFIG] RATE_LIMIT_SECONDS:", cls.SESSION_RATE_LIMIT_SECONDS)


class DevelopmentConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True


class ProductionConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False


class TestingConfig(Config):
    FLASK_ENV = "testing"
    DEBUG = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": ProductionConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "production").lower()
    cfg_cls = config.get(env, ProductionConfig)
    cfg_cls.validate()
    cfg_cls.debug_print()
    return cfg_cls
