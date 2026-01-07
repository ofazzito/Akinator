"""
Motor principal del juego Akinator
Maneja la lógica de partidas, matching de personajes y flujo del juego
"""
import uuid
from typing import Dict, List, Optional, Tuple
from models import db, Character, Question, CharacterAttribute, GameSession
from question_selector import QuestionSelector


class GameEngine:
    """Motor del juego que gestiona el flujo de una partida"""
    
    # Mapeo de respuestas a valores numéricos
    ANSWER_VALUES = {
        'yes': 2,
        'probably_yes': 1,
        'dont_know': 0,
        'probably_no': -1,
        'no': -2
    }
    
    # Umbral de confianza para hacer una adivinanza
    GUESS_THRESHOLD = 0.80  # 80% de confianza
    MIN_QUESTIONS = 5  # Mínimo de preguntas antes de adivinar
    MAX_QUESTIONS = 30  # Máximo de preguntas
    
    def __init__(self):
        self.sessions = {}  # Almacena sesiones activas en memoria
        self.question_selector = QuestionSelector(db.session)
    
    def start_game(self) -> Dict:
        """
        Inicia una nueva partida
        
        Returns:
            Dict con session_id y primera pregunta
        """
        session_id = str(uuid.uuid4())
        
        # Obtener todos los personajes como candidatos iniciales
        all_characters = db.session.query(Character).all()
        candidate_ids = [char.id for char in all_characters]
        
        # Inicializar estado de la sesión
        self.sessions[session_id] = {
            'candidate_ids': candidate_ids,
            'candidate_scores': {char_id: 0 for char_id in candidate_ids},
            'asked_questions': set(),
            'answers': {},
            'question_count': 0
        }
        
        # Obtener primera pregunta
        first_question = self.question_selector.select_best_question(
            candidate_ids,
            set(),
            {}
        )
        
        if not first_question:
            return {'error': 'No hay preguntas disponibles'}
        
        return {
            'session_id': session_id,
            'question': first_question.to_dict(),
            'progress': 0,
            'candidates_remaining': len(candidate_ids)
        }
    
    def process_answer(self, session_id: str, question_id: int, answer: str) -> Dict:
        """
        Procesa una respuesta y devuelve la siguiente pregunta o adivinanza
        
        Args:
            session_id: ID de la sesión
            question_id: ID de la pregunta respondida
            answer: Respuesta del usuario ('yes', 'probably_yes', etc.)
        
        Returns:
            Dict con siguiente pregunta o adivinanza
        """
        if session_id not in self.sessions:
            return {'error': 'Sesión no encontrada'}
        
        session = self.sessions[session_id]
        
        # Obtener pregunta
        question = db.session.query(Question).get(question_id)
        if not question:
            return {'error': 'Pregunta no encontrada'}
        
        # Convertir respuesta a valor numérico
        answer_value = self.ANSWER_VALUES.get(answer, 0)
        
        # Actualizar estado de la sesión
        session['asked_questions'].add(question_id)
        session['answers'][question.attribute_key] = answer_value
        session['question_count'] += 1
        
        # Actualizar estadísticas de la pregunta
        question.times_asked += 1
        db.session.commit()
        
        # Actualizar puntuaciones de candidatos
        self._update_candidate_scores(session, question.attribute_key, answer_value)
        
        # Filtrar candidatos con puntuación muy baja
        session['candidate_ids'] = self._filter_candidates(session)
        
        # Calcular progreso
        progress = min(int((session['question_count'] / self.MAX_QUESTIONS) * 100), 100)
        
        # Verificar si debemos hacer una adivinanza
        should_guess, top_character = self._should_make_guess(session)
        
        if should_guess:
            character = db.session.query(Character).get(top_character)
            return {
                'session_id': session_id,
                'type': 'guess',
                'character': character.to_dict(),
                'progress': progress,
                'question_count': session['question_count']
            }
        
        # Si llegamos al máximo de preguntas, adivinar el mejor candidato
        if session['question_count'] >= self.MAX_QUESTIONS:
            if session['candidate_ids']:
                best_candidate = max(
                    session['candidate_ids'],
                    key=lambda cid: session['candidate_scores'][cid]
                )
                character = db.session.query(Character).get(best_candidate)
                return {
                    'session_id': session_id,
                    'type': 'guess',
                    'character': character.to_dict(),
                    'progress': 100,
                    'question_count': session['question_count']
                }
            else:
                return {
                    'session_id': session_id,
                    'type': 'give_up',
                    'message': 'No pude adivinar tu personaje',
                    'progress': 100
                }
        
        # Obtener siguiente pregunta
        next_question = self.question_selector.select_best_question(
            session['candidate_ids'],
            session['asked_questions'],
            session['answers']
        )
        
        if not next_question:
            # No hay más preguntas, hacer mejor adivinanza posible
            if session['candidate_ids']:
                best_candidate = max(
                    session['candidate_ids'],
                    key=lambda cid: session['candidate_scores'][cid]
                )
                character = db.session.query(Character).get(best_candidate)
                return {
                    'session_id': session_id,
                    'type': 'guess',
                    'character': character.to_dict(),
                    'progress': progress,
                    'question_count': session['question_count']
                }
        
        return {
            'session_id': session_id,
            'type': 'question',
            'question': next_question.to_dict(),
            'progress': progress,
            'candidates_remaining': len(session['candidate_ids']),
            'question_count': session['question_count']
        }
    
    def _update_candidate_scores(self, session: Dict, attribute_key: str, answer_value: int):
        """Actualiza las puntuaciones de los candidatos basado en la respuesta"""
        # Obtener atributos de todos los candidatos para esta clave
        attributes = db.session.query(CharacterAttribute).filter(
            CharacterAttribute.character_id.in_(session['candidate_ids']),
            CharacterAttribute.attribute_key == attribute_key
        ).all()
        
        # Crear mapa de valores
        attr_map = {attr.character_id: attr.value for attr in attributes}
        
        # Actualizar puntuaciones
        for char_id in session['candidate_ids']:
            char_value = attr_map.get(char_id, 0)  # Default "No sé"
            
            # Calcular diferencia absoluta
            diff = abs(char_value - answer_value)
            
            # Puntuación: menor diferencia = mayor puntuación
            # Diferencia 0 = +4 puntos
            # Diferencia 1 = +2 puntos
            # Diferencia 2 = 0 puntos
            # Diferencia 3 = -2 puntos
            # Diferencia 4 = -4 puntos
            score_change = 4 - (diff * 2)
            session['candidate_scores'][char_id] += score_change
    
    def _filter_candidates(self, session: Dict) -> List[int]:
        """Filtra candidatos con puntuación muy baja"""
        if not session['candidate_ids']:
            return []
        
        # Obtener puntuación máxima
        max_score = max(session['candidate_scores'].values())
        
        # Mantener candidatos dentro de un rango razonable del máximo
        threshold = max_score - 10  # Tolerancia de 10 puntos
        
        filtered = [
            char_id for char_id in session['candidate_ids']
            if session['candidate_scores'][char_id] >= threshold
        ]
        
        # Siempre mantener al menos el top 5
        if len(filtered) < 5 and len(session['candidate_ids']) >= 5:
            sorted_candidates = sorted(
                session['candidate_ids'],
                key=lambda cid: session['candidate_scores'][cid],
                reverse=True
            )
            filtered = sorted_candidates[:5]
        
        return filtered if filtered else session['candidate_ids']
    
    def _should_make_guess(self, session: Dict) -> Tuple[bool, Optional[int]]:
        """
        Determina si debemos hacer una adivinanza
        
        Returns:
            (should_guess, character_id)
        """
        if session['question_count'] < self.MIN_QUESTIONS:
            return False, None
        
        if not session['candidate_ids']:
            return False, None
        
        # Obtener top candidato
        top_candidate = max(
            session['candidate_ids'],
            key=lambda cid: session['candidate_scores'][cid]
        )
        top_score = session['candidate_scores'][top_candidate]
        
        # Calcular confianza relativa
        other_scores = [
            session['candidate_scores'][cid]
            for cid in session['candidate_ids']
            if cid != top_candidate
        ]
        
        if not other_scores:
            return True, top_candidate
        
        avg_other_score = sum(other_scores) / len(other_scores)
        
        # Si el top está significativamente por encima del resto
        if top_score > avg_other_score + 8:  # 8 puntos de ventaja
            return True, top_candidate
        
        # Si solo queda un candidato
        if len(session['candidate_ids']) == 1:
            return True, top_candidate
        
        return False, None
    
    def confirm_guess(self, session_id: str, character_id: int, correct: bool) -> Dict:
        """
        Confirma si la adivinanza fue correcta
        
        Args:
            session_id: ID de la sesión
            character_id: ID del personaje adivinado
            correct: Si la adivinanza fue correcta
        
        Returns:
            Dict con resultado y estadísticas
        """
        if session_id not in self.sessions:
            return {'error': 'Sesión no encontrada'}
        
        session = self.sessions[session_id]
        
        # Guardar sesión en base de datos
        game_session = GameSession(
            session_id=session_id,
            guessed_character_id=character_id,
            success=correct,
            questions_asked=list(session['asked_questions']),
            answers_given=session['answers'],
            num_questions=session['question_count']
        )
        db.session.add(game_session)
        
        # Actualizar estadísticas del personaje
        character = db.session.query(Character).get(character_id)
        if character:
            character.times_played += 1
            if correct:
                character.times_guessed += 1
        
        db.session.commit()
        
        # Limpiar sesión
        del self.sessions[session_id]
        
        return {
            'success': correct,
            'message': '¡Genial! Adiviné correctamente' if correct else 'Vaya, fallé esta vez',
            'questions_used': session['question_count']
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Obtiene información de una sesión activa"""
        return self.sessions.get(session_id)
