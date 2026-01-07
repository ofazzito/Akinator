"""
Script para inicializar la base de datos en Docker
Ejecutar: docker-compose exec app python backend/init_db_docker.py
"""
import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, db
from backend.models import Character, Question
from backend.init_data import initialize_data


def init_database():
    """Inicializa la base de datos con datos de ejemplo"""
    with app.app_context():
        print("🔧 Creando tablas...")
        db.create_all()
        
        # Verificar si ya hay datos
        character_count = db.session.query(Character).count()
        question_count = db.session.query(Question).count()
        
        if character_count > 0:
            print(f"✅ Base de datos ya inicializada:")
            print(f"   - Personajes: {character_count}")
            print(f"   - Preguntas: {question_count}")
            return
        
        print("📊 Inicializando base de datos con datos de ejemplo...")
        initialize_data(db)
        
        # Verificar datos insertados
        character_count = db.session.query(Character).count()
        question_count = db.session.query(Question).count()
        
        print(f"✅ Base de datos inicializada exitosamente:")
        print(f"   - Personajes: {character_count}")
        print(f"   - Preguntas: {question_count}")


if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
