# Modelo de datos para gestión de sesiones de usuario
from datetime import datetime, timedelta
import uuid
import json
from typing import Dict, Optional, Any

class Sesion:
    """
    Clase que representa una sesión de usuario en el sistema
    Maneja el ciclo de vida, límites y estado de las sesiones
    """
    
    def __init__(self, id_usuario: str, id_sesion: str = None):
        """
        Constructor de la sesión
        Args:
            id_usuario: Identificador único del usuario
            id_sesion: ID de sesión (se genera automáticamente si no se proporciona)
        """
        self.id = id_sesion or str(uuid.uuid4())  # Generar ID único si no se proporciona
        self.id_usuario = id_usuario              # ID del usuario propietario de la sesión
        self.creada_en = datetime.now()           # Timestamp de creación
        self.expira_en = self.creada_en + timedelta(hours=8)  # Expiración en 8 horas
        self.contador_interacciones = 0           # Contador de interacciones realizadas
        self.estado = EstadoSesion.ACTIVA         # Estado inicial activo
        self.ultima_actividad = datetime.now()    # Timestamp de última actividad
        self.metadatos = {}                       # Metadatos adicionales de la sesión
        
    def es_valida(self) -> bool:
        """
        Verifica si la sesión es válida y activa
        Returns:
            bool: True si la sesión es válida, False en caso contrario
        """
        ahora = datetime.now()
        
        # Verificar si la sesión no ha expirado por tiempo
        if ahora > self.expira_en:
            self.estado = EstadoSesion.EXPIRADA
            return False
            
        # Verificar si el estado permite uso
        if self.estado != EstadoSesion.ACTIVA:
            return False
            
        return True
    
    def incrementar_interaccion(self, max_interacciones: int = 50) -> bool:
        """
        Incrementa el contador de interacciones y verifica límites
        Args:
            max_interacciones: Número máximo de interacciones permitidas
        Returns:
            bool: True si se puede incrementar, False si se alcanzó el límite
        """
        # Verificar si se alcanzó el límite de interacciones
        if self.contador_interacciones >= max_interacciones:
            self.estado = EstadoSesion.LIMITADA_POR_VELOCIDAD
            return False
            
        # Incrementar contador y actualizar última actividad
        self.contador_interacciones += 1
        self.ultima_actividad = datetime.now()
        return True
    
    def extender_sesion(self, horas: int = 2) -> None:
        """
        Extiende el tiempo de vida de la sesión
        Args:
            horas: Número de horas a extender
        """
        self.expira_en += timedelta(hours=horas)
        self.ultima_actividad = datetime.now()
    
    def agregar_metadatos(self, clave: str, valor: Any) -> None:
        """
        Añade metadatos a la sesión
        Args:
            clave: Clave del metadato
            valor: Valor del metadato
        """
        self.metadatos[clave] = valor
    
    def a_diccionario(self) -> Dict[str, Any]:
        """
        Convierte la sesión a diccionario para serialización
        Returns:
            Dict con todos los datos de la sesión
        """
        return {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'creada_en': self.creada_en.isoformat(),
            'expira_en': self.expira_en.isoformat(),
            'contador_interacciones': self.contador_interacciones,
            'estado': self.estado,
            'ultima_actividad': self.ultima_actividad.isoformat(),
            'metadatos': self.metadatos
        }
    
    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> 'Sesion':
        """
        Crea una instancia de Sesion desde un diccionario
        Args:
            datos: Diccionario con datos de la sesión
        Returns:
            Instancia de Sesion
        """
        # Crear sesión con ID existente
        sesion = cls(datos['id_usuario'], datos['id'])
        
        # Restaurar timestamps desde strings ISO
        sesion.creada_en = datetime.fromisoformat(datos['creada_en'].replace('Z', '+00:00'))
        sesion.expira_en = datetime.fromisoformat(datos['expira_en'].replace('Z', '+00:00'))
        sesion.ultima_actividad = datetime.fromisoformat(datos['ultima_actividad'].replace('Z', '+00:00'))
        
        # Restaurar contadores y estado
        sesion.contador_interacciones = datos['contador_interacciones']
        sesion.estado = datos['estado']
        sesion.metadatos = datos.get('metadatos', {})
        
        return sesion

class EstadoSesion:
    """
    Enumeración de estados posibles para una sesión
    """
    ACTIVA = 'activa'                      # Sesión activa y usable
    EXPIRADA = 'expirada'                  # Sesión expirada por tiempo
    LIMITADA_POR_VELOCIDAD = 'limitada'    # Sesión limitada por exceso de uso
    BLOQUEADA = 'bloqueada'                # Sesión bloqueada por seguridad