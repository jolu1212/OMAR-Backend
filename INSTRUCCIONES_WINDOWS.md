# 🪟 Instrucciones para Windows - OMAR Backend

## 🚨 **PRIMERO: Instalar Herramientas Necesarias**

### **1. Instalar Git (OBLIGATORIO)**
1. Ve a [Git for Windows](https://git-scm.com/download/win)
2. Descarga la versión para Windows
3. **Ejecuta el instalador** como administrador
4. **IMPORTANTE**: Selecciona "Git from the command line and also from 3rd-party software"
5. Completa la instalación
6. **Reinicia** tu terminal/CMD

### **2. Instalar Python (OBLIGATORIO)**
1. Ve a [Python.org](https://www.python.org/downloads/)
2. Descarga Python 3.8+ para Windows
3. **Ejecuta el instalador** como administrador
4. **IMPORTANTE**: ✅ Marca "Add Python to PATH"
5. ✅ Marca "Install for all users"
6. Completa la instalación
7. **Reinicia** tu terminal/CMD

### **3. Verificar Instalación**
Abre una **nueva** ventana de CMD y ejecuta:
```cmd
git --version
python --version
pip --version
```

## 🚀 **DESPUÉS: Subir a GitHub**

### **Opción A: Usar CMD (Recomendado para desarrolladores)**
```cmd
# 1. Navegar a la carpeta
cd C:\Users\HP 2025\AndroidStudioProjects\Omar\omar-backend

# 2. Inicializar Git
git init

# 3. Agregar todos los archivos
git add .

# 4. Hacer commit inicial
git commit -m "feat: Despliegue inicial de OMAR Backend con OpenAI"

# 5. Conectar con tu repositorio de GitHub
git remote add origin https://github.com/TU_USUARIO/omar-backend.git

# 6. Crear rama main y subir
git branch -M main
git push -u origin main
```

### **Opción B: Usar GitHub Desktop (Más fácil para principiantes)**
1. **Instalar GitHub Desktop** desde [desktop.github.com](https://desktop.github.com/)
2. **Iniciar sesión** con tu cuenta de GitHub
3. **Clonar repositorio** o **crear nuevo**
4. **Arrastrar la carpeta** `omar-backend` al repositorio
5. **Hacer commit** y **push**

## 🔗 **Crear Repositorio en GitHub**

### **1. Ve a GitHub.com**
1. Inicia sesión en tu cuenta
2. Haz clic en **"New repository"** (botón verde)

### **2. Configura el Repositorio**
- **Repository name**: `omar-backend`
- **Description**: "Backend de OMAR - Asistente Técnico con OpenAI"
- **Visibility**: Public o Private (según prefieras)
- **❌ NO marques** "Add a README file"
- **❌ NO marques** "Add .gitignore"
- **❌ NO marques** "Choose a license"
- Haz clic en **"Create repository"**

### **3. Copia la URL**
GitHub te mostrará algo como:
```
https://github.com/TU_USUARIO/omar-backend.git
```
**Guarda esta URL** para usarla en los comandos Git.

## 🐛 **Solución de Problemas Comunes**

### **Error: "git no se reconoce como comando"**
- **Reinicia** tu terminal/CMD después de instalar Git
- Verifica que Git esté en el PATH del sistema

### **Error: "python no se reconoce como comando"**
- **Reinicia** tu terminal/CMD después de instalar Python
- Verifica que Python esté en el PATH del sistema

### **Error: "Authentication failed"**
- Usa **token de acceso personal** en lugar de contraseña
- O configura **SSH keys**

### **Error: "Repository not found"**
- Verifica que el repositorio existe en GitHub
- Verifica que tienes permisos de escritura
- Verifica la URL del remote: `git remote -v`

## 📋 **Checklist de Verificación**

- [ ] ✅ **Git instalado** y funcionando
- [ ] ✅ **Python instalado** y funcionando
- [ ] ✅ **Repositorio creado** en GitHub
- [ ] ✅ **Código subido** a GitHub
- [ ] ✅ **Repositorio conectado** con Railway
- [ ] ✅ **Variables de entorno** configuradas

## 🎯 **Comandos de Verificación**

```cmd
# Verificar Git
git --version

# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar directorio actual
dir

# Verificar archivos en la carpeta
dir omar-backend
```

## 🚀 **¡Listo para Desplegar!**

Una vez que hayas instalado Git y Python, y creado el repositorio en GitHub, podrás ejecutar los comandos para subir tu código.

**¿Necesitas ayuda con algún paso específico? ¡Pregunta!**

---

*Estas instrucciones están optimizadas para Windows 10/11*
