#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de IA Industrial simplificado para OMAR
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SimpleAISystem:
    """Sistema de IA Industrial simplificado"""
    
    def __init__(self):
        self.failure_patterns = {}
        self.operator_feedback = {}
        self.load_sample_data()
    
    def load_sample_data(self):
        """Carga datos de ejemplo para demostración"""
        self.failure_patterns = {
            "empacadora_1": {
                "motor_sobrecalentamiento": {
                    "sintomas": ["temperatura_alta", "olor_quemado", "ruido_anormal"],
                    "causas": ["filtro_aire_sucio", "aceite_bajo", "rodamiento_desgastado"],
                    "soluciones": ["limpiar_filtro_aire", "verificar_nivel_aceite", "revisar_rodamiento"],
                    "tiempo_estimado": "15-30 minutos",
                    "experto": "operador_juan",
                    "frecuencia": 5,
                    "ultima_ocurrencia": "2024-01-15"
                },
                "cinta_no_avanza": {
                    "sintomas": ["cinta_parada", "motor_funcionando", "tension_baja"],
                    "causas": ["sensor_proximidad_sucio", "rodillo_traccion_desgastado", "tension_insuficiente"],
                    "soluciones": ["limpiar_sensor_proximidad", "verificar_rodillo_traccion", "ajustar_tension"],
                    "tiempo_estimado": "10-20 minutos",
                    "experto": "mantenedor_carlos",
                    "frecuencia": 3,
                    "ultima_ocurrencia": "2024-01-10"
                }
            },
            "hornos_2": {
                "temperatura_inestable": {
                    "sintomas": ["temperatura_fluctua", "producto_quemado", "consumo_energetico_alto"],
                    "causas": ["termocupla_dañada", "controlador_pid_descalibrado", "aislamiento_termico_deteriorado"],
                    "soluciones": ["reemplazar_termocupla", "recalibrar_controlador", "reparar_aislamiento"],
                    "tiempo_estimado": "45-90 minutos",
                    "experto": "mantenedor_ana",
                    "frecuencia": 2,
                    "ultima_ocurrencia": "2024-01-12"
                }
            }
        }
        
        logger.info("Datos de ejemplo cargados para demostración")
    
    def get_recommendation(self, machine_id: str, symptoms: List[str]) -> Optional[Dict]:
        """Obtiene recomendación basada en síntomas"""
        if machine_id not in self.failure_patterns:
            return None
        
        # Buscar coincidencias
        for failure_type, data in self.failure_patterns[machine_id].items():
            matches = sum(1 for s in symptoms if s in data['sintomas'])
            if matches > 0:
                return {
                    'failure_type': failure_type,
                    'confidence': matches / len(data['sintomas']),
                    'solutions': data['soluciones'],
                    'estimated_time': data['tiempo_estimado'],
                    'expert': data['experto']
                }
        
        return None
    
    def add_feedback(self, feedback: Dict) -> str:
        """Agrega feedback de operador"""
        feedback_id = f"fb_{datetime.now().timestamp()}"
        self.operator_feedback[feedback_id] = feedback
        return feedback_id
    
    def search_solutions(self, query: str) -> List[Dict]:
        """Busca soluciones en la base de datos"""
        results = []
        query_lower = query.lower()
        
        for machine_id, machine_failures in self.failure_patterns.items():
            for failure_type, failure_data in machine_failures.items():
                # Buscar en síntomas, causas y soluciones
                searchable_text = ' '.join([
                    ' '.join(failure_data.get('sintomas', [])),
                    ' '.join(failure_data.get('causas', [])),
                    ' '.join(failure_data.get('soluciones', []))
                ]).lower()
                
                if query_lower in searchable_text:
                    results.append({
                        'machine_id': machine_id,
                        'failure_type': failure_type,
                        'match_score': searchable_text.count(query_lower),
                        'failure_data': failure_data
                    })
        
        # Ordenar por score de coincidencia
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results[:5]  # Máximo 5 resultados
    
    def get_machine_statistics(self, machine_id: str) -> Optional[Dict]:
        """Obtiene estadísticas de una máquina específica"""
        if machine_id not in self.failure_patterns:
            return None
        
        machine_data = self.failure_patterns[machine_id]
        total_failures = len(machine_data)
        total_frequency = sum(failure.get('frecuencia', 1) for failure in machine_data.values())
        
        return {
            'machine_id': machine_id,
            'total_failure_types': total_failures,
            'total_occurrences': total_frequency,
            'most_frequent_failures': [
                {
                    'type': failure_type,
                    'frequency': failure_data.get('frecuencia', 1),
                    'last_occurrence': failure_data.get('ultima_ocurrencia', 'desconocida')
                }
                for failure_type, failure_data in sorted(
                    machine_data.items(),
                    key=lambda x: x[1].get('frecuencia', 1),
                    reverse=True
                )[:3]
            ]
        }
