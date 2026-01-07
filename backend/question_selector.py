"""
Algoritmo de selección inteligente de preguntas basado en entropía
"""
import math
from collections import defaultdict
from typing import List, Dict, Set
from models import Question, Character, CharacterAttribute


class QuestionSelector:
    """Selecciona la mejor pregunta usando ganancia de información"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def select_best_question(
        self, 
        candidate_ids: List[int], 
        asked_questions: Set[int],
        answers: Dict[str, int]
    ) -> Question:
        """
        Selecciona la pregunta que maximiza la ganancia de información
        
        Args:
            candidate_ids: IDs de personajes candidatos actuales
            asked_questions: Set de IDs de preguntas ya realizadas
            answers: Diccionario de respuestas previas {attribute_key: value}
        
        Returns:
            Objeto Question con la mejor pregunta
        """
        if not candidate_ids:
            return None
        
        # Obtener todas las preguntas disponibles
        available_questions = self.db.query(Question).filter(
            ~Question.id.in_(asked_questions)
        ).all()
        
        if not available_questions:
            return None
        
        # Calcular entropía actual
        current_entropy = self._calculate_entropy(len(candidate_ids))
        
        best_question = None
        best_gain = -1
        
        for question in available_questions:
            # Calcular ganancia de información para esta pregunta
            gain = self._calculate_information_gain(
                question,
                candidate_ids,
                current_entropy
            )
            
            # Ajustar por efectividad histórica
            adjusted_gain = gain * question.effectiveness_score
            
            if adjusted_gain > best_gain:
                best_gain = adjusted_gain
                best_question = question
        
        return best_question
    
    def _calculate_entropy(self, num_candidates: int) -> float:
        """Calcula la entropía del conjunto actual"""
        if num_candidates <= 1:
            return 0.0
        
        # Asumiendo distribución uniforme
        probability = 1.0 / num_candidates
        return -num_candidates * (probability * math.log2(probability))
    
    def _calculate_information_gain(
        self,
        question: Question,
        candidate_ids: List[int],
        current_entropy: float
    ) -> float:
        """
        Calcula la ganancia de información de una pregunta
        
        Ganancia = Entropía(S) - Σ((|Sv|/|S|) * Entropía(Sv))
        """
        # Obtener distribución de respuestas para esta pregunta
        distribution = self._get_answer_distribution(question, candidate_ids)
        
        if not distribution:
            return 0.0
        
        # Calcular entropía ponderada después de la pregunta
        weighted_entropy = 0.0
        total_candidates = len(candidate_ids)
        
        for value, count in distribution.items():
            if count > 0:
                probability = count / total_candidates
                subset_entropy = self._calculate_entropy(count)
                weighted_entropy += probability * subset_entropy
        
        # Ganancia de información
        gain = current_entropy - weighted_entropy
        
        return gain
    
    def _get_answer_distribution(
        self,
        question: Question,
        candidate_ids: List[int]
    ) -> Dict[int, int]:
        """
        Obtiene la distribución de respuestas para una pregunta entre los candidatos
        
        Returns:
            Dict {value: count} donde value es -2, -1, 0, 1, 2
        """
        distribution = defaultdict(int)
        
        # Obtener atributos de los candidatos para esta pregunta
        attributes = self.db.query(CharacterAttribute).filter(
            CharacterAttribute.character_id.in_(candidate_ids),
            CharacterAttribute.attribute_key == question.attribute_key
        ).all()
        
        # Contar respuestas
        for attr in attributes:
            distribution[attr.value] += 1
        
        # Personajes sin este atributo definido (asumir "No sé" = 0)
        characters_with_attr = len(attributes)
        if characters_with_attr < len(candidate_ids):
            distribution[0] += len(candidate_ids) - characters_with_attr
        
        return dict(distribution)
    
    def get_fallback_question(self, asked_questions: Set[int]) -> Question:
        """
        Obtiene una pregunta de respaldo cuando el algoritmo falla
        Prioriza preguntas con alta efectividad que no se han hecho
        """
        question = self.db.query(Question).filter(
            ~Question.id.in_(asked_questions)
        ).order_by(Question.effectiveness_score.desc()).first()
        
        return question
