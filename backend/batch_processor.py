"""
Sistema de procesamiento batch asíncrono
Importa múltiples personajes en paralelo con imágenes
"""
import asyncio
import aiohttp
import os
import json
from typing import List, Dict, Optional
from pathlib import Path
from PIL import Image
from io import BytesIO
import hashlib


class BatchProcessor:
    """Procesa múltiples personajes en paralelo de forma asíncrona"""
    
    def __init__(self, ai_expansion_system, max_concurrent: int = 5):
        """
        Args:
            ai_expansion_system: Instancia de AIExpansionSystem
            max_concurrent: Número máximo de tareas concurrentes
        """
        self.ai_system = ai_expansion_system
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Directorio para imágenes
        self.images_dir = Path('static/images/characters')
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_batch(self, names: List[str], generate_images: bool = True) -> Dict:
        """
        Procesa un lote de personajes de forma asíncrona
        
        Args:
            names: Lista de nombres de personajes
            generate_images: Si True, genera/descarga imágenes
            
        Returns:
            Dict con estadísticas del procesamiento
        """
        stats = {
            'total': len(names),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'images_generated': 0,
            'images_downloaded': 0,
            'errors': []
        }
        
        # Crear tareas asíncronas
        tasks = [
            self._process_character(name, generate_images, stats)
            for name in names
        ]
        
        # Ejecutar en paralelo con límite de concurrencia
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                stats['failed'] += 1
                stats['errors'].append({
                    'name': names[i],
                    'error': str(result)
                })
        
        return stats
    
    async def _process_character(self, name: str, generate_images: bool, stats: Dict) -> Optional[Dict]:
        """Procesa un personaje individual"""
        async with self.semaphore:
            try:
                print(f"  📥 Procesando: {name}")
                
                # 1. Generar datos del personaje (síncrono)
                char_data = await asyncio.to_thread(
                    self.ai_system.generate_character_from_name,
                    name
                )
                
                if not char_data:
                    stats['failed'] += 1
                    return None
                
                # 2. Obtener/generar imagen
                if generate_images:
                    image_url = await self._get_or_generate_image(name, char_data)
                    if image_url:
                        char_data['image_url'] = image_url
                        if image_url.startswith('http'):
                            stats['images_downloaded'] += 1
                        else:
                            stats['images_generated'] += 1
                
                # 3. Guardar en base de datos (síncrono)
                success = await asyncio.to_thread(
                    self._save_character,
                    char_data
                )
                
                if success:
                    stats['success'] += 1
                    print(f"  ✓ Completado: {name}")
                else:
                    stats['skipped'] += 1
                
                return char_data
                
            except Exception as e:
                print(f"  ✗ Error en {name}: {e}")
                stats['failed'] += 1
                raise
    
    async def _get_or_generate_image(self, name: str, char_data: Dict) -> Optional[str]:
        """
        Obtiene imagen de internet o la genera con DALL-E
        
        Prioridad:
        1. Buscar en Wikipedia/Wikidata
        2. Buscar en Google Images (scraping)
        3. Generar con DALL-E
        """
        # 1. Intentar obtener de Wikipedia
        wiki_image = await self._get_wikipedia_image(name)
        if wiki_image:
            return wiki_image
        
        # 2. Intentar buscar en web
        web_image = await self._search_web_image(name)
        if web_image:
            return web_image
        
        # 3. Generar con DALL-E
        if self.ai_system.client:
            dalle_image = await self._generate_dalle_image(name, char_data)
            if dalle_image:
                return dalle_image
        
        return None
    
    async def _get_wikipedia_image(self, name: str) -> Optional[str]:
        """Obtiene imagen de Wikipedia"""
        try:
            import wikipedia
            wikipedia.set_lang("es")
            
            page = await asyncio.to_thread(wikipedia.page, name, auto_suggest=True)
            
            if hasattr(page, 'images') and page.images:
                # Tomar la primera imagen que no sea un icono
                for img_url in page.images:
                    if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png']):
                        if 'icon' not in img_url.lower() and 'logo' not in img_url.lower():
                            # Descargar y guardar localmente con timeout más largo
                            local_path = await self._download_image(img_url, name, timeout=10)
                            return local_path if local_path else img_url
            
        except Exception as e:
            print(f"    ⚠️  No se pudo obtener imagen de Wikipedia: {e}")
        
        return None
    
    async def _search_web_image(self, name: str) -> Optional[str]:
        """
        Busca imagen en la web usando DuckDuckGo (no requiere API key)
        """
        try:
            # Usar DuckDuckGo Instant Answer API (gratuito)
            url = f"https://api.duckduckgo.com/"
            params = {
                'q': name,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Intentar obtener imagen del resultado
                        if data.get('Image'):
                            image_url = data['Image']
                            if not image_url.startswith('http'):
                                image_url = f"https://duckduckgo.com{image_url}"
                            
                            # Descargar y guardar
                            local_path = await self._download_image(image_url, name)
                            return local_path if local_path else image_url
        
        except Exception as e:
            print(f"    ⚠️  No se pudo buscar imagen en web: {e}")
        
        return None
    
    async def _generate_dalle_image(self, name: str, char_data: Dict) -> Optional[str]:
        """Genera imagen con DALL-E"""
        try:
            if not self.ai_system.client:
                return None
            
            # Crear prompt descriptivo
            description = char_data.get('description', '')
            prompt = f"Portrait photo of {name}. {description[:100]}. Professional headshot, neutral background, high quality."
            
            print(f"    🎨 Generando imagen con DALL-E...")
            
            # Generar imagen
            response = await asyncio.to_thread(
                self.ai_system.client.images.generate,
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Descargar y guardar localmente
            local_path = await self._download_image(image_url, name)
            
            return local_path if local_path else image_url
            
        except Exception as e:
            print(f"    ⚠️  No se pudo generar imagen con DALL-E: {e}")
            return None
    
    async def _download_image(self, url: str, name: str, timeout: int = 10) -> Optional[str]:
        """Descarga imagen y la guarda localmente"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Crear nombre de archivo único
                        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
                        filename = f"{name_hash}_{name.replace(' ', '_')[:30]}.jpg"
                        filepath = self.images_dir / filename
                        
                        # Procesar y guardar imagen
                        image = Image.open(BytesIO(image_data))
                        
                        # Convertir a RGB si es necesario
                        if image.mode in ('RGBA', 'P'):
                            image = image.convert('RGB')
                        
                        # Redimensionar si es muy grande
                        max_size = (512, 512)
                        image.thumbnail(max_size, Image.Resampling.LANCZOS)
                        
                        # Guardar
                        image.save(filepath, 'JPEG', quality=85, optimize=True)
                        
                        # Retornar ruta relativa para la web
                        return f"/static/images/characters/{filename}"
        
        except Exception as e:
            print(f"    ⚠️  Error descargando imagen: {e}")
        
        return None
    
    def _save_character(self, char_data: Dict) -> bool:
        """Guarda personaje en base de datos (método síncrono)"""
        try:
            from models import db, Character, CharacterAttribute
            
            # Verificar si ya existe
            existing = db.session.query(Character).filter_by(name=char_data['name']).first()
            if existing:
                return False
            
            # Crear personaje
            character = Character(
                name=char_data['name'],
                description=char_data['description'],
                image_url=char_data.get('image_url', '')
            )
            db.session.add(character)
            db.session.flush()
            
            # Agregar atributos
            for attr_key, value in char_data['attributes'].items():
                char_attr = CharacterAttribute(
                    character_id=character.id,
                    attribute_key=attr_key,
                    value=value,
                    confidence=0.8
                )
                db.session.add(char_attr)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"    ✗ Error guardando en BD: {e}")
            return False


def run_batch_import(names: List[str], generate_images: bool = True, max_concurrent: int = 5):
    """
    Función helper para ejecutar importación batch
    
    Args:
        names: Lista de nombres de personajes
        generate_images: Si True, genera/descarga imágenes
        max_concurrent: Número de tareas concurrentes
    """
    from ai_expansion import AIExpansionSystem
    
    ai_system = AIExpansionSystem()
    processor = BatchProcessor(ai_system, max_concurrent)
    
    # Ejecutar procesamiento asíncrono
    stats = asyncio.run(processor.process_batch(names, generate_images))
    
    return stats
