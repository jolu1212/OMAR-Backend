#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo de configuración para el servidor OMAR Industrial AI
"""

import os
from typing import Optional

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('CLAVE API DE OPENAI', 'omar_industrial_ai_2024')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    
    # Configuración del servidor
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', 500))
    OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', 0.3))
    
    # Configuración de sesiones
    SESSION_GREETING_TTL_MIN = int(os.environ.get('SESSION_GREETING_TTL_MIN', 30))
    SESSION_MAX_TURNS = int(os.environ.get('SESSION_MAX_TURNS', 10))
    SESSION_RATE_LIMIT_SECONDS = int(os.environ.get('SESSION_RATE_LIMIT_SECONDS', 2))
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Configuración de base de datos (futuro)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que la configuración sea correcta y muestra la API key parcialmente"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY es requerida")

        # Mostrar la API key parcialmente para verificar que está cargada
        masked_key = cls.OPENAI_API_KEY[:4] + "..." + cls.OPENAI_API_KEY[-4:]
        print(f"[DEBUG] OPENAI_API_KEY detectada: {masked_key}")

        if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 2:
            raise ValueError("OPENAI_TEMPERATURE debe estar entre 0 y 2")
        
        if cls.OPENAI_MAX_TOKENS < 1 or cls.OPENAI_MAX_TOKENS > 4000:
            raise ValueError("OPENAI_MAX_TOKENS debe estar entre 1 y 4000")
        
        return True


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    FLASK_ENV = 'development'
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuración para producción"""
    FLASK_ENV = 'production'
    DEBUG = False
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Configuración para testing"""
    FLASK_ENV = 'testing'
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'


# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}
