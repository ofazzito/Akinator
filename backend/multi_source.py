"""
Sistema de fuentes de datos múltiples
Integra Wikipedia, Wikidata, IMDb y otras fuentes
"""
import requests
import json
from typing import Dict, List, Optional


class MultiSourceDataFetcher:
    """Obtiene datos de múltiples fuentes para enriquecer personajes"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Akinator-Bot/1.0 (Educational Project)'
        })
    
    def fetch_all_sources(self, name: str) -> Dict:
        """
        Obtiene datos de todas las fuentes disponibles
        
        Args:
            name: Nombre del personaje
            
        Returns:
            Dict con datos combinados de todas las fuentes
        """
        data = {
            'name': name,
            'sources': {},
            'combined_info': {}
        }
        
        # Wikipedia (ya implementado en ai_expansion.py)
        data['sources']['wikipedia'] = self._fetch_wikipedia(name)
        
        # Wikidata - IDs y datos estructurados
        data['sources']['wikidata'] = self._fetch_wikidata(name)
        
        # DBpedia - Datos semánticos
        data['sources']['dbpedia'] = self._fetch_dbpedia(name)
        
        # Combinar información
        data['combined_info'] = self._combine_sources(data['sources'])
        
        return data
    
    def _fetch_wikipedia(self, name: str) -> Optional[Dict]:
        """Obtiene datos de Wikipedia (español)"""
        try:
            import wikipedia
            wikipedia.set_lang("es")
            page = wikipedia.page(name, auto_suggest=True)
            
            return {
                'title': page.title,
                'summary': page.summary[:500],
                'url': page.url,
                'categories': page.categories[:10],
                'links': page.links[:20]
            }
        except:
            return None
    
    def _fetch_wikidata(self, name: str) -> Optional[Dict]:
        """
        Obtiene datos estructurados de Wikidata
        Incluye: fecha de nacimiento, ocupación, nacionalidad, etc.
        """
        try:
            # Buscar entidad en Wikidata
            search_url = "https://www.wikidata.org/w/api.php"
            params = {
                'action': 'wbsearchentities',
                'format': 'json',
                'language': 'es',
                'search': name,
                'limit': 1
            }
            
            response = self.session.get(search_url, params=params, timeout=5)
            data = response.json()
            
            if not data.get('search'):
                return None
            
            entity_id = data['search'][0]['id']
            
            # Obtener datos de la entidad
            entity_url = "https://www.wikidata.org/w/api.php"
            params = {
                'action': 'wbgetentities',
                'format': 'json',
                'ids': entity_id,
                'languages': 'es|en'
            }
            
            response = self.session.get(entity_url, params=params, timeout=5)
            entity_data = response.json()
            
            if entity_id not in entity_data.get('entities', {}):
                return None
            
            entity = entity_data['entities'][entity_id]
            claims = entity.get('claims', {})
            
            # Extraer información útil
            info = {
                'id': entity_id,
                'label': entity.get('labels', {}).get('es', {}).get('value', name),
                'description': entity.get('descriptions', {}).get('es', {}).get('value', ''),
                'occupation': self._extract_claim_labels(claims.get('P106', [])),  # Ocupación
                'nationality': self._extract_claim_labels(claims.get('P27', [])),  # Nacionalidad
                'gender': self._extract_claim_labels(claims.get('P21', [])),  # Género
                'birth_date': self._extract_claim_time(claims.get('P569', [])),  # Fecha nacimiento
                'death_date': self._extract_claim_time(claims.get('P570', [])),  # Fecha muerte
            }
            
            return info
            
        except Exception as e:
            print(f"Error obteniendo Wikidata: {e}")
            return None
    
    def _fetch_dbpedia(self, name: str) -> Optional[Dict]:
        """
        Obtiene datos de DBpedia (datos semánticos de Wikipedia)
        """
        try:
            # Buscar recurso en DBpedia español
            search_url = "http://es.dbpedia.org/sparql"
            
            # Query SPARQL para buscar el recurso
            query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            
            SELECT DISTINCT ?resource ?label ?abstract ?type
            WHERE {{
                ?resource rdfs:label ?label .
                FILTER(CONTAINS(LCASE(?label), LCASE("{name}")))
                OPTIONAL {{ ?resource dbo:abstract ?abstract . FILTER(LANG(?abstract) = 'es') }}
                OPTIONAL {{ ?resource rdf:type ?type }}
            }}
            LIMIT 1
            """
            
            params = {
                'query': query,
                'format': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=5)
            data = response.json()
            
            if not data.get('results', {}).get('bindings'):
                return None
            
            result = data['results']['bindings'][0]
            
            return {
                'resource': result.get('resource', {}).get('value', ''),
                'label': result.get('label', {}).get('value', ''),
                'abstract': result.get('abstract', {}).get('value', '')[:500],
                'type': result.get('type', {}).get('value', '')
            }
            
        except Exception as e:
            print(f"Error obteniendo DBpedia: {e}")
            return None
    
    def _extract_claim_labels(self, claims: List) -> List[str]:
        """Extrae labels de claims de Wikidata"""
        labels = []
        for claim in claims[:3]:  # Máximo 3
            try:
                mainsnak = claim.get('mainsnak', {})
                if mainsnak.get('datatype') == 'wikibase-item':
                    item_id = mainsnak.get('datavalue', {}).get('value', {}).get('id')
                    if item_id:
                        # Obtener label del item
                        label = self._get_wikidata_label(item_id)
                        if label:
                            labels.append(label)
            except:
                pass
        return labels
    
    def _extract_claim_time(self, claims: List) -> Optional[str]:
        """Extrae fechas de claims de Wikidata"""
        if not claims:
            return None
        try:
            time_value = claims[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('time')
            if time_value:
                # Formato: +1879-03-14T00:00:00Z -> 1879-03-14
                return time_value.split('T')[0].replace('+', '')
        except:
            pass
        return None
    
    def _get_wikidata_label(self, item_id: str) -> Optional[str]:
        """Obtiene el label de un item de Wikidata"""
        try:
            url = "https://www.wikidata.org/w/api.php"
            params = {
                'action': 'wbgetentities',
                'format': 'json',
                'ids': item_id,
                'props': 'labels',
                'languages': 'es'
            }
            
            response = self.session.get(url, params=params, timeout=3)
            data = response.json()
            
            return data.get('entities', {}).get(item_id, {}).get('labels', {}).get('es', {}).get('value')
        except:
            return None
    
    def _combine_sources(self, sources: Dict) -> Dict:
        """Combina información de todas las fuentes"""
        combined = {
            'summary': '',
            'birth_year': None,
            'death_year': None,
            'occupation': [],
            'nationality': [],
            'gender': None,
            'categories': [],
            'is_alive': None
        }
        
        # Wikipedia
        if sources.get('wikipedia'):
            combined['summary'] = sources['wikipedia'].get('summary', '')
            combined['categories'] = sources['wikipedia'].get('categories', [])
        
        # Wikidata
        if sources.get('wikidata'):
            wd = sources['wikidata']
            
            # Fechas
            if wd.get('birth_date'):
                try:
                    combined['birth_year'] = int(wd['birth_date'][:4])
                except:
                    pass
            
            if wd.get('death_date'):
                try:
                    combined['death_year'] = int(wd['death_date'][:4])
                except:
                    pass
            
            # Determinar si está vivo
            combined['is_alive'] = combined['death_year'] is None
            
            # Ocupación y nacionalidad
            combined['occupation'] = wd.get('occupation', [])
            combined['nationality'] = wd.get('nationality', [])
            
            # Género
            if wd.get('gender'):
                gender_list = wd['gender']
                if gender_list:
                    combined['gender'] = gender_list[0].lower()
        
        # DBpedia
        if sources.get('dbpedia'):
            if not combined['summary']:
                combined['summary'] = sources['dbpedia'].get('abstract', '')
        
        return combined
    
    def generate_attributes_from_sources(self, combined_info: Dict) -> Dict[str, int]:
        """
        Genera atributos basados en información combinada de fuentes
        
        Returns:
            Dict {attribute_key: value} con valores de -2 a 2
        """
        attributes = {}
        
        # Vivo/Muerto
        if combined_info.get('is_alive') is not None:
            attributes['is_alive'] = 2 if combined_info['is_alive'] else -2
            attributes['is_dead'] = -2 if combined_info['is_alive'] else 2
        
        # Género
        gender = combined_info.get('gender')
        if gender:
            gender = str(gender).lower() if not isinstance(gender, str) else gender.lower()
            if 'masculino' in gender or 'male' in gender:
                attributes['is_male'] = 2
            elif 'femenino' in gender or 'female' in gender:
                attributes['is_male'] = -2
        
        # Ocupaciones
        occupations_list = combined_info.get('occupation', [])
        occupations = ' '.join(occupations_list).lower() if occupations_list else ''
        
        occupation_map = {
            'is_scientist': ['científico', 'physicist', 'chemist', 'biologist'],
            'is_artist': ['artista', 'pintor', 'painter', 'sculptor'],
            'is_musician': ['músico', 'musician', 'singer', 'cantante'],
            'is_actor': ['actor', 'actress', 'actriz'],
            'is_writer': ['escritor', 'writer', 'author', 'novelist'],
            'is_politician': ['político', 'politician', 'president', 'presidente'],
            'is_athlete': ['deportista', 'athlete', 'footballer', 'futbolista'],
        }
        
        for attr, keywords in occupation_map.items():
            if any(kw in occupations for kw in keywords):
                attributes[attr] = 2
        
        # Época
        birth_year = combined_info.get('birth_year')
        if birth_year:
            if birth_year < 1800:
                attributes['is_ancient'] = 2
            elif birth_year > 1950:
                attributes['is_young'] = 1
        
        # Categorías de Wikipedia
        categories_list = combined_info.get('categories', [])
        categories = ' '.join(categories_list).lower() if categories_list else ''
        
        if 'ficción' in categories or 'personaje' in categories:
            attributes['is_fictional'] = 2
            attributes['is_real'] = -2
        else:
            attributes['is_real'] = 2
            attributes['is_fictional'] = -2
        
        return attributes
