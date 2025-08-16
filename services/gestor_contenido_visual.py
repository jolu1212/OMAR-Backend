# Gestor de contenido visual para respuestas técnicas del chatbot
import os
import logging
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
import hashlib

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

class GestorContenidoVisual:
    """
    Gestor centralizado para contenido visual técnico
    Maneja imágenes, diagramas y referencias visuales para el ABB ACS150
    """
    
    def __init__(self, directorio_imagenes: str = "static/images"):
        """
        Constructor del gestor de contenido visual
        Args:
            directorio_imagenes: Directorio donde se almacenan las imágenes
        """
        self.directorio_imagenes = directorio_imagenes
        
        # Crear directorio si no existe
        os.makedirs(directorio_imagenes, exist_ok=True)
        
        # Base de datos en memoria de contenido visual (en producción usar BD real)
        self.base_datos_visual = {}
        
        # Mapeo de temas técnicos a contenido visual
        self.mapeo_temas_visuales = {
            'instalacion': [
                'abb_acs150_diagrama_conexiones',
                'abb_acs150_montaje_panel',
                'abb_acs150_cableado_potencia'
            ],
            'codigo_error': [
                'abb_acs150_display_errores',
                'abb_acs150_codigos_falla',
                'abb_acs150_led_estados'
            ],
            'parametro': [
                'abb_acs150_menu_parametros',
                'abb_acs150_configuracion_basica',
                'abb_acs150_parametros_motor'
            ],
            'mantenimiento': [
                'abb_acs150_limpieza_filtros',
                'abb_acs150_inspeccion_visual',
                'abb_acs150_verificacion_conexiones'
            ],
            'diagnostico': [
                'abb_acs150_mediciones_electricas',
                'abb_acs150_pruebas_funcionamiento',
                'abb_acs150_analisis_vibraciones'
            ]
        }
        
        # Inicializar contenido visual predefinido
        self._inicializar_contenido_predefinido()
        
        logger.info(f"GestorContenidoVisual inicializado con directorio: {directorio_imagenes}")
    
    def _inicializar_contenido_predefinido(self):
        """
        Inicializa el contenido visual predefinido para ABB ACS150
        """
        contenido_predefinido = [
            {
                'id': 'abb_acs150_diagrama_conexiones',
                'titulo': 'Diagrama de Conexiones ABB ACS150',
                'descripcion': 'Diagrama completo de conexiones eléctricas del variador ABB ACS150',
                'url': '/images/abb_acs150_conexiones.png',
                'tags': ['instalacion', 'conexiones', 'diagrama', 'cableado'],
                'temas_relacionados': ['instalacion', 'parametro'],
                'tipo_contenido': 'diagrama_tecnico',
                'prioridad': 1
            },
            {
                'id': 'abb_acs150_display_errores',
                'titulo': 'Display de Códigos de Error',
                'descripcion': 'Pantalla LCD mostrando códigos de error y su interpretación',
                'url': '/images/abb_acs150_display.png',
                'tags': ['error', 'display', 'codigos', 'fallas'],
                'temas_relacionados': ['codigo_error', 'diagnostico'],
                'tipo_contenido': 'captura_pantalla',
                'prioridad': 1
            },
            {
                'id': 'abb_acs150_menu_parametros',
                'titulo': 'Menú de Parámetros',
                'descripcion': 'Navegación por el menú de parámetros del ABB ACS150',
                'url': '/images/abb_acs150_menu.png',
                'tags': ['parametros', 'menu', 'configuracion'],
                'temas_relacionados': ['parametro'],
                'tipo_contenido': 'captura_pantalla',
                'prioridad': 2
            },
            {
                'id': 'abb_acs150_montaje_panel',
                'titulo': 'Montaje en Panel',
                'descripcion': 'Procedimiento de montaje del variador en panel eléctrico',
                'url': '/images/abb_acs150_montaje.png',
                'tags': ['instalacion', 'montaje', 'panel', 'mecanico'],
                'temas_relacionados': ['instalacion', 'mantenimiento'],
                'tipo_contenido': 'foto_procedimiento',
                'prioridad': 2
            },
            {
                'id': 'abb_acs150_led_estados',
                'titulo': 'LEDs de Estado',
                'descripcion': 'Interpretación de los LEDs indicadores de estado del variador',
                'url': '/images/abb_acs150_leds.png',
                'tags': ['estado', 'led', 'indicadores', 'diagnostico'],
                'temas_relacionados': ['diagnostico', 'codigo_error'],
                'tipo_contenido': 'diagrama_tecnico',
                'prioridad': 2
            }
        ]
        
        # Almacenar contenido predefinido en la base de datos
        for contenido in contenido_predefinido:
            self.base_datos_visual[contenido['id']] = {
                **contenido,
                'fecha_creacion': datetime.now().isoformat(),
                'fecha_actualizacion': datetime.now().isoformat(),
                'contador_uso': 0,
                'calificacion_promedio': 0.0
            }
        
        logger.info(f"Inicializados {len(contenido_predefinido)} elementos de contenido visual")
    
    def obtener_contenido_visual(self, consulta: str, tipo_consulta: str) -> List[Dict[str, Any]]:
        """
        Obtiene contenido visual relevante para una consulta técnica
        Args:
            consulta: Texto de la consulta del usuario
            tipo_consulta: Tipo de consulta detectado
        Returns:
            Lista de referencias a contenido visual relevante
        """
        try:
            logger.debug(f"Buscando contenido visual para consulta tipo: {tipo_consulta}")
            
            # Obtener IDs de contenido relevante por tipo
            ids_relevantes = self.mapeo_temas_visuales.get(tipo_consulta, [])
            
            # Buscar contenido adicional por palabras clave en la consulta
            ids_por_palabras_clave = self._buscar_por_palabras_clave(consulta)
            
            # Combinar y eliminar duplicados
            todos_los_ids = list(set(ids_relevantes + ids_por_palabras_clave))
            
            # Obtener detalles del contenido y ordenar por relevancia
            contenido_encontrado = []
            for id_contenido in todos_los_ids:
                if id_contenido in self.base_datos_visual:
                    contenido = self.base_datos_visual[id_contenido].copy()
                    
                    # Calcular puntuación de relevancia
                    contenido['puntuacion_relevancia'] = self._calcular_relevancia(
                        contenido, consulta, tipo_consulta
                    )
                    
                    contenido_encontrado.append(contenido)
                    
                    # Incrementar contador de uso
                    self.base_datos_visual[id_contenido]['contador_uso'] += 1
            
            # Ordenar por relevancia y prioridad
            contenido_ordenado = sorted(
                contenido_encontrado,
                key=lambda x: (x['puntuacion_relevancia'], x['prioridad']),
                reverse=True
            )
            
            # Limitar a máximo 3 elementos para no sobrecargar la respuesta
            contenido_final = contenido_ordenado[:3]
            
            logger.info(f"Encontrados {len(contenido_final)} elementos visuales para tipo: {tipo_consulta}")
            return contenido_final
            
        except Exception as e:
            logger.error(f"Error obteniendo contenido visual: {str(e)}")
            return []
    
    def _buscar_por_palabras_clave(self, consulta: str) -> List[str]:
        """
        Busca contenido visual basado en palabras clave en la consulta
        Args:
            consulta: Texto de la consulta
        Returns:
            Lista de IDs de contenido relevante
        """
        palabras_consulta = consulta.lower().split()
        ids_encontrados = []
        
        # Buscar en tags y descripciones de todo el contenido
        for id_contenido, datos in self.base_datos_visual.items():
            # Verificar coincidencias en tags
            for tag in datos['tags']:
                if any(palabra in tag.lower() for palabra in palabras_consulta):
                    ids_encontrados.append(id_contenido)
                    break
            
            # Verificar coincidencias en descripción
            descripcion_lower = datos['descripcion'].lower()
            if any(palabra in descripcion_lower for palabra in palabras_consulta):
                if id_contenido not in ids_encontrados:
                    ids_encontrados.append(id_contenido)
        
        return ids_encontrados
    
    def _calcular_relevancia(self, contenido: Dict, consulta: str, tipo_consulta: str) -> float:
        """
        Calcula puntuación de relevancia para un contenido visual
        Args:
            contenido: Datos del contenido visual
            consulta: Consulta original del usuario
            tipo_consulta: Tipo de consulta detectado
        Returns:
            Puntuación de relevancia (0.0 - 1.0)
        """
        puntuacion = 0.0
        
        # Puntuación base por tipo de consulta
        if tipo_consulta in contenido['temas_relacionados']:
            puntuacion += 0.5
        
        # Puntuación por coincidencias de palabras clave
        palabras_consulta = set(consulta.lower().split())
        palabras_contenido = set()
        
        # Añadir palabras de tags y descripción
        for tag in contenido['tags']:
            palabras_contenido.update(tag.lower().split())
        palabras_contenido.update(contenido['descripcion'].lower().split())
        
        # Calcular coincidencias
        coincidencias = len(palabras_consulta.intersection(palabras_contenido))
        if len(palabras_consulta) > 0:
            puntuacion += (coincidencias / len(palabras_consulta)) * 0.3
        
        # Puntuación por popularidad (uso frecuente)
        contador_uso = contenido.get('contador_uso', 0)
        if contador_uso > 0:
            puntuacion += min(contador_uso / 100.0, 0.1)  # Máximo 0.1 por popularidad
        
        # Puntuación por calificación de usuarios
        calificacion = contenido.get('calificacion_promedio', 0.0)
        if calificacion > 0:
            puntuacion += (calificacion / 5.0) * 0.1  # Máximo 0.1 por calificación
        
        return min(puntuacion, 1.0)  # Limitar a máximo 1.0
    
    def agregar_contenido_visual(self, datos_contenido: Dict[str, Any]) -> str:
        """
        Agrega nuevo contenido visual al sistema
        Args:
            datos_contenido: Datos del nuevo contenido visual
        Returns:
            ID del contenido creado
        """
        try:
            # Generar ID único
            id_contenido = self._generar_id_contenido(datos_contenido)
            
            # Validar datos requeridos
            campos_requeridos = ['titulo', 'descripcion', 'url', 'tags', 'tipo_contenido']
            for campo in campos_requeridos:
                if campo not in datos_contenido:
                    raise ValueError(f"Campo requerido faltante: {campo}")
            
            # Preparar datos completos
            contenido_completo = {
                'id': id_contenido,
                'titulo': datos_contenido['titulo'],
                'descripcion': datos_contenido['descripcion'],
                'url': datos_contenido['url'],
                'tags': datos_contenido['tags'],
                'temas_relacionados': datos_contenido.get('temas_relacionados', []),
                'tipo_contenido': datos_contenido['tipo_contenido'],
                'prioridad': datos_contenido.get('prioridad', 3),
                'fecha_creacion': datetime.now().isoformat(),
                'fecha_actualizacion': datetime.now().isoformat(),
                'contador_uso': 0,
                'calificacion_promedio': 0.0
            }
            
            # Almacenar en base de datos
            self.base_datos_visual[id_contenido] = contenido_completo
            
            logger.info(f"Contenido visual agregado: {id_contenido}")
            return id_contenido
            
        except Exception as e:
            logger.error(f"Error agregando contenido visual: {str(e)}")
            raise
    
    def _generar_id_contenido(self, datos: Dict[str, Any]) -> str:
        """
        Genera un ID único para el contenido visual
        Args:
            datos: Datos del contenido
        Returns:
            ID único generado
        """
        # Crear hash basado en título y timestamp
        contenido_hash = hashlib.md5(
            f"{datos['titulo']}_{datetime.now().timestamp()}".encode()
        ).hexdigest()[:8]
        
        return f"visual_{contenido_hash}"
    
    def actualizar_calificacion(self, id_contenido: str, calificacion: float) -> bool:
        """
        Actualiza la calificación de un contenido visual
        Args:
            id_contenido: ID del contenido a calificar
            calificacion: Nueva calificación (1.0 - 5.0)
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if id_contenido not in self.base_datos_visual:
                logger.warning(f"Contenido no encontrado para calificar: {id_contenido}")
                return False
            
            # Validar rango de calificación
            if not (1.0 <= calificacion <= 5.0):
                logger.warning(f"Calificación fuera de rango: {calificacion}")
                return False
            
            contenido = self.base_datos_visual[id_contenido]
            
            # Calcular nueva calificación promedio (implementación simplificada)
            calificacion_actual = contenido.get('calificacion_promedio', 0.0)
            contador_calificaciones = contenido.get('contador_calificaciones', 0)
            
            # Calcular nuevo promedio
            total_puntos = calificacion_actual * contador_calificaciones + calificacion
            nuevo_contador = contador_calificaciones + 1
            nueva_calificacion = total_puntos / nuevo_contador
            
            # Actualizar datos
            contenido['calificacion_promedio'] = nueva_calificacion
            contenido['contador_calificaciones'] = nuevo_contador
            contenido['fecha_actualizacion'] = datetime.now().isoformat()
            
            logger.info(f"Calificación actualizada para {id_contenido}: {nueva_calificacion:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando calificación: {str(e)}")
            return False
    
    def obtener_estadisticas_uso(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso del contenido visual
        Returns:
            Diccionario con estadísticas
        """
        try:
            total_contenido = len(self.base_datos_visual)
            contenido_usado = sum(1 for c in self.base_datos_visual.values() if c['contador_uso'] > 0)
            uso_total = sum(c['contador_uso'] for c in self.base_datos_visual.values())
            
            # Contenido más popular
            contenido_popular = max(
                self.base_datos_visual.values(),
                key=lambda x: x['contador_uso'],
                default=None
            )
            
            estadisticas = {
                'total_contenido': total_contenido,
                'contenido_usado': contenido_usado,
                'uso_total': uso_total,
                'promedio_uso': uso_total / total_contenido if total_contenido > 0 else 0,
                'contenido_mas_popular': {
                    'id': contenido_popular['id'],
                    'titulo': contenido_popular['titulo'],
                    'uso': contenido_popular['contador_uso']
                } if contenido_popular else None
            }
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}