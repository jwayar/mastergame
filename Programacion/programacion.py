"""
╔══════════════════════════════════════════════════════╗
║         APRENDE PYTHON  v3.0                         ║
║  Juego educativo de programación para niños 8-12     ║
╚══════════════════════════════════════════════════════╝
"""

import pygame
import sys
import json
import os
import math
import random
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ── Resolver ruta (para .exe con PyInstaller) ─────────
def resolver_ruta(relativa):
    """Devuelve la ruta correcta tanto en desarrollo como en .exe."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relativa)

# ── Pantalla ──────────────────────────────────────────
ANCHO, ALTO = 1000, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("¡Aprende Python Jugando! 🐍")
clock = pygame.time.Clock()

# ── Colores ───────────────────────────────────────────
BLANCO       = (255, 255, 255)
NEGRO        = (20,  20,  35)
FONDO        = (245, 248, 255)
AZUL         = (60,  120, 255)
AZUL_OSC     = (30,  70,  180)
AZUL_CLARO   = (180, 210, 255)
VERDE        = (40,  195,  90)
VERDE_OSC    = (20,  130,  55)
ROJO         = (230,  60,  60)
ROJO_OSC     = (160,  30,  30)
AMARILLO     = (255, 210,   0)
AMARILLO_OSC = (200, 155,   0)
NARANJA      = (255, 145,  30)
PURPURA      = (150,  80, 230)
PURPURA_OSC  = (90,   40, 160)
ROSA         = (255, 100, 180)
CIAN         = (0,   200, 220)
GRIS         = (180, 185, 200)
GRIS_OSC     = (100, 105, 120)
GRIS_CLARO   = (225, 228, 240)

# ── Fuentes ───────────────────────────────────────────
try:
    f_titulo  = pygame.font.SysFont("comicsansms", 52, bold=True)
    f_grande  = pygame.font.SysFont("comicsansms", 34, bold=True)
    f_normal  = pygame.font.SysFont("comicsansms", 24, bold=True)
    f_pequena = pygame.font.SysFont("comicsansms", 18)
    f_mini    = pygame.font.SysFont("comicsansms", 14)
except Exception:
    f_titulo  = pygame.font.SysFont(None, 52, bold=True)
    f_grande  = pygame.font.SysFont(None, 34, bold=True)
    f_normal  = pygame.font.SysFont(None, 24, bold=True)
    f_pequena = pygame.font.SysFont(None, 18)
    f_mini    = pygame.font.SysFont(None, 14)

# ── Ranking ───────────────────────────────────────────
ARCHIVO_RANKING = "ranking_python.json"

def cargar_ranking():
    if os.path.exists(ARCHIVO_RANKING):
        try:
            with open(ARCHIVO_RANKING, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []

def guardar_ranking(nombre, puntos):
    r = cargar_ranking()
    r.append({"nombre": nombre, "puntos": puntos})
    r.sort(key=lambda x: x["puntos"], reverse=True)
    r = r[:10]
    try:
        with open(ARCHIVO_RANKING, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
    return r

# ── Generador de sonidos con numpy (sin archivos externos) ──
SAMPLE_RATE = 44100

def _make_sound(arr_mono, vol=0.4):
    arr = (arr_mono * vol * 32767).astype(np.int16)
    stereo = np.column_stack([arr, arr])
    return pygame.sndarray.make_sound(stereo)

def gen_tono(freq=440, dur=0.18, vol=0.35, fade=True):
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, False)
    wave = np.sin(2 * np.pi * freq * t)
    if fade:
        env = np.linspace(1, 0, n) ** 1.5
        wave *= env
    return _make_sound(wave, vol)

def gen_acorde(freqs, dur=0.22, vol=0.28):
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, False)
    wave = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)
    env = np.linspace(1, 0, n) ** 1.2
    wave *= env
    return _make_sound(wave, vol)

def gen_sweep(f0=300, f1=800, dur=0.25, vol=0.35):
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, False)
    freq = np.linspace(f0, f1, n)
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    wave = np.sin(phase)
    env = np.linspace(1, 0, n) ** 1.3
    wave *= env
    return _make_sound(wave, vol)

def gen_error(dur=0.3, vol=0.3):
    n = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n, False)
    wave = np.sin(2 * np.pi * 180 * t) * 0.5 + np.sin(2 * np.pi * 120 * t) * 0.5
    env = np.linspace(1, 0, n) ** 0.8
    wave *= env
    return _make_sound(wave, vol)

def gen_click(vol=0.25):
    n = int(0.04 * SAMPLE_RATE)
    wave = np.random.uniform(-1, 1, n)
    env = np.linspace(1, 0, n) ** 3
    wave *= env
    return _make_sound(wave, vol)

def gen_musica_menu():
    """Genera una melodía corta tipo jingle para el menú (loop)."""
    notas = [
        (523, 0.18), (659, 0.18), (784, 0.18), (1047, 0.28),
        (880, 0.18), (784, 0.18), (659, 0.28), (523, 0.18),
        (587, 0.18), (698, 0.18), (880, 0.28), (784, 0.18),
        (698, 0.18), (587, 0.18), (523, 0.38),
    ]
    duracion_total = sum(d for _, d in notas)
    n_total = int(duracion_total * SAMPLE_RATE)
    wave = np.zeros(n_total)
    pos = 0
    for freq, dur in notas:
        n = int(dur * SAMPLE_RATE)
        t = np.linspace(0, dur, n, False)
        seg = np.sin(2 * np.pi * freq * t) * 0.5
        seg += np.sin(2 * np.pi * freq * 2 * t) * 0.15
        env = np.ones(n)
        fade_n = min(int(0.04 * SAMPLE_RATE), n)
        env[-fade_n:] = np.linspace(1, 0.1, fade_n)
        env[:fade_n] = np.linspace(0, 1, fade_n)
        seg *= env
        end = min(pos + n, n_total)
        wave[pos:end] += seg[:end - pos]
        pos += n
    wave = wave / (np.max(np.abs(wave)) + 1e-8) * 0.45
    return _make_sound(wave, 1.0)

def gen_musica_juego():
    """Melodía más rítmica para la pantalla de juego."""
    notas = [
        (392, 0.15), (440, 0.15), (494, 0.15), (523, 0.22),
        (494, 0.15), (440, 0.15), (392, 0.22),
        (349, 0.15), (392, 0.15), (440, 0.22), (494, 0.15),
        (440, 0.15), (392, 0.15), (349, 0.30),
    ]
    duracion_total = sum(d for _, d in notas)
    n_total = int(duracion_total * SAMPLE_RATE)
    wave = np.zeros(n_total)
    pos = 0
    for freq, dur in notas:
        n = int(dur * SAMPLE_RATE)
        t = np.linspace(0, dur, n, False)
        seg = np.sin(2 * np.pi * freq * t) * 0.4
        seg += np.sin(2 * np.pi * freq * 1.5 * t) * 0.1
        env = np.ones(n)
        fade_n = min(int(0.03 * SAMPLE_RATE), n)
        env[-fade_n:] = np.linspace(1, 0.1, fade_n)
        env[:fade_n] = np.linspace(0, 1, fade_n)
        seg *= env
        end = min(pos + n, n_total)
        wave[pos:end] += seg[:end - pos]
        pos += n
    wave = wave / (np.max(np.abs(wave)) + 1e-8) * 0.38
    return _make_sound(wave, 1.0)

# ── Cargar sonido desde archivo .mp3/.wav (si existe) ──
def cargar_sonido_archivo(nombre):
    """Intenta cargar archivo de audio; devuelve None si no existe."""
    for ext in [".mp3", ".wav", ".ogg"]:
        ruta = resolver_ruta(nombre + ext)
        if os.path.exists(ruta):
            try:
                return pygame.mixer.Sound(ruta)
            except Exception:
                pass
    return None

# ── Sistema de audio ──────────────────────────────────
class Audio:
    def __init__(self):
        # Intentar cargar desde archivos primero; si no, generar
        self.snd_ok     = cargar_sonido_archivo("acierto") or gen_sweep(300, 900, 0.22)
        self.snd_error  = cargar_sonido_archivo("error")   or gen_error()
        self.snd_nivel  = cargar_sonido_archivo("nivel")   or gen_acorde([523, 659, 784], 0.35)
        self.snd_click  = cargar_sonido_archivo("click")   or gen_click()
        self.snd_bloque = cargar_sonido_archivo("bloque")  or gen_tono(660, 0.07, 0.2)

        # Música generada siempre internamente para garantizar calidad
        self.mus_menu  = gen_musica_menu()
        self.mus_juego = gen_musica_juego()

        self.canal_musica = pygame.mixer.Channel(0)
        self.musica_actual = None
        self.volumen_musica = 0.55

    def play(self, snd):
        if snd:
            snd.play()

    def play_musica(self, nombre):
        if self.musica_actual == nombre:
            return
        self.musica_actual = nombre
        self.canal_musica.stop()
        mus = self.mus_menu if nombre == "menu" else self.mus_juego
        mus.set_volume(self.volumen_musica)
        self.canal_musica.play(mus, loops=-1)

    def stop_musica(self):
        self.canal_musica.stop()
        self.musica_actual = None

audio = Audio()

# ── Niveles (mejorados, bloques ajustados para que quepan) ───
NIVELES = [
    # ── BLOQUE 1: print ──
    {
        "tema": "print() - Mostrar en pantalla",
        "explicacion": "print() muestra texto en la pantalla.\n¡Es lo primero que aprende todo programador!",
        "objetivo": 'Mostrar: Hola Mundo',
        "bloques": ['print', '(', '"Hola Mundo"', ')'],
        "respuesta": 'print ( "Hola Mundo" )',
        "pista": 'print  →  (  →  "Hola Mundo"  →  )',
        "color": AZUL,
    },
    {
        "tema": "print() - Mostrar numeros",
        "explicacion": "Tambien podes mostrar numeros con print().\n¡Los numeros van sin comillas!",
        "objetivo": "Mostrar el numero: 42",
        "bloques": ['print', '(', '42', ')'],
        "respuesta": 'print ( 42 )',
        "pista": 'print  →  (  →  42  →  )',
        "color": AZUL,
    },
    {
        "tema": "print() - Suma dentro",
        "explicacion": "Podes hacer calculos dentro de print().\nPython calcula primero y luego muestra.",
        "objetivo": "Mostrar el resultado de 5 + 3",
        "bloques": ['print', '(', '5', '+', '3', ')'],
        "respuesta": 'print ( 5 + 3 )',
        "pista": 'print  →  (  →  5  →  +  →  3  →  )',
        "color": AZUL,
    },
    # ── BLOQUE 2: variables ──
    {
        "tema": "Variables - Guardar numeros",
        "explicacion": "Una variable guarda informacion.\nUsamos = para guardar un valor.",
        "objetivo": "Guardar el numero 10 en una variable 'edad'",
        "bloques": ['edad', '=', '10'],
        "respuesta": 'edad = 10',
        "pista": 'edad  →  =  →  10',
        "color": VERDE,
    },
    {
        "tema": "Variables - Guardar texto",
        "explicacion": "Podemos guardar texto en variables.\nEl texto siempre va entre comillas.",
        "objetivo": 'Guardar "Ana" en la variable nombre',
        "bloques": ['nombre', '=', '"Ana"'],
        "respuesta": 'nombre = "Ana"',
        "pista": 'nombre  →  =  →  "Ana"',
        "color": VERDE,
    },
    {
        "tema": "Variables - Mostrar variable",
        "explicacion": "Podemos mostrar una variable con print().\n¡Sin comillas cuando es una variable!",
        "objetivo": "Mostrar el contenido de la variable edad",
        "bloques": ['print', '(', 'edad', ')'],
        "respuesta": 'print ( edad )',
        "pista": 'print  →  (  →  edad  →  )',
        "color": VERDE,
    },
    {
        "tema": "Variables - Suma de variables",
        "explicacion": "Podes sumar variables entre si.\nPython usa el valor guardado.",
        "objetivo": "Sumar 'a' mas 'b' y guardarlo en 'total'",
        "bloques": ['total', '=', 'a', '+', 'b'],
        "respuesta": 'total = a + b',
        "pista": 'total  →  =  →  a  →  +  →  b',
        "color": VERDE,
    },
    # ── BLOQUE 3: if ──
    {
        "tema": "Condiciones - if mayor que",
        "explicacion": "if significa 'si'. Ejecuta codigo\nsolo cuando una condicion es verdadera.",
        "objetivo": "Escribir: si edad es mayor que 5",
        "bloques": ['if', 'edad', '>', '5', ':'],
        "respuesta": 'if edad > 5 :',
        "pista": 'if  →  edad  →  >  →  5  →  :',
        "color": NARANJA,
    },
    {
        "tema": "Condiciones - if igual",
        "explicacion": "== compara si dos cosas son iguales.\n¡Un = guarda, dos == compara!",
        "objetivo": 'Si nombre es igual a "Ana"',
        "bloques": ['if', 'nombre', '==', '"Ana"', ':'],
        "respuesta": 'if nombre == "Ana" :',
        "pista": 'if  →  nombre  →  ==  →  "Ana"  →  :',
        "color": NARANJA,
    },
    {
        "tema": "Condiciones - if menor",
        "explicacion": "< significa 'menor que'.\nCompara si un numero es mas chico.",
        "objetivo": "Si temperatura es menor que 0",
        "bloques": ['if', 'temperatura', '<', '0', ':'],
        "respuesta": 'if temperatura < 0 :',
        "pista": 'if  →  temperatura  →  <  →  0  →  :',
        "color": NARANJA,
    },
    # ── BLOQUE 4: listas ──
    {
        "tema": "Listas - Crear lista",
        "explicacion": "Una lista guarda varios elementos juntos.\nSe crean con corchetes [ ].",
        "objetivo": 'Crear lista frutas con "manzana"',
        "bloques": ['frutas', '=', '[', '"manzana"', ']'],
        "respuesta": 'frutas = [ "manzana" ]',
        "pista": 'frutas  →  =  →  [  →  "manzana"  →  ]',
        "color": ROSA,
    },
    {
        "tema": "Listas - Contar elementos",
        "explicacion": "len() cuenta cuantos elementos\ntiene una lista o texto.",
        "objetivo": "Contar elementos de la lista frutas",
        "bloques": ['len', '(', 'frutas', ')'],
        "respuesta": 'len ( frutas )',
        "pista": 'len  →  (  →  frutas  →  )',
        "color": ROSA,
    },
    {
        "tema": "Listas - Agregar elemento",
        "explicacion": "append() agrega un elemento al final\nde una lista existente.",
        "objetivo": 'Agregar "pera" a la lista frutas',
        "bloques": ['frutas', '.', 'append', '(', '"pera"', ')'],
        "respuesta": 'frutas . append ( "pera" )',
        "pista": 'frutas  →  .  →  append  →  (  →  "pera"  →  )',
        "color": ROSA,
    },
    # ── BLOQUE 5: for ──
    {
        "tema": "Bucles for - Recorrer lista",
        "explicacion": "for repite codigo para cada elemento.\n'para cada cosa en la lista' hace algo.",
        "objetivo": "Recorrer cada fruta en la lista",
        "bloques": ['for', 'fruta', 'in', 'frutas', ':'],
        "respuesta": 'for fruta in frutas :',
        "pista": 'for  →  fruta  →  in  →  frutas  →  :',
        "color": PURPURA,
    },
    {
        "tema": "Bucles for - range()",
        "explicacion": "range(n) genera numeros del 0 al n-1.\n¡Muy util para repetir N veces!",
        "objetivo": "Repetir 5 veces usando range",
        "bloques": ['for', 'i', 'in', 'range', '(', '5', ')', ':'],
        "respuesta": 'for i in range ( 5 ) :',
        "pista": 'for  →  i  →  in  →  range  →  (  →  5  →  )  →  :',
        "color": PURPURA,
    },
    {
        "tema": "Bucles for - Mostrar numeros",
        "explicacion": "Podemos mostrar cada numero\nque genera range() con print.",
        "objetivo": "Mostrar 'i' dentro de un for con range(3)",
        "bloques": ['for', 'i', 'in', 'range', '(', '3', ')', ':'],
        "respuesta": 'for i in range ( 3 ) :',
        "pista": 'for  →  i  →  in  →  range  →  (  →  3  →  )  →  :',
        "color": PURPURA,
    },
    # ── BLOQUE 6: funciones ──
    {
        "tema": "Funciones - def basico",
        "explicacion": "def crea una funcion que podes usar\nmuchas veces. ¡Tu propio comando!",
        "objetivo": "Crear una funcion llamada saludar",
        "bloques": ['def', 'saludar', '(', ')', ':'],
        "respuesta": 'def saludar ( ) :',
        "pista": 'def  →  saludar  →  (  →  )  →  :',
        "color": CIAN,
    },
    {
        "tema": "Funciones - Con parametro",
        "explicacion": "Las funciones pueden recibir datos.\nEse dato se llama parametro o argumento.",
        "objetivo": "Crear funcion saludar que recibe 'nombre'",
        "bloques": ['def', 'saludar', '(', 'nombre', ')', ':'],
        "respuesta": 'def saludar ( nombre ) :',
        "pista": 'def  →  saludar  →  (  →  nombre  →  )  →  :',
        "color": CIAN,
    },
    {
        "tema": "Funciones - Llamar funcion",
        "explicacion": "Para usar una funcion la llamamos\nescribiendo su nombre con parentesis.",
        "objetivo": "Llamar a la funcion saludar()",
        "bloques": ['saludar', '(', ')'],
        "respuesta": 'saludar ( )',
        "pista": 'saludar  →  (  →  )',
        "color": CIAN,
    },
]

# ── Utilidades de dibujo ──────────────────────────────
def texto_centrado(txt, fuente, color, y, sombra=True):
    w = pantalla.get_width()
    if sombra:
        s = fuente.render(txt, True, (0, 0, 0))
        pantalla.blit(s, (w // 2 - s.get_width() // 2 + 2, y + 2))
    r = fuente.render(txt, True, color)
    pantalla.blit(r, (w // 2 - r.get_width() // 2, y))

def barra(x, y, ancho, alto, prog, col, col2=GRIS_CLARO, radio=6):
    pygame.draw.rect(pantalla, col2, (x, y, ancho, alto), border_radius=radio)
    if prog > 0:
        w = max(radio * 2, int(ancho * min(prog, 1.0)))
        pygame.draw.rect(pantalla, col, (x, y, w, alto), border_radius=radio)

def boton(rect, txt, bg, fg=BLANCO, fuente=None, radio=14):
    if fuente is None:
        fuente = f_normal
    mx, my = pygame.mouse.get_pos()
    over = rect.collidepoint(mx, my)
    c = tuple(min(v + 30, 255) for v in bg) if over else bg
    sombra_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(sombra_surf, (0, 0, 0, 80),
                     (0, 0, rect.width, rect.height), border_radius=radio)
    pantalla.blit(sombra_surf, (rect.x + 3, rect.y + 4))
    pygame.draw.rect(pantalla, c, rect, border_radius=radio)
    borde = tuple(min(v + 60, 255) for v in bg)
    pygame.draw.rect(pantalla, borde, rect, 2, border_radius=radio)
    s = fuente.render(txt, True, fg)
    pantalla.blit(s, (rect.centerx - s.get_width() // 2,
                      rect.centery - s.get_height() // 2))
    return over

# ── Partículas ────────────────────────────────────────
class Estrella:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x   = random.uniform(0, ANCHO)
        self.y   = random.uniform(0, ALTO)
        self.r   = random.randint(1, 3)
        self.vel = random.uniform(0.3, 1.2)
        self.col = random.choice([AZUL_CLARO, AMARILLO, BLANCO, CIAN, ROSA])

    def update(self):
        self.y -= self.vel
        if self.y < -5:
            self.reset()
            self.y = ALTO + 5

    def draw(self, surf):
        pygame.draw.circle(surf, self.col, (int(self.x), int(self.y)), self.r)


estrellas = [Estrella() for _ in range(60)]


class Confetti:
    def __init__(self, x, y):
        self.x    = x
        self.y    = y
        self.vx   = random.uniform(-5, 5)
        self.vy   = random.uniform(-10, -3)
        self.col  = random.choice([AMARILLO, ROSA, VERDE, AZUL, NARANJA, PURPURA, CIAN])
        self.r    = random.randint(4, 9)
        self.vida = 90

    def update(self):
        self.x  += self.vx
        self.vy += 0.4
        self.y  += self.vy
        self.vida -= 1

    def draw(self, surf):
        if self.vida > 0:
            alpha = min(255, self.vida * 3)
            s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.col, alpha), (self.r, self.r), self.r)
            surf.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


confettis: list[Confetti] = []


def explotar_confetti(x, y, n=40):
    for _ in range(n):
        confettis.append(Confetti(x, y))


def limpiar_confetti():
    confettis.clear()


def actualizar_confetti():
    for c in confettis[:]:
        c.update()
        c.draw(pantalla)
        if c.vida <= 0:
            confettis.remove(c)

# ── Fondo decorativo ──────────────────────────────────
BURBUJAS = [
    (80,  80,  60, AZUL_CLARO),
    (900, 150, 45, ROSA),
    (500, 650, 55, AMARILLO),
    (150, 600, 40, VERDE),
    (850, 550, 50, PURPURA),
    (400, 80,  35, CIAN),
]

def dibujar_fondo(t=0):
    pantalla.fill(FONDO)
    for i, (cx, cy, cr, col) in enumerate(BURBUJAS):
        oy = int(math.sin(t * 0.03 + i * 1.1) * 8)
        s = pygame.Surface((cr * 2, cr * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, 45), (cr, cr), cr)
        pantalla.blit(s, (cx - cr, cy + oy - cr))
    for e in estrellas:
        e.update()
        e.draw(pantalla)

# ── Pantalla de inicio ────────────────────────────────
def pantalla_inicio():
    btn_jugar   = pygame.Rect(ANCHO // 2 - 130, 390, 260, 60)
    btn_ranking = pygame.Rect(ANCHO // 2 - 130, 465, 260, 60)
    btn_salir   = pygame.Rect(ANCHO // 2 - 130, 540, 260, 60)
    t = 0
    audio.play_musica("menu")

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                audio.play(audio.snd_click)
                if btn_jugar.collidepoint(ev.pos):
                    return "jugar"
                if btn_ranking.collidepoint(ev.pos):
                    pantalla_ranking()
                if btn_salir.collidepoint(ev.pos):
                    pygame.quit()
                    sys.exit()

        t += 1
        dibujar_fondo(t)

        escala = 1 + 0.03 * math.sin(t * 0.06)
        for surf_orig, y in [
            (f_titulo.render("¡Aprende", True, AZUL),  100),
            (f_titulo.render("Python!",  True, VERDE), 165),
        ]:
            sw = int(surf_orig.get_width()  * escala)
            sh = int(surf_orig.get_height() * escala)
            sc = pygame.transform.scale(surf_orig, (sw, sh))
            so = sc.copy()
            so.set_alpha(60)
            pantalla.blit(so, (ANCHO // 2 - sw // 2 + 3, y + 3))
            pantalla.blit(sc, (ANCHO // 2 - sw // 2, y))

        sub = f_normal.render("Jugando y aprendiendo a programar", True, GRIS_OSC)
        pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2, 245))

        for i in range(5):
            ang = t * 0.04 + i * math.pi * 2 / 5
            sx = int(ANCHO // 2 + math.cos(ang) * 280)
            sy = int(200 + math.sin(ang) * 60)
            pygame.draw.circle(pantalla, AMARILLO, (sx, sy), 6)
            pygame.draw.circle(pantalla, BLANCO,   (sx, sy), 3)

        boton(btn_jugar,   "▶  JUGAR",   VERDE,        radio=18)
        boton(btn_ranking, "🏆 RANKING", AMARILLO_OSC, radio=18)
        boton(btn_salir,   "✖  SALIR",   ROJO_OSC,     radio=18)

        ver = f_mini.render("v3.0 - Educativo para ninos 8-12 anos  |  18 niveles", True, GRIS)
        pantalla.blit(ver, (ANCHO // 2 - ver.get_width() // 2, ALTO - 26))

        actualizar_confetti()
        pygame.display.flip()
        clock.tick(60)

# ── Pantalla ranking ──────────────────────────────────
def pantalla_ranking():
    ranking = cargar_ranking()
    btn_v = pygame.Rect(ANCHO // 2 - 90, 610, 180, 48)
    t = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_v.collidepoint(ev.pos):
                    audio.play(audio.snd_click)
                    return
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return

        t += 1
        dibujar_fondo(t)

        caja = pygame.Rect(150, 60, 700, 540)
        s = pygame.Surface(caja.size, pygame.SRCALPHA)
        s.fill((255, 255, 255, 220))
        pantalla.blit(s, caja.topleft)
        pygame.draw.rect(pantalla, AMARILLO, caja, 3, border_radius=20)

        texto_centrado("🏆  TOP 10", f_grande, AMARILLO_OSC, 80)
        texto_centrado("Mejores programadores", f_pequena, GRIS_OSC, 125)

        medallas = ["🥇", "🥈", "🥉"] + [f"#{i+4}" for i in range(7)]
        cols = [AMARILLO_OSC, GRIS_OSC, NARANJA] + [NEGRO] * 7

        if not ranking:
            texto_centrado("¡Aun no hay puntajes!", f_normal, GRIS_OSC, 300)
        for i, e in enumerate(ranking[:10]):
            col = cols[i]
            y = 162 + i * 36
            txt = f_pequena.render(
                f"{medallas[i]}  {e['nombre'][:12]:<12}   {e['puntos']:>4} pts",
                True, col,
            )
            pantalla.blit(txt, (ANCHO // 2 - txt.get_width() // 2, y))

        boton(btn_v, "VOLVER", AZUL_OSC)
        pygame.display.flip()
        clock.tick(60)

# ── Pedir nombre ──────────────────────────────────────
def pedir_nombre(puntos):
    nombre = ""
    btn_ok = pygame.Rect(ANCHO // 2 - 80, 430, 160, 52)
    t = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and nombre.strip():
                    return nombre.strip()
                elif ev.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                elif len(nombre) < 12 and ev.unicode.isprintable():
                    nombre += ev.unicode
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_ok.collidepoint(ev.pos) and nombre.strip():
                    audio.play(audio.snd_click)
                    return nombre.strip()

        t += 1
        dibujar_fondo(t)

        caja = pygame.Rect(200, 150, 600, 340)
        s = pygame.Surface(caja.size, pygame.SRCALPHA)
        s.fill((255, 255, 255, 220))
        pantalla.blit(s, caja.topleft)
        pygame.draw.rect(pantalla, VERDE, caja, 3, border_radius=20)

        texto_centrado("¡Terminaste!",             f_grande, VERDE_OSC, 175)
        texto_centrado(f"Puntaje: {puntos} puntos", f_normal, AZUL,     225)
        texto_centrado("¿Cual es tu nombre?",       f_normal, NEGRO,    275)

        campo = pygame.Rect(ANCHO // 2 - 140, 310, 280, 50)
        pygame.draw.rect(pantalla, GRIS_CLARO, campo, border_radius=12)
        pygame.draw.rect(pantalla, AZUL, campo, 2, border_radius=12)
        cursor = "|" if pygame.time.get_ticks() % 800 < 400 else ""
        nt = f_normal.render(nombre + cursor, True, NEGRO)
        pantalla.blit(nt, (campo.x + 10, campo.y + 12))

        if nombre.strip():
            boton(btn_ok, "GUARDAR", VERDE_OSC)

        pygame.display.flip()
        clock.tick(60)

# ── Pantalla de fin ───────────────────────────────────
def pantalla_fin(puntos):
    nombre = pedir_nombre(puntos)
    guardar_ranking(nombre, puntos)
    ranking = cargar_ranking()
    audio.play_musica("menu")

    btn_menu = pygame.Rect(ANCHO // 2 - 220, 530, 190, 52)
    btn_rank = pygame.Rect(ANCHO // 2 + 30,  530, 190, 52)
    t = 0

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                audio.play(audio.snd_click)
                if btn_menu.collidepoint(ev.pos):
                    limpiar_confetti()
                    return "menu"
                if btn_rank.collidepoint(ev.pos):
                    pantalla_ranking()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                limpiar_confetti()
                return "menu"

        t += 1
        if t % 8 == 0:
            explotar_confetti(random.randint(100, 900), random.randint(100, 400), 6)

        dibujar_fondo(t)
        actualizar_confetti()

        caja = pygame.Rect(100, 60, 800, 460)
        s = pygame.Surface(caja.size, pygame.SRCALPHA)
        s.fill((255, 255, 255, 215))
        pantalla.blit(s, caja.topleft)
        pygame.draw.rect(pantalla, AMARILLO, caja, 4, border_radius=22)

        texto_centrado("🎉 ¡FELICITACIONES! 🎉",               f_grande, AMARILLO_OSC, 85)
        texto_centrado(f"{nombre} completo todos los niveles!", f_normal, VERDE_OSC,   140)
        texto_centrado(f"Puntaje final: {puntos} puntos",       f_grande, AZUL,        185)

        pygame.draw.line(pantalla, GRIS, (200, 238), (800, 238), 1)
        texto_centrado("TOP 5", f_pequena, GRIS_OSC, 248)

        for i, e in enumerate(ranking[:5]):
            col = AMARILLO_OSC if e["nombre"] == nombre else NEGRO
            rt = f_pequena.render(
                f"#{i+1}  {e['nombre'][:10]:<10}  {e['puntos']:>4} pts",
                True, col,
            )
            pantalla.blit(rt, (ANCHO // 2 - rt.get_width() // 2, 278 + i * 30))

        boton(btn_menu, "MENU",    AZUL_OSC)
        boton(btn_rank, "RANKING", AMARILLO_OSC)

        pygame.display.flip()
        clock.tick(60)

# ── Crear botones de bloque (con ajuste automático de tamaño) ──
def crear_botones_bloque(nivel):
    bloques = nivel["bloques"]
    total   = len(bloques)

    # Calcular ancho dinámico según cantidad de bloques
    espacio = 10
    if total <= 4:
        ancho_bloque = 160
    elif total <= 6:
        ancho_bloque = 140
    elif total <= 8:
        ancho_bloque = 118
    else:
        ancho_bloque = 100

    bloque_total = ancho_bloque + espacio
    ancho_disponible = ANCHO - 80
    # Si no caben en una fila, reducir más
    while total * bloque_total > ancho_disponible and ancho_bloque > 70:
        ancho_bloque -= 5
        bloque_total = ancho_bloque + espacio

    start_x = ANCHO // 2 - (total * bloque_total) // 2
    bots = []
    for i, b in enumerate(bloques):
        rect = pygame.Rect(start_x + i * bloque_total, 315, ancho_bloque, 50)
        bots.append({"texto": b, "rect": rect, "usado": False})
    return bots

# ── Juego principal ───────────────────────────────────
def jugar():
    nivel_idx     = 0
    puntos        = 0
    codigo_usr    = []
    mensaje       = ""
    color_msg     = NEGRO
    timer_msg     = 0
    mostrar_pista = False
    anim_ok       = 0
    anim_err      = 0
    t             = 0

    botones_bloque = crear_botones_bloque(NIVELES[nivel_idx])
    audio.play_musica("juego")

    btn_verificar = pygame.Rect(80,  600, 190, 48)
    btn_borrar    = pygame.Rect(290, 600, 190, 48)
    btn_pista     = pygame.Rect(500, 600, 190, 48)
    btn_menu      = pygame.Rect(710, 600, 190, 48)

    while True:
        nv = NIVELES[nivel_idx]

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                limpiar_confetti()
                return "menu"

            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos

                # Seleccionar bloque
                for b in botones_bloque:
                    if not b["usado"] and b["rect"].collidepoint(mx, my):
                        codigo_usr.append(b["texto"])
                        b["usado"] = True
                        mostrar_pista = False
                        audio.play(audio.snd_bloque)
                        break

                # Verificar
                if btn_verificar.collidepoint(mx, my):
                    generado = " ".join(codigo_usr)
                    if generado == nv["respuesta"]:
                        audio.play(audio.snd_ok)
                        audio.play(audio.snd_nivel)
                        puntos   += 20
                        mensaje   = "¡Correcto! ¡Muy bien! 🎉"
                        color_msg = VERDE_OSC
                        timer_msg = 120
                        anim_ok   = 50
                        explotar_confetti(ANCHO // 2, ALTO // 2, 50)

                        nivel_idx += 1
                        if nivel_idx >= len(NIVELES):
                            pygame.time.delay(800)
                            limpiar_confetti()
                            return pantalla_fin(puntos)

                        codigo_usr     = []
                        botones_bloque = crear_botones_bloque(NIVELES[nivel_idx])
                        mostrar_pista  = False
                    else:
                        audio.play(audio.snd_error)
                        mensaje   = "Ese orden no es correcto. ¡Intenta de nuevo!"
                        color_msg = ROJO_OSC
                        timer_msg = 140
                        anim_err  = 30
                        codigo_usr = []
                        for b in botones_bloque:
                            b["usado"] = False

                # Borrar
                if btn_borrar.collidepoint(mx, my):
                    audio.play(audio.snd_click)
                    codigo_usr = []
                    for b in botones_bloque:
                        b["usado"] = False
                    mostrar_pista = False

                # Pista
                if btn_pista.collidepoint(mx, my):
                    audio.play(audio.snd_click)
                    mostrar_pista = not mostrar_pista

                # Menú
                if btn_menu.collidepoint(mx, my):
                    audio.play(audio.snd_click)
                    limpiar_confetti()
                    return "menu"

        t += 1
        if timer_msg > 0:
            timer_msg -= 1
        if anim_ok > 0:
            anim_ok -= 1
        if anim_err > 0:
            anim_err -= 1

        # ── Dibujo ────────────────────────────────────
        dibujar_fondo(t)
        actualizar_confetti()

        col_tema = nv["color"]

        # Panel principal
        panel = pygame.Rect(30, 20, ANCHO - 60, 560)
        ps = pygame.Surface(panel.size, pygame.SRCALPHA)
        ps.fill((255, 255, 255, 200))
        pantalla.blit(ps, panel.topleft)
        borde_col = VERDE if anim_ok > 0 else (ROJO if anim_err > 0 else col_tema)
        pygame.draw.rect(pantalla, borde_col, panel, 3, border_radius=18)

        # Tema
        tema_s = f_normal.render(f"📚 {nv['tema']}", True, col_tema)
        pantalla.blit(tema_s, (55, 30))

        # Barra de progreso
        prog = nivel_idx / len(NIVELES)
        barra(420, 34, 400, 16, prog, col_tema, GRIS_CLARO)
        pg = f_mini.render(f"Nivel {nivel_idx + 1} de {len(NIVELES)}", True, GRIS_OSC)
        pantalla.blit(pg, (420, 18))

        # Puntos
        pt = f_normal.render(f"⭐ {puntos} pts", True, AMARILLO_OSC)
        pantalla.blit(pt, (ANCHO - pt.get_width() - 20, 26))

        # Separador
        pygame.draw.line(pantalla, GRIS_CLARO, (50, 64), (ANCHO - 50, 64), 1)

        # Explicación
        ex_y = 72
        for linea in nv["explicacion"].split("\n"):
            s = f_pequena.render(linea, True, NEGRO)
            pantalla.blit(s, (55, ex_y))
            ex_y += 26

        # Objetivo
        pygame.draw.rect(pantalla, col_tema, (50, 130, ANCHO - 100, 46), border_radius=12)
        obj_s = f_normal.render(f"🎯 Objetivo: {nv['objetivo']}", True, BLANCO)
        pantalla.blit(obj_s, (ANCHO // 2 - obj_s.get_width() // 2, 141))

        # Etiqueta bloques
        lb = f_pequena.render("Toca los bloques en el orden correcto:", True, GRIS_OSC)
        pantalla.blit(lb, (55, 288))

        # Bloques disponibles
        f_bloque = f_pequena if len(nv["bloques"]) <= 6 else f_mini
        for b in botones_bloque:
            if b["usado"]:
                pygame.draw.rect(pantalla, GRIS_CLARO, b["rect"], border_radius=10)
                pygame.draw.rect(pantalla, GRIS,       b["rect"], 2, border_radius=10)
                gt = f_bloque.render(b["texto"], True, GRIS)
                pantalla.blit(gt, (b["rect"].centerx - gt.get_width() // 2,
                                   b["rect"].centery - gt.get_height() // 2))
            else:
                mx2, my2 = pygame.mouse.get_pos()
                over = b["rect"].collidepoint(mx2, my2)
                bg_c = tuple(min(v + 25, 255) for v in col_tema) if over else col_tema
                sombra_s = pygame.Surface((b["rect"].w, b["rect"].h), pygame.SRCALPHA)
                pygame.draw.rect(sombra_s, (0, 0, 0, 60),
                                 (0, 0, b["rect"].w, b["rect"].h), border_radius=10)
                pantalla.blit(sombra_s, (b["rect"].x + 3, b["rect"].y + 4))
                pygame.draw.rect(pantalla, bg_c, b["rect"], border_radius=10)
                borde2 = tuple(min(v + 60, 255) for v in col_tema)
                pygame.draw.rect(pantalla, borde2, b["rect"], 2, border_radius=10)
                bt = f_bloque.render(b["texto"], True, BLANCO)
                pantalla.blit(bt, (b["rect"].centerx - bt.get_width() // 2,
                                   b["rect"].centery - bt.get_height() // 2))

        # Área código construido
        area = pygame.Rect(50, 380, ANCHO - 100, 56)
        if anim_ok > 0:
            bg_area = (210, 255, 210)
        elif anim_err > 0:
            bg_area = (255, 210, 210)
        else:
            bg_area = GRIS_CLARO
        pygame.draw.rect(pantalla, bg_area, area, border_radius=12)
        pygame.draw.rect(pantalla, col_tema, area, 2, border_radius=12)

        label_area = f_mini.render("Tu codigo:", True, GRIS_OSC)
        pantalla.blit(label_area, (55, 368))

        codigo_txt = " ".join(codigo_usr)
        ct = f_normal.render(codigo_txt, True, NEGRO)
        pantalla.blit(ct, (65, 396))

        if pygame.time.get_ticks() % 800 < 400:
            cx_cur = 65 + ct.get_width() + 4
            pygame.draw.line(pantalla, NEGRO, (cx_cur, 394), (cx_cur, 420), 2)

        # Pista
        if mostrar_pista:
            pista_bg = pygame.Rect(50, 448, ANCHO - 100, 34)
            pygame.draw.rect(pantalla, (255, 248, 200), pista_bg, border_radius=10)
            pygame.draw.rect(pantalla, AMARILLO_OSC, pista_bg, 2, border_radius=10)
            ps_txt = f_pequena.render(f"💡 Pista: {nv['pista']}", True, AMARILLO_OSC)
            pantalla.blit(ps_txt, (60, 456))

        # Botones inferiores
        boton(btn_verificar, "✔ VERIFICAR", VERDE_OSC,   fuente=f_pequena)
        boton(btn_borrar,    "✖ BORRAR",    ROJO_OSC,    fuente=f_pequena)
        boton(btn_pista,     "💡 PISTA",    AMARILLO_OSC, fuente=f_pequena)
        boton(btn_menu,      "🏠 MENU",     AZUL_OSC,    fuente=f_pequena)

        # Mensaje feedback
        if timer_msg > 0:
            alpha = min(255, timer_msg * 4)
            ms = f_normal.render(mensaje, True, color_msg)
            bg_w = ms.get_width() + 30
            bg_m = pygame.Surface((bg_w, 38), pygame.SRCALPHA)
            bg_m.fill((255, 255, 255, min(alpha, 200)))
            px = ANCHO // 2 - bg_w // 2
            pantalla.blit(bg_m, (px, ALTO - 42))
            pygame.draw.rect(pantalla, color_msg, (px, ALTO - 42, bg_w, 38), 1, border_radius=8)
            ms.set_alpha(alpha)
            pantalla.blit(ms, (ANCHO // 2 - ms.get_width() // 2, ALTO - 36))

        pygame.display.flip()
        clock.tick(60)

# ── Main ──────────────────────────────────────────────
def main():
    estado = "menu"
    while True:
        if estado == "jugar":
            estado = jugar()
        else:
            estado = pantalla_inicio()
        if estado not in ("jugar", "menu"):
            estado = "menu"


if __name__ == "__main__":
    main()