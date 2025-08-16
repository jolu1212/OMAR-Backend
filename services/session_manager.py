# Servicio para gestión completa de sesiones de usuario
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
import threading
from collections import defaultdict

from models.session import Sesion, EstadoSesion

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

class GestorSesiones:
    """
    Gestor centralizado de sesiones de usuario
    Maneja creación, validación, limitación de velocidad y limpieza de sesiones
    """
    
    def __init__(self, max_interacciones: int = 50, limite_por_minuto: int = 10):
        """
        Constructor del gestor de sesiones
        Args:
            max_interacciones: Máximo número de interacciones por sesión
            limite_por_minuto: Máximo número de requests por minuto por sesión
        """
        self.sesiones: Dict[str, Sesion] = {}     # Almacén de sesiones activas
        self.max_interacciones = max_interacciones # Límite de interacciones
        self.limite_por_minuto = limite_por_minuto # Límite de velocidad
        
        # Diccionario para seguimiento de limitación de velocidad por minuto
        self.seguimiento_velocidad: Dict[str, List[datetime]] = defaultdict(list)
        
        # Lock para thread safety en operaciones concurrentes
        self.bloqueo = threading.Lock()
        
        logger.info(f"GestorSesiones inicializado con max_interacciones={max_interacciones}, limite={limite_por_minuto}/min")
    
    def create_session(self, user_credentials: Dict[str, str]) -> Session:
        """
        Crea una nueva sesión para un usuario
        Args:
            user_credentials: Diccionarios con credenciales del usuario (user_id, etc.)
        Returns:
            Nueva instancia de Session
        """
        with self.lock:  # Asegurar thread safety
            user_id = user_credentials.get('user_id', 'anonymous')
            
            # Crear nueva sesión
            session = Session(user_id)
            
            # Almacenar en el gestor
            self.sessions[session.id] = session
            
            # Inicializar tracking de rate limiting
            self.rate_tracking[session.id] = []
            
            logger.info(f"Created new session {session.id} for user {user_id}")
            return session
    
    def validate_session(self, session_id: str) -> Optional[Session]:
        """
        Valida y retorna una sesión si es válida
        Args:
            session_id: ID de la sesión a validar
        Returns:
            Session si es válida, None si no existe o es inválida
        """
        with self.lock:
            # Verificar si la sesión existe
            if session_id not in self.sessions:
                logger.warning(f"Session {session_id} not found")
                return None
            
            session = self.sessions[session_id]
            
            # Verificar si la sesión es válida
            if not session.is_valid():
                logger.info(f"Session {session_id} is invalid, status: {session.status}")
                # Remover sesión inválida del almacén
                del self.sessions[session_id]
                if session_id in self.rate_tracking:
                    del self.rate_tracking[session_id]
                return None
            
            return session
    
    def track_interaction(self, session_id: str, interaction_type: str = 'chat') -> bool:
        """
        Registra una interacción y verifica límites
        Args:
            session_id: ID de la sesión
            interaction_type: Tipo de interacción (chat, upload, etc.)
        Returns:
            bool: True si la interacción es permitida, False si excede límites
        """
        with self.lock:
            session = self.validate_session(session_id)
            if not session:
                return False
            
            # Verificar rate limiting por minuto
            if not self._check_rate_limit(session_id):
                session.status = SessionStatus.RATE_LIMITED
                logger.warning(f"Rate limit exceeded for session {session_id}")
                return False
            
            # Incrementar contador de interacciones
            if not session.increment_interaction(self.max_interactions):
                logger.warning(f"Interaction limit exceeded for session {session_id}")
                return False
            
            # Registrar la interacción en rate tracking
            self.rate_tracking[session_id].append(datetime.now())
            
            # Añadir metadatos de la interacción
            session.add_metadata(f'last_{interaction_type}', datetime.now().isoformat())
            
            logger.debug(f"Tracked {interaction_type} interaction for session {session_id}")
            return True
    
    def _check_rate_limit(self, session_id: str) -> bool:
        """
        Verifica si la sesión está dentro del límite de rate por minuto
        Args:
            session_id: ID de la sesión a verificar
        Returns:
            bool: True si está dentro del límite, False si lo excede
        """
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Obtener requests del último minuto
        recent_requests = self.rate_tracking[session_id]
        
        # Filtrar solo los requests del último minuto
        recent_requests = [req for req in recent_requests if req > one_minute_ago]
        
        # Actualizar la lista con solo los requests recientes
        self.rate_tracking[session_id] = recent_requests
        
        # Verificar si excede el límite
        return len(recent_requests) < self.rate_limit_per_minute
    
    def apply_rate_limiting(self, session_id: str) -> Dict[str, any]:
        """
        Aplica rate limiting y retorna información del estado
        Args:
            session_id: ID de la sesión
        Returns:
            Dict con información del rate limiting
        """
        with self.lock:
            session = self.validate_session(session_id)
            if not session:
                return {
                    'allowed': False,
                    'reason': 'invalid_session',
                    'retry_after': None
                }
            
            # Verificar rate limit
            if not self._check_rate_limit(session_id):
                # Calcular tiempo de espera hasta el próximo minuto
                now = datetime.now()
                next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
                retry_after = int((next_minute - now).total_seconds())
                
                return {
                    'allowed': False,
                    'reason': 'rate_limit_exceeded',
                    'retry_after': retry_after,
                    'current_count': len(self.rate_tracking[session_id]),
                    'limit': self.rate_limit_per_minute
                }
            
            return {
                'allowed': True,
                'remaining': self.rate_limit_per_minute - len(self.rate_tracking[session_id]),
                'limit': self.rate_limit_per_minute
            }
    
    def cleanup_expired_sessions(self) -> int:
        """
        Limpia sesiones expiradas del almacén
        Returns:
            int: Número de sesiones limpiadas
        """
        with self.lock:
            expired_sessions = []
            
            # Identificar sesiones expiradas
            for session_id, session in self.sessions.items():
                if not session.is_valid():
                    expired_sessions.append(session_id)
            
            # Remover sesiones expiradas
            for session_id in expired_sessions:
                del self.sessions[session_id]
                if session_id in self.rate_tracking:
                    del self.rate_tracking[session_id]
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
            return len(expired_sessions)
    
    def get_session_stats(self) -> Dict[str, any]:
        """
        Obtiene estadísticas generales de las sesiones
        Returns:
            Dict con estadísticas del sistema de sesiones
        """
        with self.lock:
            active_count = len([s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE])
            expired_count = len([s for s in self.sessions.values() if s.status == SessionStatus.EXPIRED])
            rate_limited_count = len([s for s in self.sessions.values() if s.status == SessionStatus.RATE_LIMITED])
            
            return {
                'total_sessions': len(self.sessions),
                'active_sessions': active_count,
                'expired_sessions': expired_count,
                'rate_limited_sessions': rate_limited_count,
                'rate_tracking_entries': len(self.rate_tracking)
            }
    
    def extend_session(self, session_id: str, hours: int = 2) -> bool:
        """
        Extiende el tiempo de vida de una sesión
        Args:
            session_id: ID de la sesión a extender
            hours: Horas adicionales de vida
        Returns:
            bool: True si se extendió exitosamente
        """
        with self.lock:
            session = self.validate_session(session_id)
            if not session:
                return False
            
            session.extend_session(hours)
            logger.info(f"Extended session {session_id} by {hours} hours")
            return True