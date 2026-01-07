"""
Aplicación Flask principal - API REST para Akinator
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models import db, Character, Question, SystemStats
from game_engine import GameEngine
from learning_system import LearningSystem
import os



app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# Configuración
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos (soporta SQLite y PostgreSQL con psycopg3)
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Fallback a SQLite si no hay DATABASE_URL
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    DATABASE_URL = f'sqlite:///{db_path}'
else:
    # Si es PostgreSQL, asegurar que use psycopg3
    if DATABASE_URL.startswith('postgresql://'):
        # Reemplazar postgresql:// con postgresql+psycopg:// para usar psycopg3
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Inicializar base de datos
db.init_app(app)

# Instancias globales
game_engine = GameEngine()
learning_system = LearningSystem()


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Inicia una nueva partida"""
    try:
        result = game_engine.start_game()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/game/answer', methods=['POST'])
def answer_question():
    """
    Procesa una respuesta del usuario
    
    Body:
        {
            "session_id": "uuid",
            "question_id": 1,
            "answer": "yes" | "probably_yes" | "dont_know" | "probably_no" | "no"
        }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not all([session_id, question_id, answer]):
            return jsonify({'error': 'Faltan parámetros requeridos'}), 400
        
        result = game_engine.process_answer(session_id, question_id, answer)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/game/confirm', methods=['POST'])
def confirm_guess():
    """
    Confirma si la adivinanza fue correcta
    
    Body:
        {
            "session_id": "uuid",
            "character_id": 1,
            "correct": true | false
        }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        character_id = data.get('character_id')
        correct = data.get('correct')
        
        if not all([session_id, character_id is not None, correct is not None]):
            return jsonify({'error': 'Faltan parámetros requeridos'}), 400
        
        result = game_engine.confirm_guess(session_id, character_id, correct)
        
        # Analizar sesión para aprendizaje
        if correct:
            learning_system.analyze_game_session(session_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/character/add', methods=['POST'])
def add_character():
    """
    Agrega un nuevo personaje
    
    Body:
        {
            "name": "Nombre del personaje",
            "description": "Descripción opcional",
            "attributes": {
                "is_fictional": 2,
                "is_human": -2,
                ...
            }
        }
    """
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        attributes = data.get('attributes', {})
        
        if not name or not attributes:
            return jsonify({'error': 'Faltan parámetros requeridos'}), 400
        
        character = learning_system.add_new_character(name, attributes, description)
        
        return jsonify({
            'success': True,
            'character': character.to_dict(),
            'message': f'Personaje "{name}" agregado exitosamente'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas del sistema"""
    try:
        stats = learning_system.get_learning_stats()
        
        # Agregar estadísticas de base de datos
        total_characters = db.session.query(Character).count()
        total_questions = db.session.query(Question).count()
        
        stats['database'] = {
            'total_characters': total_characters,
            'total_questions': total_questions
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Obtiene lista de todos los personajes"""
    try:
        characters = db.session.query(Character).order_by(Character.name).all()
        return jsonify({
            'characters': [char.to_dict() for char in characters]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Obtiene lista de todas las preguntas"""
    try:
        questions = db.session.query(Question).order_by(Question.effectiveness_score.desc()).all()
        return jsonify({
            'questions': [q.to_dict() for q in questions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def init_database():
    """Inicializa la base de datos con datos de ejemplo"""
    with app.app_context():
        # Crear tablas
        db.create_all()
        
        # Verificar si ya hay datos
        if db.session.query(Character).count() > 0:
            print("Base de datos ya inicializada")
            return
        
        print("Inicializando base de datos con datos de ejemplo...")
        
        # Importar datos iniciales
        from init_data import initialize_data
        initialize_data(db)
        
        print("Base de datos inicializada exitosamente")


if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
