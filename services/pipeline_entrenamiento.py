# Pipeline de entrenamiento para procesamiento de contenido técnico
import os
import logging
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime
import hashlib
import mimetypes
from PIL import Image
import speech_recognition as sr
from io import BytesIO
import base64

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

class PipelineEntrenamiento:
    """
    Pipeline centralizado para procesamiento de contenido de entrenamiento
    Maneja texto, imágenes y audio para mejorar la base de conocimiento
    """
    
    def __init__(self, directorio_uploads: str = "uploads"):
        """
        Constructor del pipeline de entrenamiento
        Args:
            directorio_uploads: Directorio para almacenar archivos subidos
        """
        self.directorio_uploads = directorio_uploads
        
        # Crear directorios necesarios
        self.directorio_texto = os.path.join(directorio_uploads, "texto")
        self.directorio_imagenes = os.path.join(directorio_uploads, "imagenes")
        self.directorio_audio = os.path.join(directorio_uploads, "audio")
        
        for directorio in [self.directorio_texto, self.directorio_imagenes, self.directorio_audio]:
            os.makedirs(directorio, exist_ok=True)
        
        # Configuración de límites de archivo
        self.limites_archivo = {
            'texto': 50000,        # 50KB para texto
            'imagen': 5242880,     # 5MB para imágenes
            'audio': 10485760      # 10MB para audio
        }
        
        # Formatos permitidos
        self.formatos_permitidos = {
            'imagen': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'},
            'audio': {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}
        }
        
        # Inicializar reconocedor de voz
        self.reconocedor_voz = sr.Recognizer()
        
        # Base de datos en memoria para submissions (en producción usar BD real)
        self.submissions_pendientes = {}
        
        logger.info(f"PipelineEntrenamiento inicializado en directorio: {directorio_uploads}")
    
    def procesar_contenido_texto(self, contenido: str, id_usuario: str, metadatos: Dict = None) -> Dict[str, Any]:
        """
        Procesa contenido de texto para entrenamiento
        Args:
            contenido: Texto del contenido técnico
            id_usuario: ID del usuario que sube el contenido
            metadatos: Metadatos adicionales del contenido
        Returns:
            Diccionario con resultado del procesamiento
        """
        try:
            logger.info(f"Procesando contenido de texto de usuario: {id_usuario}")
            
            # Validar longitud del contenido
            if len(contenido) > self.limites_archivo['texto']:
                raise ValueError(f"Contenido de texto demasiado largo: {len(contenido)} caracteres")
            
            if len(contenido.strip()) < 10:
                raise ValueError("Contenido de texto demasiado corto (mínimo 10 caracteres)")
            
            # Limpiar y normalizar texto
            contenido_limpio = self._limpiar_texto(contenido)
            
            # Extraer información técnica relevante
            info_tecnica = self._extraer_informacion_tecnica(contenido_limpio)
            
            # Generar ID único para la submission
            id_submission = self._generar_id_submission('texto', id_usuario)
            
            # Crear objeto de submission
            submission = {
                'id': id_submission,
                'tipo_contenido': 'texto',
                'contenido_original': contenido,
                'contenido_procesado': contenido_limpio,
                'informacion_tecnica': info_tecnica,
                'id_usuario': id_usuario,
                'fecha_submission': datetime.now().isoformat(),
                'estado': 'pendiente_validacion',
                'metadatos': metadatos or {},
                'puntuacion_calidad': self._evaluar_calidad_texto(contenido_limpio),
                'archivo_guardado': None
            }
            
            # Guardar archivo de texto
            ruta_archivo = self._guardar_archivo_texto(id_submission, contenido_limpio)
            submission['archivo_guardado'] = ruta_archivo
            
            # Almacenar submission para validación
            self.submissions_pendientes[id_submission] = submission
            
            logger.info(f"Contenido de texto procesado exitosamente: {id_submission}")
            
            return {
                'exito': True,
                'id_submission': id_submission,
                'estado': 'pendiente_validacion',
                'puntuacion_calidad': submission['puntuacion_calidad'],
                'informacion_extraida': info_tecnica
            }
            
        except Exception as e:
            logger.error(f"Error procesando contenido de texto: {str(e)}")
            return {
                'exito': False,
                'error': str(e),
                'codigo_error': 'ERROR_PROCESAMIENTO_TEXTO'
            }
    
    def procesar_contenido_imagen(self, datos_imagen: bytes, nombre_archivo: str, 
                                 id_usuario: str, metadatos: Dict = None) -> Dict[str, Any]:
        """
        Procesa contenido de imagen para entrenamiento
        Args:
            datos_imagen: Datos binarios de la imagen
            nombre_archivo: Nombre original del archivo
            id_usuario: ID del usuario que sube la imagen
            metadatos: Metadatos adicionales
        Returns:
            Diccionario con resultado del procesamiento
        """
        try:
            logger.info(f"Procesando imagen de usuario: {id_usuario}, archivo: {nombre_archivo}")
            
            # Validar tamaño del archivo
            if len(datos_imagen) > self.limites_archivo['imagen']:
                raise ValueError(f"Imagen demasiado grande: {len(datos_imagen)} bytes")
            
            # Validar formato de archivo
            extension = os.path.splitext(nombre_archivo.lower())[1]
            if extension not in self.formatos_permitidos['imagen']:
                raise ValueError(f"Formato de imagen no permitido: {extension}")
            
            # Procesar imagen con PIL
            imagen_procesada = self._procesar_imagen_pil(datos_imagen)
            
            # Extraer metadatos de la imagen
            metadatos_imagen = self._extraer_metadatos_imagen(imagen_procesada, nombre_archivo)
            
            # Generar ID único para la submission
            id_submission = self._generar_id_submission('imagen', id_usuario)
            
            # Guardar archivo de imagen
            ruta_archivo = self._guardar_archivo_imagen(id_submission, datos_imagen, extension)
            
            # Crear objeto de submission
            submission = {
                'id': id_submission,
                'tipo_contenido': 'imagen',
                'nombre_archivo_original': nombre_archivo,
                'extension': extension,
                'tamaño_bytes': len(datos_imagen),
                'metadatos_imagen': metadatos_imagen,
                'id_usuario': id_usuario,
                'fecha_submission': datetime.now().isoformat(),
                'estado': 'pendiente_validacion',
                'metadatos': metadatos or {},
                'puntuacion_calidad': self._evaluar_calidad_imagen(metadatos_imagen),
                'archivo_guardado': ruta_archivo
            }
            
            # Almacenar submission para validación
            self.submissions_pendientes[id_submission] = submission
            
            logger.info(f"Imagen procesada exitosamente: {id_submission}")
            
            return {
                'exito': True,
                'id_submission': id_submission,
                'estado': 'pendiente_validacion',
                'puntuacion_calidad': submission['puntuacion_calidad'],
                'metadatos_extraidos': metadatos_imagen
            }
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {str(e)}")
            return {
                'exito': False,
                'error': str(e),
                'codigo_error': 'ERROR_PROCESAMIENTO_IMAGEN'
            }
    
    def procesar_contenido_audio(self, datos_audio: bytes, nombre_archivo: str,
                                id_usuario: str, metadatos: Dict = None) -> Dict[str, Any]:
        """
        Procesa contenido de audio para entrenamiento con transcripción automática
        Args:
            datos_audio: Datos binarios del audio
            nombre_archivo: Nombre original del archivo
            id_usuario: ID del usuario que sube el audio
            metadatos: Metadatos adicionales
        Returns:
            Diccionario con resultado del procesamiento
        """
        try:
            logger.info(f"Procesando audio de usuario: {id_usuario}, archivo: {nombre_archivo}")
            
            # Validar tamaño del archivo
            if len(datos_audio) > self.limites_archivo['audio']:
                raise ValueError(f"Archivo de audio demasiado grande: {len(datos_audio)} bytes")
            
            # Validar formato de archivo
            extension = os.path.splitext(nombre_archivo.lower())[1]
            if extension not in self.formatos_permitidos['audio']:
                raise ValueError(f"Formato de audio no permitido: {extension}")
            
            # Generar ID único para la submission
            id_submission = self._generar_id_submission('audio', id_usuario)
            
            # Guardar archivo de audio
            ruta_archivo = self._guardar_archivo_audio(id_submission, datos_audio, extension)
            
            # Transcribir audio a texto
            resultado_transcripcion = self._transcribir_audio(ruta_archivo)
            
            # Procesar texto transcrito si fue exitoso
            info_tecnica = {}
            puntuacion_calidad = 0.5  # Puntuación base para audio
            
            if resultado_transcripcion['exito']:
                texto_transcrito = resultado_transcripcion['texto']
                info_tecnica = self._extraer_informacion_tecnica(texto_transcrito)
                puntuacion_calidad = self._evaluar_calidad_texto(texto_transcrito)
            
            # Crear objeto de submission
            submission = {
                'id': id_submission,
                'tipo_contenido': 'audio',
                'nombre_archivo_original': nombre_archivo,
                'extension': extension,
                'tamaño_bytes': len(datos_audio),
                'transcripcion': resultado_transcripcion,
                'informacion_tecnica': info_tecnica,
                'id_usuario': id_usuario,
                'fecha_submission': datetime.now().isoformat(),
                'estado': 'pendiente_validacion',
                'metadatos': metadatos or {},
                'puntuacion_calidad': puntuacion_calidad,
                'archivo_guardado': ruta_archivo
            }
            
            # Almacenar submission para validación
            self.submissions_pendientes[id_submission] = submission
            
            logger.info(f"Audio procesado exitosamente: {id_submission}")
            
            return {
                'exito': True,
                'id_submission': id_submission,
                'estado': 'pendiente_validacion',
                'transcripcion': resultado_transcripcion,
                'puntuacion_calidad': puntuacion_calidad,
                'informacion_extraida': info_tecnica
            }
            
        except Exception as e:
            logger.error(f"Error procesando audio: {str(e)}")
            return {
                'exito': False,
                'error': str(e),
                'codigo_error': 'ERROR_PROCESAMIENTO_AUDIO'
            }
    
    def _limpiar_texto(self, texto: str) -> str:
        """
        Limpia y normaliza texto de entrada
        Args:
            texto: Texto original
        Returns:
            Texto limpio y normalizado
        """
        # Eliminar caracteres de control y espacios extra
        texto_limpio = ' '.join(texto.split())
        
        # Normalizar saltos de línea
        texto_limpio = texto_limpio.replace('\r\n', '\n').replace('\r', '\n')
        
        # Eliminar caracteres especiales problemáticos pero mantener acentos
        caracteres_permitidos = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                                  'áéíóúüñÁÉÍÓÚÜÑ .,;:()[]{}¿?¡!-_/\\@#$%&*+=<>|~`"\'')
        texto_limpio = ''.join(c for c in texto_limpio if c in caracteres_permitidos)
        
        return texto_limpio.strip()
    
    def _extraer_informacion_tecnica(self, texto: str) -> Dict[str, Any]:
        """
        Extrae información técnica relevante del texto
        Args:
            texto: Texto a analizar
        Returns:
            Diccionario con información técnica extraída
        """
        info_tecnica = {
            'parametros_mencionados': [],
            'codigos_error_mencionados': [],
            'procedimientos_identificados': [],
            'componentes_mencionados': [],
            'palabras_clave_tecnicas': []
        }
        
        texto_lower = texto.lower()
        
        # Buscar parámetros (P seguido de números)
        import re
        parametros = re.findall(r'p\d+(?:\.\d+)?', texto_lower)
        info_tecnica['parametros_mencionados'] = list(set(parametros))
        
        # Buscar códigos de error comunes del ABB ACS150
        codigos_error = re.findall(r'(?:error|falla|alarma)\s*(?:código\s*)?([a-z]?\d+)', texto_lower)
        info_tecnica['codigos_error_mencionados'] = list(set(codigos_error))
        
        # Identificar palabras clave técnicas específicas del ABB ACS150
        palabras_clave_abb = [
            'variador', 'frecuencia', 'motor', 'velocidad', 'torque', 'corriente',
            'voltaje', 'potencia', 'instalacion', 'configuracion', 'parametro',
            'mantenimiento', 'diagnostico', 'conexion', 'cableado', 'display',
            'menu', 'programacion', 'arranque', 'parada', 'proteccion'
        ]
        
        palabras_encontradas = []
        for palabra in palabras_clave_abb:
            if palabra in texto_lower:
                palabras_encontradas.append(palabra)
        
        info_tecnica['palabras_clave_tecnicas'] = palabras_encontradas
        
        # Identificar procedimientos (palabras que indican pasos o acciones)
        indicadores_procedimiento = [
            'paso', 'procedimiento', 'instruccion', 'configurar', 'ajustar',
            'verificar', 'comprobar', 'medir', 'instalar', 'conectar'
        ]
        
        procedimientos = []
        for indicador in indicadores_procedimiento:
            if indicador in texto_lower:
                procedimientos.append(indicador)
        
        info_tecnica['procedimientos_identificados'] = procedimientos
        
        return info_tecnica
    
    def _evaluar_calidad_texto(self, texto: str) -> float:
        """
        Evalúa la calidad del contenido de texto
        Args:
            texto: Texto a evaluar
        Returns:
            Puntuación de calidad (0.0 - 1.0)
        """
        puntuacion = 0.0
        
        # Puntuación por longitud (textos muy cortos o muy largos penalizan)
        longitud = len(texto)
        if 50 <= longitud <= 2000:
            puntuacion += 0.3
        elif 20 <= longitud < 50 or 2000 < longitud <= 5000:
            puntuacion += 0.2
        else:
            puntuacion += 0.1
        
        # Puntuación por contenido técnico
        info_tecnica = self._extraer_informacion_tecnica(texto)
        
        if info_tecnica['parametros_mencionados']:
            puntuacion += 0.2
        if info_tecnica['palabras_clave_tecnicas']:
            puntuacion += 0.2 * min(len(info_tecnica['palabras_clave_tecnicas']) / 5, 1.0)
        if info_tecnica['procedimientos_identificados']:
            puntuacion += 0.2
        
        # Puntuación por estructura (presencia de puntuación, mayúsculas, etc.)
        if any(c in texto for c in '.,;:'):
            puntuacion += 0.1
        
        return min(puntuacion, 1.0)
    
    def _procesar_imagen_pil(self, datos_imagen: bytes) -> Image.Image:
        """
        Procesa imagen usando PIL
        Args:
            datos_imagen: Datos binarios de la imagen
        Returns:
            Objeto Image de PIL
        """
        try:
            imagen = Image.open(BytesIO(datos_imagen))
            
            # Convertir a RGB si es necesario
            if imagen.mode not in ('RGB', 'RGBA'):
                imagen = imagen.convert('RGB')
            
            return imagen
            
        except Exception as e:
            logger.error(f"Error procesando imagen con PIL: {str(e)}")
            raise ValueError(f"Imagen corrupta o formato no válido: {str(e)}")
    
    def _extraer_metadatos_imagen(self, imagen: Image.Image, nombre_archivo: str) -> Dict[str, Any]:
        """
        Extrae metadatos de una imagen
        Args:
            imagen: Objeto Image de PIL
            nombre_archivo: Nombre del archivo original
        Returns:
            Diccionario con metadatos
        """
        metadatos = {
            'ancho': imagen.width,
            'alto': imagen.height,
            'modo_color': imagen.mode,
            'formato': imagen.format or 'desconocido',
            'nombre_archivo': nombre_archivo,
            'relacion_aspecto': round(imagen.width / imagen.height, 2) if imagen.height > 0 else 0
        }
        
        # Extraer información EXIF si está disponible
        try:
            if hasattr(imagen, '_getexif') and imagen._getexif():
                exif_data = imagen._getexif()
                metadatos['tiene_exif'] = True
                metadatos['datos_exif'] = dict(exif_data) if exif_data else {}
            else:
                metadatos['tiene_exif'] = False
        except Exception:
            metadatos['tiene_exif'] = False
        
        return metadatos
    
    def _evaluar_calidad_imagen(self, metadatos: Dict[str, Any]) -> float:
        """
        Evalúa la calidad de una imagen basada en sus metadatos
        Args:
            metadatos: Metadatos de la imagen
        Returns:
            Puntuación de calidad (0.0 - 1.0)
        """
        puntuacion = 0.5  # Puntuación base
        
        # Puntuación por resolución
        ancho = metadatos.get('ancho', 0)
        alto = metadatos.get('alto', 0)
        pixeles_totales = ancho * alto
        
        if pixeles_totales >= 1920 * 1080:  # Full HD o superior
            puntuacion += 0.3
        elif pixeles_totales >= 1280 * 720:  # HD
            puntuacion += 0.2
        elif pixeles_totales >= 640 * 480:   # VGA
            puntuacion += 0.1
        
        # Puntuación por relación de aspecto (imágenes muy distorsionadas penalizan)
        relacion_aspecto = metadatos.get('relacion_aspecto', 1.0)
        if 0.5 <= relacion_aspecto <= 2.0:  # Relación razonable
            puntuacion += 0.1
        
        # Puntuación por modo de color
        if metadatos.get('modo_color') in ('RGB', 'RGBA'):
            puntuacion += 0.1
        
        return min(puntuacion, 1.0)
    
    def _transcribir_audio(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Transcribe archivo de audio a texto
        Args:
            ruta_archivo: Ruta al archivo de audio
        Returns:
            Diccionario con resultado de transcripción
        """
        try:
            # Cargar archivo de audio
            with sr.AudioFile(ruta_archivo) as fuente_audio:
                # Ajustar para ruido ambiente
                self.reconocedor_voz.adjust_for_ambient_noise(fuente_audio, duration=0.5)
                
                # Grabar audio
                audio_data = self.reconocedor_voz.record(fuente_audio)
            
            # Transcribir usando Google Speech Recognition
            texto_transcrito = self.reconocedor_voz.recognize_google(
                audio_data, 
                language='es-ES'  # Español de España
            )
            
            logger.info(f"Audio transcrito exitosamente: {len(texto_transcrito)} caracteres")
            
            return {
                'exito': True,
                'texto': texto_transcrito,
                'confianza': 0.8,  # Valor estimado
                'idioma_detectado': 'es-ES'
            }
            
        except sr.UnknownValueError:
            logger.warning("No se pudo entender el audio")
            return {
                'exito': False,
                'error': 'Audio no comprensible o sin voz detectada',
                'codigo_error': 'AUDIO_NO_COMPRENSIBLE'
            }
        except sr.RequestError as e:
            logger.error(f"Error en servicio de transcripción: {str(e)}")
            return {
                'exito': False,
                'error': f'Error en servicio de transcripción: {str(e)}',
                'codigo_error': 'ERROR_SERVICIO_TRANSCRIPCION'
            }
        except Exception as e:
            logger.error(f"Error transcribiendo audio: {str(e)}")
            return {
                'exito': False,
                'error': str(e),
                'codigo_error': 'ERROR_TRANSCRIPCION_GENERAL'
            }
    
    def _generar_id_submission(self, tipo: str, id_usuario: str) -> str:
        """
        Genera ID único para una submission
        Args:
            tipo: Tipo de contenido (texto, imagen, audio)
            id_usuario: ID del usuario
        Returns:
            ID único generado
        """
        timestamp = datetime.now().timestamp()
        contenido_hash = hashlib.md5(f"{tipo}_{id_usuario}_{timestamp}".encode()).hexdigest()[:8]
        return f"{tipo}_{contenido_hash}"
    
    def _guardar_archivo_texto(self, id_submission: str, contenido: str) -> str:
        """
        Guarda archivo de texto en disco
        Args:
            id_submission: ID de la submission
            contenido: Contenido de texto
        Returns:
            Ruta del archivo guardado
        """
        nombre_archivo = f"{id_submission}.txt"
        ruta_archivo = os.path.join(self.directorio_texto, nombre_archivo)
        
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)
        
        return ruta_archivo
    
    def _guardar_archivo_imagen(self, id_submission: str, datos_imagen: bytes, extension: str) -> str:
        """
        Guarda archivo de imagen en disco
        Args:
            id_submission: ID de la submission
            datos_imagen: Datos binarios de la imagen
            extension: Extensión del archivo
        Returns:
            Ruta del archivo guardado
        """
        nombre_archivo = f"{id_submission}{extension}"
        ruta_archivo = os.path.join(self.directorio_imagenes, nombre_archivo)
        
        with open(ruta_archivo, 'wb') as archivo:
            archivo.write(datos_imagen)
        
        return ruta_archivo
    
    def _guardar_archivo_audio(self, id_submission: str, datos_audio: bytes, extension: str) -> str:
        """
        Guarda archivo de audio en disco
        Args:
            id_submission: ID de la submission
            datos_audio: Datos binarios del audio
            extension: Extensión del archivo
        Returns:
            Ruta del archivo guardado
        """
        nombre_archivo = f"{id_submission}{extension}"
        ruta_archivo = os.path.join(self.directorio_audio, nombre_archivo)
        
        with open(ruta_archivo, 'wb') as archivo:
            archivo.write(datos_audio)
        
        return ruta_archivo
    
    def obtener_submission(self, id_submission: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una submission por su ID
        Args:
            id_submission: ID de la submission
        Returns:
            Datos de la submission o None si no existe
        """
        return self.submissions_pendientes.get(id_submission)
    
    def listar_submissions_pendientes(self, id_usuario: str = None) -> List[Dict[str, Any]]:
        """
        Lista submissions pendientes de validación
        Args:
            id_usuario: Filtrar por usuario específico (opcional)
        Returns:
            Lista de submissions pendientes
        """
        submissions = list(self.submissions_pendientes.values())
        
        if id_usuario:
            submissions = [s for s in submissions if s['id_usuario'] == id_usuario]
        
        # Ordenar por fecha de submission (más recientes primero)
        submissions.sort(key=lambda x: x['fecha_submission'], reverse=True)
        
        return submissions