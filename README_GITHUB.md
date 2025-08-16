# 🚀 OMAR Backend - Asistente Técnico con OpenAI

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com/)
[![Railway](https://img.shields.io/badge/Railway-Deployed-success.svg)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 ¿Qué es OMAR?

**OMAR** es un asistente técnico inteligente especializado en el variador de frecuencia ABB ACS150, construido con Flask y OpenAI GPT-4o-mini.

## ✨ Características

- 🤖 **OpenAI GPT-4o-mini** para respuestas técnicas precisas
- 📷 **OpenAI Vision** para análisis de imágenes técnicas
- 🎤 **OpenAI Whisper** para transcripción de audio
- 🔧 **API RESTful** completa para chat y entrenamiento
- 🚀 **Despliegue automático** en Railway
- 📱 **Integración completa** con app Android

## 🌐 Demo

**Servidor en vivo**: https://omar-backend-production.up.railway.app

## 🚀 Despliegue Rápido

### 1. Clonar
```bash
git clone https://github.com/TU_USUARIO/omar-backend.git
cd omar-backend
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tus claves
```

### 4. Ejecutar
```bash
python app.py
```

## 📁 Estructura

```
omar-backend/
├── app.py                      # Aplicación principal
├── services/                   # Lógica de negocio
├── routes/                     # Endpoints de la API
├── models/                     # Modelos de datos
├── middleware/                 # Middleware personalizado
└── requirements.txt            # Dependencias
```

## 🔌 API Endpoints

- `GET /ping` - Estado del servidor
- `POST /api/chat/ask` - Chat con IA
- `POST /api/training/text` - Entrenamiento con texto
- `POST /api/openai/vision` - Análisis de imágenes
- `POST /api/openai/transcribe` - Transcripción de audio

## 🔐 Variables de Entorno

```bash
OPENAI_API_KEY=tu_api_key_de_openai
SECRET_KEY=tu_clave_secreta
FLASK_ENV=production
```

## 🚀 Railway

Este proyecto está configurado para despliegue automático en Railway:

1. Conecta tu repositorio de GitHub
2. Configura las variables de entorno
3. ¡Despliegue automático en cada push!

## 📱 Integración Android

La app Android OMAR está completamente integrada con este backend. Ver [OMAR Android App](https://github.com/TU_USUARIO/omar-android).

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 📞 Contacto

- **Desarrollador**: Omar
- **Proyecto**: OMAR - Asistente Técnico
- **GitHub**: [@tu-usuario](https://github.com/tu-usuario)

---

## ⭐ ¡Dale una estrella si te gusta!

**OMAR** está diseñado para mejorar la eficiencia de técnicos industriales con la potencia de la IA.

---

*"La tecnología debe servir a la humanidad, no al revés" - OMAR*
