# 🌐 Sistema de Fuentes Múltiples

El sistema ahora integra **múltiples fuentes de datos** para obtener información más rica y precisa sobre los personajes.

## 📚 Fuentes Integradas

### 1. **Wikipedia** (Español)
- ✅ Resúmenes y descripciones
- ✅ Categorías
- ✅ Enlaces relacionados
- ✅ Ya implementado

### 2. **Wikidata** (NUEVO)
- ✅ Datos estructurados
- ✅ Fecha de nacimiento/muerte
- ✅ Ocupación
- ✅ Nacionalidad
- ✅ Género
- ✅ IDs únicos

### 3. **DBpedia** (NUEVO)
- ✅ Datos semánticos
- ✅ Ontologías
- ✅ Relaciones entre entidades
- ✅ Tipos de recursos

## 🎯 Ventajas

### Datos Más Precisos
- **Fechas exactas**: Nacimiento y muerte desde Wikidata
- **Ocupaciones verificadas**: Múltiples fuentes confirman
- **Género confirmado**: Datos estructurados
- **Nacionalidad**: Información oficial

### Atributos Automáticos
El sistema ahora genera atributos automáticamente desde fuentes estructuradas:

```python
# Ejemplo de atributos generados automáticamente
{
    'is_alive': 2,          # Desde Wikidata (sin fecha de muerte)
    'is_male': 2,           # Desde Wikidata (género)
    'is_scientist': 2,      # Desde ocupación en Wikidata
    'is_real': 2,           # Desde categorías de Wikipedia
    'is_ancient': -2        # Desde año de nacimiento
}
```

### Mejor Calidad
- **Sin IA**: Atributos básicos desde fuentes
- **Con IA**: Atributos enriquecidos con GPT-4
- **Combinación**: Lo mejor de ambos mundos

## 🔄 Flujo de Datos

```
1. Usuario solicita personaje
         ↓
2. Wikipedia → Resumen, categorías
         ↓
3. Wikidata → Datos estructurados (fechas, ocupación, etc.)
         ↓
4. DBpedia → Datos semánticos adicionales
         ↓
5. Combinar todas las fuentes
         ↓
6. Generar atributos base automáticos
         ↓
7. (Opcional) Enriquecer con GPT-4
         ↓
8. Guardar en base de datos
```

## 📊 Ejemplo Real

### Entrada
```
Nombre: "Marie Curie"
```

### Fuentes Consultadas

**Wikipedia:**
```json
{
  "summary": "Marie Curie fue una científica polaca...",
  "categories": ["Científicos de Polonia", "Premios Nobel"]
}
```

**Wikidata:**
```json
{
  "occupation": ["física", "química"],
  "nationality": ["Polonia", "Francia"],
  "gender": "femenino",
  "birth_date": "1867-11-07",
  "death_date": "1934-07-04"
}
```

**DBpedia:**
```json
{
  "type": "http://dbpedia.org/ontology/Scientist",
  "abstract": "Marie Skłodowska-Curie..."
}
```

### Atributos Generados

```python
{
    'is_real': 2,           # De categorías Wikipedia
    'is_fictional': -2,     # De categorías Wikipedia
    'is_male': -2,          # De Wikidata (género femenino)
    'is_scientist': 2,      # De Wikidata (ocupación)
    'is_alive': -2,         # De Wikidata (tiene fecha muerte)
    'is_dead': 2,           # De Wikidata
    'won_nobel': 2,         # De categorías Wikipedia
    'is_female': 2,         # De Wikidata
    'is_polish': 2,         # De Wikidata (nacionalidad)
}
```

## 🚀 Uso

El sistema de fuentes múltiples se activa automáticamente:

```bash
python backend/expand_database.py
```

Al importar personajes, verás:
```
📚 Obteniendo datos de múltiples fuentes...
🤖 Generando atributos con IA...
✓ Importado: Marie Curie
```

## ⚙️ Configuración

No requiere configuración adicional. El sistema:
- ✅ Detecta automáticamente si está disponible
- ✅ Hace fallback a Wikipedia si falla
- ✅ Funciona sin API keys (solo fuentes públicas)
- ✅ Se combina perfectamente con OpenAI

## 📈 Mejoras de Calidad

### Antes (Solo Wikipedia)
```python
{
    'is_real': 2,
    'is_scientist': 2,
    # ~5-10 atributos básicos
}
```

### Ahora (Fuentes Múltiples + IA)
```python
{
    'is_real': 2,
    'is_fictional': -2,
    'is_male': -2,
    'is_scientist': 2,
    'is_alive': -2,
    'is_dead': 2,
    'won_nobel': 2,
    'is_female': 2,
    'is_polish': 2,
    'is_french': 1,
    # ~20-30 atributos precisos
}
```

## 🔒 Privacidad y Límites

- ✅ Todas las fuentes son públicas y gratuitas
- ✅ No requiere autenticación
- ✅ Respeta rate limits automáticamente
- ✅ Timeouts configurados (5 segundos)
- ✅ Manejo robusto de errores

## 🎯 Próximas Fuentes

Planeadas para futuras versiones:
- [ ] IMDb (películas y actores)
- [ ] MusicBrainz (músicos)
- [ ] OpenLibrary (escritores y libros)
- [ ] Sports databases (atletas)
- [ ] Fandom wikis (personajes ficticios)

---

**¡Tu Akinator ahora tiene acceso a datos de calidad profesional!** 🌟
