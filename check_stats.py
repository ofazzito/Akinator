"""Script para verificar contador de personajes"""
import sys
import os
sys.path.insert(0, 'backend')
os.chdir('backend')

from models import db, Character, Question
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    total_chars = db.session.query(Character).count()
    total_questions = db.session.query(Question).count()
    
    print(f"\n📊 Estadísticas de la Base de Datos:")
    print(f"  Personajes: {total_chars}")
    print(f"  Preguntas: {total_questions}")
    
    # Listar algunos personajes
    print(f"\n📝 Últimos 10 personajes:")
    chars = db.session.query(Character).order_by(Character.id.desc()).limit(10).all()
    for char in chars:
        print(f"  - {char.name}")
