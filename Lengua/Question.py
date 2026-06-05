"""
Question.py — Banco de preguntas para Pasapalabra: Edición Literatura y Lengua.
Selección aleatoria por letra, validación sin tildes ni mayúsculas.
"""

from __future__ import annotations
import random

# ── Las 25 letras oficiales del rosco (sin K, W) ─────────────────────────────
ROSCO_LETTERS = (
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
    "K", "L", "M", "N", "Ñ", "O", "P", "Q", "R", "S",
    "T", "U", "V", "W", "X", "Y", "Z"
)


class Question:
    def __init__(self, letter: str, hint_type: str, clue: str, answer: str):
        self.letter    = letter
        self.hint_type = hint_type   # "empieza" | "contiene"
        self.clue      = clue
        self.answer    = answer


def normalize_text(text: str) -> str:
    """Elimina espacios, pasa a minúsculas y quita tildes comunes."""
    text = text.strip().lower()
    for orig, rep in {"á":"a","é":"e","í":"i","ó":"o","ú":"u","ü":"u"}.items():
        text = text.replace(orig, rep)
    return text


# ── Banco de preguntas ────────────────────────────────────────────────────────
# Formato: (hint_type, clue, answer)
# Cada letra tiene al menos 2 variantes; build_round_questions elige 1 al azar.

BANK: dict[str, list[tuple[str, str, str]]] = {

    "A": [
        ("empieza",
         "Tipo de palabra que acompaña al sustantivo para describirlo, "
         "como cuando dices que un libro es 'aburrido' o 'fascinante'.",
         "Adjetivo"),
        ("empieza",
         "El hermano malvado de un sinónimo: una palabra que significa "
         "exactamente lo opuesto que otra.",
         "Antónimo"),
    ],

    "B": [
        ("empieza",
         "Apellido del famoso autor argentino al que le fascinaban los "
         "laberintos, los espejos y las bibliotecas infinitas.",
         "Borges"),
        ("empieza",
         "Lugar donde se guardan y se consultan libros.",
         "Biblioteca"),
    ],

    "C": [
        ("empieza",
         "Apellido del escritor español que perdió la movilidad de su mano "
         "izquierda en Lepanto y escribió sobre un caballero muy loco.",
         "Cervantes"),
        ("empieza",
         "Tipo de relato narrativo corto, ideal para leer antes de dormir.",
         "Cuento"),
    ],

    "D": [
        ("empieza",
         "Género teatral muy intenso donde los personajes suelen sufrir "
         "bastante y no terminan riendo como en la comedia.",
         "Drama"),
        ("empieza",
         "Famoso conde transilvano protagonista de la oscura novela "
         "epistolar de Bram Stoker.",
         "Drácula"),
    ],

    "E": [
        ("empieza",
         "La parte final de una novela donde el autor cierra la historia; "
         "es el antónimo del prólogo.",
         "Epílogo"),
        ("empieza",
         "Poema épico narrativo que cuenta grandes hazañas de héroes "
         "clásicos, como La Ilíada o el Cantar de mio Cid.",
         "Epopeya"),
    ],

    "F": [
        ("empieza",
         "Relato corto protagonizado generalmente por animales que te deja "
         "una moraleja para que no cometas sus mismos errores.",
         "Fábula"),
        ("empieza",
         "Apellido del famoso monstruo literario (y de su doctor creador) "
         "en la novela clásica de la escritora Mary Shelley.",
         "Frankenstein"),
    ],

    "G": [
        ("empieza",
         "Gran conjunto de reglas y normas que ordenan nuestro idioma para "
         "que podamos comunicarnos con sentido.",
         "Gramática"),
        ("empieza",
         "Antónimo de 'diminuto'. Es la palabra que describe al personaje "
         "enorme de los cuentos que vive en las nubes y persigue a Jack.",
         "Gigante"),
    ],

    "H": [
        ("empieza",
         "Famoso poeta de la antigua Grecia, creador de La Odisea, que "
         "casualmente tiene el mismo nombre que el papá de Bart Simpson.",
         "Homero"),
        ("empieza",
         "Joven protagonista literario creado por J.K. Rowling que descubre "
         "que es mago al recibir una carta por lechuza.",
         "Harry Potter"),
    ],

    "I": [
        ("empieza",
         "Figura retórica que consiste en dar a entender lo opuesto de lo "
         "que se dice literalmente. Por ejemplo: '¡Qué hermoso clima!' "
         "en medio de una lluvia torrencial.",
         "Ironía"),
        ("empieza",
         "Antónimo de 'final'. Es la primera parte de cualquier cuento, "
         "que muchas veces arranca con 'Había una vez...'.",
         "Inicio"),
    ],

    "J": [
        ("empieza",
         "Famosa joven de Verona, protagonista de la tragedia más romántica "
         "y adaptada de William Shakespeare.",
         "Julieta"),
        ("empieza",
         "Antónimo de 'anciano'. Adjetivo que describe la etapa de la vida "
         "en la que están los adolescentes y los protagonistas de muchas "
         "novelas fantásticas.",
         "Joven"),
    ],

    "K": [
        ("contiene",
         "El gigantesco y temible monstruo marino de la mitología que "
         "atacaba barcos en las historias clásicas de marineros.",
         "Kraken"),
        ("contiene",
         "Apellido del escritor checo autor de 'La metamorfosis', donde "
         "un hombre amanece convertido en insecto.",
         "Kafka"),
    ],

    "L": [
        ("empieza",
         "Relato transmitido de generación en generación sobre héroes o "
         "apariciones misteriosas, cuya veracidad nunca se confirma, "
         "como la historia de La Llorona.",
         "Leyenda"),
        ("empieza",
         "Conjunto de hojas encuadernadas que forman una obra escrita.",
         "Libro"),
    ],

    "M": [
        ("empieza",
         "Recurso literario que se usa cuando algo no se dice literalmente "
         "sino en sentido figurado. Ejemplo: 'Tus ojos son luceros'.",
         "Metáfora"),
        ("empieza",
         "Antónimo de 'mínimo'.",
         "Máximo"),
    ],

    "N": [
        ("empieza",
         "Capitán literario del submarino Nautilus creado por Julio Verne, "
         "cuyo nombre hoy asociamos con un pez payaso perdido.",
         "Nemo"),
        ("empieza",
         "Voz incorpórea que cuenta todo lo que pasa en una novela y que "
         "a veces sabe hasta lo que piensan los personajes.",
         "Narrador"),
    ],

    "Ñ": [
        ("contiene",
         "Sinónimo literario y sofisticado de una trampa o engaño hecho "
         "con mucha astucia.",
         "Artimaña"),
        ("contiene",
         "El idioma de Miguel de Cervantes, famoso en la lingüística "
         "por ser dueño de esta letra tan particular.",
         "Español"),
    ],

    "O": [
        ("empieza",
         "Título del poema épico griego sobre un héroe astuto que tarda "
         "10 años en volver a su hogar en Ítaca.",
         "Odisea"),
        ("empieza",
         "Palabra que en literatura se refiere al conjunto completo de "
         "la creación de un autor.",
         "Obra"),
    ],

    "P": [
        ("empieza",
         "Apellido del escritor estadounidense considerado el gran maestro "
         "del cuento moderno de terror y creador del poema El cuervo.",
         "Poe"),
        ("empieza",
         "Texto introductorio de un libro que prepara al lector para la "
         "historia que va a encontrar; lo opuesto al epílogo.",
         "Prólogo"),
    ],

    "Q": [
        ("empieza",
         "El caballero de la armadura oxidada más famoso de la literatura, "
         "tan obsesionado con los libros de caballería que confundía "
         "molinos de viento con gigantes.",
         "Quijote"),
        ("empieza",
         "Sinónimo de 'amar' o 'apreciar'. Es el verbo que expresa afecto "
         "hacia una persona muy cercana, o a tu libro favorito.",
         "Querer"),
    ],

    "R": [
        ("empieza",
         "Famoso joven trágicamente enamorado de la familia Montesco, "
         "que haría cualquier cosa por su amada Capuleto.",
         "Romeo"),
        ("empieza",
         "Antónimo de 'lento'. Es la velocidad a la que necesitas contestar "
         "en este juego antes de que se te acabe el tiempo.",
         "Rápido"),
    ],

    "S": [
        ("empieza",
         "Apellido del dramaturgo inglés más reverenciado de la historia, "
         "creador de Hamlet y Macbeth.",
         "Shakespeare"),
        ("empieza",
         "El fiel y regordete escudero de Don Quijote, encargado de aportar "
         "el sentido común terrenal a las aventuras.",
         "Sancho"),
    ],

    "T": [
        ("empieza",
         "Género teatral fatalista donde el destino de los personajes es "
         "inevitable y suele terminar con la muerte del protagonista.",
         "Tragedia"),
        ("empieza",
         "Sinónimo extremo de 'miedo'. Es el género literario y "
         "cinematográfico de historias como Drácula o Frankenstein.",
         "Terror"),
    ],

    "U": [
        ("empieza",
         "Concepto literario y filosófico de una sociedad perfecta, "
         "justa e ideal, pero que lamentablemente no existe.",
         "Utopía"),
        ("empieza",
         "Antónimo de 'primero'. Es la posición que ocupa la letra Z "
         "en el abecedario.",
         "Último"),
    ],

    "V": [
        ("empieza",
         "Cada una de las líneas rítmicas que componen un poema y que, "
         "al agruparse, forman una estrofa.",
         "Verso"),
        ("empieza",
         "Antónimo absoluto de 'mentira'. Es lo que Pinocho no podía decir "
         "sin que la nariz lo delatara.",
         "Verdad"),
    ],

    "W": [
        ("empieza",
         "Apellido del amigo inseparable, médico y biógrafo del detective "
         "Sherlock Holmes en las novelas de Arthur Conan Doyle.",
         "Watson"),
        ("empieza",
         "Primer nombre de pila del creador de Romeo y Julieta, y también "
         "el nombre de un aclamado poeta de apellido Whitman.",
         "William"),
    ],

    "X": [
        ("contiene",
         "Entorno lingüístico o situación que rodea a una palabra y que "
         "resulta vital para deducir su verdadero significado.",
         "Contexto"),
        ("contiene",
         "Sinónimo de 'raro' o 'desconocido'. Palabra que aparece en el "
         "título en español de la serie Stranger Things.",
         "Extraño"),
    ],

    "Y": [
        ("empieza",
         "Antónimo exacto del pronombre personal 'tú', usado constantemente "
         "en los libros narrados en primera persona.",
         "Yo"),
        ("empieza",
         "Adverbio que indica que algo ya ha ocurrido o que expresa "
         "afirmación. Aparece mucho en los títulos de canciones románticas.",
         "Ya"),
    ],

    "Z": [
        ("empieza",
         "Héroe literario de ficción que viste de negro, cabalga en su "
         "caballo Tornado y tiene la mala costumbre de rayar las paredes "
         "con su espada.",
         "Zorro"),
        ("contiene",
         "Juego de palabras y rimas que plantea un enigma para que lo "
         "resuelvas. Es exactamente el tipo de reto al que estás jugando.",
         "Adivinanza"),
    ],
}


def parse_question_file() -> dict:
    """Devuelve el banco de preguntas completo."""
    return BANK


def build_round_questions(bank: dict, rng: random.Random) -> dict[str, Question]:
    """
    Para cada letra del rosco elige al azar una de las variantes disponibles
    en el banco y devuelve un diccionario {letra: Question}.
    """
    round_questions: dict[str, Question] = {}
    for letter in ROSCO_LETTERS:
        variants = bank.get(letter)
        if not variants:
            # Fallback por si faltara alguna letra
            round_questions[letter] = Question(
                letter=letter,
                hint_type="empieza",
                clue=f"Pregunta de prueba para la letra {letter}.",
                answer="test",
            )
            continue
        hint_type, clue, answer = rng.choice(variants)
        round_questions[letter] = Question(
            letter=letter,
            hint_type=hint_type,
            clue=clue,
            answer=answer,
        )
    return round_questions