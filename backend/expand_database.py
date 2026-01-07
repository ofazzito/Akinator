"""
Script de utilidad para expandir la base de datos usando IA
Ejecutar: python backend/expand_database.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cambiar al directorio backend para imports correctos
os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from models import db, Character, Question
from ai_expansion import AIExpansionSystem
from flask import Flask
from dotenv import load_dotenv

# Cargar variables de entorno desde el directorio raíz
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Crear app Flask
app = Flask(__name__)
# Usar la MISMA configuración que app.py
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def init_database():
    """Inicializa la base de datos si no existe"""
    with app.app_context():
        # Verificar que las tablas existan
        try:
            db.session.query(Character).first()
            print("✅ Conectado a la base de datos existente\n")
        except:
            print("\n⚠️  Tablas no encontradas. Creando...")
            db.create_all()
            
            # Cargar datos iniciales
            from init_data import initialize_data
            initialize_data(db)
            print("✅ Base de datos inicializada\n")



def main():
    """Función principal"""
    # Inicializar base de datos
    init_database()
    
    with app.app_context():
        ai_system = AIExpansionSystem()
        
        print("=" * 60)
        print("🤖 SISTEMA DE EXPANSIÓN CON IA")
        print("=" * 60)
        
        if not ai_system.client:
            print("\n⚠️  Para usar este sistema necesitas:")
            print("1. Crear un archivo .env en la raíz del proyecto")
            print("2. Agregar: OPENAI_API_KEY=tu-api-key")
            print("3. Obtener API key en: https://platform.openai.com/api-keys")
            return
        
        while True:
            print("\n¿Qué deseas hacer?")
            print("1. Agregar un personaje específico")
            print("2. Importar personajes por categoría")
            print("3. Generar nuevas preguntas inteligentes")
            print("4. Importación masiva (lista personalizada)")
            print("5. 🚀 Importación BATCH asíncrona con imágenes")
            print("6. Salir")
            
            choice = input("\nOpción: ").strip()
            
            if choice == '1':
                add_single_character(ai_system)
            elif choice == '2':
                import_by_category(ai_system)
            elif choice == '3':
                generate_questions(ai_system)
            elif choice == '4':
                bulk_import(ai_system)
            elif choice == '5':
                import_batch_async(ai_system)
            elif choice == '6':
                print("\n¡Hasta luego! 👋")
                break
            else:
                print("Opción inválida")


def add_single_character(ai_system):
    """Agrega un personaje individual"""
    name = input("\nNombre del personaje: ").strip()
    
    if not name:
        print("Nombre vacío")
        return
    
    print(f"\n🔍 Buscando información sobre '{name}'...")
    char_data = ai_system.generate_character_from_name(name)
    
    if not char_data:
        print("❌ No se pudo obtener información")
        return
    
    print(f"\n✓ Información encontrada:")
    print(f"  Nombre: {char_data['name']}")
    print(f"  Descripción: {char_data['description'][:100]}...")
    print(f"  Atributos generados: {len(char_data['attributes'])}")
    
    confirm = input("\n¿Agregar este personaje? (s/n): ").lower()
    
    if confirm == 's':
        stats = ai_system.bulk_import_characters([name])
        if stats['success'] > 0:
            print(f"\n✅ Personaje agregado exitosamente!")
        else:
            print(f"\n❌ Error al agregar personaje")


def import_by_category(ai_system):
    """Importa personajes por categoría"""
    print("\nCategorías sugeridas:")
    print("- científicos famosos")
    print("- superhéroes de Marvel")
    print("- personajes de anime")
    print("- futbolistas legendarios")
    print("- músicos de rock")
    print("- presidentes históricos")
    
    category = input("\nCategoría: ").strip()
    
    if not category:
        return
    
    try:
        limit = int(input("¿Cuántos personajes? (1-50): "))
        limit = max(1, min(50, limit))
    except:
        limit = 10
    
    print(f"\n🤖 Generando sugerencias de '{category}'...")
    names = ai_system.suggest_characters_by_category(category, limit)
    
    if not names:
        print("❌ No se pudieron generar sugerencias")
        return
    
    print(f"\n📋 Personajes sugeridos:")
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")
    
    confirm = input(f"\n¿Importar estos {len(names)} personajes? (s/n): ").lower()
    
    if confirm == 's':
        print(f"\n⏳ Importando personajes...")
        stats = ai_system.bulk_import_characters(names)
        
        print(f"\n📊 Resultados:")
        print(f"  ✅ Exitosos: {stats['success']}")
        print(f"  ⏭️  Omitidos (ya existían): {stats['skipped']}")
        print(f"  ❌ Fallidos: {stats['failed']}")


def generate_questions(ai_system):
    """Genera nuevas preguntas"""
    try:
        num = int(input("\n¿Cuántas preguntas generar? (1-50): "))
        num = max(1, min(50, num))
    except:
        num = 10
    
    print(f"\n🤖 Generando {num} preguntas inteligentes...")
    questions = ai_system.generate_smart_questions(num)
    
    if not questions:
        print("❌ No se pudieron generar preguntas")
        return
    
    print(f"\n📋 Preguntas generadas:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q.get('text', '')}")
    
    confirm = input(f"\n¿Agregar estas preguntas a la base de datos? (s/n): ").lower()
    
    if confirm == 's':
        added = 0
        skipped = 0
        
        for q_data in questions:
            try:
                # Verificar si la pregunta ya existe
                existing = db.session.query(Question).filter_by(text=q_data['text']).first()
                if existing:
                    skipped += 1
                    continue
                
                question = Question(
                    text=q_data['text'],
                    attribute_key=q_data['attribute_key'],
                    effectiveness_score=1.0
                )
                db.session.add(question)
                added += 1
            except Exception as e:
                print(f"Error agregando pregunta: {e}")
                pass
        
        try:
            db.session.commit()
            print(f"\n✅ {added} preguntas agregadas exitosamente!")
            if skipped > 0:
                print(f"⏭️  {skipped} preguntas omitidas (ya existían)")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar preguntas: {e}")


def bulk_import(ai_system):
    """Importación masiva desde lista"""
    print("\nIngresa nombres de personajes (uno por línea)")
    print("Escribe 'FIN' cuando termines:")
    
    names = []
    while True:
        name = input().strip()
        if name.upper() == 'FIN':
            break
        if name:
            names.append(name)
    
    if not names:
        print("No se ingresaron nombres")
        return
    
    print(f"\n⏳ Importando {len(names)} personajes...")
    stats = ai_system.bulk_import_characters(names)
    
    print(f"\n📊 Resultados:")
    print(f"  ✅ Exitosos: {stats['success']}")
    print(f"  ⏭️  Omitidos: {stats['skipped']}")
    print(f"  ❌ Fallidos: {stats['failed']}")


def import_batch_async(ai_system):
    """Importación batch asíncrona con imágenes"""
    try:
        import asyncio
        from batch_processor import BatchProcessor
    except ImportError:
        print("\n❌ Módulo batch_processor no disponible")
        print("Instala dependencias: uv pip install aiohttp Pillow")
        return
    
    print("\n🚀 IMPORTACIÓN BATCH ASÍNCRONA CON IMÁGENES")
    print("=" * 60)
    
    print("\nCategorías sugeridas:")
    print("- actores de Hollywood")
    print("- músicos de rock")
    print("- futbolistas legendarios")
    print("- personajes de Marvel")
    print("- científicos famosos")
    
    category = input("\nCategoría: ").strip()
    
    if not category:
        return
    
    try:
        limit = int(input("¿Cuántos personajes? (1-100): "))
        limit = max(1, min(100, limit))
    except:
        limit = 20
    
    concurrent = input(f"¿Cuántos procesar en paralelo? (1-10, recomendado: 5): ").strip()
    try:
        concurrent = max(1, min(10, int(concurrent)))
    except:
        concurrent = 5
    
    print(f"\n🤖 Generando sugerencias de '{category}'...")
    names = ai_system.suggest_characters_by_category(category, limit)
    
    if not names:
        print("❌ No se pudieron generar sugerencias")
        return
    
    print(f"\n📋 Personajes sugeridos ({len(names)}):")
    for i, name in enumerate(names[:10], 1):
        print(f"  {i}. {name}")
    if len(names) > 10:
        print(f"  ... y {len(names) - 10} más")
    
    confirm = input(f"\n¿Importar estos {len(names)} personajes con imágenes? (s/n): ").lower()
    
    if confirm == 's':
        print(f"\n⏳ Procesando {len(names)} personajes en paralelo...")
        print(f"   Concurrencia: {concurrent} tareas simultáneas")
        print(f"   Imágenes: Sí (Wikipedia → Web → DALL-E)\n")
        
        processor = BatchProcessor(ai_system, max_concurrent=concurrent)
        
        async def run_batch():
            return await processor.process_batch(names, generate_images=True)
        
        stats = asyncio.run(run_batch())
        
        print(f"\n📊 Resultados:")
        print(f"  ✅ Exitosos: {stats['success']}")
        print(f"  🖼️  Imágenes descargadas: {stats['images_downloaded']}")
        print(f"  🎨 Imágenes generadas (DALL-E): {stats['images_generated']}")
        print(f"  ⏭️  Omitidos: {stats['skipped']}")
        print(f"  ❌ Fallidos: {stats['failed']}")


if __name__ == '__main__':
    main()
