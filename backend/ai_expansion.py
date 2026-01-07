"""
Sistema de expansión automática usando OpenAI y Wikipedia
Genera personajes, preguntas y atributos automáticamente
"""
import os
import json
import wikipedia
from openai import OpenAI
from typing import Dict, List, Optional
from models import db, Character, Question, CharacterAttribute

# Importar sistema de fuentes múltiples
try:
    from multi_source import MultiSourceDataFetcher
    MULTI_SOURCE_AVAILABLE = True
except:
    MULTI_SOURCE_AVAILABLE = False
    print("⚠️  Sistema de fuentes múltiples no disponible")


class AIExpansionSystem:
    """Sistema que usa IA para expandir la base de datos automáticamente"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el sistema con la API key de OpenAI
        
        Args:
            api_key: API key de OpenAI (si no se provee, usa variable de entorno)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            print("⚠️  OPENAI_API_KEY no configurada. Funcionalidad de IA limitada.")
        
        # Configurar Wikipedia en español
        wikipedia.set_lang("es")
        
        # Inicializar sistema de fuentes múltiples
        if MULTI_SOURCE_AVAILABLE:
            self.multi_source = MultiSourceDataFetcher()
            print("✅ Sistema de fuentes múltiples activado")
        else:
            self.multi_source = None
    
    def generate_character_from_name(self, name: str, use_multi_source: bool = True) -> Optional[Dict]:
        """
        Genera un personaje completo usando múltiples fuentes y OpenAI
        
        Args:
            name: Nombre del personaje
            use_multi_source: Si True, usa Wikidata, DBpedia además de Wikipedia
            
        Returns:
            Dict con datos del personaje o None si falla
        """
        # 1. Obtener información de múltiples fuentes
        if use_multi_source and self.multi_source:
            print(f"  📚 Obteniendo datos de múltiples fuentes...")
            all_data = self.multi_source.fetch_all_sources(name)
            wiki_info = all_data['sources'].get('wikipedia')
            combined_info = all_data['combined_info']
            
            # Generar atributos base desde fuentes estructuradas
            base_attributes = self.multi_source.generate_attributes_from_sources(combined_info)
        else:
            # Fallback a solo Wikipedia
            wiki_info = self._get_wikipedia_info(name)
            combined_info = None
            base_attributes = {}
        
        if not wiki_info and not self.client:
            return None
        
        # 2. Usar OpenAI para generar/mejorar atributos
        if self.client:
            print(f"  🤖 Generando atributos con IA...")
            ai_attributes = self._generate_attributes_with_ai(name, wiki_info, combined_info)
            # Combinar atributos (IA tiene prioridad)
            attributes = {**base_attributes, **ai_attributes}
        else:
            # Sin IA, usar solo atributos de fuentes
            if base_attributes:
                attributes = base_attributes
            else:
                attributes = self._generate_basic_attributes(wiki_info)
        
        # 3. Preparar descripción enriquecida
        description = wiki_info.get('summary', '')[:200] if wiki_info else ''
        
        # Agregar información adicional si está disponible
        if combined_info:
            extra_info = []
            if combined_info.get('birth_year'):
                extra_info.append(f"Nacido en {combined_info['birth_year']}")
            if combined_info.get('occupation'):
                extra_info.append(', '.join(combined_info['occupation'][:2]))
            
            if extra_info:
                description += f" ({'; '.join(extra_info)})"
        
        return {
            'name': name,
            'description': description[:250],  # Límite de 250 caracteres
            'attributes': attributes,
            'source': 'multi_source' if use_multi_source and self.multi_source else 'wikipedia',
            'data_quality': 'high' if self.client and use_multi_source else 'medium'
        }
    
    def _get_wikipedia_info(self, name: str) -> Optional[Dict]:
        """Obtiene información de Wikipedia"""
        try:
            # Buscar página
            page = wikipedia.page(name, auto_suggest=True)
            
            return {
                'title': page.title,
                'summary': page.summary,
                'url': page.url,
                'categories': page.categories[:10]  # Primeras 10 categorías
            }
        except wikipedia.exceptions.DisambiguationError as e:
            # Si hay ambigüedad, tomar la primera opción
            try:
                page = wikipedia.page(e.options[0])
                return {
                    'title': page.title,
                    'summary': page.summary,
                    'url': page.url,
                    'categories': page.categories[:10]
                }
            except:
                return None
        except:
            return None
    
    def _generate_attributes_with_ai(self, name: str, wiki_info: Optional[Dict], combined_info: Optional[Dict] = None) -> Dict[str, int]:
        """
        Usa OpenAI para generar atributos del personaje
        
        Args:
            name: Nombre del personaje
            wiki_info: Información de Wikipedia
            combined_info: Información combinada de múltiples fuentes
        
        Returns:
            Dict {attribute_key: value} con valores de -2 a 2
        """
        # Obtener todas las preguntas existentes
        questions = db.session.query(Question).all()
        attribute_keys = [q.attribute_key for q in questions[:30]]  # Top 30 preguntas
        
        # Crear contexto enriquecido
        context = f"Personaje: {name}\n"
        
        if wiki_info:
            context += f"Wikipedia: {wiki_info.get('summary', '')[:500]}\n"
        
        if combined_info:
            if combined_info.get('occupation'):
                context += f"Ocupación: {', '.join(combined_info['occupation'])}\n"
            if combined_info.get('nationality'):
                context += f"Nacionalidad: {', '.join(combined_info['nationality'])}\n"
            if combined_info.get('birth_year'):
                context += f"Año de nacimiento: {combined_info['birth_year']}\n"
            if combined_info.get('is_alive') is not None:
                context += f"Vivo: {'Sí' if combined_info['is_alive'] else 'No'}\n"
        
        prompt = f"""Eres un experto en clasificar personajes para un juego tipo Akinator.

{context}

Para cada atributo, asigna un valor de -2 a 2:
- 2: Definitivamente SÍ
- 1: Probablemente sí
- 0: No sé / Neutral / No aplica
- -1: Probablemente no
- -2: Definitivamente NO

Atributos a evaluar:
{', '.join(attribute_keys)}

Responde SOLO con un JSON válido en este formato:
{{"attribute_key": valor, ...}}

No incluyas explicaciones, solo el JSON."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un asistente que genera atributos en formato JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parsear respuesta
            content = response.choices[0].message.content.strip()
            
            # Limpiar markdown si existe
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            attributes = json.loads(content)
            
            # Validar valores
            validated = {}
            for key, value in attributes.items():
                if isinstance(value, (int, float)) and -2 <= value <= 2:
                    validated[key] = int(value)
            
            return validated
            
        except Exception as e:
            print(f"Error generando atributos con IA: {e}")
            return self._generate_basic_attributes(wiki_info)
    
    def _generate_basic_attributes(self, wiki_info: Optional[Dict]) -> Dict[str, int]:
        """Genera atributos básicos sin IA basándose en categorías de Wikipedia"""
        attributes = {}
        
        if not wiki_info:
            return {'is_real': 0, 'is_fictional': 0}
        
        categories = ' '.join(wiki_info.get('categories', [])).lower()
        summary = wiki_info.get('summary', '').lower()
        
        # Reglas básicas basadas en palabras clave
        keywords = {
            'is_real': (['nacido', 'fallecido', 'político', 'científico'], 2),
            'is_fictional': (['ficción', 'personaje', 'novela', 'película'], 2),
            'is_human': (['persona', 'humano', 'hombre', 'mujer'], 2),
            'is_male': (['hombre', 'masculino', 'actor'], 1),
            'is_scientist': (['científico', 'física', 'química', 'matemático'], 2),
            'is_artist': (['artista', 'pintor', 'músico', 'cantante'], 2),
            'is_athlete': (['deportista', 'futbolista', 'atleta'], 2),
        }
        
        for attr, (words, value) in keywords.items():
            if any(word in summary or word in categories for word in words):
                attributes[attr] = value
        
        return attributes
    
    def generate_smart_questions(self, num_questions: int = 20) -> List[Dict]:
        """
        Genera nuevas preguntas inteligentes usando OpenAI
        
        Args:
            num_questions: Número de preguntas a generar
            
        Returns:
            Lista de dicts con preguntas
        """
        if not self.client:
            return []
        
        # Obtener preguntas existentes para evitar duplicados
        existing = db.session.query(Question).all()
        existing_texts = [q.text for q in existing]
        
        prompt = f"""Genera {num_questions} preguntas nuevas para un juego tipo Akinator en español.

Preguntas existentes (NO repetir):
{', '.join(existing_texts[:20])}

Requisitos:
1. Preguntas claras y específicas
2. Que ayuden a diferenciar personajes
3. Formato: pregunta de Sí/No
4. Variedad de categorías (físico, personalidad, contexto, habilidades)

Responde con un JSON array:
[
  {{"text": "¿Pregunta?", "attribute_key": "clave_snake_case"}},
  ...
]

Solo el JSON, sin explicaciones."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en crear preguntas para juegos de adivinanzas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Limpiar markdown
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            questions = json.loads(content)
            return questions
            
        except Exception as e:
            print(f"Error generando preguntas: {e}")
            return []
    
    def bulk_import_characters(self, names: List[str]) -> Dict:
        """
        Importa múltiples personajes en lote
        
        Args:
            names: Lista de nombres de personajes
            
        Returns:
            Dict con estadísticas de importación
        """
        stats = {
            'total': len(names),
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for name in names:
            # Verificar si ya existe
            existing = db.session.query(Character).filter_by(name=name).first()
            if existing:
                stats['skipped'] += 1
                continue
            
            # Generar personaje
            char_data = self.generate_character_from_name(name)
            
            if not char_data:
                stats['failed'] += 1
                continue
            
            try:
                # Crear personaje
                character = Character(
                    name=char_data['name'],
                    description=char_data['description']
                )
                db.session.add(character)
                db.session.flush()
                
                # Agregar atributos
                for attr_key, value in char_data['attributes'].items():
                    char_attr = CharacterAttribute(
                        character_id=character.id,
                        attribute_key=attr_key,
                        value=value,
                        confidence=0.8  # Confianza media para datos generados por IA
                    )
                    db.session.add(char_attr)
                
                db.session.commit()
                stats['success'] += 1
                print(f"✓ Importado: {name}")
                
            except Exception as e:
                db.session.rollback()
                stats['failed'] += 1
                print(f"✗ Error importando {name}: {e}")
        
        return stats
    
    def suggest_characters_by_category(self, category: str, limit: int = 10) -> List[str]:
        """
        Sugiere personajes de una categoría usando OpenAI
        
        Args:
            category: Categoría (ej: "científicos famosos", "superhéroes")
            limit: Número de sugerencias
            
        Returns:
            Lista de nombres
        """
        if not self.client:
            return []
        
        prompt = f"""Lista {limit} {category} famosos y reconocibles mundialmente.

Requisitos:
- Personajes muy conocidos
- Variedad (diferentes épocas, nacionalidades)
- Solo nombres, sin descripciones

Formato: JSON array de strings
["Nombre 1", "Nombre 2", ...]"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            names = json.loads(content)
            return names
            
        except Exception as e:
            print(f"Error sugiriendo personajes: {e}")
            return []
