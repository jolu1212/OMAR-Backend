# Motor principal de chat con integración a OpenAI GPT-4o-mini
import openai
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

class MotorChat:
    """
    Motor principal de conversación que procesa consultas técnicas
    y genera respuestas contextuales usando OpenAI GPT-4o-mini
    """
    
    def __init__(self, clave_api_openai: str):
        """
        Constructor del motor de chat
        Args:
            clave_api_openai: Clave de API de OpenAI para autenticación
        """
        # Configurar cliente de OpenAI
        openai.api_key = clave_api_openai
        self.cliente_openai = openai
        
        # Configuración específica para respuestas técnicas
        self.temperatura = 0.3          # Temperatura baja para respuestas más precisas
        self.max_tokens = 1500          # Límite de tokens por respuesta
        self.modelo = 'gpt-4o-mini'     # Modelo específico para uso técnico
        
        # Contexto especializado para ABB ACS150
        self.contexto_abb_acs150 = """
        Eres OMAR, un asistente técnico especializado en el variador de frecuencia ABB ACS150.
        Tu función es ayudar a técnicos, operadores y supervisores industriales con:
        
        - Diagnóstico de problemas y fallas del variador ABB ACS150
        - Configuración y parametrización del equipo
        - Procedimientos de mantenimiento preventivo y correctivo
        - Interpretación de códigos de error y alarmas
        - Guías de instalación y conexión eléctrica
        - Optimización de parámetros para diferentes aplicaciones
        
        INSTRUCCIONES IMPORTANTES:
        - Siempre proporciona respuestas técnicas precisas y concisas
        - Usa terminología técnica apropiada pero explicada claramente
        - Si necesitas más información, solicita clarificación específica
        - Prioriza la seguridad en todas las recomendaciones
        - Incluye referencias a códigos de parámetros cuando sea relevante
        - Responde en español de manera profesional y técnica
        """
        
        # Cache para respuestas frecuentes
        self.cache_respuestas = {}
        
        # Patrones para detectar tipos de consulta
        self.patrones_consulta = {
            'codigo_error': r'(error|falla|alarma|código)\s*(\d+|[A-Z]+\d*)',
            'parametro': r'(parámetro|param|P\d+|configurar)',
            'instalacion': r'(instalar|conexión|cableado|montaje)',
            'mantenimiento': r'(mantenimiento|limpieza|revisión|preventivo)',
            'diagnostico': r'(problema|no funciona|falla|diagnóstico)'
        }
        
        logger.info("MotorChat inicializado con modelo GPT-4o-mini para ABB ACS150")
    
    def procesar_consulta(self, consulta: str, id_sesion: str, contexto: Dict = None) -> Dict[str, Any]:
        """
        Procesa una consulta técnica y genera respuesta contextual
        Args:
            consulta: Texto de la consulta del usuario
            id_sesion: ID de la sesión para contexto
            contexto: Información adicional de contexto
        Returns:
            Dict con la respuesta procesada
        """
        try:
            logger.info(f"Procesando consulta para sesión {id_sesion}: {consulta[:50]}...")
            
            # Verificar cache para respuestas frecuentes
            clave_cache = self._generar_clave_cache(consulta)
            if clave_cache in self.cache_respuestas:
                logger.debug(f"Respuesta encontrada en cache para: {clave_cache}")
                return self.cache_respuestas[clave_cache]
            
            # Detectar tipo de consulta
            tipo_consulta = self._detectar_tipo_consulta(consulta)
            
            # Construir prompt especializado
            prompt_completo = self._construir_prompt(consulta, tipo_consulta, contexto)
            
            # Llamar a OpenAI
            respuesta_openai = self._llamar_openai(prompt_completo)
            
            # Procesar y formatear respuesta
            respuesta_formateada = self._formatear_respuesta_tecnica(
                respuesta_openai, tipo_consulta
            )
            
            # Determinar si requiere clarificación
            requiere_clarificacion = self._evaluar_necesidad_clarificacion(
                consulta, respuesta_openai
            )
            
            # Obtener contenido visual relacionado
            contenido_visual = self._obtener_contenido_visual(consulta, tipo_consulta)
            
            # Generar acciones sugeridas
            acciones_sugeridas = self._generar_acciones_sugeridas(tipo_consulta, consulta)
            
            # Construir respuesta final
            respuesta_final = {
                'mensaje': respuesta_formateada,
                'puntuacion_confianza': self._calcular_puntuacion_confianza(respuesta_openai),
                'contenido_visual': contenido_visual,
                'acciones_sugeridas': acciones_sugeridas,
                'requiere_clarificacion': requiere_clarificacion,
                'tipo_consulta': tipo_consulta,
                'timestamp': datetime.now().isoformat()
            }
            
            # Guardar en cache si es una respuesta de alta confianza
            if respuesta_final['puntuacion_confianza'] > 0.8:
                self.cache_respuestas[clave_cache] = respuesta_final
            
            logger.info(f"Consulta procesada exitosamente para sesión {id_sesion}")
            return respuesta_final
            
        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            return self._generar_respuesta_error(str(e))
    
    def _detectar_tipo_consulta(self, consulta: str) -> str:
        """
        Detecta el tipo de consulta basado en patrones de texto
        Args:
            consulta: Texto de la consulta
        Returns:
            Tipo de consulta detectado
        """
        consulta_lower = consulta.lower()
        
        # Verificar cada patrón
        for tipo, patron in self.patrones_consulta.items():
            if re.search(patron, consulta_lower):
                logger.debug(f"Tipo de consulta detectado: {tipo}")
                return tipo
        
        # Tipo general si no se detecta patrón específico
        return 'general'
    
    def _construir_prompt(self, consulta: str, tipo_consulta: str, contexto: Dict = None) -> str:
        """
        Construye el prompt completo para OpenAI incluyendo contexto especializado
        Args:
            consulta: Consulta del usuario
            tipo_consulta: Tipo de consulta detectado
            contexto: Contexto adicional
        Returns:
            Prompt completo para OpenAI
        """
        # Prompt base con contexto ABB ACS150
        prompt = self.contexto_abb_acs150 + "\n\n"
        
        # Añadir instrucciones específicas según tipo de consulta
        if tipo_consulta == 'codigo_error':
            prompt += """
            CONSULTA SOBRE CÓDIGO DE ERROR:
            - Identifica el código de error específico
            - Explica la causa probable del error
            - Proporciona pasos de diagnóstico
            - Sugiere soluciones paso a paso
            - Incluye medidas preventivas
            """
        elif tipo_consulta == 'parametro':
            prompt += """
            CONSULTA SOBRE PARÁMETROS:
            - Identifica el parámetro específico
            - Explica la función del parámetro
            - Proporciona rangos de valores recomendados
            - Incluye consideraciones de aplicación
            - Menciona parámetros relacionados
            """
        elif tipo_consulta == 'instalacion':
            prompt += """
            CONSULTA SOBRE INSTALACIÓN:
            - Proporciona pasos de instalación ordenados
            - Incluye consideraciones de seguridad
            - Especifica herramientas necesarias
            - Menciona verificaciones post-instalación
            - Incluye diagramas de conexión si es relevante
            """
        
        # Añadir contexto adicional si está disponible
        if contexto:
            prompt += f"\nCONTEXTO ADICIONAL:\n{json.dumps(contexto, indent=2)}\n"
        
        # Añadir la consulta del usuario
        prompt += f"\nCONSULTA DEL USUARIO:\n{consulta}\n\n"
        prompt += "RESPUESTA TÉCNICA:"
        
        return prompt
    
    def _llamar_openai(self, prompt: str) -> str:
        """
        Realiza la llamada a la API de OpenAI
        Args:
            prompt: Prompt completo para enviar
        Returns:
            Respuesta de OpenAI
        """
        try:
            respuesta = self.cliente_openai.ChatCompletion.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": "Eres OMAR, asistente técnico especializado en ABB ACS150"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperatura,
                max_tokens=self.max_tokens,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return respuesta.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error en llamada a OpenAI: {str(e)}")
            # Respuesta de fallback
            return self._generar_respuesta_fallback()
    
    def _formatear_respuesta_tecnica(self, respuesta_cruda: str, tipo_consulta: str) -> str:
        """
        Formatea la respuesta para mejorar legibilidad técnica
        Args:
            respuesta_cruda: Respuesta original de OpenAI
            tipo_consulta: Tipo de consulta para formateo específico
        Returns:
            Respuesta formateada
        """
        # Limpiar y estructurar la respuesta
        respuesta = respuesta_cruda.strip()
        
        # Añadir estructura según tipo de consulta
        if tipo_consulta == 'codigo_error':
            # Asegurar estructura para códigos de error
            if not re.search(r'(CAUSA|SOLUCIÓN|DIAGNÓSTICO)', respuesta, re.IGNORECASE):
                respuesta = f"📋 DIAGNÓSTICO:\n{respuesta}"
        
        elif tipo_consulta == 'parametro':
            # Estructurar respuestas de parámetros
            if not re.search(r'(PARÁMETRO|RANGO|FUNCIÓN)', respuesta, re.IGNORECASE):
                respuesta = f"⚙️ CONFIGURACIÓN DE PARÁMETRO:\n{respuesta}"
        
        # Añadir emojis técnicos para mejor visualización
        respuesta = self._añadir_emojis_tecnicos(respuesta)
        
        return respuesta
    
    def _añadir_emojis_tecnicos(self, texto: str) -> str:
        """
        Añade emojis técnicos para mejorar la visualización
        Args:
            texto: Texto original
        Returns:
            Texto con emojis técnicos
        """
        # Mapeo de palabras técnicas a emojis
        mapeo_emojis = {
            r'\b(error|falla|alarma)\b': '⚠️ \\1',
            r'\b(solución|resolver)\b': '✅ \\1',
            r'\b(parámetro|configurar)\b': '⚙️ \\1',
            r'\b(instalación|conexión)\b': '🔧 \\1',
            r'\b(mantenimiento|revisión)\b': '🛠️ \\1',
            r'\b(seguridad|peligro)\b': '🚨 \\1',
            r'\b(voltaje|corriente|potencia)\b': '⚡ \\1'
        }
        
        for patron, reemplazo in mapeo_emojis.items():
            texto = re.sub(patron, reemplazo, texto, flags=re.IGNORECASE)
        
        return texto
    
    def _evaluar_necesidad_clarificacion(self, consulta: str, respuesta: str) -> bool:
        """
        Evalúa si la consulta requiere clarificación adicional
        Args:
            consulta: Consulta original
            respuesta: Respuesta generada
        Returns:
            True si requiere clarificación
        """
        # Indicadores de consulta ambigua
        indicadores_ambiguedad = [
            'más información', 'especificar', 'clarificar', 'detalles',
            'qué tipo', 'cuál modelo', 'en qué condiciones'
        ]
        
        # Verificar si la respuesta contiene indicadores de ambigüedad
        respuesta_lower = respuesta.lower()
        for indicador in indicadores_ambiguedad:
            if indicador in respuesta_lower:
                return True
        
        # Verificar si la consulta es muy corta o vaga
        if len(consulta.split()) < 3:
            return True
        
        return False
    
    def _obtener_contenido_visual(self, consulta: str, tipo_consulta: str) -> List[Dict]:
        """
        Obtiene referencias a contenido visual relacionado
        Args:
            consulta: Consulta del usuario
            tipo_consulta: Tipo de consulta
        Returns:
            Lista de referencias a imágenes
        """
        contenido_visual = []
        
        # Mapeo de tipos de consulta a imágenes relevantes
        if tipo_consulta == 'instalacion':
            contenido_visual.append({
                'id': 'abb_acs150_conexiones',
                'url': '/images/abb_acs150_diagrama_conexiones.png',
                'descripcion': 'Diagrama de conexiones ABB ACS150',
                'tags': ['instalacion', 'conexiones', 'diagrama']
            })
        
        elif tipo_consulta == 'codigo_error':
            contenido_visual.append({
                'id': 'abb_acs150_display',
                'url': '/images/abb_acs150_display_errores.png',
                'descripcion': 'Display de códigos de error ABB ACS150',
                'tags': ['errores', 'display', 'codigos']
            })
        
        return contenido_visual
    
    def _generar_acciones_sugeridas(self, tipo_consulta: str, consulta: str) -> List[str]:
        """
        Genera acciones sugeridas basadas en el tipo de consulta
        Args:
            tipo_consulta: Tipo de consulta detectado
            consulta: Consulta original
        Returns:
            Lista de acciones sugeridas
        """
        acciones = []
        
        if tipo_consulta == 'codigo_error':
            acciones = [
                "Verificar conexiones eléctricas",
                "Revisar parámetros de configuración",
                "Consultar manual técnico",
                "Contactar soporte técnico si persiste"
            ]
        elif tipo_consulta == 'parametro':
            acciones = [
                "Respaldar configuración actual",
                "Modificar parámetro gradualmente",
                "Probar funcionamiento",
                "Documentar cambios realizados"
            ]
        elif tipo_consulta == 'instalacion':
            acciones = [
                "Verificar herramientas necesarias",
                "Revisar especificaciones técnicas",
                "Seguir procedimientos de seguridad",
                "Realizar pruebas de funcionamiento"
            ]
        else:
            acciones = [
                "Proporcionar más detalles específicos",
                "Consultar documentación técnica",
                "Verificar estado del equipo"
            ]
        
        return acciones
    
    def _calcular_puntuacion_confianza(self, respuesta: str) -> float:
        """
        Calcula una puntuación de confianza para la respuesta
        Args:
            respuesta: Respuesta generada
        Returns:
            Puntuación de confianza entre 0 y 1
        """
        puntuacion = 0.5  # Puntuación base
        
        # Factores que aumentan la confianza
        if len(respuesta) > 100:  # Respuesta detallada
            puntuacion += 0.1
        
        if re.search(r'(parámetro|P\d+)', respuesta, re.IGNORECASE):  # Menciona parámetros específicos
            puntuacion += 0.2
        
        if re.search(r'(paso|procedimiento|instrucción)', respuesta, re.IGNORECASE):  # Incluye pasos
            puntuacion += 0.1
        
        if re.search(r'(seguridad|precaución|advertencia)', respuesta, re.IGNORECASE):  # Considera seguridad
            puntuacion += 0.1
        
        return min(puntuacion, 1.0)  # Máximo 1.0
    
    def _generar_clave_cache(self, consulta: str) -> str:
        """
        Genera una clave de cache para la consulta
        Args:
            consulta: Consulta del usuario
        Returns:
            Clave de cache normalizada
        """
        # Normalizar consulta para cache
        consulta_normalizada = re.sub(r'[^\w\s]', '', consulta.lower())
        palabras_clave = consulta_normalizada.split()[:5]  # Primeras 5 palabras
        return '_'.join(palabras_clave)
    
    def _generar_respuesta_fallback(self) -> str:
        """
        Genera una respuesta de fallback cuando OpenAI no está disponible
        Returns:
            Respuesta de fallback
        """
        return """
        🔧 OMAR - Asistente Técnico ABB ACS150
        
        Actualmente experimento dificultades técnicas para procesar tu consulta.
        
        📋 RECOMENDACIONES GENERALES:
        • Verifica las conexiones eléctricas del variador
        • Revisa que los parámetros básicos estén configurados correctamente
        • Consulta el manual técnico ABB ACS150 para procedimientos específicos
        • Si el problema persiste, contacta al soporte técnico
        
        ⚠️ IMPORTANTE: Siempre sigue los procedimientos de seguridad antes de realizar cualquier intervención.
        
        Intenta tu consulta nuevamente en unos momentos.
        """
    
    def _generar_respuesta_error(self, error: str) -> Dict[str, Any]:
        """
        Genera una respuesta de error estructurada
        Args:
            error: Mensaje de error
        Returns:
            Respuesta de error formateada
        """
        return {
            'mensaje': self._generar_respuesta_fallback(),
            'puntuacion_confianza': 0.0,
            'contenido_visual': [],
            'acciones_sugeridas': [
                "Verificar conexión a internet",
                "Intentar nuevamente en unos momentos",
                "Contactar soporte técnico si el problema persiste"
            ],
            'requiere_clarificacion': False,
            'tipo_consulta': 'error',
            'timestamp': datetime.now().isoformat(),
            'error_tecnico': error
        }