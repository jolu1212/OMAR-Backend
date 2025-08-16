# 🚀 Instrucciones para Subir OMAR Backend a GitHub

## 📋 Pasos para Subir a GitHub

### **1. Crear Repositorio en GitHub**
1. Ve a [GitHub.com](https://github.com)
2. Haz clic en **"New repository"**
3. **Nombre del repositorio**: `omar-backend` o `omar-server`
4. **Descripción**: "Backend de OMAR - Asistente Técnico con OpenAI"
5. **Público** o **Privado** (según prefieras)
6. **NO** inicialices con README, .gitignore o licencia
7. Haz clic en **"Create repository"**

### **2. Subir Código desde tu Computadora**

#### **Opción A: Usar el Script Automatizado (Recomendado)**
```bash
# 1. Navegar a la carpeta omar-backend
cd omar-backend

# 2. Hacer ejecutable el script (en Linux/Mac)
chmod +x deploy.sh

# 3. Ejecutar el script
./deploy.sh
```

#### **Opción B: Comandos Manuales**
```bash
# 1. Navegar a la carpeta omar-backend
cd omar-backend

# 2. Inicializar Git
git init

# 3. Agregar todos los archivos
git add .

# 4. Hacer commit inicial
git commit -m "feat: Despliegue inicial de OMAR Backend

- Servidor Flask con integración OpenAI GPT-4o-mini
- API para chat, imágenes y audio
- Sistema de sesiones y validación
- Configuración para Railway
- Documentación completa"

# 5. Conectar con tu repositorio de GitHub
git remote add origin https://github.com/TU_USUARIO/omar-backend.git

# 6. Crear rama main y hacer push
git branch -M main
git push -u origin main
```

### **3. Verificar en GitHub**
1. Ve a tu repositorio en GitHub
2. Verifica que todos los archivos estén ahí:
   - ✅ `app.py`
   - ✅ `requirements.txt`
   - ✅ `README.md`
   - ✅ `.gitignore`
   - ✅ `railway.json`
   - ✅ `env.example`
   - ✅ `LICENSE`
   - ✅ `deploy.sh`
   - ✅ Carpeta `services/`
   - ✅ Carpeta `routes/`
   - ✅ Carpeta `models/`
   - ✅ Carpeta `middleware/`

## 🔗 Conectar con Railway

### **1. En Railway Dashboard**
1. Ve a [Railway.app](https://railway.app)
2. Haz clic en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Selecciona tu repositorio `omar-backend`
5. Haz clic en **"Deploy Now"**

### **2. Configurar Variables de Entorno**
En Railway, ve a **Variables** y configura:

```bash
# OBLIGATORIAS
OPENAI_API_KEY1=tu_api_key_real_de_openai
SECRET_KEY=tu_clave_secreta_aqui

# OPCIONALES
FLASK_ENV=production
FLASK_DEBUG=false
DATABASE_URL=tu_url_de_postgresql
```

### **3. Despliegue Automático**
- Cada vez que hagas `git push` a GitHub
- Railway automáticamente desplegará los cambios
- Tu servidor estará disponible en: `https://omar-backend-production.up.railway.app`

## 📁 Estructura del Repositorio

```
omar-backend/
├── 📄 app.py                      # Aplicación principal Flask
├── 📄 config.py                   # Configuración del servidor
├── 📄 requirements.txt            # Dependencias Python
├── 📄 .gitignore                  # Archivos a ignorar en Git
├── 📄 env.example                 # Variables de entorno (sin claves)
├── 📄 README.md                   # Documentación completa
├── 📄 railway.json                # Configuración para Railway
├── 📄 deploy.sh                   # Script de despliegue
├── 📄 LICENSE                     # Licencia MIT
├── 📁 models/                     # Modelos de datos
│   └── 📄 session.py             # Modelo de sesión
├── 📁 services/                   # Lógica de negocio
│   ├── 📄 motor_chat.py          # Motor de chat con OpenAI
│   ├── 📄 session_manager.py     # Gestor de sesiones
│   ├── 📄 sistema_validacion.py  # Sistema de validación
│   ├── 📄 pipeline_entrenamiento.py # Pipeline de entrenamiento
│   └── 📄 gestor_contenido_visual.py # Gestor de contenido visual
├── 📁 routes/                     # Endpoints de la API
│   └── 📄 chat_routes.py         # Rutas de chat
└── 📁 middleware/                 # Middleware personalizado
    └── 📄 session_middleware.py  # Middleware de sesiones
```

## 🚨 Archivos Importantes

### **✅ Archivos que SÍ van a GitHub:**
- Todo el código Python (`.py`)
- `requirements.txt`
- `README.md`
- `.gitignore`
- `railway.json`
- `env.example`
- `LICENSE`
- `deploy.sh`

### **❌ Archivos que NO van a GitHub:**
- `.env` (con claves reales)
- `__pycache__/`
- `*.pyc`
- `venv/` o `env/`
- Archivos de logs
- Archivos temporales

## 🔄 Flujo de Trabajo Diario

### **Para hacer cambios:**
```bash
# 1. Editar archivos
# 2. Probar localmente
# 3. Hacer commit
git add .
git commit -m "feat: descripción del cambio"

# 4. Subir a GitHub
git push origin main

# 5. Railway se despliega automáticamente
```

## 🐛 Solución de Problemas

### **Error: "Repository not found"**
- Verifica que el repositorio existe en GitHub
- Verifica que tienes permisos de escritura
- Verifica la URL del remote: `git remote -v`

### **Error: "Authentication failed"**
- Usa token de acceso personal en lugar de contraseña
- O configura SSH keys

### **Error: "Branch main not found"**
```bash
git branch -M main
git push -u origin main
```

## 🎯 Checklist Final

- [ ] ✅ Repositorio creado en GitHub
- [ ] ✅ Código subido a GitHub
- [ ] ✅ Repositorio conectado con Railway
- [ ] ✅ Variables de entorno configuradas en Railway
- [ ] ✅ Servidor desplegado y funcionando
- [ ] ✅ App Android conectada al servidor

## 🚀 ¡Listo para Desplegar!

Una vez que hayas seguido estos pasos, tu servidor OMAR estará:
- ✅ **En GitHub** para control de versiones
- ✅ **En Railway** para despliegue automático
- ✅ **Conectado con OpenAI** para IA
- ✅ **Integrado con tu app Android**

**¡OMAR Backend estará listo para el mundo! 🌍**

---

*¿Necesitas ayuda con algún paso específico? ¡Pregunta!*
