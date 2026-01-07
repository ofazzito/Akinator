"""
Modelos de base de datos para el sistema Akinator
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


class Character(db.Model):
    """Modelo de personaje"""
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    times_guessed = db.Column(db.Integer, default=0)
    times_played = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con atributos
    attributes = db.relationship('CharacterAttribute', back_populates='character', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Character {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'times_guessed': self.times_guessed,
            'times_played': self.times_played
        }


class Question(db.Model):
    """Modelo de pregunta"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False, unique=True)
    attribute_key = db.Column(db.String(100), nullable=False)
    times_asked = db.Column(db.Integer, default=0)
    effectiveness_score = db.Column(db.Float, default=1.0)  # Qué tan útil es la pregunta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.text[:50]}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'attribute_key': self.attribute_key,
            'times_asked': self.times_asked,
            'effectiveness_score': self.effectiveness_score
        }


class CharacterAttribute(db.Model):
    """Relación entre personajes y sus atributos"""
    __tablename__ = 'character_attributes'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    attribute_key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # -2 a 2 (No, Prob no, No sé, Prob sí, Sí)
    confidence = db.Column(db.Float, default=1.0)  # Confianza en este valor
    
    # Relaciones
    character = db.relationship('Character', back_populates='attributes')
    
    __table_args__ = (
        db.UniqueConstraint('character_id', 'attribute_key', name='unique_character_attribute'),
    )
    
    def __repr__(self):
        return f'<CharacterAttribute {self.character_id}:{self.attribute_key}={self.value}>'


class GameSession(db.Model):
    """Historial de partidas para aprendizaje"""
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    target_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    guessed_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    success = db.Column(db.Boolean, default=False)
    questions_asked = db.Column(JSON)  # Lista de IDs de preguntas
    answers_given = db.Column(JSON)  # Lista de respuestas
    num_questions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    target_character = db.relationship('Character', foreign_keys=[target_character_id])
    guessed_character = db.relationship('Character', foreign_keys=[guessed_character_id])
    
    def __repr__(self):
        return f'<GameSession {self.session_id}>'


class SystemStats(db.Model):
    """Estadísticas globales del sistema"""
    __tablename__ = 'system_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    total_games = db.Column(db.Integer, default=0)
    successful_guesses = db.Column(db.Integer, default=0)
    total_characters = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemStats games={self.total_games}>'
    
    def to_dict(self):
        return {
            'total_games': self.total_games,
            'successful_guesses': self.successful_guesses,
            'success_rate': round(self.successful_guesses / self.total_games * 100, 2) if self.total_games > 0 else 0,
            'total_characters': self.total_characters,
            'total_questions': self.total_questions
        }
