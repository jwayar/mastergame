"""
GEO BATTLE - con sistema de clasificación completo
==============================
Sprites: colocá tus .png en una carpeta  assets/  al lado de este script.
  assets/cannon_base.png   (base del cañón, ~60x50 px)
  assets/cannon_barrel.png (caño, ~80x20 px, apuntando a la DERECHA)
  assets/ship_0.png        (barco, ~170x80 px)
  assets/ship_1.png
  assets/ship_2.png
  assets/cannonball.png    (bala, ~20x20 px)
  assets/cloud.png         (nube, transparente, ~120x60 px)

Música: colocá los .mp3 al lado de este script (o en assets/).
  menu.mp3     (música del menú)
  juego.mp3    (música durante el juego)

Si algún archivo falta, el juego usa gráficos/sonidos generados automáticamente.
"""

import pygame
import random
import math
import sys
import os
import json

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

# ==================== CONFIGURACIÓN Y GUARDADO ====================
SAVE_FILE     = "highscores.json"
SETTINGS_FILE = "settings.json"

def load_highscores():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("highscores", []), data.get("hi_score", 0)
    except:
        return [], 0

def save_highscores(highscores, hi_score):
    data = {"highscores": highscores[:10], "hi_score": hi_score}
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"music_vol": 0.55, "sfx_vol": 0.70}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

# ─── PANTALLA ────────────────────────────────────────────────
W, H = 1100, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Geo Battle")
clock  = pygame.time.Clock()

# ─── PALETA ──────────────────────────────────────────────────
C = dict(
    sky_top    = (  8,  18,  50),
    sky_mid    = ( 20,  50, 110),
    sky_bot    = ( 40,  90, 160),
    horiz      = (160, 200, 230),
    water_deep = ( 10,  45,  95),
    water_mid  = ( 18,  75, 155),
    water_lite = ( 55, 130, 210),
    water_foam = (190, 220, 255),
    reflect    = ( 30,  90, 180),
    ground     = (170, 140,  70),
    ground2    = (130, 100,  45),
    white      = (240, 240, 240),
    black      = ( 10,  10,  10),
    yellow     = (255, 220,  40),
    red        = (200,  45,  45),
    red2       = (240,  90,  90),
    green      = ( 45, 200,  75),
    green2     = ( 25, 130,  45),
    gray       = (130, 130, 145),
    gray2      = ( 65,  65,  78),
    orange     = (230, 135,  35),
    teal       = ( 35, 175, 155),
    brown      = (105,  65,  35),
    brown2     = (155,  95,  55),
    purple     = (115,  55, 180),
    gold       = (255, 195,   0),
    silver     = (192, 192, 192),
    bronze     = (205, 127,  50),
)

# ─── FUENTES ─────────────────────────────────────────────────
def _font(size):
    for name in ("Courier New", "couriernew", "Courier", "monospace"):
        try:
            return pygame.font.SysFont(name, size, bold=True)
        except:
            pass
    return pygame.font.SysFont(None, size)

FSM = _font(17)
FMD = _font(23)
FLG = _font(34)
FXL = _font(50)
FXX = _font(64)

# Cargar datos guardados
highscores, hi_score = load_highscores()
settings = load_settings()

# ─── MÚSICA ──────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR  = SCRIPT_DIR

def _find_music(name):
    for folder in [SCRIPT_DIR, ASSET_DIR]:
        path = os.path.join(folder, name)
        if os.path.exists(path):
            return path
    return None

_current_music = None

def play_music(name, volume=None, loops=-1):
    global _current_music
    if _current_music == name:
        return
    if volume is None:
        volume = settings["music_vol"]
    path = _find_music(name)
    if path:
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            _current_music = name
        except Exception as e:
            print(f"[música] Error: {e}")
    else:
        print(f"[música] Archivo no encontrado: {name}")

def stop_music():
    global _current_music
    pygame.mixer.music.stop()
    _current_music = None

# ─── EFECTOS DE SONIDO ───────────────────────────────────────
try:
    import numpy as np

    def _snd(freq, dur, wave="sq", vol=0.28, env="decay"):
        sr = 44100
        n  = int(sr * dur)
        t  = np.linspace(0, dur, n, False)
        if wave == "sq":
            s = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave == "noise":
            s = np.random.uniform(-1, 1, n)
        elif wave == "tri":
            s = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        else:
            s = np.sin(2 * np.pi * freq * t)
        if env == "decay":
            s *= np.linspace(1, 0, n)
        elif env == "adsr":
            att = int(n * 0.05); rel = int(n * 0.3)
            env_arr = np.ones(n)
            env_arr[:att] = np.linspace(0, 1, att)
            env_arr[-rel:] = np.linspace(1, 0, rel)
            s *= env_arr
        elif env == "punch":
            s *= np.exp(-np.linspace(0, 8, n))
        s = (s * vol * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack([s, s]))

    def _snd_sweep(f0, f1, dur, wave="sin", vol=0.25):
        sr = 44100; n = int(sr * dur)
        t  = np.linspace(0, dur, n, False)
        freq = np.linspace(f0, f1, n)
        phase = np.cumsum(2 * np.pi * freq / sr)
        s = np.sin(phase) if wave == "sin" else np.sign(np.sin(phase))
        s *= np.linspace(1, 0, n)
        s = (s * vol * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack([s, s]))

    CH_SHOOT  = pygame.mixer.Channel(0)
    CH_HIT    = pygame.mixer.Channel(1)
    CH_RESULT = pygame.mixer.Channel(2)
    CH_UI     = pygame.mixer.Channel(3)

    SND = {
        "shoot"     : _snd(160, .10, "sq",    vol=0.32, env="punch"),
        "shoot_air" : _snd_sweep(320, 600, .18, "sin",  vol=0.18),
        "hit"       : _snd(220, .12, "sq",    vol=0.25, env="decay"),
        "splash"    : _snd(110, .20, "noise", vol=0.20, env="decay"),
        "ok"        : _snd(523, .15, "sin",   vol=0.30, env="adsr"),
        "ok2"       : _snd(659, .15, "sin",   vol=0.25, env="adsr"),
        "ok3"       : _snd(784, .20, "sin",   vol=0.20, env="adsr"),
        "bad"       : _snd(100, .30, "sq",    vol=0.30, env="decay"),
        "bad2"      : _snd( 80, .40, "sq",    vol=0.22, env="decay"),
        "no_ammo"   : _snd_sweep(400, 80,  .35, "sq",  vol=0.28),
        "level"     : _snd_sweep(440, 880, .45, "sin", vol=0.28),
        "level2"    : _snd(880, .25, "sin",   vol=0.22, env="adsr"),
        "over"      : _snd_sweep(300, 60,  .80, "sq",  vol=0.32),
        "tick"      : _snd(800, .04, "sin",   vol=0.08, env="decay"),
        "sink_ok"   : _snd_sweep(200, 50,  .55, "noise", vol=0.22),
        "sink_bad"  : _snd(140, .25, "noise", vol=0.25, env="punch"),
        "menu_blip" : _snd(440, .08, "sin",   vol=0.15, env="decay"),
        "record"    : _snd_sweep(523, 1046, .6, "sin", vol=0.30),
    }

    def play(k):
        snd = SND.get(k)
        if not snd:
            return
        vol = settings["sfx_vol"]
        if k in ("shoot", "shoot_air"):
            CH_SHOOT.set_volume(vol)
            CH_SHOOT.play(snd)
        elif k in ("hit", "splash", "sink_ok", "sink_bad"):
            CH_HIT.set_volume(vol)
            CH_HIT.play(snd)
        elif k in ("ok","ok2","ok3","bad","bad2","no_ammo","level","level2","over","record"):
            CH_RESULT.set_volume(vol)
            CH_RESULT.play(snd)
        else:
            CH_UI.set_volume(vol)
            CH_UI.play(snd)

    def play_chord_ok():
        play("ok")
        pygame.time.set_timer(pygame.USEREVENT + 1, 110, 1)
        pygame.time.set_timer(pygame.USEREVENT + 2, 220, 1)

    def play_levelup_fanfare():
        play("level")
        pygame.time.set_timer(pygame.USEREVENT + 3, 460, 1)

    SOUND_EVENTS = {
        pygame.USEREVENT + 1: "ok2",
        pygame.USEREVENT + 2: "ok3",
        pygame.USEREVENT + 3: "level2",
    }

except Exception as e:
    print(f"[sonido] numpy no disponible, usando stubs: {e}")
    def play(k): pass
    def play_chord_ok(): pass
    def play_levelup_fanfare(): pass
    SOUND_EVENTS = {}

def update_volumes():
    try:
        pygame.mixer.music.set_volume(settings["music_vol"])
    except:
        pass

# ─── SPRITES ─────────────────────────────────────────────────
def load_sprite(name, size=None):
    path = os.path.join(ASSET_DIR, name + ".png")
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            return img
        except:
            pass
    return None

def make_cannon_base():
    surf = pygame.Surface((64, 50), pygame.SRCALPHA)
    for rx in (10, 50):
        pygame.draw.circle(surf, C["brown"],  (rx, 42), 12)
        pygame.draw.circle(surf, C["brown2"], (rx, 42),  8)
        pygame.draw.circle(surf, C["black"],  (rx, 42), 12, 2)
    pts = [(4,18),(60,18),(55,40),(9,40)]
    pygame.draw.polygon(surf, C["gray2"], pts)
    pygame.draw.polygon(surf, C["black"], pts, 2)
    return surf

def make_cannon_barrel():
    surf = pygame.Surface((90, 22), pygame.SRCALPHA)
    pygame.draw.rect(surf, C["gray2"], (0,  4, 82, 14))
    pygame.draw.rect(surf, C["gray"],  (0,  6, 80, 10))
    pygame.draw.rect(surf, C["black"], (0,  4, 82, 14), 2)
    pygame.draw.ellipse(surf, C["gray2"], (78, 0, 12, 22))
    pygame.draw.ellipse(surf, C["black"], (78, 0, 12, 22), 2)
    return surf

SHIP_COLS = [
    (C["teal"],   ( 20,145,135)),
    (C["purple"], ( 90, 38,148)),
    (C["orange"], (185,108, 28)),
]

def make_ship_surf(idx):
    sw, sh = 170, 75
    surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
    col, dark = SHIP_COLS[idx % len(SHIP_COLS)]
    pygame.draw.ellipse(surf, (*C["water_deep"], 80), (10, sh-12, sw-20, 14))
    hull = [(0, 28),(sw, 28),(sw-12, sh),(12, sh)]
    pygame.draw.polygon(surf, dark, hull)
    pygame.draw.polygon(surf, C["black"], hull, 2)
    deck = [(14, 4),(sw-14, 4),(sw, 28),(0, 28)]
    pygame.draw.polygon(surf, col, deck)
    pygame.draw.polygon(surf, C["black"], deck, 2)
    for wx in range(22, sw-22, 28):
        pygame.draw.rect(surf, C["yellow"], (wx, 10, 14, 10))
        pygame.draw.rect(surf, C["black"],  (wx, 10, 14, 10), 1)
    cx = sw//2
    pygame.draw.rect(surf, C["gray2"], (cx-7, -14, 14, 20))
    pygame.draw.rect(surf, C["black"], (cx-7, -14, 14, 20), 2)
    return surf

def make_ball_surf():
    surf = pygame.Surface((18, 18), pygame.SRCALPHA)
    pygame.draw.circle(surf, C["black"], (9, 9), 8)
    pygame.draw.circle(surf, C["gray"],  (6, 6), 3)
    return surf

def make_cloud_surf():
    surf = pygame.Surface((130, 55), pygame.SRCALPHA)
    for cx, cy, r in [(30,35,22),(60,25,30),(95,32,24),(115,38,18)]:
        pygame.draw.circle(surf, (220,230,255,180), (cx, cy), r)
    return surf

# ─── ESTRELLA (decorativa para ranking) ──────────────────────
def make_star_surf(color, size=20):
    surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    pts = []
    for i in range(10):
        angle = math.pi/2 + i * math.pi/5
        r = size if i%2==0 else size*0.45
        pts.append((size + r*math.cos(angle), size - r*math.sin(angle)))
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, C["black"], pts, 1)
    return surf

SPR = {}
SPR["cannon_base"]   = load_sprite("cannon_base",   (64, 50)) or make_cannon_base()
SPR["cannon_barrel"] = load_sprite("cannon_barrel",  (90, 22)) or make_cannon_barrel()
SPR["ball"]          = load_sprite("cannonball",     (18, 18)) or make_ball_surf()
SPR["cloud"]         = load_sprite("cloud",          (130,55)) or make_cloud_surf()
SPR["star_gold"]     = make_star_surf(C["gold"],   14)
SPR["star_silver"]   = make_star_surf(C["silver"], 12)
SPR["star_bronze"]   = make_star_surf(C["bronze"], 11)
for i in range(3):
    SPR[f"ship_{i}"] = load_sprite(f"ship_{i}", (170, 75)) or make_ship_surf(i)

# ─── PREGUNTAS ───────────────────────────────────────────────
QUESTIONS = {
    "Capitales": [
        ("Capital de Argentina",        "Buenos Aires",        ["Lima","Bogotá"],               1),
        ("Capital de Brasil",           "Brasilia",            ["Santiago","Quito"],             1),
        ("Capital de Chile",            "Santiago",            ["Lima","Brasilia"],              1),
        ("Capital de Perú",             "Lima",                ["Bogotá","Montevideo"],          1),
        ("Capital de Uruguay",          "Montevideo",          ["Buenos Aires","Asunción"],      1),
        ("Capital de Colombia",         "Bogotá",              ["Medellín","Cali"],              1),
        ("Capital de Venezuela",        "Caracas",             ["Maracaibo","Valencia"],         1),
        ("Capital de Bolivia",          "Sucre",               ["La Paz","Cochabamba"],          2),
        ("Capital de Paraguay",         "Asunción",            ["Encarnación","Pedro Juan"],     1),
        ("Capital de Ecuador",          "Quito",               ["Guayaquil","Cuenca"],           1),
        ("Capital de Francia",          "París",               ["Lyon","Marsella"],              1),
        ("Capital de Alemania",         "Berlín",              ["Múnich","Hamburgo"],            1),
        ("Capital de Italia",           "Roma",                ["Milán","Nápoles"],              1),
        ("Capital de España",           "Madrid",              ["Barcelona","Sevilla"],          1),
        ("Capital de Australia",        "Canberra",            ["Sídney","Melbourne"],           2),
        ("Capital de Canadá",           "Ottawa",              ["Toronto","Vancouver"],          2),
        ("Capital de Japón",            "Tokio",               ["Osaka","Kioto"],               1),
        ("Capital de China",            "Pekín",               ["Shanghái","Hong Kong"],         1),
        ("Capital de Egipto",           "El Cairo",            ["Alejandría","Giza"],            1),
        ("Capital de Sudáfrica",        "Pretoria",            ["Johannesburgo","Durban"],       2),
        ("Capital de Nigeria",          "Abuya",               ["Lagos","Ibadán"],               2),
        ("Capital de Kazajistán",       "Astana",              ["Almaty","Shymkent"],            3),
        ("Capital de Myanmar",          "Naipyidó",            ["Rangún","Mandalay"],            3),
        ("Capital de Sri Lanka",        "Sri Jayawardenepura", ["Colombo","Kandy"],              3),
    ],
    "Geografía": [
        ("¿Río más largo del mundo?",            "Nilo",       ["Amazonas","Yangtsé"],          2),
        ("¿Océano más grande?",                  "Pacífico",   ["Atlántico","Índico"],           1),
        ("¿Desierto más grande del mundo?",      "Sahara",     ["Gobi","Atacama"],               1),
        ("¿Montaña más alta del mundo?",         "Everest",    ["K2","Aconcagua"],               1),
        ("¿Lago más grande del mundo?",          "Mar Caspio", ["Superior","Victoria"],          2),
        ("¿País más grande del mundo?",          "Rusia",      ["Canadá","China"],               1),
        ("¿País más pequeño del mundo?",         "Vaticano",   ["Mónaco","San Marino"],          2),
        ("Pirámides de Guiza: ¿en qué país?",    "Egipto",     ["Iraq","Irán"],                  1),
        ("¿Sahara: en qué continente?",          "África",     ["Asia","América"],               1),
        ("¿Cordillera más larga del mundo?",     "Andes",      ["Himalaya","Alpes"],             2),
        ("¿Río más largo de Europa?",            "Volga",      ["Danubio","Rin"],                2),
        ("¿País con más habitantes en 2024?",    "India",      ["China","EE.UU."],               2),
        ("Atlántico-Mediterráneo: ¿qué estrecho?","Gibraltar", ["Magallanes","Bósforo"],         2),
        ("¿En qué país está el Kilimanjaro?",    "Tanzania",   ["Kenia","Uganda"],               2),
        ("¿Qué país tiene más islas?",           "Suecia",     ["Filipinas","Indonesia"],        3),
    ],
    "Historia": [
        ("¿Año en que Colón llegó a América?",    "1492",      ["1498","1510"],                  1),
        ("¿Quién construyó Machu Picchu?",        "Incas",     ["Mayas","Aztecas"],              1),
        ("¿Año fin de la 2ª Guerra Mundial?",     "1945",      ["1939","1918"],                  1),
        ("¿Primer presidente de EE.UU.?",         "Washington",["Jefferson","Lincoln"],          1),
        ("¿En qué continente surgió el humano?",  "África",    ["Asia","Europa"],                2),
        ("¿Quién pintó la Mona Lisa?",            "Da Vinci",  ["Miguel Ángel","Rafael"],        1),
        ("¿Año de la Revolución Rusa?",           "1917",      ["1905","1924"],                  2),
        ("¿Año caída del Muro de Berlín?",        "1989",      ["1991","1985"],                  2),
        ("¿Primer hombre en pisar la Luna?",      "Armstrong", ["Aldrin","Glenn"],               1),
        ("¿Año Revolución de Mayo (Argentina)?",  "1810",      ["1816","1820"],                  1),
        ("¿Qué civilización construyó Pirámides?","Egipcia",   ["Romana","Griega"],              1),
    ],
}

def _get_pool(max_diff):
    pool = []
    for cat, qs in QUESTIONS.items():
        for q in qs:
            pregunta, correcta, incorrectas, dif = q
            if dif <= max_diff:
                pool.append((cat, pregunta, correcta, incorrectas))
    return pool if pool else _get_pool(max_diff + 1)

def new_round(max_diff):
    pool = _get_pool(max_diff)
    cat, pregunta, correcta, incorrectas = random.choice(pool)
    wrongs = random.sample(incorrectas, min(2, len(incorrectas)))
    opts   = wrongs + [correcta]
    random.shuffle(opts)
    return cat, pregunta, correcta, opts

# ─── PARTÍCULAS ──────────────────────────────────────────────
class Particle:
    __slots__ = ("x","y","vx","vy","life","decay","sz","color")
    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        self.vx = random.uniform(-130, 130)
        self.vy = random.uniform(-210, -50)
        self.life  = 1.0
        self.decay = random.uniform(1.4, 2.8)
        self.sz    = random.randint(3, 8)
        self.color = color
    def update(self, dt):
        self.vy  += 320 * dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt
        self.life -= self.decay * dt
        return self.life > 0
    def draw(self, surf):
        s = max(1, int(self.sz * self.life))
        pygame.draw.rect(surf, self.color,
            (int(self.x)-s//2, int(self.y)-s//2, s, s))

class WaterParticle:
    __slots__ = ("x","y","vx","vy","life","r")
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx = random.uniform(-80, 80)
        self.vy = random.uniform(-150, -20)
        self.life = 1.0
        self.r = random.randint(4, 10)
    def update(self, dt):
        self.vy  += 200 * dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt
        self.life -= 1.8 * dt
        return self.life > 0
    def draw(self, surf):
        r = max(1, int(self.r * self.life))
        a = int(self.life * 180)
        tmp = pygame.Surface((r*2+1, r*2+1), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (*C["water_lite"], a), (r, r), r)
        surf.blit(tmp, (int(self.x)-r, int(self.y)-r))

class FloatText:
    __slots__ = ("x","y","vy","text","color","size","life")
    def __init__(self, x, y, text, color, size=26):
        self.x, self.y = float(x), float(y)
        self.vy   = -65.0
        self.text = text
        self.color= color
        self.size = size
        self.life = 1.0
    def update(self, dt):
        self.y   += self.vy * dt
        self.life -= 1.1 * dt
        return self.life > 0
    def draw(self, surf):
        img = _font(self.size).render(self.text, True, self.color)
        img.set_alpha(max(0, int(self.life * 255)))
        surf.blit(img, (int(self.x) - img.get_width()//2, int(self.y)))

particles   = []
float_texts = []

def explode(x, y, color, n=22):
    for _ in range(n): particles.append(Particle(x, y, color))

def water_splash(x, y, n=18):
    for _ in range(n): particles.append(WaterParticle(x, y))

def sparks(x, y):
    for _ in range(8): particles.append(Particle(x, y, C["yellow"]))

# ─── NUBES ───────────────────────────────────────────────────
class Cloud:
    def __init__(self, x=None):
        self.y     = random.randint(30, H//3 - 20)
        self.x     = float(x if x is not None else random.randint(0, W))
        self.speed = random.uniform(12, 30)
        self.scale = random.uniform(0.6, 1.3)
        w = int(130 * self.scale); h_px = int(55 * self.scale)
        self.img   = pygame.transform.smoothscale(SPR["cloud"], (w, h_px))
    def update(self, dt):
        self.x += self.speed * dt
        if self.x > W + 140: self.x = -140
    def draw(self, surf):
        surf.blit(self.img, (int(self.x), self.y))

clouds = [Cloud() for _ in range(7)]

# ─── FONDO ───────────────────────────────────────────────────
_sky_surf = pygame.Surface((W, H))
_SKY_H    = int(H * 0.55)

def _bake_sky():
    for y in range(_SKY_H):
        t = y / _SKY_H
        if t < 0.5:
            r = C["sky_top"]; s = C["sky_mid"]; tt = t / 0.5
        else:
            r = C["sky_mid"]; s = C["sky_bot"]; tt = (t-0.5)/0.5
        col = tuple(int(r[i] + (s[i]-r[i])*tt) for i in range(3))
        pygame.draw.line(_sky_surf, col, (0, y), (W, y))
    pygame.draw.rect(_sky_surf, C["horiz"],      (0, _SKY_H-2, W, 4))
    pygame.draw.rect(_sky_surf, C["ground"],     (0, _SKY_H-4, 220, H-_SKY_H+4))
    pygame.draw.rect(_sky_surf, C["ground2"],    (0, _SKY_H+10, 220, H))
    pygame.draw.rect(_sky_surf, C["water_deep"], (0, _SKY_H+2, W, H))

_bake_sky()

def draw_bg(surf, t):
    surf.blit(_sky_surf, (0, 0))
    for c in clouds:
        c.update(1/60)
        c.draw(surf)
    water_y = _SKY_H + 2
    for layer in range(5):
        phase = t * (0.8 + layer*0.25) + layer*1.1
        for x in range(0, W, 8):
            wy  = water_y + layer*14 + int(math.sin(x*0.04+phase)*5)
            h_b = 10 - layer
            col = C["water_lite"] if layer==0 else C["water_mid"]
            pygame.draw.rect(surf, col, (x, wy, 7, h_b))
    for x in range(220, W, 22):
        fx = x + int(math.sin(t*1.5+x*0.02)*6)
        pygame.draw.ellipse(surf, C["water_foam"], (fx, water_y, 14, 5))
    refl_x = W - 100
    for i in range(8):
        ry = water_y + 10 + i*9
        rw = max(2, 60 - i*7 + int(math.sin(t*2+i)*4))
        pygame.draw.rect(surf, C["reflect"], (refl_x-rw//2, ry, rw, 5))
    pygame.draw.rect(surf, C["yellow"],  (W-120, 28, 44, 44))
    pygame.draw.rect(surf, C["sky_top"], (W-100, 22, 28, 28))
    pygame.draw.rect(surf, C["black"],   (W-120, 28, 44, 44), 2)

# ─── CAÑÓN ───────────────────────────────────────────────────
CANNON_X = 112
CANNON_Y = _SKY_H + 2

class Cannon:
    def __init__(self):
        self.angle_deg = 0.0
        self.recoil    = 0.0
        self._base   = SPR["cannon_base"]
        self._barrel = SPR["cannon_barrel"]
        self._bw = self._barrel.get_width()
        self._bh = self._barrel.get_height()

    def update(self, dt, mx, my):
        dx = mx - CANNON_X
        dy = my - CANNON_Y
        raw = math.degrees(math.atan2(-dy, dx))
        self.angle_deg = max(-70.0, min(70.0, raw))
        if self.recoil > 0:
            self.recoil = max(0.0, self.recoil - dt*5)

    def muzzle_world(self):
        length = (self._bw - 5) * (1 - self.recoil*0.2)
        rad = math.radians(self.angle_deg)
        return (CANNON_X + math.cos(rad)*length,
                CANNON_Y - math.sin(rad)*length)

    def shoot(self):
        self.recoil = 1.0

    def draw(self, surf):
        rad = math.radians(self.angle_deg)
        recoil_px = self.recoil * 14
        rotated = pygame.transform.rotate(self._barrel, self.angle_deg)
        orig_pivot = pygame.math.Vector2(0, self._bh//2)
        offset = pygame.math.Vector2(self._bw/2, self._bh/2) - orig_pivot
        rot_offset = offset.rotate(-self.angle_deg)
        rot_center = (CANNON_X + rot_offset.x - math.cos(rad)*recoil_px,
                      CANNON_Y + rot_offset.y + math.sin(rad)*recoil_px)
        rect = rotated.get_rect(center=rot_center)
        surf.blit(rotated, rect)
        bx = CANNON_X - self._base.get_width()//2
        by = CANNON_Y - self._base.get_height() + 18
        surf.blit(self._base, (bx, by))

cannon = Cannon()

# ─── BARCO ───────────────────────────────────────────────────
SHIP_W, SHIP_H = 170, 75
SHIP_SLOTS = [175, 460, 750]

class Ship:
    def __init__(self, slot_idx, text, is_correct, max_life):
        self.base_x    = float(SHIP_SLOTS[slot_idx])
        self.base_y    = float(_SKY_H + 30)
        self.w, self.h = SHIP_W, SHIP_H
        self.text      = text
        self.is_correct= is_correct
        self.max_life  = max_life
        self.life      = max_life
        self.img       = SPR[f"ship_{slot_idx}"]
        self.bob_off   = random.uniform(0, math.pi*2)
        self.flash     = 0.0
        self._flash_surf = pygame.Surface((SHIP_W, SHIP_H), pygame.SRCALPHA)
        self._flash_surf.fill((255,255,255,160))

    @property
    def rect(self):
        return pygame.Rect(int(self.base_x),
                           int(self.base_y + self._bob()),
                           self.w, self.h)

    def _bob(self):
        return math.sin(pygame.time.get_ticks()/1000*1.4 + self.bob_off) * 5

    def draw(self, surf):
        rx = int(self.base_x)
        ry = int(self.base_y + self._bob())
        pygame.draw.ellipse(surf, C["water_deep"],
            (rx+10, ry+self.h-8, self.w-20, 14))
        surf.blit(self.img, (rx, ry))
        if self.flash > 0:
            self._flash_surf.set_alpha(int(self.flash*200))
            surf.blit(self._flash_surf, (rx, ry))
            self.flash = max(0.0, self.flash - 1/60*6)
        bx, by = rx+8, ry-22
        bw = self.w - 16
        pygame.draw.rect(surf, C["gray2"], (bx, by, bw, 8))
        ratio = self.life / self.max_life
        col   = C["green"] if ratio>.5 else (C["yellow"] if ratio>.25 else C["red"])
        pygame.draw.rect(surf, col, (bx, by, int(bw*ratio), 8))
        pygame.draw.rect(surf, C["black"], (bx, by, bw, 8), 1)
        words = self.text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur+" "+w).strip()
            tw, _ = FSM.size(test)
            if tw < self.w - 12:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        total_h = len(lines)*18
        start_y = ry + (self.h - total_h)//2
        for i, ln in enumerate(lines[:3]):
            img_ln = FSM.render(ln, True, C["white"])
            shadow = FSM.render(ln, True, C["black"])
            sx = rx + self.w//2 - img_ln.get_width()//2
            sy = start_y + i*18
            surf.blit(shadow, (sx+1, sy+1))
            surf.blit(img_ln, (sx,   sy))

    def hit(self):
        self.life -= 1
        self.flash  = 1.0
        return self.life <= 0

# ─── PROYECTIL ───────────────────────────────────────────────
class Projectile:
    GRAVITY = 520
    def __init__(self, x, y, vx, vy):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.trail = []
        self.img   = SPR["ball"]
        self._tick_timer = 0.0

    def update(self, dt):
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 14: self.trail.pop(0)
        self.vy += self.GRAVITY * dt
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self._tick_timer += dt
        if self._tick_timer >= 0.25:
            self._tick_timer = 0.0
            play("tick")

    @property
    def rect(self):
        return pygame.Rect(int(self.x)-9, int(self.y)-9, 18, 18)

    def draw(self, surf):
        for i, pos in enumerate(self.trail):
            r = max(1, int(5*i/len(self.trail)))
            a = int(180*i/len(self.trail))
            tmp = pygame.Surface((r*2+1, r*2+1), pygame.SRCALPHA)
            pygame.draw.circle(tmp, (*C["yellow"], a), (r, r), r)
            surf.blit(tmp, (pos[0]-r, pos[1]-r))
        surf.blit(self.img, (int(self.x)-9, int(self.y)-9))

# ─── HUD ─────────────────────────────────────────────────────
def draw_hud(score, lives, level, cat, ammo):
    pygame.draw.rect(screen, (8,10,28), (0, 0, W, 56))
    pygame.draw.rect(screen, C["yellow"], (0, 56, W, 3))
    screen.blit(FMD.render(f"PUNTOS: {score:05d}", True, C["yellow"]), (14, 10))
    screen.blit(FMD.render(f"NIVEL {level}",       True, C["teal"]),   (290, 10))
    screen.blit(FSM.render(f"[{cat}]",             True, C["gray"]),   (410, 17))
    hx = W - 210
    screen.blit(FMD.render("VIDAS:", True, C["white"]), (hx, 10))
    for i in range(lives):
        pygame.draw.rect(screen, C["red"],  (hx+90+i*28, 12, 20, 20))
        pygame.draw.rect(screen, C["red2"], (hx+92+i*28, 13,  8,  8))
        pygame.draw.rect(screen, C["black"],(hx+90+i*28, 12, 20, 20), 2)
    ammo_str = "■"*ammo + "□"*max(0, 5-ammo)
    screen.blit(FSM.render(f"AMMO {ammo_str}", True, C["orange"]), (14, H-24))
    # Barra de progreso de nivel
    prog_x, prog_y = W//2 - 80, H - 22
    prog_w = 160
    pygame.draw.rect(screen, C["gray2"], (prog_x, prog_y, prog_w, 12))
    prog_fill = int(prog_w * (correct_in_level / NEED))
    pygame.draw.rect(screen, C["teal"], (prog_x, prog_y, prog_fill, 12))
    pygame.draw.rect(screen, C["black"], (prog_x, prog_y, prog_w, 12), 1)
    prog_lbl = FSM.render(f"NIVEL {correct_in_level}/{NEED}", True, C["white"])
    screen.blit(prog_lbl, (prog_x + prog_w//2 - prog_lbl.get_width()//2, prog_y - 16))

def draw_question(question, cat):
    qy = 62
    pygame.draw.rect(screen, (10,18,48), (0, qy, W, 52))
    pygame.draw.rect(screen, C["teal"],  (0, qy, W, 52), 2)
    screen.blit(FSM.render(f"▶ {cat.upper()}", True, C["teal"]), (12, qy+5))
    qtxt = FMD.render(question, True, C["white"])
    screen.blit(qtxt, (W//2 - qtxt.get_width()//2, qy+22))

# ─── PANTALLA MENÚ ───────────────────────────────────────────
def draw_menu(t, hi):
    draw_bg(screen, t)
    sh = FXL.render("GEO  BATTLE", True, C["black"])
    tl = FXL.render("GEO  BATTLE", True, C["yellow"])
    screen.blit(sh, (W//2 - sh.get_width()//2+4, 104))
    screen.blit(tl, (W//2 - tl.get_width()//2,   100))
    sub = FLG.render("El juego de preguntas sobre geografía", True, C["white"])
    screen.blit(sub, (W//2 - sub.get_width()//2, 168))
    for i, line in enumerate([
        "▶  Apuntá con el mouse y hacé click para disparar",
        "▶  Hundí el barco con la RESPUESTA CORRECTA",
        "▶  Cada nivel los barcos aguantan más impactos",
        "▶  5 aciertos = subís de nivel",
    ]):
        img = FSM.render(line, True, C["gray"])
        screen.blit(img, (W//2 - img.get_width()//2, 255+i*30))
    if int(t*2)%2 == 0:
        btn = FLG.render("[ PRECIONA ESPACIO PARA JUGAR ]", True, C["green"])
        screen.blit(btn, (W//2 - btn.get_width()//2, 400))
    hi_img = FMD.render(f"RECORD: {hi:05d}", True, C["orange"])
    screen.blit(hi_img, (W//2 - hi_img.get_width()//2, 450))

    # Botón clasificación
    rank_rect = pygame.Rect(W//2 - 110, 490, 220, 38)
    pygame.draw.rect(screen, C["gray2"], rank_rect, border_radius=6)
    pygame.draw.rect(screen, C["gold"],  rank_rect, 2, border_radius=6)
    rank_lbl = FSM.render("🏆  VER CLASIFICACIÓN", True, C["gold"])
    screen.blit(rank_lbl, (rank_rect.centerx - rank_lbl.get_width()//2,
                            rank_rect.centery - rank_lbl.get_height()//2))

    # Botón ajustes (esquina)
    gear_rect = pygame.Rect(W-72, 20, 50, 50)
    pygame.draw.circle(screen, C["gray2"], gear_rect.center, 22)
    pygame.draw.circle(screen, C["black"], gear_rect.center, 22, 3)
    gear_lbl = FLG.render("⚙", True, C["white"])
    screen.blit(gear_lbl, (gear_rect.centerx - gear_lbl.get_width()//2,
                            gear_rect.centery - gear_lbl.get_height()//2))
    return gear_rect, rank_rect

# ─── PANTALLA CLASIFICACIÓN ───────────────────────────────────
def draw_leaderboard(t):
    draw_bg(screen, t)

    # Fondo panel
    panel = pygame.Surface((700, 480), pygame.SRCALPHA)
    panel.fill((8, 12, 40, 220))
    screen.blit(panel, (W//2 - 350, 80))
    pygame.draw.rect(screen, C["gold"], (W//2-350, 80, 700, 480), 3, border_radius=8)

    # Título
    title = FXL.render("🏆  CLASIFICACIÓN", True, C["gold"])
    screen.blit(title, (W//2 - title.get_width()//2, 92))
    pygame.draw.line(screen, C["gold"], (W//2-320, 148), (W//2+320, 148), 2)

    if not highscores:
        msg = FLG.render("¡Todavía no hay registros!", True, C["gray"])
        screen.blit(msg, (W//2 - msg.get_width()//2, 280))
        msg2 = FSM.render("Jugá y aparecé en el ranking", True, C["teal"])
        screen.blit(msg2, (W//2 - msg2.get_width()//2, 330))
    else:
        headers = ["#", "NOMBRE", "PUNTAJE"]
        hx = [W//2 - 280, W//2 - 130, W//2 + 130]
        for hh, hpos in zip(headers, hx):
            hlbl = FSM.render(hh, True, C["teal"])
            screen.blit(hlbl, (hpos - hlbl.get_width()//2, 156))
        pygame.draw.line(screen, C["gray2"], (W//2-310, 178), (W//2+310, 178), 1)

        medal_stars = [SPR["star_gold"], SPR["star_silver"], SPR["star_bronze"]]
        row_cols = [C["gold"], C["silver"], C["bronze"]]

        for i, entry in enumerate(highscores[:10]):
            name  = entry.get("name", "???")
            pscore = entry.get("score", 0)
            ry    = 184 + i*28

            # Fila alterna
            if i % 2 == 0:
                row_surf = pygame.Surface((620, 26), pygame.SRCALPHA)
                row_surf.fill((255,255,255,12))
                screen.blit(row_surf, (W//2-310, ry))

            col = row_cols[i] if i < 3 else C["white"]

            # Medalla/estrella para top 3
            if i < 3:
                star = medal_stars[i]
                screen.blit(star, (hx[0] - 12 - star.get_width()//2, ry + 3))

            rank_lbl = FMD.render(str(i+1), True, col)
            name_lbl = FMD.render(name[:14], True, col)
            scr_lbl  = FMD.render(f"{pscore:05d}", True, col)
            screen.blit(rank_lbl, (hx[0] - rank_lbl.get_width()//2, ry))
            screen.blit(name_lbl, (hx[1] - name_lbl.get_width()//2, ry))
            screen.blit(scr_lbl,  (hx[2] - scr_lbl.get_width()//2,  ry))

    back = FSM.render("[ ESC = Volver ]", True, C["gray"])
    screen.blit(back, (W//2 - back.get_width()//2, 530))

# ─── PANTALLA GAME OVER ───────────────────────────────────────
def draw_gameover(score, hi, t):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0,0,0,190))
    screen.blit(ov, (0,0))
    screen.blit(FXL.render("GAME  OVER", True, C["red"]),
        (W//2 - FXL.size("GAME  OVER")[0]//2, 160))
    screen.blit(FLG.render(f"PUNTAJE: {score:05d}", True, C["yellow"]),
        (W//2 - FLG.size(f"PUNTAJE: {score:05d}")[0]//2, 255))
    screen.blit(FLG.render(f"RECORD:  {hi:05d}", True, C["orange"]),
        (W//2 - FLG.size(f"RECORD:  {hi:05d}")[0]//2, 305))
    if int(t*2)%2 == 0:
        msg = FLG.render("[PRECIONA ESPACIO PARA VOLVER AL MENÚ]", True, C["white"])
        screen.blit(msg, (W//2 - msg.get_width()//2, 400))
    # Mostrar posición en ranking si está
    for idx, entry in enumerate(highscores[:10]):
        if entry.get("score",0) == score:
            pos_msg = FSM.render(f"¡Quedaste en el puesto #{idx+1} del ranking!", True, C["teal"])
            screen.blit(pos_msg, (W//2 - pos_msg.get_width()//2, 460))
            break

# ─── PANTALLA AJUSTES ────────────────────────────────────────
def draw_settings(t):
    draw_bg(screen, t)
    title = FXL.render("AJUSTES", True, C["yellow"])
    screen.blit(title, (W//2 - title.get_width()//2, 80))

    y = 200
    screen.blit(FLG.render("Música", True, C["white"]), (250, y))
    vol = int(settings["music_vol"] * 100)
    pygame.draw.rect(screen, C["gray2"], (450, y+10, 300, 20))
    pygame.draw.rect(screen, C["teal"],  (450, y+10, 3*vol, 20))
    pygame.draw.rect(screen, C["black"], (450, y+10, 300, 20), 2)
    screen.blit(FSM.render(f"{vol}%", True, C["white"]), (780, y+8))

    y = 280
    screen.blit(FLG.render("Efectos", True, C["white"]), (250, y))
    vol = int(settings["sfx_vol"] * 100)
    pygame.draw.rect(screen, C["gray2"],   (450, y+10, 300, 20))
    pygame.draw.rect(screen, C["orange"],  (450, y+10, 3*vol, 20))
    pygame.draw.rect(screen, C["black"],   (450, y+10, 300, 20), 2)
    screen.blit(FSM.render(f"{vol}%", True, C["white"]), (780, y+8))

    screen.blit(FLG.render("[ ESC = Volver ]", True, C["gray"]),
                (W//2 - 140, 480))

# ─── PANTALLA INGRESO DE NOMBRE ──────────────────────────────
def draw_name_input(score, player_name):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0,0,0,200))
    screen.blit(ov, (0,0))

    title = FXX.render("¡NUEVO RECORD!", True, C["gold"])
    screen.blit(title, (W//2 - title.get_width()//2, 110))
    # Estrellas decorativas alrededor del título
    for sx, sy in [(W//2-240, 120),(W//2+200, 120),(W//2-260, 160),(W//2+220, 160)]:
        screen.blit(SPR["star_gold"], (sx, sy))

    sc_lbl = FLG.render(f"Puntaje: {score:05d}", True, C["yellow"])
    screen.blit(sc_lbl, (W//2 - sc_lbl.get_width()//2, 215))

    screen.blit(FSM.render("Ingresá tu nombre (máx. 12 caracteres):", True, C["white"]),
                (W//2 - 195, 295))

    # Cuadro de texto
    pygame.draw.rect(screen, C["gray2"], (W//2-160, 330, 320, 54), border_radius=8)
    pygame.draw.rect(screen, C["gold"],  (W//2-160, 330, 320, 54), 3, border_radius=8)
    blink = "_" if int(pygame.time.get_ticks()/500)%2==0 else " "
    name_surf = FLG.render(player_name + blink, True, C["white"])
    screen.blit(name_surf, (W//2 - name_surf.get_width()//2, 342))

    screen.blit(FSM.render("[ ENTER = Guardar ]", True, C["teal"]),
                (W//2 - 100, 410))

# ─── PANTALLA NIVEL SUPERADO ─────────────────────────────────
def draw_levelup(level, t):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0,0,0,180))
    screen.blit(ov, (0,0))
    screen.blit(FXL.render("¡NIVEL SUPERADO!", True, C["green"]),
        (W//2 - FXL.size("¡NIVEL SUPERADO!")[0]//2, 140))
    screen.blit(FLG.render(f"SUBISTE AL NIVEL {level}", True, C["yellow"]),
        (W//2 - FLG.size(f"SUBISTE AL NIVEL {level}")[0]//2, 240))
    screen.blit(FSM.render("Los barcos ahora aguantan más impactos", True, C["gray"]),
        (W//2 - FSM.size("Los barcos ahora aguantan más impactos")[0]//2, 295))
    if int(t*2)%2 == 0:
        screen.blit(FMD.render("[ PRECIONA ESPACIO PARA CONTINUAR ]", True, C["white"]),
            (W//2 - FMD.size("[ PRECIONA ESPACIO PARA CONTINUAR ]")[0]//2, 370))

# ─── ESTADOS ─────────────────────────────────────────────────
MENU, PLAYING, LEVELUP, OVER, SETTINGS, NAME_INPUT, LEADERBOARD = \
    "menu","playing","levelup","over","settings","name_input","leaderboard"

state            = MENU
score            = 0
lives            = 3
level            = 1
ammo             = 5
t                = 0.0
correct_in_level = 0
NEED             = 5
lv_timer         = 0.0

cat = question = correct = ""
options: list[str] = []
ships: list[Ship]  = []
proj: Projectile | None = None
player_name = ""
_is_new_record = False

def start_game():
    global score, lives, level, ammo, correct_in_level, proj
    score = 0; lives = 3; level = 1; ammo = 5
    correct_in_level = 0
    proj = None
    new_round_state()

def new_round_state():
    global cat, question, correct, options, ships, ammo, proj
    cat, question, correct, options = new_round(level)
    ships = [Ship(i, opt, opt==correct, min(1 + level//2, 6))
             for i, opt in enumerate(options)]
    ammo = 5
    proj = None

# ── Música inicial ──
update_volumes()
play_music("menu.mp3")

# ─── LOOP PRINCIPAL ──────────────────────────────────────────
running = True

while running:
    dt = min(clock.tick(60)/1000, 0.05)
    t += dt

    mx, my = pygame.mouse.get_pos()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        # Sonidos encadenados (timers)
        if ev.type in SOUND_EVENTS:
            play(SOUND_EVENTS[ev.type])

        # ── Teclado ──
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                if state == PLAYING:
                    state = MENU
                    play_music("menu.mp3")
                elif state in (SETTINGS, NAME_INPUT, LEADERBOARD):
                    state = MENU
                else:
                    running = False

            # Ingreso de nombre
            if state == NAME_INPUT:
                if ev.key == pygame.K_RETURN:
                    name_clean = player_name.strip()
                    if not name_clean:
                        name_clean = "Anónimo"
                    highscores.append({"name": name_clean[:12], "score": score})
                    highscores.sort(key=lambda x: x["score"], reverse=True)
                    new_hi = max(hi_score, score)
                    save_highscores(highscores, new_hi)
                    hi_score = new_hi
                    state = OVER
                elif ev.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 12 and ev.unicode.isprintable() and ev.unicode != "":
                    player_name += ev.unicode

            # Espacio para acciones principales
            if ev.key == pygame.K_SPACE:
                if state == MENU:
                    start_game()
                    state = PLAYING
                    play_music("juego.mp3")
                elif state == OVER:
                    state = MENU
                    play_music("menu.mp3")
                elif state == LEVELUP:
                    state = PLAYING
                    new_round_state()
                    play_music("juego.mp3")

        # ── Click del mouse ──
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx_c, my_c = ev.pos

            if state == MENU:
                gear_rect, rank_rect = draw_menu(t, hi_score)
                if gear_rect.collidepoint(mx_c, my_c):
                    state = SETTINGS
                elif rank_rect.collidepoint(mx_c, my_c):
                    state = LEADERBOARD
                    play("menu_blip")

            elif state == SETTINGS:
                if 450 <= mx_c <= 750:
                    if 210 <= my_c <= 230:
                        settings["music_vol"] = max(0.0, min(1.0, (mx_c - 450) / 300))
                        update_volumes()
                        save_settings(settings)
                    elif 290 <= my_c <= 310:
                        settings["sfx_vol"] = max(0.0, min(1.0, (mx_c - 450) / 300))
                        update_volumes()
                        save_settings(settings)

            elif state == PLAYING and proj is None and ammo > 0:
                mx2, my2 = cannon.muzzle_world()
                power = 500 + level * 12
                rad   = math.radians(cannon.angle_deg)
                proj  = Projectile(mx2, my2,
                                   math.cos(rad)*power,
                                  -math.sin(rad)*power)
                ammo -= 1
                cannon.shoot()
                play("shoot")
                SOUND_EVENTS[pygame.USEREVENT + 10] = "shoot_air"
                pygame.time.set_timer(pygame.USEREVENT + 10, 60, 1)
                sparks(mx2, my2)

    # ── Lógica de juego ──
    if state == PLAYING:
        cannon.update(dt, mx, my)

        if proj:
            proj.update(dt)
            hit_happened = False
            for ship in ships[:]:
                if proj.rect.colliderect(ship.rect):
                    hit_happened = True
                    rect = ship.rect
                    cx, cy = rect.centerx, rect.centery
                    if ship.hit():
                        ships.remove(ship)
                        if ship.is_correct:
                            pts = 100 + level * 50
                            score += pts
                            correct_in_level += 1
                            explode(cx, cy, C["green"], 28)
                            water_splash(cx, cy+40)
                            float_texts.append(FloatText(cx, cy-40, f"+{pts}", C["green"]))
                            play_chord_ok()
                            play("sink_ok")
                            if correct_in_level >= NEED:
                                correct_in_level = 0
                                level += 1
                                lv_timer = 3.0
                                state = LEVELUP
                                stop_music()
                                play_levelup_fanfare()
                            else:
                                new_round_state()
                        else:
                            lives  -= 1
                            score   = max(0, score - 30)
                            explode(cx, cy, C["red"], 22)
                            water_splash(cx, cy+40, 12)
                            float_texts.append(
                                FloatText(cx, cy-40, "INCORRECTO  -30", C["red"], 22))
                            play("bad")
                            play("sink_bad")
                            if lives <= 0:
                                # Fin de juego
                                hi_score = max(hi_score, score)
                                play("over")
                                stop_music()
                                # ¿Es nuevo record?
                                _is_new_record = (
                                    len(highscores) < 10 or
                                    score > (highscores[-1].get("score",0) if highscores else 0)
                                ) and score > 0
                                if _is_new_record:
                                    player_name = ""
                                    state = NAME_INPUT
                                    play("record")
                                else:
                                    save_highscores(highscores, hi_score)
                                    state = OVER
                            else:
                                new_round_state()
                    else:
                        explode(cx, cy, C["orange"], 10)
                        play("hit")
                        play("splash")
                        float_texts.append(FloatText(cx, cy-30, "HIT!", C["yellow"], 22))
                    proj = None
                    break

            if not hit_happened and proj is not None:
                if proj.y > H+60 or proj.x > W+60 or proj.x < -60:
                    proj = None

        # Sin munición y todavía hay barco correcto
        if proj is None and ammo <= 0 and state == PLAYING:
            if any(s.is_correct for s in ships):
                lives -= 1
                float_texts.append(FloatText(W//2, H//2-60,
                    "¡SIN MUNICIÓN!  -1 VIDA", C["red"], 26))
                play("no_ammo")
                if lives <= 0:
                    hi_score = max(hi_score, score)
                    play("over")
                    stop_music()
                    _is_new_record = (
                        len(highscores) < 10 or
                        score > (highscores[-1].get("score",0) if highscores else 0)
                    ) and score > 0
                    if _is_new_record:
                        player_name = ""
                        state = NAME_INPUT
                        play("record")
                    else:
                        save_highscores(highscores, hi_score)
                        state = OVER
                else:
                    new_round_state()

        particles[:]   = [p for p in particles   if p.update(dt)]
        float_texts[:] = [f for f in float_texts if f.update(dt)]

    elif state == LEVELUP:
        lv_timer -= dt
        particles[:]   = [p for p in particles   if p.update(dt)]
        float_texts[:] = [f for f in float_texts if f.update(dt)]
        if lv_timer <= 0:
            state = PLAYING
            new_round_state()
            play_music("juego.mp3")

    # ── Dibujo ──
    draw_bg(screen, t)

    if state == MENU:
        gear_rect, rank_rect = draw_menu(t, hi_score)
    elif state == SETTINGS:
        draw_settings(t)
    elif state == LEADERBOARD:
        draw_leaderboard(t)
    elif state == NAME_INPUT:
        draw_name_input(score, player_name)
    elif state == LEVELUP:
        draw_levelup(level, t)
        for p in particles: p.draw(screen)
        for ft in float_texts: ft.draw(screen)
    elif state == OVER:
        draw_gameover(score, hi_score, t)
    else:  # PLAYING
        for ship in ships: ship.draw(screen)
        cannon.draw(screen)
        if proj: proj.draw(screen)
        for p in particles: p.draw(screen)
        for ft in float_texts: ft.draw(screen)
        draw_hud(score, lives, level, cat, ammo)
        draw_question(question, cat)

    pygame.display.flip()

save_highscores(highscores, hi_score)
pygame.quit()
sys.exit()