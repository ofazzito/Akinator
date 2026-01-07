"""
Script de inicialización de datos
Carga personajes y preguntas iniciales en la base de datos
"""
from models import Character, Question, CharacterAttribute


def initialize_data(db):
    """Inicializa la base de datos con personajes y preguntas de ejemplo"""
    
    # ===== PERSONAJES INICIALES =====
    characters_data = [
        # Personajes de ficción - Películas/Series
        {
            'name': 'Harry Potter',
            'description': 'Joven mago con cicatriz en forma de rayo',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 2, 'is_male': 2,
                'has_magic': 2, 'from_book': 2, 'from_movie': 2, 'wears_glasses': 2,
                'is_hero': 2, 'is_young': 2
            }
        },
        {
            'name': 'Darth Vader',
            'description': 'Villano icónico de Star Wars',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 1, 'is_male': 2,
                'is_villain': 2, 'from_movie': 2, 'wears_mask': 2, 'has_powers': 2,
                'from_space': 2, 'is_dark': 2
            }
        },
        {
            'name': 'Iron Man',
            'description': 'Superhéroe millonario con armadura tecnológica',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 2, 'is_male': 2,
                'is_hero': 2, 'from_movie': 2, 'is_rich': 2, 'has_technology': 2,
                'wears_armor': 2, 'is_smart': 2
            }
        },
        {
            'name': 'Elsa',
            'description': 'Reina de Frozen con poderes de hielo',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 2, 'is_male': -2,
                'has_magic': 2, 'from_movie': 2, 'is_princess': 2, 'has_powers': 2,
                'is_animated': 2, 'is_young': 1
            }
        },
        {
            'name': 'Sherlock Holmes',
            'description': 'Detective británico famoso por su deducción',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 2, 'is_male': 2,
                'is_detective': 2, 'from_book': 2, 'is_smart': 2, 'is_british': 2,
                'wears_hat': 2, 'smokes_pipe': 2
            }
        },
        
        # Personajes históricos
        {
            'name': 'Albert Einstein',
            'description': 'Físico alemán, teoría de la relatividad',
            'attributes': {
                'is_real': 2, 'is_fictional': -2, 'is_human': 2, 'is_male': 2,
                'is_scientist': 2, 'is_smart': 2, 'is_famous': 2, 'is_dead': 2,
                'has_mustache': 2, 'won_nobel': 2
            }
        },
        {
            'name': 'Cleopatra',
            'description': 'Última reina del Antiguo Egipto',
            'attributes': {
                'is_real': 2, 'is_fictional': -2, 'is_human': 2, 'is_male': -2,
                'is_royalty': 2, 'is_ancient': 2, 'is_egyptian': 2, 'is_dead': 2,
                'is_beautiful': 2, 'is_powerful': 2
            }
        },
        {
            'name': 'Leonardo da Vinci',
            'description': 'Artista e inventor del Renacimiento',
            'attributes': {
                'is_real': 2, 'is_fictional': -2, 'is_human': 2, 'is_male': 2,
                'is_artist': 2, 'is_inventor': 2, 'is_smart': 2, 'is_dead': 2,
                'is_italian': 2, 'is_famous': 2
            }
        },
        
        # Personajes de videojuegos
        {
            'name': 'Mario',
            'description': 'Fontanero italiano de Nintendo',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 2, 'is_male': 2,
                'from_videogame': 2, 'is_italian': 2, 'has_mustache': 2, 'wears_hat': 2,
                'wears_red': 2, 'is_hero': 2
            }
        },
        {
            'name': 'Sonic',
            'description': 'Erizo azul súper rápido',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': -2, 'is_male': 2,
                'from_videogame': 2, 'is_animal': 2, 'is_fast': 2, 'is_blue': 2,
                'is_hero': 2, 'is_hedgehog': 2
            }
        },
        {
            'name': 'Pikachu',
            'description': 'Pokémon eléctrico amarillo',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': -2, 'is_male': 0,
                'from_videogame': 2, 'is_pokemon': 2, 'is_yellow': 2, 'has_powers': 2,
                'is_cute': 2, 'is_electric': 2
            }
        },
        
        # Celebridades
        {
            'name': 'Lionel Messi',
            'description': 'Futbolista argentino',
            'attributes': {
                'is_real': 2, 'is_fictional': -2, 'is_human': 2, 'is_male': 2,
                'is_athlete': 2, 'plays_football': 2, 'is_argentinian': 2, 'is_famous': 2,
                'is_alive': 2, 'is_rich': 2
            }
        },
        {
            'name': 'Taylor Swift',
            'description': 'Cantante y compositora estadounidense',
            'attributes': {
                'is_real': 2, 'is_fictional': -2, 'is_human': 2, 'is_male': -2,
                'is_singer': 2, 'is_american': 2, 'is_famous': 2, 'is_alive': 2,
                'is_blonde': 2, 'is_rich': 2
            }
        },
        
        # Personajes de anime/manga
        {
            'name': 'Goku',
            'description': 'Guerrero Saiyan de Dragon Ball',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 0, 'is_male': 2,
                'from_anime': 2, 'has_powers': 2, 'is_fighter': 2, 'is_hero': 2,
                'has_spiky_hair': 2, 'is_strong': 2
            }
        },
        {
            'name': 'Naruto',
            'description': 'Ninja con zorro de nueve colas',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 2, 'is_male': 2,
                'from_anime': 2, 'is_ninja': 2, 'has_powers': 2, 'is_hero': 2,
                'is_blonde': 2, 'is_young': 2
            }
        },
        
        # Más personajes variados
        {
            'name': 'Mickey Mouse',
            'description': 'Ratón icónico de Disney',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': -2, 'is_male': 2,
                'is_animal': 2, 'is_mouse': 2, 'from_movie': 2, 'is_animated': 2,
                'wears_gloves': 2, 'is_disney': 2
            }
        },
        {
            'name': 'Batman',
            'description': 'Superhéroe millonario de Gotham',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 2, 'is_male': 2,
                'is_hero': 2, 'is_rich': 2, 'wears_mask': 2, 'is_dark': 2,
                'from_comic': 2, 'has_technology': 2
            }
        },
        {
            'name': 'Hermione Granger',
            'description': 'Bruja inteligente amiga de Harry Potter',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 2, 'is_male': -2,
                'has_magic': 2, 'from_book': 2, 'from_movie': 2, 'is_smart': 2,
                'is_young': 2, 'is_hero': 1
            }
        },
        {
            'name': 'SpongeBob',
            'description': 'Esponja de mar que vive en una piña',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': -2, 'is_male': 2,
                'is_animated': 2, 'lives_underwater': 2, 'is_yellow': 2, 'is_funny': 2,
                'from_tv': 2, 'is_sponge': 2
            }
        },
        {
            'name': 'Wonder Woman',
            'description': 'Superheroína amazona con lazo de la verdad',
            'attributes': {
                'is_real': -2, 'is_fictional': 2, 'is_human': 1, 'is_male': -2,
                'is_hero': 2, 'has_powers': 2, 'is_strong': 2, 'from_comic': 2,
                'is_warrior': 2, 'wears_armor': 1
            }
        }
    ]
    
    # Crear personajes
    for char_data in characters_data:
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
                confidence=1.0
            )
            db.session.add(char_attr)
    
    # ===== PREGUNTAS INICIALES =====
    questions_data = [
        # Preguntas básicas de categorización
        ('¿Es un personaje real?', 'is_real'),
        ('¿Es un personaje de ficción?', 'is_fictional'),
        ('¿Es humano?', 'is_human'),
        ('¿Es hombre?', 'is_male'),
        
        # Características físicas
        ('¿Usa lentes/gafas?', 'wears_glasses'),
        ('¿Tiene bigote?', 'has_mustache'),
        ('¿Usa sombrero?', 'wears_hat'),
        ('¿Usa máscara?', 'wears_mask'),
        ('¿Tiene pelo rubio?', 'is_blonde'),
        ('¿Tiene pelo puntiagudo/despeinado?', 'has_spiky_hair'),
        ('¿Es de color azul?', 'is_blue'),
        ('¿Es de color amarillo?', 'is_yellow'),
        ('¿Usa ropa roja?', 'wears_red'),
        ('¿Usa armadura?', 'wears_armor'),
        ('¿Usa guantes?', 'wears_gloves'),
        
        # Poderes y habilidades
        ('¿Tiene poderes mágicos?', 'has_magic'),
        ('¿Tiene superpoderes?', 'has_powers'),
        ('¿Es muy inteligente?', 'is_smart'),
        ('¿Es muy fuerte físicamente?', 'is_strong'),
        ('¿Es muy rápido?', 'is_fast'),
        ('¿Tiene tecnología avanzada?', 'has_technology'),
        ('¿Es detective?', 'is_detective'),
        ('¿Es ninja?', 'is_ninja'),
        ('¿Es guerrero/luchador?', 'is_fighter'),
        ('¿Es guerrero?', 'is_warrior'),
        
        # Rol/Profesión
        ('¿Es un héroe?', 'is_hero'),
        ('¿Es un villano?', 'is_villain'),
        ('¿Es científico?', 'is_scientist'),
        ('¿Es artista?', 'is_artist'),
        ('¿Es inventor?', 'is_inventor'),
        ('¿Es cantante?', 'is_singer'),
        ('¿Es deportista/atleta?', 'is_athlete'),
        ('¿Juega fútbol?', 'plays_football'),
        ('¿Es de la realeza?', 'is_royalty'),
        ('¿Es princesa/príncipe?', 'is_princess'),
        
        # Características personales
        ('¿Es famoso?', 'is_famous'),
        ('¿Es rico/millonario?', 'is_rich'),
        ('¿Es joven?', 'is_young'),
        ('¿Está vivo actualmente?', 'is_alive'),
        ('¿Está muerto?', 'is_dead'),
        ('¿Es de la antigüedad?', 'is_ancient'),
        ('¿Es hermoso/bella?', 'is_beautiful'),
        ('¿Es tierno/adorable?', 'is_cute'),
        ('¿Es gracioso/cómico?', 'is_funny'),
        ('¿Es oscuro/tenebroso?', 'is_dark'),
        ('¿Es poderoso?', 'is_powerful'),
        
        # Medio/Origen
        ('¿Aparece en películas?', 'from_movie'),
        ('¿Aparece en libros?', 'from_book'),
        ('¿Es de un videojuego?', 'from_videogame'),
        ('¿Es de un anime?', 'from_anime'),
        ('¿Es de un cómic?', 'from_comic'),
        ('¿Es de TV/serie?', 'from_tv'),
        ('¿Es animado/caricatura?', 'is_animated'),
        ('¿Es de Disney?', 'is_disney'),
        ('¿Es un Pokémon?', 'is_pokemon'),
        
        # Nacionalidad/Origen
        ('¿Es italiano?', 'is_italian'),
        ('¿Es británico?', 'is_british'),
        ('¿Es estadounidense?', 'is_american'),
        ('¿Es argentino?', 'is_argentinian'),
        ('¿Es egipcio?', 'is_egyptian'),
        ('¿Es del espacio/extraterrestre?', 'from_space'),
        
        # Tipo de criatura
        ('¿Es un animal?', 'is_animal'),
        ('¿Es un ratón?', 'is_mouse'),
        ('¿Es un erizo?', 'is_hedgehog'),
        ('¿Es una esponja?', 'is_sponge'),
        ('¿Vive bajo el agua?', 'lives_underwater'),
        
        # Características específicas
        ('¿Tiene poderes eléctricos?', 'is_electric'),
        ('¿Fuma pipa?', 'smokes_pipe'),
        ('¿Ganó el Premio Nobel?', 'won_nobel'),
    ]
    
    # Crear preguntas
    for text, attr_key in questions_data:
        question = Question(
            text=text,
            attribute_key=attr_key,
            effectiveness_score=1.0
        )
        db.session.add(question)
    
    # Guardar todo
    db.session.commit()
    
    print(f"✓ {len(characters_data)} personajes creados")
    print(f"✓ {len(questions_data)} preguntas creadas")
