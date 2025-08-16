# 🚀 OMAR Backend - Servidor de IA para Asistente Técnico

## 📋 Descripción

**OMAR** es un asistente técnico inteligente especializado en el variador de frecuencia ABB ACS150, construido con Flask y OpenAI GPT-4o-mini. Este backend proporciona una API robusta para procesar consultas técnicas, analizar imágenes y transcribir audio.

## ✨ Características Principales

### 🤖 **Inteligencia Artificial**
- **OpenAI GPT-4o-mini**: Modelo avanzado para respuestas técnicas precisas
- **OpenAI Vision**: Análisis automático de imágenes técnicas
- **OpenAI Whisper**: Transcripción de audio a texto en español
- **Contexto especializado**: Conocimiento específico del ABB ACS150

### 🔧 **Funcionalidades Técnicas**
- **Chat inteligente**: Respuestas contextuales a consultas técnicas
- **Análisis de imágenes**: Identificación de componentes y problemas
- **Transcripción de audio**: Conversión de explicaciones técnicas a texto
- **Sistema de sesiones**: Manejo de conversaciones persistentes
- **Validación de contenido**: Sistema de revisión y aprobación

### 🏗️ **Arquitectura**
- **Flask**: Framework web robusto y escalable
- **Arquitectura modular**: Servicios separados por funcionalidad
- **Middleware personalizado**: Manejo de sesiones y autenticación
- **CORS habilitado**: Compatible con aplicaciones móviles

## 🚀 Despliegue

### **Railway (Recomendado)**
```bash
# El servidor está desplegado en:
https://omar-backend-production.up.railway.app
```

### **Variables de Entorno Requeridas**
```bash
# Copia env.example a .env y configura:
OPENAI_API_KEY=tu_api_key_de_openai
SECRET_KEY=tu_clave_secreta
DATABASE_URL=tu_url_de_postgresql
```

## 📁 Estructura del Proyecto

```
backend/
├── app.py                      # Aplicación principal Flask
├── config.py                   # Configuración del servidor
├── requirements.txt            # Dependencias Python
├── .gitignore                  # Archivos a ignorar en Git
├── env.example                 # Ejemplo de variables de entorno
├── README.md                   # Este archivo
├── models/                     # Modelos de datos
│   └── session.py             # Modelo de sesión
├── services/                   # Lógica de negocio
│   ├── motor_chat.py          # Motor principal de chat con OpenAI
│   ├── session_manager.py     # Gestor de sesiones
│   ├── sistema_validacion.py  # Sistema de validación de contenido
│   ├── pipeline_entrenamiento.py # Pipeline de entrenamiento
│   └── gestor_contenido_visual.py # Gestor de contenido visual
├── routes/                     # Endpoints de la API
│   └── chat_routes.py         # Rutas de chat
└── middleware/                 # Middleware personalizado
    └── session_middleware.py  # Middleware de sesiones
```

## 🔌 Endpoints de la API

### **Estado del Servidor**
- `GET /ping` - Verificar conectividad
- `GET /status` - Estado de salud del sistema

### **Chat y Sesiones**
- `POST /api/session/create` - Crear nueva sesión
- `POST /api/chat/ask` - Enviar mensaje de chat

### **Entrenamiento con OpenAI**
- `POST /api/training/text` - Procesar texto con GPT-4o-mini
- `POST /api/openai/vision` - Análisis de imágenes con Vision
- `POST /api/openai/transcribe` - Transcripción de audio con Whisper

## 🛠️ Instalación Local

### **Requisitos Previos**
- Python 3.8+
- pip
- Git

### **Pasos de Instalación**
```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/omar-backend.git
cd omar-backend

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp env.example .env
# Editar .env con tus valores reales

# 5. Ejecutar el servidor
python app.py
```

### **Variables de Entorno para Desarrollo**
```bash
FLASK_ENV=development
FLASK_DEBUG=true
OPENAI_API_KEY=tu_api_key_de_openai
SECRET_KEY=dev-secret-key
```

## 🔐 Seguridad

### **Características de Seguridad**
- **CORS configurado**: Solo orígenes autorizados
- **Rate limiting**: Protección contra spam
- **Validación de entrada**: Sanitización de datos
- **Manejo de sesiones**: Timeout automático
- **Logging de seguridad**: Auditoría de accesos

### **Headers de Seguridad**
```http
X-OpenAI-API-Key: tu_api_key
X-Session-ID: id_de_sesion
Content-Type: application/json
```

## 📊 Monitoreo y Logging

### **Logs Disponibles**
- **Requests HTTP**: Método, URL, tiempo de respuesta
- **Errores de OpenAI**: Códigos de error y mensajes
- **Sesiones**: Creación, uso y expiración
- **Validaciones**: Estado de contenido enviado

### **Métricas del Sistema**
- Estado de servicios (OpenAI, base de datos)
- Número de sesiones activas
- Contenido pendiente de validación
- Tiempo de respuesta promedio

## 🧪 Testing

### **Ejecutar Tests**
```bash
# Instalar dependencias de testing
pip install pytest pytest-flask pytest-cov

# Ejecutar tests
pytest

# Con cobertura
pytest --cov=.
```

### **Tests Disponibles**
- Tests unitarios para servicios
- Tests de integración para endpoints
- Tests de validación de datos
- Tests de manejo de errores

## 🚀 Despliegue en Producción

### **Railway (Actual)**
```bash
# El servidor está configurado para Railway
# Variables de entorno configuradas en Railway dashboard
# Despliegue automático desde GitHub
```

### **Docker (Opcional)**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
```

## 🔄 Integración con Android

### **App OMAR**
- **Repository**: [OMAR Android App](https://github.com/tu-usuario/omar-android)
- **API Client**: Configurado para este backend
- **Endpoints**: Todos los endpoints están documentados

### **Flujo de Trabajo**
1. **Usuario** envía contenido desde la app Android
2. **Backend** procesa con OpenAI
3. **Respuesta** se envía de vuelta a la app
4. **Contenido** se almacena para entrenamiento

## 🐛 Solución de Problemas

### **Errores Comunes**

#### **Error 401: API Key Inválida**
```bash
# Verificar variable de entorno
echo $OPENAI_API_KEY

# Verificar en Railway dashboard
```

#### **Error 429: Rate Limit Excedido**
```bash
# Esperar antes de hacer más requests
# Verificar límites de OpenAI
```

#### **Error 500: Servidor Interno**
```bash
# Revisar logs del servidor
# Verificar conectividad con OpenAI
```

### **Debugging**
```bash
# Habilitar debug en desarrollo
export FLASK_DEBUG=true

# Ver logs detallados
tail -f logs/omar_backend.log
```

## 📈 Roadmap

### **Próximas Funcionalidades**
- [ ] **Cache Redis**: Mejorar rendimiento
- [ ] **Base de datos**: PostgreSQL para persistencia
- [ ] **Autenticación**: Sistema de usuarios
- [ ] **Webhooks**: Notificaciones en tiempo real
- [ ] **Analytics**: Métricas de uso

### **Mejoras Técnicas**
- [ ] **Async/await**: Mejor manejo de requests
- [ ] **Microservicios**: Arquitectura distribuida
- [ ] **Kubernetes**: Orquestación de contenedores
- [ ] **Monitoring**: Prometheus + Grafana

## 🤝 Contribución

### **Cómo Contribuir**
1. **Fork** el repositorio
2. **Crea** una rama para tu feature
3. **Commit** tus cambios
4. **Push** a la rama
5. **Crea** un Pull Request

### **Estándares de Código**
- **PEP 8**: Estilo de código Python
- **Docstrings**: Documentación de funciones
- **Type hints**: Tipado estático
- **Tests**: Cobertura mínima del 80%

## 📞 Soporte

### **Contacto**
- **Desarrollador**: Omar
- **Proyecto**: OMAR - Asistente Técnico
- **Email**: [tu-email@ejemplo.com]

### **Recursos**
- [Documentación de OpenAI](https://platform.openai.com/docs)
- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de Railway](https://docs.railway.app/)

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 🎯 Estado Actual

**✅ Servidor funcionando en Railway**
**✅ Integración con OpenAI completa**
**✅ API documentada y funcional**
**✅ App Android conectada**

**¡OMAR está listo para ayudar con el ABB ACS150! 🚀**

---

*Última actualización: $(date)*
