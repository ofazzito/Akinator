"""
Sistema de aprendizaje incremental
Mejora el sistema basado en las partidas jugadas
"""
from typing import Dict, List
from models import db, Character, Question, CharacterAttribute, GameSession, SystemStats
from collections import defaultdict


class LearningSystem:
    """Sistema que aprende de las partidas para mejorar"""
    
    def __init__(self):
        pass
    
    def add_new_character(self, name: str, attributes: Dict[str, int], description: str = None) -> Character:
        """
        Agrega un nuevo personaje al sistema
        
        Args:
            name: Nombre del personaje
            attributes: Dict {attribute_key: value} con valores de -2 a 2
            description: Descripción opcional
        
        Returns:
            Objeto Character creado
        """
        # Verificar si ya existe
        existing = db.session.query(Character).filter_by(name=name).first()
        if existing:
            return existing
        
        # Crear personaje
        character = Character(
            name=name,
            description=description
        )
        db.session.add(character)
        db.session.flush()  # Para obtener el ID
        
        # Agregar atributos
        for attr_key, value in attributes.items():
            char_attr = CharacterAttribute(
                character_id=character.id,
                attribute_key=attr_key,
                value=value,
                confidence=1.0
            )
            db.session.add(char_attr)
        
        db.session.commit()
        
        # Actualizar estadísticas
        self._update_system_stats()
        
        return character
    
    def update_character_attributes(self, character_id: int, attributes: Dict[str, int]):
        """
        Actualiza o agrega atributos a un personaje existente
        
        Args:
            character_id: ID del personaje
            attributes: Dict {attribute_key: value}
        """
        for attr_key, value in attributes.items():
            # Buscar atributo existente
            existing_attr = db.session.query(CharacterAttribute).filter_by(
                character_id=character_id,
                attribute_key=attr_key
            ).first()
            
            if existing_attr:
                # Actualizar valor con promedio ponderado
                existing_attr.value = int((existing_attr.value + value) / 2)
                existing_attr.confidence = min(existing_attr.confidence + 0.1, 1.0)
            else:
                # Crear nuevo atributo
                new_attr = CharacterAttribute(
                    character_id=character_id,
                    attribute_key=attr_key,
                    value=value,
                    confidence=0.8
                )
                db.session.add(new_attr)
        
        db.session.commit()
    
    def analyze_game_session(self, session_id: str):
        """
        Analiza una sesión de juego completada para aprender
        
        Args:
            session_id: ID de la sesión a analizar
        """
        session = db.session.query(GameSession).filter_by(session_id=session_id).first()
        if not session:
            return
        
        # Actualizar efectividad de preguntas
        self._update_question_effectiveness(session)
        
        # Si fue exitoso, reforzar atributos del personaje
        if session.success and session.guessed_character_id:
            self._reinforce_character_attributes(session)
    
    def _update_question_effectiveness(self, session: GameSession):
        """
        Actualiza la efectividad de las preguntas basado en el resultado
        """
        if not session.questions_asked:
            return
        
        # Factor de ajuste basado en éxito y número de preguntas
        if session.success:
            # Éxito con pocas preguntas = preguntas muy efectivas
            effectiveness_boost = 1.0 + (1.0 / max(session.num_questions, 1))
        else:
            # Fallo = preguntas menos efectivas
            effectiveness_boost = 0.95
        
        # Actualizar cada pregunta
        for question_id in session.questions_asked:
            question = db.session.query(Question).get(question_id)
            if question:
                # Promedio móvil exponencial
                question.effectiveness_score = (
                    question.effectiveness_score * 0.9 + effectiveness_boost * 0.1
                )
        
        db.session.commit()
    
    def _reinforce_character_attributes(self, session: GameSession):
        """
        Refuerza los atributos del personaje basado en respuestas correctas
        """
        if not session.answers_given:
            return
        
        character_id = session.guessed_character_id
        
        # Para cada respuesta dada, reforzar el atributo
        for attr_key, answer_value in session.answers_given.items():
            # Buscar atributo existente
            char_attr = db.session.query(CharacterAttribute).filter_by(
                character_id=character_id,
                attribute_key=attr_key
            ).first()
            
            if char_attr:
                # Ajustar valor hacia la respuesta del usuario (aprendizaje)
                # Promedio ponderado: 80% valor actual, 20% respuesta usuario
                char_attr.value = int(char_attr.value * 0.8 + answer_value * 0.2)
                char_attr.confidence = min(char_attr.confidence + 0.05, 1.0)
            else:
                # Crear nuevo atributo basado en la respuesta
                new_attr = CharacterAttribute(
                    character_id=character_id,
                    attribute_key=attr_key,
                    value=answer_value,
                    confidence=0.7
                )
                db.session.add(new_attr)
        
        db.session.commit()
    
    def get_learning_stats(self) -> Dict:
        """
        Obtiene estadísticas del sistema de aprendizaje
        
        Returns:
            Dict con métricas de aprendizaje
        """
        # Estadísticas de sesiones
        total_sessions = db.session.query(GameSession).count()
        successful_sessions = db.session.query(GameSession).filter_by(success=True).count()
        
        # Promedio de preguntas
        avg_questions = db.session.query(db.func.avg(GameSession.num_questions)).scalar() or 0
        
        # Personajes más jugados
        top_characters = db.session.query(
            Character.name,
            Character.times_played,
            Character.times_guessed
        ).order_by(Character.times_played.desc()).limit(5).all()
        
        # Preguntas más efectivas
        top_questions = db.session.query(
            Question.text,
            Question.effectiveness_score,
            Question.times_asked
        ).order_by(Question.effectiveness_score.desc()).limit(5).all()
        
        return {
            'total_games': total_sessions,
            'successful_games': successful_sessions,
            'success_rate': round(successful_sessions / total_sessions * 100, 2) if total_sessions > 0 else 0,
            'avg_questions': round(avg_questions, 1),
            'top_characters': [
                {
                    'name': name,
                    'times_played': played,
                    'times_guessed': guessed,
                    'guess_rate': round(guessed / played * 100, 1) if played > 0 else 0
                }
                for name, played, guessed in top_characters
            ],
            'top_questions': [
                {
                    'text': text,
                    'effectiveness': round(eff, 2),
                    'times_asked': asked
                }
                for text, eff, asked in top_questions
            ]
        }
    
    def _update_system_stats(self):
        """Actualiza las estadísticas globales del sistema"""
        stats = db.session.query(SystemStats).first()
        if not stats:
            stats = SystemStats()
            db.session.add(stats)
        
        stats.total_characters = db.session.query(Character).count()
        stats.total_questions = db.session.query(Question).count()
        stats.total_games = db.session.query(GameSession).count()
        stats.successful_guesses = db.session.query(GameSession).filter_by(success=True).count()
        
        db.session.commit()
