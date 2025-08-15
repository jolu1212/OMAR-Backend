# 🏭 OMAR Industrial AI - Servidor Flask

Servidor backend para el sistema de inteligencia artificial industrial OMAR, diseñado para asistir a operadores y mantenedores en plantas industriales.

## 🚀 Características

- **Chat con IA**: Integración con OpenAI GPT-4o-mini para consultas técnicas
- **Gestión de Sesiones**: Mantiene contexto de conversación por usuario
- **Sistema de Feedback**: Permite a operadores evaluar respuestas de la IA
- **Entrenamiento de Modelos**: Preparado para ML en detección de fallas
- **API RESTful**: Endpoints bien documentados para integración
- **100% Compatible**: Mantiene compatibilidad total con la app Android existente

## 🛠️ Tecnologías

- **Backend**: Flask 3.0.0
- **IA**: OpenAI API (GPT-4o-mini)
- **CORS**: flask-cors para integración cross-origin
- **Logging**: Sistema de logs estructurado
- **Configuración**: Sistema de configuración por entorno

## 📋 Requisitos

- Python 3.8+
- OpenAI API Key
- Railway (para despliegue) o servidor local

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/jolu1212/OMAR-Backend.git
cd OMAR-Backend
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crear archivo `.env` con:
```env
OPENAI_API_KEY=tu_api_key_aqui
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta
```

### 4. Ejecutar el servidor
```bash
python app.py
```

## 🌐 Endpoints de la API

### `/ping` (GET)
Verifica el estado del servidor
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0",
  "ai_system": "Industrial OMAR"
}
```

### `/ask` (POST) - **ENDPOINT PRINCIPAL**
Consulta principal a la IA - **100% COMPATIBLE CON APP ANDROID**
```json
{
  "pregunta": "¿Qué hacer si el motor se sobrecalienta?",
  "sessionId": "user123"
}
```

**Respuesta:**
```json
{
  "respuesta": "Para el sobrecalentamiento del motor...",
  "imagenes": [],
  "error": null
}
```

### `/train/text` (POST) - **COMPATIBLE CON APP ANDROID**
Entrenamiento de texto
```json
{
  "nota": "Texto para entrenar al modelo"
}
```

### `/train/image` (POST) - **COMPATIBLE CON APP ANDROID**
Subir imagen para entrenamiento
```multipart
imagen: [archivo]
```

### `/train/audio` (POST) - **COMPATIBLE CON APP ANDROID**
Subir audio para entrenamiento
```multipart
audio: [archivo]
```

### `/feedback` (POST)
Envía feedback de operador
```json
{
  "sessionId": "user123",
  "machineId": "empacadora_1",
  "question": "¿Cómo resolver sobrecalentamiento?",
  "answer": "Limpiar filtro de aire",
  "wasHelpful": true,
  "feedbackText": "Solución funcionó perfectamente"
}
```

### `/reset` (POST)
Resetea sesión del usuario
```json
{
  "sessionId": "user123"
}
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   App Android   │    │  Servidor Flask │    │   OpenAI API    │
│                 │◄──►│                 │◄──►│                 │
│ - Chat UI       │    │ - Sesiones      │    │ - GPT-4o-mini   │
│ - Entrenamiento │    │ - IA Industrial │    │ - Respuestas    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 Configuración de Seguridad

- **Rate Limiting**: Máximo 1 consulta cada 2 segundos por sesión
- **Validación de Entrada**: Sanitización de datos de entrada
- **Manejo de Errores**: Respuestas de error estructuradas
- **Logging**: Registro de todas las operaciones

## 🚀 Despliegue en Railway

### 1. Conectar con GitHub
- Conecta tu repositorio en Railway
- Railway detectará automáticamente que es una app Python

### 2. Variables de Entorno
Configura en Railway:
- `OPENAI_API_KEY`: Tu clave de API de OpenAI
- `FLASK_ENV`: `production`
- `SECRET_KEY`: Clave secreta para sesiones

### 3. Despliegue Automático
- Cada push a `main` se despliega automáticamente
- Railway usa `gunicorn` para servir la aplicación

## 📊 Monitoreo y Logs

El servidor incluye logging estructurado para:
- Consultas a la API
- Errores y excepciones
- Entrenamiento de modelos
- Feedback de usuarios
- Estado de sesiones

## 🔮 Funcionalidades Futuras

- [ ] **Base de Datos**: PostgreSQL con pgvector para embeddings
- [ ] **Modelos ML**: Entrenamiento real con scikit-learn
- [ ] **RAG**: Retrieval Augmented Generation con documentos técnicos
- [ ] **Autenticación**: Sistema de usuarios y permisos
- [ ] **Webhooks**: Notificaciones en tiempo real
- [ ] **Analytics**: Métricas de uso y efectividad

## 🧪 Testing

```bash
# Verificar endpoints
curl -X GET https://tu-app.railway.app/ping

# Probar chat
curl -X POST https://tu-app.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"¿Qué hacer si el motor se sobrecalienta?","sessionId":"test123"}'
```

## 📝 Estructura del Proyecto

```
OMAR-Backend/
├── app.py                 # Servidor Flask principal con IA
├── config.py             # Sistema de configuración
├── ai_system.py          # Sistema de IA industrial
├── requirements.txt      # Dependencias completas
├── Procfile             # Configuración para Railway
├── README.md            # Este archivo
└── data/                # Directorio para datos (futuro)
    ├── models/          # Modelos entrenados
    └── training/        # Datos de entrenamiento
```

## 🔒 Compatibilidad con App Android

**Este servidor mantiene 100% compatibilidad con tu app Android existente:**

- ✅ **Variables**: `pregunta`, `respuesta`, `sessionId`, `imagenes`, `error`
- ✅ **Endpoints**: `/ask`, `/train/text`, `/train/image`, `/train/audio`
- ✅ **Estructura JSON**: Exactamente igual que espera tu app
- ✅ **Funcionalidad**: Chat, entrenamiento, feedback

**No se requieren cambios en tu app Android.**

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Abre un issue en GitHub
- Contacta al equipo de desarrollo
- Revisa la documentación de la API

---

**Desarrollado con ❤️ para la industria chilena**
