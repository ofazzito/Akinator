# 🤖 Sistema de Expansión con IA

Este módulo permite expandir automáticamente la base de datos de Akinator usando **OpenAI** y **Wikipedia**.

## 🎯 Características

- **Generación automática de personajes** desde Wikipedia
- **Atributos inteligentes** generados por GPT-4
- **Importación masiva** por categorías
- **Generación de preguntas** inteligentes
- **Validación automática** de datos

## 📋 Requisitos

1. **API Key de OpenAI**
   - Crear cuenta en https://platform.openai.com
   - Generar API key en https://platform.openai.com/api-keys
   - Costo aproximado: $0.01-0.05 por personaje

2. **Instalar dependencias**
   ```bash
   uv pip install -r requirements.txt
   ```

## ⚙️ Configuración

1. **Crear archivo `.env`** en la raíz del proyecto:
   ```bash
   cp .env.example .env
   ```

2. **Agregar tu API key**:
   ```
   OPENAI_API_KEY=sk-tu-api-key-aqui
   ```

## 🚀 Uso

### Modo Interactivo

Ejecuta el script de expansión:

```bash
python backend/expand_database.py
```

Opciones disponibles:
1. **Agregar personaje específico** - Busca y agrega un personaje por nombre
2. **Importar por categoría** - Genera y agrega múltiples personajes de una categoría
3. **Generar preguntas** - Crea nuevas preguntas inteligentes
4. **Importación masiva** - Importa lista personalizada de personajes

### Ejemplos de Uso

#### 1. Agregar un personaje específico
```
Opción: 1
Nombre del personaje: Elon Musk

🔍 Buscando información...
✓ Información encontrada
¿Agregar? (s/n): s
✅ Personaje agregado!
```

#### 2. Importar por categoría
```
Opción: 2
Categoría: científicos famosos
¿Cuántos personajes?: 10

🤖 Generando sugerencias...
📋 Personajes sugeridos:
  1. Marie Curie
  2. Stephen Hawking
  3. Carl Sagan
  ...

¿Importar? (s/n): s
⏳ Importando...
✅ Exitosos: 8
⏭️  Omitidos: 2
```

#### 3. Generar preguntas
```
Opción: 3
¿Cuántas preguntas?: 20

🤖 Generando preguntas...
📋 Preguntas generadas:
  1. ¿Tiene un premio Nobel?
  2. ¿Es conocido por la música?
  ...

¿Agregar? (s/n): s
✅ 20 preguntas agregadas!
```

## 🔧 Uso Programático

También puedes usar el sistema directamente en tu código:

```python
from backend.ai_expansion import AIExpansionSystem
from backend.models import db

# Inicializar sistema
ai_system = AIExpansionSystem()

# Agregar un personaje
char_data = ai_system.generate_character_from_name("Nikola Tesla")
print(char_data)

# Importar múltiples personajes
names = ["Ada Lovelace", "Alan Turing", "Grace Hopper"]
stats = ai_system.bulk_import_characters(names)
print(f"Importados: {stats['success']}")

# Generar preguntas
questions = ai_system.generate_smart_questions(10)
print(questions)

# Sugerir personajes por categoría
names = ai_system.suggest_characters_by_category("superhéroes de DC", 15)
print(names)
```

## 📊 Cómo Funciona

### 1. Obtención de Datos (Wikipedia)
- Busca el personaje en Wikipedia
- Extrae resumen y categorías
- Maneja desambiguaciones automáticamente

### 2. Generación de Atributos (OpenAI)
- Envía información del personaje a GPT-4
- Solicita evaluación de ~30 atributos
- Valida respuestas (-2 a 2)
- Asigna confianza de 0.8 (datos generados por IA)

### 3. Almacenamiento
- Crea registro en tabla `characters`
- Genera relaciones en `character_attributes`
- Marca como `ai_generated`

## 💡 Categorías Sugeridas

- **Históricos**: científicos famosos, presidentes históricos, exploradores
- **Entretenimiento**: actores de Hollywood, músicos de rock, directores de cine
- **Deportes**: futbolistas legendarios, campeones de NBA, tenistas famosos
- **Ficción**: superhéroes de Marvel, personajes de Disney, villanos de películas
- **Tecnología**: fundadores de startups, pioneros de la computación
- **Arte**: pintores renacentistas, escultores famosos, fotógrafos icónicos

## 🎨 Prompt Engineering

El sistema usa prompts optimizados para:

### Generación de Atributos
```
Eres un experto en clasificar personajes para un juego tipo Akinator.

Personaje: [nombre]
Información: [resumen de Wikipedia]

Para cada atributo, asigna un valor de -2 a 2...
```

### Generación de Preguntas
```
Genera N preguntas nuevas para un juego tipo Akinator.

Requisitos:
1. Preguntas claras y específicas
2. Que ayuden a diferenciar personajes
3. Formato: pregunta de Sí/No
...
```

## 📈 Escalabilidad

Con este sistema puedes:
- ✅ Agregar **cientos de personajes** en minutos
- ✅ Generar **preguntas ilimitadas**
- ✅ Mantener **consistencia** en los datos
- ✅ **Aprender continuamente** de Wikipedia

## 💰 Costos Estimados

Usando GPT-4o-mini:
- **Por personaje**: ~$0.01 USD
- **100 personajes**: ~$1 USD
- **1000 personajes**: ~$10 USD

## ⚠️ Limitaciones

- Requiere conexión a internet
- Depende de disponibilidad de Wikipedia
- Puede haber errores en datos generados por IA
- Confianza de 0.8 (vs 1.0 para datos manuales)

## 🔒 Seguridad

- ✅ API key en archivo `.env` (no versionado)
- ✅ Validación de respuestas de IA
- ✅ Manejo de errores robusto
- ✅ Rollback automático en fallos

## 🚀 Próximas Mejoras

- [ ] Soporte para múltiples idiomas
- [ ] Integración con más fuentes (IMDb, Wikidata)
- [ ] Generación de imágenes con DALL-E
- [ ] Sistema de verificación humana
- [ ] Cache de respuestas de IA
- [ ] Modo batch asíncrono

---

**¡Ahora tu Akinator puede conocer a miles de personajes!** 🎉
