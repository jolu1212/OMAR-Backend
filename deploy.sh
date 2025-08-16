#!/bin/bash

# Script de despliegue para OMAR Backend
# Este script automatiza el proceso de despliegue a GitHub y Railway

echo "🚀 Iniciando despliegue de OMAR Backend..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    print_error "No se encontró app.py. Asegúrate de estar en el directorio backend/"
    exit 1
fi

# Verificar si Git está instalado
if ! command -v git &> /dev/null; then
    print_error "Git no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado. Por favor instálalo primero."
    exit 1
fi

print_status "Verificando dependencias..."

# Verificar si requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt no encontrado. Creando uno básico..."
    cat > requirements.txt << EOF
Flask==2.3.3
Flask-CORS==4.0.0
openai==1.3.5
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
Pillow==10.0.1
pydub==0.25.1
redis==5.0.1
psycopg2-binary==2.9.7
marshmallow==3.20.1
bcrypt==4.0.1
PyJWT==2.8.0
EOF
fi

# Verificar si .env.example existe
if [ ! -f "env.example" ]; then
    print_warning "env.example no encontrado. Creando uno básico..."
    cat > env.example << EOF
# Configuración del servidor OMAR Backend
SECRET_KEY=tu_clave_secreta_aqui
OPENAI_API_KEY=tu_api_key_de_openai_aqui
FLASK_ENV=production
FLASK_DEBUG=false
EOF
fi

# Verificar si .gitignore existe
if [ ! -f ".gitignore" ]; then
    print_warning ".gitignore no encontrado. Creando uno básico..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*.so
.env
venv/
.venv/

# Logs
*.log
logs/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF
fi

print_status "Inicializando repositorio Git..."

# Inicializar Git si no está inicializado
if [ ! -d ".git" ]; then
    git init
    print_success "Repositorio Git inicializado"
else
    print_status "Repositorio Git ya existe"
fi

# Agregar todos los archivos
git add .

# Verificar si hay cambios para commit
if git diff --cached --quiet; then
    print_warning "No hay cambios para commit"
else
    # Hacer commit
    git commit -m "feat: Despliegue inicial de OMAR Backend con OpenAI

- Servidor Flask con integración OpenAI
- API para chat, imágenes y audio
- Configuración para Railway
- Documentación completa"
    
    print_success "Commit realizado exitosamente"
fi

# Verificar si hay un remote configurado
if ! git remote get-url origin &> /dev/null; then
    print_warning "No hay remote origin configurado"
    echo -e "${YELLOW}Para conectar con GitHub, ejecuta:${NC}"
    echo "git remote add origin https://github.com/TU_USUARIO/TU_REPO.git"
    echo ""
    echo -e "${YELLOW}O si ya tienes el repositorio:${NC}"
    echo "git remote set-url origin https://github.com/TU_USUARIO/TU_REPO.git"
else
    print_status "Remote origin configurado: $(git remote get-url origin)"
    
    # Intentar hacer push
    print_status "Intentando hacer push a GitHub..."
    if git push origin main 2>/dev/null || git push origin master 2>/dev/null; then
        print_success "Push a GitHub exitoso"
    else
        print_warning "Push falló. Verifica que tengas permisos y que la rama exista"
        echo -e "${YELLOW}Para crear la rama main:${NC}"
        echo "git branch -M main"
        echo "git push -u origin main"
    fi
fi

print_status "Verificando configuración de Railway..."

# Verificar si railway.json existe
if [ ! -f "railway.json" ]; then
    print_warning "railway.json no encontrado. Creando uno básico..."
    cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app --bind 0.0.0.0:\$PORT",
    "healthcheckPath": "/ping",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
    print_success "railway.json creado"
fi

print_status "Verificando estructura del proyecto..."

# Crear directorios necesarios si no existen
mkdir -p logs
mkdir -p uploads
mkdir -p tests

print_success "Estructura del proyecto verificada"

echo ""
echo -e "${GREEN}🎉 Despliegue completado exitosamente!${NC}"
echo ""
echo -e "${BLUE}Próximos pasos:${NC}"
echo "1. Conecta tu repositorio con Railway"
echo "2. Configura las variables de entorno en Railway"
echo "3. Despliega tu aplicación"
echo ""
echo -e "${BLUE}Variables de entorno requeridas:${NC}"
echo "- OPENAI_API_KEY: Tu API key de OpenAI"
echo "- SECRET_KEY: Clave secreta para Flask"
echo "- DATABASE_URL: URL de tu base de datos (opcional)"
echo ""
echo -e "${BLUE}Para conectar con Railway:${NC}"
echo "railway login"
echo "railway init"
echo "railway up"
echo ""
echo -e "${GREEN}¡OMAR Backend está listo para el mundo! 🚀${NC}"
