import pygame
import sys
import random
import math
import array
import os
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))
# ====================== RESOLVER RUTA (PyInstaller) ======================
def resolver_ruta(ruta_relativa):
    """ Obtiene la ruta absoluta de los recursos, compatible con PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)
# =========================================================================

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

ANCHO_JUEGO = 1200
ALTO_JUEGO  = 700
ANCHO = ANCHO_JUEGO
ALTO  = ALTO_JUEGO

pantalla_real     = pygame.display.set_mode((ANCHO_JUEGO, ALTO_JUEGO))
pantalla          = pygame.Surface((ANCHO_JUEGO, ALTO_JUEGO))
pantalla_completa = False
pygame.display.set_caption("Historia Platformer")

reloj = pygame.time.Clock()
FPS   = 60

BLANCO            = (255, 255, 255)
NEGRO             = (15,  10,  25)
GRIS_OSCURO       = (40,  40,  50)
GRIS_CLARO        = (220, 225, 235)
GRIS_BOTON        = (180, 190, 200)
FONDO_MENU_TOP    = (26,  0,   51)
FONDO_MENU_BOTTOM = (0,   26,  51)
BTN_AZUL_NEON     = (0,   150, 255)
BTN_HOVER_MAGENTA = (255, 0,   128)
COLOR_FACIL       = (46,  204, 113)
COLOR_NORMAL      = (241, 196,  15)
COLOR_DIFICIL     = (231,  76,  60)
COLOR_INFINITO    = (155,  89, 182)
AZUL_PLAT         = (52,  152, 219)
AZUL_PLAT_OSC     = (41,  128, 185)
VERDE_SUELO       = (39,  174,  96)
VERDE_SUELO_OSC   = (30,  132,  73)
PLAT_MOVIL_COLOR  = (155,  89, 182)
PLAT_MOVIL_OSC    = (125,  60, 152)
PLAT_CAE_COLOR    = (230, 126,  34)
PLAT_CAE_OSC      = (211,  84,   0)
NARANJA_LAVA      = (230, 126,  34)
ROJO_LAVA         = (192,  57,  43)
AMARILLO_PER      = (254, 211,  48)
ORO_MONEDA        = (255, 215,   0)
COLOR_ENEMIGO     = (211,  47,  47)
CIELO_TOP         = (12,   8,  40)
CIELO_MID         = (30,  20,  80)
CIELO_BOTTOM      = (60,  30, 100)
COLOR_PU_VEL      = (0,   255, 200)
COLOR_PU_ESCUDO   = (100, 180, 255)
COLOR_PU_VIDA     = (255,  80, 120)
COLOR_BOSS        = (180,  20, 220)
COLOR_BOSS_OSC    = (100,   0, 140)
COLOR_PROYECTIL   = (255, 100,   0)
COLOR_J2          = (255, 120,  40)

fuente        = pygame.font.SysFont("arial", 26, bold=True)
fuente_hud    = pygame.font.SysFont("arial", 22, bold=True)
fuente_grande = pygame.font.SysFont("arial", 55, bold=True)
fuente_titulo = pygame.font.SysFont("arial", 72, bold=True)
fuente_small  = pygame.font.SysFont("arial", 18, bold=True)

class GestorSprites:
    NOMBRES = [
        "jugador_idle", "jugador_walk1", "jugador_walk2",
        "jugador_dash", "jugador_jump",
        "enemigo", "enemigo_lava", "moneda1", "moneda2",
    ]
    
    def __init__(self):
        self.cache = {}
        print("[Sprites] Iniciando carga de sprites...")
        
        for nombre in self.NOMBRES:
            cargado = False
            for ext in [".png", ".jpg", ".jpeg"]:
                # Intentos con diferentes rutas
                rutas_a_probar = [
                    resolver_ruta(f"historia/{nombre}{ext}"),
                    resolver_ruta(f"Historia/{nombre}{ext}"),   # mayúscula
                    resolver_ruta(f"{nombre}{ext}"),            # sin carpeta
                ]
                
                for ruta in rutas_a_probar:
                    if os.path.exists(ruta):
                        try:
                            self.cache[nombre] = pygame.image.load(ruta).convert_alpha()
                            print(f"[Sprites] ✅ Cargado: {nombre}{ext}")
                            cargado = True
                            break
                        except Exception as e:
                            print(f"[Sprites] Error cargando {ruta}: {e}")
                
                if cargado:
                    break
            
            if not cargado:
                print(f"[Sprites] ❌ No se encontró: {nombre}")

    def get(self, nombre, tamaño):
        img = self.cache.get(nombre)
        if img:
            return pygame.transform.scale(img, tamaño)
        else:
            print(f"[Sprites] ⚠️ Sprite no encontrado en cache: {nombre}")
            return None

sprites = GestorSprites()

RANKING_FILE = "ranking.json"

def cargar_ranking():
    if os.path.exists(RANKING_FILE):
        try:
            with open(RANKING_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def guardar_ranking(lista):
    try:
        with open(RANKING_FILE, "w") as f:
            json.dump(lista[:10], f)
    except Exception:
        pass

def agregar_a_ranking(nombre, puntos, modo):
    lista = cargar_ranking()
    lista.append({"nombre": nombre, "puntos": puntos, "modo": modo.upper()})
    lista.sort(key=lambda x: x["puntos"], reverse=True)
    guardar_ranking(lista)
    return lista[:10]

ESTADO_MENU       = "menu"
ESTADO_DIFICULTAD = "dificultad"
ESTADO_JUEGO      = "juego"
ESTADO_PAUSA      = "pausa"
ESTADO_GAMEOVER   = "gameover"
ESTADO_CONFIG     = "config"
ESTADO_RANKING    = "ranking"

estado_actual       = ESTADO_MENU
dificultad_guardada = "normal"

vol_musica_menu    = 0.40
vol_musica_juego   = 0.25
vol_efectos_sfx    = 0.95
musica_actual_clave = ""

MUSICA = {
    "menu":     "Menu.mp3",
    "facil":    "Facil.mp3",
    "normal":   "Medio.mp3",
    "dificil":  "Dificil.mp3",
    "infinito": "Infinito.mp3",
    "reloj":    "Dificil.mp3",
    "2p":       "Medio.mp3",
}

VELOCIDAD              = 9
GRAVEDAD               = 0.8
SALTO                  = -16.5
MAX_SALTOS_PERMITIDOS  = 2
ANCHO_JUGADOR          = 45
ALTO_JUGADOR           = 45
DASH_FUERZA            = 22
DASH_DURACION_FRAMES   = 12
DASH_COOLDOWN_MS       = 1000
LAVA_Y                 = 660
TIEMPO_RELOJ_SEG       = 120

vel_x = 0
vel_y = 0
en_suelo           = True
saltos_realizados  = 0
direccion_mirada   = 1
dash_frames_restantes = 0
ultimo_dash_tiempo = 0
esta_dashing       = False
invulnerable_frames = 0
anim_frame  = 0
anim_timer  = 0

modo_2p            = False
jugador2           = None
vel_x2             = 0
vel_y2             = 0
en_suelo2          = False
saltos_realizados2 = 0
direccion_mirada2  = 1
vidas2             = 3
invulnerable2      = 0
esta_dashing2      = False
dash_frames2       = 0
ultimo_dash2       = 0
anim_frame2        = 0
anim_timer2        = 0
j2_muerto          = False

vidas              = 3
max_vidas_hud      = 3
score              = 0
monedas_recogidas  = 0
combo_multiplicador = 1
checkpoint_x       = 200
checkpoint_y       = 450
meta_alcanzada     = False
bandera_y          = 220
mastil_meta        = None
texto_gameover     = ""
color_fondo_gameover = NEGRO
nombre_dificultad_actual = "NORMAL"

ingresando_nombre  = False
nombre_input       = ""

muro_pinchos_x    = 0
muro_pinchos_vel  = 1.2
muro_pinchos_color = (120, 120, 140)

ultimo_x_generado        = 0
indice_pregunta_infinito = 0

duracion_temblor  = 0
intensidad_temblor = 0

powerups           = []
pu_velocidad_timer = 0
pu_escudo_activo   = False
escudo_absorbido   = False

boss             = None
proyectiles_boss = []
boss_activado    = False

enemigos_proyectil   = []
proyectiles_enemigos = []

modo_reloj_activo = False
tiempo_restante   = 0

preguntas             = []
plataformas           = []
plataformas_moviles   = []
plataformas_inestables= []
monedas               = []
particulas            = []
enemigos              = []
enemigos_lava         = []
textos_flotantes      = []
nubes_lejanas         = []
nubes_medias          = []
nubes_cercanas        = []

lava      = None
jugador   = None
camera_x  = 0

estrellas_fondo = [
    {
        "x":      random.randint(0, ANCHO),
        "y":      random.randint(0, ALTO),
        "r":      random.uniform(0.5, 2.5),
        "brillo": random.randint(80, 255),
        "vel":    random.uniform(0.05, 0.3),
    }
    for _ in range(220)
]
nebulosas = [
    {
        "x":     random.randint(0, 5000),
        "y":     random.randint(50, 400),
        "radio": random.randint(80, 180),
        "color": random.choice([
            (80, 20, 120, 40),
            (20, 60, 140, 35),
            (140, 40, 80, 30),
        ]),
    }
    for _ in range(6)
]

Banco_preguntas = {
    "facil": [
        {"pregunta": "¿Quién descubrió América?",              "correcta": "Colón",      "incorrecta": "Napoleón"},
        {"pregunta": "¿Dónde ocurrió la Rev. Francesa?",       "correcta": "Francia",    "incorrecta": "Italia"},
        {"pregunta": "¿Qué muro cayó en 1989?",                "correcta": "Berlín",     "incorrecta": "China"},
        {"pregunta": "¿En qué continente está Egipto?",        "correcta": "África",     "incorrecta": "Asia"},
        {"pregunta": "¿Primer hombre en la Luna?",             "correcta": "Armstrong",  "incorrecta": "Gagarin"},
        {"pregunta": "¿De qué país era Napoleón?",             "correcta": "Francia",    "incorrecta": "Italia"},
        {"pregunta": "¿Dónde están las pirámides?",            "correcta": "Egipto",     "incorrecta": "México"},
        {"pregunta": "¿Qué civilización construyó el Coliseo?","correcta": "Roma",       "incorrecta": "Grecia"},
        {"pregunta": "¿Año inicio 2ª Guerra Mundial?",         "correcta": "1939",       "incorrecta": "1941"},
        {"pregunta": "¿Quién pintó la Mona Lisa?",             "correcta": "Da Vinci",   "incorrecta": "Picasso"},
    ],
    "normal": [
        {"pregunta": "¿Primer emperador de Roma?",             "correcta": "Augusto",    "incorrecta": "Julio César"},
        {"pregunta": "¿Dónde nació Adolf Hitler?",             "correcta": "Austria",    "incorrecta": "Alemania"},
        {"pregunta": "¿Quién construyó Machu Picchu?",         "correcta": "Inca",       "incorrecta": "Maya"},
        {"pregunta": "¿Qué imperio dominó Mesopotamia?",       "correcta": "Babilónico", "incorrecta": "Persa"},
        {"pregunta": "¿Quién lideró la Revolución Rusa?",      "correcta": "Lenin",      "incorrecta": "Stalin"},
        {"pregunta": "¿Año de la Revolución Francesa?",        "correcta": "1789",       "incorrecta": "1776"},
        {"pregunta": "¿Quién escribió el Quijote?",            "correcta": "Cervantes",  "incorrecta": "Lope de Vega"},
        {"pregunta": "¿Dónde fue el Desembarco de Normandía?", "correcta": "Francia",    "incorrecta": "Italia"},
        {"pregunta": "¿Cuál fue la primera civilización?",     "correcta": "Sumeria",    "incorrecta": "Egipcia"},
        {"pregunta": "¿Quién venció a Napoleón en Waterloo?",  "correcta": "Wellington", "incorrecta": "Nelson"},
    ],
    "dificil": [
        {"pregunta": "¿Última reina Ptolemaica?",               "correcta": "Cleopatra VII", "incorrecta": "Nefertiti"},
        {"pregunta": "¿Año independencia EE.UU.?",              "correcta": "1776",           "incorrecta": "1789"},
        {"pregunta": "¿Código legal con Ley del Talión?",       "correcta": "Hammurabi",      "incorrecta": "Ur-Nammu"},
        {"pregunta": "¿Batalla que terminó el Imp. Romano?",    "correcta": "Adrianópolis",   "incorrecta": "Zama"},
        {"pregunta": "¿Dónde murió Alejandro Magno?",           "correcta": "Babilonia",      "incorrecta": "Persépolis"},
        {"pregunta": "¿Quién fundó el Imperio Mongol?",         "correcta": "Gengis Kan",     "incorrecta": "Kublai Kan"},
        {"pregunta": "¿Año caída de Constantinopla?",           "correcta": "1453",           "incorrecta": "1492"},
        {"pregunta": "¿Faraón de la Gran Pirámide?",            "correcta": "Keops",          "incorrecta": "Ramsés II"},
        {"pregunta": "¿Dónde se firmó la Magna Carta?",         "correcta": "Runnymede",      "incorrecta": "Londres"},
        {"pregunta": "¿Quién inventó la escritura cuneiforme?", "correcta": "Sumeria",        "incorrecta": "Fenicia"},
    ],
}

def reproducir_musica(clave):
    global musica_actual_clave
    if clave == musica_actual_clave:
        return
    
    musica_actual_clave = clave
    archivo = MUSICA.get(clave, "")
    if not archivo:
        print(f"[Audio] ❌ Clave '{clave}' no encontrada")
        return

    try:
        pygame.mixer.music.stop()
        
        # Intentos en orden de prioridad
        posibles_rutas = [
            resolver_ruta(f"historia/{archivo}"),
            resolver_ruta(archivo),                    # sin carpeta
            resolver_ruta(f"historia/{archivo.lower()}"),
            resolver_ruta(f"{archivo}"),
        ]
        
        ruta_final = None
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                ruta_final = ruta
                break
        
        if ruta_final:
            pygame.mixer.music.load(ruta_final)
            vol = vol_musica_juego if estado_actual in (ESTADO_JUEGO, ESTADO_PAUSA) else vol_musica_menu
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)
            print(f"[Audio] ✅ Reproduciendo: {archivo} → {ruta_final}")
        else:
            print(f"[Audio] ❌ No se encontró el archivo: {archivo}")
            print("   Verifica que esté en la carpeta 'historia/'")
            
    except Exception as e:
        print(f"[Audio] Error cargando '{archivo}': {e}")

def _gen_sfx_golpe():
    fs, dur = 22050, 0.25
    n = int(fs * dur)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / fs
        f = max(0.0, 1 - (t / dur))
        buf[i] = int((0.3 * math.sin(2 * math.pi * 80 * f * t)
                      + 0.7 * random.uniform(-1, 1)) * 16000 * f)
    try:
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def _gen_sfx_powerup():
    fs, dur = 22050, 0.3
    n = int(fs * dur)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / fs
        freq = 300 + 800 * (t / dur)
        env  = math.sin(math.pi * t / dur)
        buf[i] = int(math.sin(2 * math.pi * freq * t) * 12000 * env)
    try:
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def _gen_sfx_escudo():
    fs, dur = 22050, 0.2
    n = int(fs * dur)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / fs
        env = max(0.0, 1 - (t / dur))
        buf[i] = int((math.sin(2 * math.pi * 600 * t)
                      + random.uniform(-0.3, 0.3)) * 14000 * env)
    try:
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def _gen_sfx_boss_hit():
    fs, dur = 22050, 0.15
    n = int(fs * dur)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / fs
        env = max(0.0, 1 - (t / dur))
        buf[i] = int((math.sin(2 * math.pi * 200 * t)
                      + random.uniform(-0.5, 0.5)) * 15000 * env)
    try:
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

sonido_shake    = _gen_sfx_golpe()
sonido_pu       = _gen_sfx_powerup()
sonido_escudo   = _gen_sfx_escudo()
sonido_boss_hit = _gen_sfx_boss_hit()

def activar_temblor(dur, intens):
    global duracion_temblor, intensidad_temblor
    duracion_temblor   = dur
    intensidad_temblor = intens
    if sonido_shake:
        sonido_shake.set_volume(vol_efectos_sfx)
        sonido_shake.play()

def agregar_texto_flotante(x, y, texto, color=AMARILLO_PER):
    textos_flotantes.append({
        "x": x, "y": float(y),
        "texto": texto, "color": color,
        "vida": 55, "vy": -1.5,
    })

def actualizar_textos_flotantes():
    for t in textos_flotantes[:]:
        t["y"]   += t["vy"]
        t["vida"] -= 1
        if t["vida"] <= 0:
            textos_flotantes.remove(t)

def dibujar_textos_flotantes():
    for t in textos_flotantes:
        alpha = min(255, t["vida"] * 5)
        surf  = fuente_hud.render(t["texto"], True, t["color"])
        surf.set_alpha(alpha)
        pantalla.blit(surf, (
            t["x"] - camera_x - surf.get_width() // 2,
            int(t["y"]),
        ))

def part_polvo(x, y):
    for _ in range(5):
        particulas.append({
            "x": x + random.randint(0, ANCHO_JUGADOR),
            "y": y + ALTO_JUGADOR,
            "vx": random.uniform(-1.5, 1.5),
            "vy": random.uniform(-1, 0),
            "vida": random.randint(15, 30),
            "color": GRIS_CLARO,
        })

def part_lava(x, y):
    for _ in range(25):
        particulas.append({
            "x": x + random.randint(-20, 20),
            "y": y,
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-6, -2),
            "vida":  random.randint(20, 40),
            "color": random.choice([NARANJA_LAVA, ROJO_LAVA, AMARILLO_PER]),
        })

def part_powerup(x, y, color):
    for _ in range(18):
        particulas.append({
            "x": x, "y": y,
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-4, -1),
            "vida":  random.randint(20, 40),
            "color": color,
        })

def part_escudo_roto(x, y):
    for _ in range(20):
        particulas.append({
            "x": x + random.randint(0, ANCHO_JUGADOR),
            "y": y + random.randint(0, ALTO_JUGADOR),
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(-4, 1),
            "vida":  random.randint(15, 30),
            "color": COLOR_PU_ESCUDO,
        })

def part_explosion(x, y, color, cantidad=30):
    for _ in range(cantidad):
        particulas.append({
            "x": x, "y": y,
            "vx": random.uniform(-5, 5),
            "vy": random.uniform(-6, -1),
            "vida":  random.randint(25, 50),
            "color": color,
        })

def actualizar_particulas():
    if random.random() < 0.25:
        particulas.append({
            "x": random.randint(int(camera_x), int(camera_x + ANCHO)),
            "y": 652,
            "vx": random.uniform(-0.5, 0.5),
            "vy": random.uniform(-3, -1),
            "vida":  random.randint(30, 60),
            "color": random.choice([NARANJA_LAVA, ROJO_LAVA]),
        })
    for p in particulas[:]:
        p["x"]    += p["vx"]
        p["y"]    += p["vy"]
        p["vida"] -= 1
        if p["vida"] <= 0:
            particulas.remove(p)

def spawnear_powerup(x, y):
    tipo = random.choice(["velocidad", "escudo", "vida"])
    powerups.append({
        "rect":   pygame.Rect(int(x), int(y), 26, 26),
        "tipo":   tipo,
        "activo": True,
        "anim":   random.uniform(0, math.pi * 2),
    })

def _aplicar_powerup(pu, es_j2=False):
    global vidas, vidas2, pu_velocidad_timer, pu_escudo_activo, score
    pu["activo"] = False
    cx, cy = pu["rect"].centerx, pu["rect"].centery
    if pu["tipo"] == "velocidad":
        pu_velocidad_timer = 300
        part_powerup(cx, cy, COLOR_PU_VEL)
        agregar_texto_flotante(cx, cy - 20, "¡VELOCIDAD!", COLOR_PU_VEL)
    elif pu["tipo"] == "escudo":
        pu_escudo_activo = True
        part_powerup(cx, cy, COLOR_PU_ESCUDO)
        agregar_texto_flotante(cx, cy - 20, "¡ESCUDO!", COLOR_PU_ESCUDO)
    elif pu["tipo"] == "vida":
        if es_j2:
            if vidas2 < max_vidas_hud:
                vidas2 += 1
        else:
            if vidas < max_vidas_hud:
                vidas += 1
        part_powerup(cx, cy, COLOR_PU_VIDA)
        agregar_texto_flotante(cx, cy - 20, "¡+VIDA!", COLOR_PU_VIDA)
    score += 75
    if sonido_pu:
        sonido_pu.set_volume(vol_efectos_sfx)
        sonido_pu.play()

def actualizar_powerups():
    for pu in powerups[:]:
        if not pu["activo"]:
            continue
        pu["anim"] += 0.07
        if jugador and jugador.colliderect(pu["rect"]):
            _aplicar_powerup(pu, es_j2=False)
        elif modo_2p and jugador2 and not j2_muerto and jugador2.colliderect(pu["rect"]):
            _aplicar_powerup(pu, es_j2=True)

def dibujar_powerups(sy):
    for pu in powerups:
        if not pu["activo"]:
            continue
        px = pu["rect"].x - camera_x
        py = pu["rect"].y + sy + int(math.sin(pu["anim"]) * 5)
        if not (-30 < px < ANCHO + 30):
            continue
        w, h = pu["rect"].width, pu["rect"].height
        if pu["tipo"] == "velocidad":
            color, letra = COLOR_PU_VEL,    "V"
        elif pu["tipo"] == "escudo":
            color, letra = COLOR_PU_ESCUDO, "E"
        else:
            color, letra = COLOR_PU_VIDA,   "+"
        brillo = int(180 + 70 * math.sin(pu["anim"] * 2))
        c_bri  = tuple(min(255, int(c * brillo / 255)) for c in color)
        pygame.draw.circle(pantalla, c_bri, (px + w // 2, py + h // 2), w // 2 + 4)
        pygame.draw.circle(pantalla, NEGRO, (px + w // 2, py + h // 2), w // 2 + 4, 2)
        li = fuente_small.render(letra, True, NEGRO)
        pantalla.blit(li, (px + w // 2 - li.get_width() // 2,
                           py + h // 2 - li.get_height() // 2))

def dibujar_hud_powerups(surf):
    ox = ANCHO - 260
    if pu_velocidad_timer > 0:
        seg = round(pu_velocidad_timer / 60, 1)
        ti  = fuente_small.render(f"VEL {seg}s", True, COLOR_PU_VEL)
        surf.blit(ti, (ox, 20))
        ox -= 130
    if pu_escudo_activo:
        ti = fuente_small.render("ESCUDO", True, COLOR_PU_ESCUDO)
        surf.blit(ti, (ox, 20))

def crear_boss(x_mundo):
    return {
        "x": float(x_mundo), "y": float(380),
        "ancho": 80, "alto": 90,
        "hp": 8, "hp_max": 8,
        "vel": 2.5, "dir": -1,
        "fase": 1,
        "timer_disparo": 0, "cooldown_disparo": 90,
        "anim": 0.0, "invul": 0,
        "muerto": False, "timer_muerte": 0,
        "plat_x": x_mundo - 100, "plat_ancho": 400,
    }

def actualizar_boss():
    global boss, boss_activado, score, estado_actual
    global texto_gameover, color_fondo_gameover, meta_alcanzada, bandera_y
    global ingresando_nombre, nombre_input
    if boss is None or not boss_activado:
        return
    if boss["muerto"]:
        boss["timer_muerte"] += 1
        part_explosion(int(boss["x"] + boss["ancho"] // 2),
                       int(boss["y"] + boss["alto"] // 2), COLOR_BOSS, 3)
        if boss["timer_muerte"] > 120:
            agregar_texto_flotante(int(boss["x"]), int(boss["y"] - 40),
                                   "¡BOSS DERROTADO! +2000", AMARILLO_PER)
            score += 2000
            boss = None
            meta_alcanzada = True
        return
    if boss["hp"] <= boss["hp_max"] // 2 and boss["fase"] == 1:
        boss["fase"]             = 2
        boss["vel"]              = 4.0
        boss["cooldown_disparo"] = 50
        activar_temblor(30, 14)
        agregar_texto_flotante(int(boss["x"]), int(boss["y"] - 30), "¡FASE 2!", COLOR_DIFICIL)
    boss["anim"]          += 0.08
    boss["timer_disparo"] += 1
    if boss["invul"] > 0:
        boss["invul"] -= 1
    boss["x"] += boss["vel"] * boss["dir"]
    if boss["x"] < boss["plat_x"]:
        boss["x"]   = float(boss["plat_x"])
        boss["dir"] = 1
    if boss["x"] + boss["ancho"] > boss["plat_x"] + boss["plat_ancho"]:
        boss["x"]   = float(boss["plat_x"] + boss["plat_ancho"] - boss["ancho"])
        boss["dir"] = -1
    if boss["timer_disparo"] >= boss["cooldown_disparo"] and jugador:
        boss["timer_disparo"] = 0
        cx = boss["x"] + boss["ancho"] // 2
        cy = boss["y"] + boss["alto"]  // 2
        dx = jugador.centerx - cx
        dy = jugador.centery - cy
        dist = math.hypot(dx, dy) or 1
        spd  = 6 if boss["fase"] == 1 else 9
        proyectiles_boss.append({
            "x": float(cx), "y": float(cy),
            "vx": (dx / dist) * spd, "vy": (dy / dist) * spd,
            "vida": 120,
        })
        if boss["fase"] == 2:
            for ang in (-0.4, 0.4):
                cos_a, sin_a = math.cos(ang), math.sin(ang)
                nvx = (dx / dist) * spd * cos_a - (dy / dist) * spd * sin_a
                nvy = (dx / dist) * spd * sin_a + (dy / dist) * spd * cos_a
                proyectiles_boss.append({
                    "x": float(cx), "y": float(cy),
                    "vx": nvx, "vy": nvy,
                    "vida": 120,
                })
    for pb in proyectiles_boss[:]:
        pb["x"]    += pb["vx"]
        pb["y"]    += pb["vy"]
        pb["vida"] -= 1
        if pb["vida"] <= 0:
            proyectiles_boss.remove(pb)
            continue
        rect_pb = pygame.Rect(int(pb["x"] - 8), int(pb["y"] - 8), 16, 16)
        if jugador and jugador.colliderect(rect_pb):
            if pb in proyectiles_boss:
                proyectiles_boss.remove(pb)
            _recibir_danio_jugador("¡EL BOSS TE GOLPEÓ!", (120, 0, 120))
        elif modo_2p and jugador2 and not j2_muerto and jugador2.colliderect(rect_pb):
            if pb in proyectiles_boss:
                proyectiles_boss.remove(pb)
            _recibir_danio_j2()
    if boss and boss["invul"] == 0:
        rect_b = pygame.Rect(int(boss["x"]), int(boss["y"]), boss["ancho"], boss["alto"])
        if jugador and jugador.colliderect(rect_b):
            _recibir_danio_jugador("¡EL BOSS TE APLASTÓ!", (120, 0, 120))
        if modo_2p and jugador2 and not j2_muerto and jugador2.colliderect(rect_b):
            _recibir_danio_j2()

def boss_recibir_golpe():
    if boss is None or boss["muerto"] or boss["invul"] > 0:
        return
    boss["hp"]   -= 1
    boss["invul"] = 30
    activar_temblor(10, 6)
    if sonido_boss_hit:
        sonido_boss_hit.set_volume(vol_efectos_sfx)
        sonido_boss_hit.play()
    part_explosion(int(boss["x"] + boss["ancho"] // 2), int(boss["y"]), COLOR_BOSS, 15)
    agregar_texto_flotante(int(boss["x"] + boss["ancho"] // 2), int(boss["y"] - 20),
                           f"-1 HP  ({boss['hp']}/{boss['hp_max']})", AMARILLO_PER)
    if boss["hp"] <= 0:
        boss["muerto"]       = True
        boss["timer_muerte"] = 0
        activar_temblor(60, 18)

def dibujar_boss(sy):
    if boss is None:
        return
    bx = int(boss["x"]) - int(camera_x)
    by = int(boss["y"]) + sy
    if not (-100 < bx < ANCHO + 100):
        return
    pulso     = int(10 * math.sin(boss["anim"] * 2))
    color     = COLOR_DIFICIL if boss["fase"] == 2 else COLOR_BOSS
    color_osc = COLOR_BOSS_OSC
    if boss["invul"] > 0 and boss["invul"] % 6 < 3:
        color, color_osc = BLANCO, GRIS_CLARO
    pygame.draw.rect(pantalla, color_osc, (bx + 4, by + 10, boss["ancho"] - 8, boss["alto"] - 10), 0, 10)
    pygame.draw.rect(pantalla, color,     (bx, by, boss["ancho"], boss["alto"] - 10), 0, 10)
    pygame.draw.rect(pantalla, NEGRO,     (bx, by, boss["ancho"], boss["alto"]), 3, 10)
    pygame.draw.polygon(pantalla, color, [(bx + 12, by), (bx + 20, by - 18 + pulso // 2), (bx + 28, by)])
    pygame.draw.polygon(pantalla, color, [(bx + boss["ancho"] - 28, by),
                                          (bx + boss["ancho"] - 20, by - 18 + pulso // 2),
                                          (bx + boss["ancho"] - 12, by)])
    ojo_col = (255, 50, 50) if boss["fase"] == 2 else AMARILLO_PER
    for ox in (22, boss["ancho"] - 22):
        pygame.draw.circle(pantalla, ojo_col,  (bx + ox, by + 28), 10)
        pygame.draw.circle(pantalla, NEGRO,    (bx + ox, by + 28), 4)
    diente_y = by + 55
    for i in range(5):
        dx2 = bx + 10 + i * 13
        pygame.draw.polygon(pantalla, BLANCO,
                            [(dx2, diente_y), (dx2 + 6, diente_y - 10), (dx2 + 13, diente_y)])
    barra_x, barra_y = bx, by - 22
    barra_ancho, barra_alto = boss["ancho"], 12
    pygame.draw.rect(pantalla, (60, 0, 0), (barra_x, barra_y, barra_ancho, barra_alto), 0, 4)
    hp_ratio  = boss["hp"] / boss["hp_max"]
    hp_color  = COLOR_FACIL if hp_ratio > 0.5 else COLOR_NORMAL if hp_ratio > 0.25 else COLOR_DIFICIL
    pygame.draw.rect(pantalla, hp_color, (barra_x, barra_y, int(barra_ancho * hp_ratio), barra_alto), 0, 4)
    pygame.draw.rect(pantalla, NEGRO,    (barra_x, barra_y, barra_ancho, barra_alto), 2, 4)
    lb = fuente_small.render(f"BOSS HP {boss['hp']}/{boss['hp_max']}", True, BLANCO)
    pantalla.blit(lb, (barra_x + barra_ancho // 2 - lb.get_width() // 2, barra_y - 20))
    for pb in proyectiles_boss:
        px2 = int(pb["x"]) - int(camera_x)
        py2 = int(pb["y"]) + sy
        if not (-20 < px2 < ANCHO + 20):
            continue
        bc = COLOR_DIFICIL if boss["fase"] == 2 else COLOR_PROYECTIL
        pygame.draw.circle(pantalla, bc,          (px2, py2), 8)
        pygame.draw.circle(pantalla, AMARILLO_PER,(px2, py2), 4)
        for k in range(1, 4):
            ex2 = int(pb["x"] - pb["vx"] * k) - int(camera_x)
            ey2 = int(pb["y"] - pb["vy"] * k) + sy
            a2  = max(0, 80 - k * 25)
            s2  = pygame.Surface((8, 8), pygame.SRCALPHA)
            s2.fill((*bc, a2))
            pantalla.blit(s2, (ex2 - 4, ey2 - 4))

def spawnear_enemigo_proyectil(plat_rect, vel=2.0):
    enemigos_proyectil.append({
        "rect":          pygame.Rect(plat_rect.x + 20, plat_rect.y - 40, 38, 38),
        "plat":          plat_rect,
        "vel":           vel,
        "dir":           1,
        "timer_disparo": random.randint(0, 120),
        "cooldown":      180,
        "hp":            2,
        "anim":          random.uniform(0, math.pi * 2),
    })

def _matar_enemigo_proyectil(ent):
    global score
    part_explosion(ent["rect"].centerx, ent["rect"].top, COLOR_ENEMIGO, 20)
    agregar_texto_flotante(ent["rect"].centerx, ent["rect"].top - 15,
                           f"+{200 * combo_multiplicador}", AMARILLO_PER)
    score += 200 * combo_multiplicador
    if ent in enemigos_proyectil:
        enemigos_proyectil.remove(ent)
    activar_temblor(6, 4)

def actualizar_enemigos_proyectil():
    global vel_y, vel_y2
    for e in enemigos_proyectil[:]:
        e["anim"] += 0.07
        pr = e["plat"]
        e["rect"].x += int(e["vel"] * e["dir"])
        if e["dir"] ==  1 and e["rect"].right >= pr.right:
            e["dir"] = -1; e["rect"].right = pr.right
        if e["dir"] == -1 and e["rect"].left  <= pr.left:
            e["dir"] =  1; e["rect"].left  = pr.left
        e["timer_disparo"] += 1
        if jugador and e["timer_disparo"] >= e["cooldown"]:
            e["timer_disparo"] = 0
            dx   = jugador.centerx - e["rect"].centerx
            dy   = jugador.centery - e["rect"].centery
            dist = math.hypot(dx, dy) or 1
            spd  = 5
            proyectiles_enemigos.append({
                "x": float(e["rect"].centerx), "y": float(e["rect"].centery),
                "vx": (dx / dist) * spd, "vy": (dy / dist) * spd,
                "vida": 90,
            })
        if jugador and jugador.colliderect(e["rect"]):
            if vel_y > 0 and jugador.bottom - vel_y <= e["rect"].top + 15:
                e["hp"] -= 1
                if e["hp"] <= 0:
                    _matar_enemigo_proyectil(e)
                    continue
                vel_y = -12
                activar_temblor(6, 4)
            elif esta_dashing:
                _matar_enemigo_proyectil(e)
                continue
            elif invulnerable_frames <= 0:
                _recibir_danio_jugador("UN ENEMIGO TE ELIMINÓ", COLOR_ENEMIGO)
        if (modo_2p and jugador2 and not j2_muerto
                and e in enemigos_proyectil and jugador2.colliderect(e["rect"])):
            if vel_y2 > 0 and jugador2.bottom - vel_y2 <= e["rect"].top + 15:
                e["hp"] -= 1
                if e["hp"] <= 0:
                    _matar_enemigo_proyectil(e)
                    continue
                vel_y2 = -12
            elif esta_dashing2:
                _matar_enemigo_proyectil(e)
                continue
            elif invulnerable2 <= 0:
                _recibir_danio_j2()
    for pb in proyectiles_enemigos[:]:
        pb["x"]    += pb["vx"]
        pb["y"]    += pb["vy"]
        pb["vida"] -= 1
        if pb["vida"] <= 0:
            proyectiles_enemigos.remove(pb)
            continue
        rect_pb = pygame.Rect(int(pb["x"] - 6), int(pb["y"] - 6), 12, 12)
        if jugador and jugador.colliderect(rect_pb):
            if pb in proyectiles_enemigos:
                proyectiles_enemigos.remove(pb)
            _recibir_danio_jugador("UN PROYECTIL TE ELIMINÓ", COLOR_ENEMIGO)
        elif (modo_2p and jugador2 and not j2_muerto
              and pb in proyectiles_enemigos and jugador2.colliderect(rect_pb)):
            proyectiles_enemigos.remove(pb)
            _recibir_danio_j2()

def dibujar_enemigos_proyectil(sy):
    for e in enemigos_proyectil:
        ex = e["rect"].x - camera_x
        ey = e["rect"].y + sy
        if not (-50 < ex < ANCHO + 50):
            continue
        pulso = int(4 * math.sin(e["anim"] * 3))
        pygame.draw.rect(pantalla, (180, 60, 20), (ex, ey + pulso, e["rect"].w, e["rect"].h), 0, 6)
        pygame.draw.rect(pantalla, NEGRO,          (ex, ey + pulso, e["rect"].w, e["rect"].h), 2, 6)
        pygame.draw.circle(pantalla, AMARILLO_PER, (ex + e["rect"].w // 2, ey + 14 + pulso), 7)
        pygame.draw.circle(pantalla, NEGRO,        (ex + e["rect"].w // 2, ey + 14 + pulso), 3)
        if jugador:
            dx   = jugador.centerx - e["rect"].centerx
            dy   = jugador.centery - e["rect"].centery
            dist = math.hypot(dx, dy) or 1
            cx2  = ex + e["rect"].w // 2
            cy2  = ey + e["rect"].h // 2 + pulso
            pygame.draw.line(pantalla, (255, 150, 0), (cx2, cy2),
                             (cx2 + int(dx / dist * 18), cy2 + int(dy / dist * 18)), 4)
        if e["hp"] > 1:
            pygame.draw.rect(pantalla, (255, 80, 0), (ex, ey - 8, e["rect"].w, 5), 0, 2)
    for pb in proyectiles_enemigos:
        px2 = int(pb["x"]) - int(camera_x)
        py2 = int(pb["y"]) + sy
        if -20 < px2 < ANCHO + 20:
            pygame.draw.circle(pantalla, COLOR_PROYECTIL, (px2, py2), 6)
            pygame.draw.circle(pantalla, AMARILLO_PER,    (px2, py2), 3)

def _calcular_vel_lava():
    if jugador is None:
        return random.uniform(7, 12)
    distancia        = LAVA_Y - jugador.y
    gravedad_efectiva = GRAVEDAD * 0.6
    vel = math.sqrt(2 * gravedad_efectiva * max(distancia, 50))
    return vel * random.uniform(0.85, 1.15)

def spawnear_enemigo_lava(x_mundo):
    enemigos_lava.append({
        "x": x_mundo, "y": float(LAVA_Y),
        "vy": -_calcular_vel_lava(),
        "estado":       "subiendo",
        "timer_hundido": 0,
        "alto": 40, "ancho": 32,
    })

def actualizar_enemigos_lava():
    global score
    if jugador and random.random() < 0.008:
        spawnear_enemigo_lava(jugador.x + random.randint(-400, 400))
    for e in enemigos_lava[:]:
        if e["estado"] == "hundido":
            e["timer_hundido"] -= 1
            if e["timer_hundido"] <= 0:
                e["estado"] = "subiendo"
                e["vy"]     = -_calcular_vel_lava()
                e["y"]      = float(LAVA_Y)
            continue
        e["vy"] += GRAVEDAD * 0.6
        e["y"]  += e["vy"]
        if e["vy"] >= 0:
            e["estado"] = "bajando"
        if e["y"] >= LAVA_Y:
            e["y"]             = float(LAVA_Y)
            e["estado"]        = "hundido"
            e["timer_hundido"] = random.randint(90, 240)
            continue
        rect_e = pygame.Rect(int(e["x"] - e["ancho"] // 2), int(e["y"]), e["ancho"], e["alto"])
        if jugador and jugador.colliderect(rect_e):
            if esta_dashing:
                part_lava(int(e["x"]), int(e["y"]))
                agregar_texto_flotante(int(e["x"]), int(e["y"]) - 20,
                                       f"+{200 * combo_multiplicador}", AMARILLO_PER)
                if e in enemigos_lava:
                    enemigos_lava.remove(e)
                score += 200 * combo_multiplicador
                activar_temblor(6, 4)
                continue
            elif invulnerable_frames <= 0:
                _recibir_danio_jugador("¡UN ENEMIGO DE LA LAVA TE ELIMINÓ!", (120, 10, 10))
                e["estado"]        = "hundido"
                e["timer_hundido"] = 60
        elif (modo_2p and jugador2 and not j2_muerto
              and e in enemigos_lava and jugador2.colliderect(rect_e)):
            if esta_dashing2:
                part_lava(int(e["x"]), int(e["y"]))
                if e in enemigos_lava:
                    enemigos_lava.remove(e)
                score += 200 * combo_multiplicador
            elif invulnerable2 <= 0:
                _recibir_danio_j2()
                e["estado"]        = "hundido"
                e["timer_hundido"] = 60

def dibujar_enemigos_lava(offset_shake):
    for e in enemigos_lava:
        if e["estado"] == "hundido":
            continue
        ex = int(e["x"]) - int(camera_x) - e["ancho"] // 2
        ey = int(e["y"]) + offset_shake
        if not (-50 < ex < ANCHO + 50):
            continue
        img = sprites.get("enemigo_lava", (e["ancho"], e["alto"]))
        if img:
            pantalla.blit(img, (ex, ey))
        else:
            color_body = (220, 50, 20) if e["estado"] == "subiendo" else (180, 30, 10)
            pygame.draw.rect(pantalla, color_body, (ex, ey, e["ancho"], e["alto"]), 0, 6)
            pygame.draw.rect(pantalla, NEGRO,       (ex, ey, e["ancho"], e["alto"]), 2, 6)
            for ox in (8, 24):
                pygame.draw.circle(pantalla, AMARILLO_PER, (ex + ox, ey + 12), 5)
                pygame.draw.circle(pantalla, NEGRO,        (ex + ox, ey + 12), 2)
            if e["estado"] == "subiendo":
                for yy in range(ey + e["alto"] - 8, ey + e["alto"] + 4, 4):
                    pygame.draw.line(pantalla, NARANJA_LAVA, (ex + 4, yy), (ex + e["ancho"] - 4, yy), 2)

def _recibir_danio_jugador(msg_gameover, color_go):
    global vidas, combo_multiplicador, invulnerable_frames
    global estado_actual, texto_gameover, color_fondo_gameover
    global vel_x, vel_y, pu_escudo_activo, escudo_absorbido
    global ingresando_nombre, nombre_input
    if invulnerable_frames > 0:
        return
    if pu_escudo_activo:
        pu_escudo_activo  = False
        escudo_absorbido  = True
        part_escudo_roto(jugador.x, jugador.y)
        agregar_texto_flotante(jugador.centerx, jugador.y - 20, "¡ESCUDO ROTO!", COLOR_PU_ESCUDO)
        if sonido_escudo:
            sonido_escudo.set_volume(vol_efectos_sfx)
            sonido_escudo.play()
        activar_temblor(10, 6)
        invulnerable_frames = 60
    else:
        vidas               -= 1
        combo_multiplicador  = 1
        activar_temblor(20, 12)
        invulnerable_frames  = 90
        if vidas <= 0:
            if modo_2p and not j2_muerto:
                agregar_texto_flotante(jugador.centerx, jugador.y - 30, "J1 eliminado", COLOR_DIFICIL)
                jugador.x = checkpoint_x
                jugador.y = checkpoint_y + 200
                vidas     = 0
                vel_x = vel_y = 0
            else:
                texto_gameover       = msg_gameover
                color_fondo_gameover = color_go
                ingresando_nombre    = True
                nombre_input         = ""
                estado_actual        = ESTADO_GAMEOVER
        else:
            jugador.x = checkpoint_x
            jugador.y = checkpoint_y
            vel_x = vel_y = 0

def _recibir_danio_j2():
    global vidas2, invulnerable2, vel_x2, vel_y2, j2_muerto
    global estado_actual, texto_gameover, color_fondo_gameover
    global ingresando_nombre, nombre_input
    if invulnerable2 > 0:
        return
    vidas2       -= 1
    invulnerable2 = 90
    activar_temblor(15, 8)
    if vidas2 <= 0:
        j2_muerto = True
        agregar_texto_flotante(jugador2.centerx, jugador2.y - 30, "J2 eliminado", COLOR_DIFICIL)
        if vidas <= 0:
            texto_gameover       = "AMBOS JUGADORES ELIMINADOS"
            color_fondo_gameover = GRIS_OSCURO
            ingresando_nombre    = True
            nombre_input         = ""
            estado_actual        = ESTADO_GAMEOVER
    else:
        jugador2.x = checkpoint_x + 60
        jugador2.y = checkpoint_y
        vel_x2 = vel_y2 = 0

def agregar_tramo_pregunta():
    global ultimo_x_generado, indice_pregunta_infinito
    es_inf = dificultad_guardada in ("infinito", "reloj", "2p")
    pool   = (Banco_preguntas["facil"] + Banco_preguntas["normal"] + Banco_preguntas["dificil"]
              if es_inf else Banco_preguntas.get(dificultad_guardada, Banco_preguntas["normal"]))
    vel_e  = random.uniform(3.0, 5.0) if es_inf else 2.0
    raw    = pool[indice_pregunta_infinito % len(pool)]
    indice_pregunta_infinito += 1
    x = ultimo_x_generado
    correcta_arriba = random.choice([True, False])
    nueva_p = {
        "pregunta":       raw["pregunta"],
        "correcta":       raw["correcta"],
        "incorrecta":     raw["incorrecta"],
        "texto_x":        x + 260,
        "respondida":     False,
        "correcta_rect":  pygame.Rect(x + 450, 260 if correcta_arriba else 420, 220, 25),
        "incorrecta_rect":pygame.Rect(x + 450, 420 if correcta_arriba else 260, 220, 25),
        "muro_bloqueo":   pygame.Rect(x + 665, 0, 15, 660),
    }
    preguntas.append(nueva_p)
    plat1 = pygame.Rect(x, 500, 220, 25)
    plataformas.append({"rect": plat1, "tipo": "normal"})
    plataformas.append({"rect": pygame.Rect(x + 350, 400, 120, 20), "tipo": "normal"})
    if x > 200:
        if random.random() < 0.5:
            enemigos.append({
                "rect":          pygame.Rect(plat1.x + 20, plat1.y - 35, 35, 35),
                "plat_asociada": plat1,
                "vel":           vel_e,
                "dir":           1,
            })
        else:
            spawnear_enemigo_proyectil(plat1, vel_e)
    for m in range(2):
        monedas.append({"rect": pygame.Rect(x + 60 + m * 50, 440, 18, 18), "activa": True})
    plat2 = pygame.Rect(x + 800, 420, 220, 25)
    plataformas.append({"rect": plat2, "tipo": "normal"})
    if random.random() < 0.4:
        spawnear_powerup(x + random.randint(100, 600), 380)
    if es_inf:
        if random.choice([True, False]):
            plataformas_moviles.append({
                "rect":      pygame.Rect(x + 1090, 420, 150, 20),
                "y_inicial": 420,
                "rango":     150,
                "velocidad": random.uniform(0.05, 0.09),
                "angulo":    random.uniform(0, math.pi),
            })
            monedas.append({"rect": pygame.Rect(x + 1150, 280, 18, 18), "activa": True})
        else:
            plataformas_inestables.append({
                "rect":        pygame.Rect(x + 1090, 440, 140, 20),
                "pisada":      False,
                "tiempo_pisada": 0,
                "cayendo":     False,
                "vel_caida":   0,
                "y_original":  440,
            })
    else:
        plataformas.append({"rect": pygame.Rect(x + 1090, 440, 150, 25), "tipo": "normal"})
    ultimo_x_generado += 1350

def iniciar_partida(dificultad):
    global preguntas, plataformas, plataformas_moviles, plataformas_inestables
    global monedas, lava, jugador, camera_x, vel_x, vel_y, en_suelo, saltos_realizados
    global vidas, max_vidas_hud, score, monedas_recogidas, combo_multiplicador
    global checkpoint_x, checkpoint_y, particulas, mastil_meta, meta_alcanzada, bandera_y
    global dificultad_guardada, muro_pinchos_x, muro_pinchos_vel
    global ultimo_x_generado, indice_pregunta_infinito, enemigos, enemigos_lava
    global esta_dashing, dash_frames_restantes, invulnerable_frames, anim_frame, anim_timer
    global nombre_dificultad_actual, nubes_lejanas, nubes_medias, nubes_cercanas
    global powerups, pu_velocidad_timer, pu_escudo_activo, textos_flotantes, escudo_absorbido
    global boss, proyectiles_boss, boss_activado
    global enemigos_proyectil, proyectiles_enemigos
    global ingresando_nombre, nombre_input
    global modo_reloj_activo, tiempo_restante
    global modo_2p, jugador2, vel_x2, vel_y2, en_suelo2, saltos_realizados2
    global vidas2, invulnerable2, esta_dashing2, dash_frames2, ultimo_dash2
    global anim_frame2, anim_timer2, j2_muerto, direccion_mirada2
    global direccion_mirada, ultimo_dash_tiempo

    dificultad_guardada      = dificultad
    nombre_dificultad_actual = dificultad.upper()
    score = monedas_recogidas = 0
    combo_multiplicador      = 1
    particulas               = []
    enemigos                 = []
    enemigos_lava            = []
    powerups                 = []
    pu_velocidad_timer       = 0
    pu_escudo_activo         = False
    textos_flotantes         = []
    escudo_absorbido         = False
    meta_alcanzada           = False
    bandera_y                = 220
    esta_dashing             = False
    dash_frames_restantes    = 0
    invulnerable_frames      = 0
    anim_frame = anim_timer  = 0
    boss                     = None
    proyectiles_boss         = []
    boss_activado            = False
    enemigos_proyectil       = []
    proyectiles_enemigos     = []
    ingresando_nombre        = False
    nombre_input             = ""
    direccion_mirada         = 1
    ultimo_dash_tiempo       = 0

    modo_reloj_activo = (dificultad == "reloj")
    modo_2p           = (dificultad == "2p")
    tiempo_restante   = TIEMPO_RELOJ_SEG * FPS if modo_reloj_activo else 0

    if modo_2p:
        vidas = vidas2 = max_vidas_hud = 3
        invulnerable2 = 0
        esta_dashing2 = False
        dash_frames2 = ultimo_dash2 = 0
        anim_frame2 = anim_timer2   = 0
        j2_muerto            = False
        vel_x2 = vel_y2       = 0
        en_suelo2             = False
        saltos_realizados2    = 0
        direccion_mirada2     = 1
        jugador2              = None
        muro_pinchos_x        = -300
        muro_pinchos_vel      = 2.25
        nombre_dificultad_actual = "2 JUGADORES"
    elif dificultad == "infinito":
        vidas = max_vidas_hud  = 1
        jugador2               = None
        muro_pinchos_x         = -150
        muro_pinchos_vel       = 4.25
    elif dificultad == "reloj":
        vidas = max_vidas_hud  = 3
        jugador2               = None
        muro_pinchos_x         = -300
        muro_pinchos_vel       = 2.0
        nombre_dificultad_actual = "CONTRA EL RELOJ"
    else:
        vidas = max_vidas_hud  = 3
        jugador2               = None
        muro_pinchos_x         = -300
        muro_pinchos_vel       = 2.25

    clave_musica = (
        "infinito" if dificultad in ("infinito", "reloj") else
        "normal"   if dificultad == "2p" else
        dificultad
    )
    reproducir_musica(clave_musica)

    preguntas = []
    plataformas = []
    plataformas_moviles = []
    plataformas_inestables = []
    monedas = []
    ultimo_x_generado        = 200
    indice_pregunta_infinito = 0

    if dificultad in ("infinito", "reloj", "2p"):
        for _ in range(3):
            agregar_tramo_pregunta()
    else:
        for _ in range(5):
            agregar_tramo_pregunta()
        xf        = ultimo_x_generado - 250
        plat_boss = pygame.Rect(xf - 100, 460, 400, 25)
        plataformas.append({"rect": plat_boss, "tipo": "normal"})
        boss                 = crear_boss(xf + 80)
        boss["plat_x"]       = plat_boss.x
        boss["plat_ancho"]   = plat_boss.width
        mastil_meta          = None

    lava = pygame.Rect(0, 660, ultimo_x_generado + 2000, 40)
    plat0       = plataformas[0]["rect"]
    checkpoint_x = plat0.x + 80
    checkpoint_y = plat0.y - ALTO_JUGADOR
    jugador      = pygame.Rect(checkpoint_x, checkpoint_y, ANCHO_JUGADOR, ALTO_JUGADOR)
    camera_x     = jugador.centerx - ANCHO // 2
    vel_x = vel_y = 0
    en_suelo      = True
    saltos_realizados = 0

    if modo_2p:
        jugador2 = pygame.Rect(checkpoint_x + 60, checkpoint_y, ANCHO_JUGADOR, ALTO_JUGADOR)

    nubes_lejanas  = [{"x": random.randint(0, 5000), "y": random.randint(60, 200),
                       "ancho": random.randint(80, 140)} for _ in range(20)]
    nubes_medias   = [{"x": random.randint(0, 5000), "y": random.randint(100, 280),
                       "ancho": random.randint(60, 110)} for _ in range(15)]
    nubes_cercanas = [{"x": random.randint(0, 5000), "y": random.randint(150, 320),
                       "ancho": random.randint(40, 80)} for _ in range(10)]

def actualizar_fisica_j2():
    global vel_x2, vel_y2, en_suelo2, saltos_realizados2
    global checkpoint_x, checkpoint_y, invulnerable2
    global esta_dashing2, dash_frames2
    global score, monedas_recogidas, combo_multiplicador
    if not modo_2p or jugador2 is None or j2_muerto:
        return
    if invulnerable2 > 0:
        invulnerable2 -= 1
    if esta_dashing2:
        vel_x2 = direccion_mirada2 * DASH_FUERZA
        dash_frames2 -= 1
        particulas.append({
            "x": jugador2.centerx,
            "y": jugador2.centery + random.randint(-10, 10),
            "vx": -direccion_mirada2 * 2, "vy": random.uniform(-1, 1),
            "vida": 10, "color": COLOR_J2,
        })
        if dash_frames2 <= 0:
            esta_dashing2 = False
            vel_x2        = 0
        if boss and boss_activado and not boss["muerto"]:
            rect_b = pygame.Rect(int(boss["x"]), int(boss["y"]), boss["ancho"], boss["alto"])
            if jugador2.colliderect(rect_b):
                boss_recibir_golpe()
    jugador2.x += vel_x2
    if jugador2.left < muro_pinchos_x:
        jugador2.left = muro_pinchos_x
    for p in preguntas:
        if not p["respondida"] and jugador2.colliderect(p["muro_bloqueo"]):
            if vel_x2 > 0:
                jugador2.right = p["muro_bloqueo"].left
    vel_y2    += GRAVEDAD
    jugador2.y += vel_y2
    tocando2   = False
    for p in plataformas:
        r = p["rect"]
        if jugador2.colliderect(r) and vel_y2 >= 0 and jugador2.bottom - vel_y2 <= r.top + 8:
            jugador2.bottom = r.top; vel_y2 = 0; tocando2 = True; saltos_realizados2 = 0
    for pm in plataformas_moviles:
        r = pm["rect"]
        if jugador2.colliderect(r) and vel_y2 >= 0 and jugador2.bottom - vel_y2 <= r.top + 12:
            jugador2.bottom = r.top; vel_y2 = 0; tocando2 = True; saltos_realizados2 = 0
    for pi in plataformas_inestables:
        r = pi["rect"]
        if (not pi["cayendo"] and jugador2.colliderect(r)
                and vel_y2 >= 0 and jugador2.bottom - vel_y2 <= r.top + 10):
            jugador2.bottom = r.top; vel_y2 = 0; tocando2 = True; saltos_realizados2 = 0
            if not pi["pisada"]:
                pi["pisada"]       = True
                pi["tiempo_pisada"] = pygame.time.get_ticks()
    for p in preguntas:
        cr = p["correcta_rect"]
        ir = p["incorrecta_rect"]
        if jugador2.colliderect(cr) and vel_y2 >= 0 and jugador2.bottom - vel_y2 <= cr.top + 8:
            jugador2.bottom = cr.top; vel_y2 = 0; tocando2 = True; saltos_realizados2 = 0
            if not p["respondida"]:
                p["respondida"]  = True
                pts = 150 * combo_multiplicador
                score           += pts
                combo_multiplicador += 1
                agregar_texto_flotante(cr.centerx, cr.top - 20, f"+{pts} (J2)", COLOR_FACIL)
                checkpoint_x = cr.x + 80
                checkpoint_y = cr.top - ALTO_JUGADOR
        if jugador2.colliderect(ir) and vel_y2 >= 0 and jugador2.bottom - vel_y2 <= ir.top + 8:
            part_lava(jugador2.centerx, jugador2.bottom)
            activar_temblor(20, 10)
            agregar_texto_flotante(ir.centerx, ir.top - 20, "J2 INCORRECTO", COLOR_DIFICIL)
            _recibir_danio_j2()
    en_suelo2 = tocando2
    if lava and jugador2.top >= lava.top - 5 and not en_suelo2:
        part_lava(jugador2.centerx, lava.top)
        _recibir_danio_j2()
    for m in monedas:
        if m["activa"] and jugador2.colliderect(m["rect"]):
            m["activa"]          = False
            monedas_recogidas   += 1
            puntos               = 50 * combo_multiplicador
            score               += puntos
            agregar_texto_flotante(m["rect"].centerx, m["rect"].top - 10,
                                   f"+{puntos}", ORO_MONEDA)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDERS — bien posicionados para 1200x700
# ══════════════════════════════════════════════════════════════════════════════
class SliderVolumen:
    def __init__(self, x, y, ancho, val, label):
        self.rect   = pygame.Rect(x, y, ancho, 10)
        self.valor  = val
        self.label  = label
        self.drag   = False
        self._sync()

    def _sync(self):
        mx = self.rect.x + int(self.valor * self.rect.width)
        self.manija = pygame.Rect(mx - 10, self.rect.centery - 12, 20, 24)

    def dibujar(self, surf):
        pygame.draw.rect(surf, GRIS_OSCURO, self.rect, 0, 4)
        pygame.draw.rect(surf, BTN_AZUL_NEON,
                         (self.rect.x, self.rect.y,
                          int(self.valor * self.rect.width), self.rect.height), 0, 4)
        pygame.draw.rect(surf,
                         BTN_HOVER_MAGENTA if self.drag else GRIS_CLARO,
                         self.manija, 0, 6)
        surf.blit(fuente_hud.render(f"{self.label}: {int(self.valor * 100)}%", True, BLANCO),
                  (self.rect.x, self.rect.y - 30))

    def scan(self, ev):
        mp = pygame.mouse.get_pos()
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.manija.collidepoint(mp) or self.rect.collidepoint(mp):
                self.drag = True
        if ev.type == pygame.MOUSEBUTTONUP:
            self.drag = False
        if self.drag:
            rx = max(0, min(mp[0] - self.rect.x, self.rect.width))
            self.valor = rx / self.rect.width
            self._sync()
            return True
        return False

# Sliders centrados: 1200/2 = 600; panel ancho=540 -> x=330; slider ancho=360
_SL_X = ANCHO // 2 - 180   # 420
_SL_W = 360
_PNL_Y = 130  # top del panel

slider_mm  = SliderVolumen(_SL_X, _PNL_Y + 110, _SL_W, vol_musica_menu,  "Musica Menu")
slider_mj  = SliderVolumen(_SL_X, _PNL_Y + 200, _SL_W, vol_musica_juego, "Musica Juego")
slider_sfx = SliderVolumen(_SL_X, _PNL_Y + 290, _SL_W, vol_efectos_sfx,  "Efectos SFX")

class BotonNeon:
    def __init__(self, texto, x, y, w, h, acento, icono=""):
        self.rect   = pygame.Rect(x, y, w, h)
        self.texto  = texto
        self.acento = acento
        self.icono  = icono
        self._ha    = 0

    def dibujar(self, surf):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        self._ha = min(255, self._ha + 20) if hover else max(0, self._ha - 20)
        a = self._ha / 255.0
        pygame.draw.rect(surf, tuple(int(c * 0.18) for c in self.acento), self.rect, 0, 12)
        if a > 0:
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            s.fill((*self.acento, int(60 * a)))
            surf.blit(s, self.rect.topleft)
        pygame.draw.rect(surf,
                         tuple(min(255, int(c * (0.7 + 0.3 * a))) for c in self.acento),
                         self.rect, 3, 12)
        pygame.draw.line(surf, BLANCO,
                         (self.rect.x + 16, self.rect.y + 2),
                         (self.rect.right - 16, self.rect.y + 2), 1)
        label = f"{self.icono}  {self.texto}" if self.icono else self.texto
        tc    = BLANCO if a > 0.3 else tuple(min(255, int(c * 1.3)) for c in self.acento)
        ti    = fuente.render(label, True, tc)
        surf.blit(ti, (self.rect.centerx - ti.get_width() // 2,
                       self.rect.centery - ti.get_height() // 2))

    def clicado(self, ev):
        return (ev.type == pygame.MOUSEBUTTONDOWN
                and ev.button == 1
                and self.rect.collidepoint(ev.pos))

class Boton:
    def __init__(self, texto, x, y, w, h, cb, ch, ct=NEGRO):
        self.rect  = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.cb    = cb
        self.ch    = ch
        self.ct    = ct

    def dibujar(self, surf):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        col   = self.ch if hover else self.cb
        pygame.draw.rect(surf, col,   self.rect, 0, 10)
        pygame.draw.rect(surf, BLANCO if hover else NEGRO, self.rect, 3, 10)
        ti = fuente.render(self.texto, True, BLANCO if hover else self.ct)
        surf.blit(ti, (self.rect.centerx - ti.get_width() // 2,
                       self.rect.centery - ti.get_height() // 2))

    def clicado(self, ev):
        return (ev.type == pygame.MOUSEBUTTONDOWN
                and ev.button == 1
                and self.rect.collidepoint(ev.pos))

btn_jugar        = BotonNeon("JUGAR",    ANCHO//2-160, 260, 320, 54, (0, 200, 255),   "")
btn_config       = BotonNeon("OPCIONES", ANCHO//2-160, 330, 320, 54, (100, 120, 255), "")
btn_ranking_menu = BotonNeon("RANKING",  ANCHO//2-160, 400, 320, 54, (255, 180, 0),   "")
btn_salir        = BotonNeon("SALIR",    ANCHO//2-160, 470, 320, 54, (255, 60, 100),  "")

btn_facil   = Boton("FACIL",           ANCHO//2-160, 175, 320, 50, COLOR_FACIL,   BTN_HOVER_MAGENTA)
btn_normal  = Boton("NORMAL",          ANCHO//2-160, 240, 320, 50, COLOR_NORMAL,  BTN_HOVER_MAGENTA)
btn_dificil = Boton("DIFICIL",         ANCHO//2-160, 305, 320, 50, COLOR_DIFICIL, BTN_HOVER_MAGENTA)
btn_inf     = Boton("HARDCORE",        ANCHO//2-160, 370, 320, 50, COLOR_INFINITO,BTN_HOVER_MAGENTA)
btn_reloj   = Boton("CONTRA EL RELOJ", ANCHO//2-160, 435, 320, 50, (255, 165, 0), BTN_HOVER_MAGENTA)
btn_volver  = Boton("VOLVER",          ANCHO//2-160, 500, 320, 50, GRIS_BOTON,    NEGRO)

# Config: boton centrado debajo del panel
btn_cfg_ok    = Boton("GUARDAR Y VOLVER", ANCHO//2-150, _PNL_Y + 420 + 18, 300, 55, COLOR_FACIL, BTN_HOVER_MAGENTA)
btn_go_menu   = Boton("MENU PRINCIPAL",   ANCHO//2-150, 570, 300, 55, BTN_AZUL_NEON, BTN_HOVER_MAGENTA)
btn_reanudar  = Boton("REANUDAR",         ANCHO//2-150, 280, 300, 55, COLOR_FACIL,   BTN_HOVER_MAGENTA)
btn_reiniciar = Boton("REINICIAR",        ANCHO//2-150, 370, 300, 55, COLOR_NORMAL,  BTN_HOVER_MAGENTA)
btn_p_salir   = Boton("SALIR AL MENU",    ANCHO//2-150, 460, 300, 55, COLOR_DIFICIL, BLANCO, BLANCO)
btn_rank_volver=Boton("VOLVER",           ANCHO//2-150, 580, 300, 55, GRIS_BOTON,    NEGRO)

def txt(texto, x, y, color=NEGRO, fnt=None):
    fnt = fnt or fuente
    pantalla.blit(fnt.render(texto, True, color), (x, y))

def dibujar_plat(rect, ctop, cbot, sy=0):
    rx = rect.x - camera_x
    ry = rect.y + sy
    if -rect.width < rx < ANCHO:
        pygame.draw.rect(pantalla, cbot, (rx, ry + 6, rect.width, rect.height - 6))
        pygame.draw.rect(pantalla, ctop, (rx, ry, rect.width, 6))
        pygame.draw.rect(pantalla, NEGRO,(rx, ry, rect.width, rect.height), 2)

def degradado(surf, ct, cb):
    for y in range(ALTO):
        f = y / ALTO
        pygame.draw.line(surf,
                         (int(ct[0] * (1-f) + cb[0] * f),
                          int(ct[1] * (1-f) + cb[1] * f),
                          int(ct[2] * (1-f) + cb[2] * f)),
                         (0, y), (ANCHO, y))

def corazones(surf, xi, yi, v, mv):
    for i in range(mv):
        c  = COLOR_DIFICIL if i < v else GRIS_OSCURO
        rx = xi + i * 35
        if i < v:
            pygame.draw.circle(surf, c, (rx,      yi),      8)
            pygame.draw.circle(surf, c, (rx + 12, yi),      8)
            pygame.draw.polygon(surf, c, [(rx - 8, yi + 3), (rx + 20, yi + 3), (rx + 6, yi + 16)])
        else:
            pygame.draw.rect(surf, c, (rx - 4, yi - 4, 20, 20), 0, 4)

def fondo_juego(sy=0):
    for y in range(ALTO):
        f = y / ALTO
        if f < 0.5:
            f2 = f / 0.5
            c  = (int(CIELO_TOP[0]*(1-f2) + CIELO_MID[0]*f2),
                  int(CIELO_TOP[1]*(1-f2) + CIELO_MID[1]*f2),
                  int(CIELO_TOP[2]*(1-f2) + CIELO_MID[2]*f2))
        else:
            f2 = (f - 0.5) / 0.5
            c  = (int(CIELO_MID[0]*(1-f2) + CIELO_BOTTOM[0]*f2),
                  int(CIELO_MID[1]*(1-f2) + CIELO_BOTTOM[1]*f2),
                  int(CIELO_MID[2]*(1-f2) + CIELO_BOTTOM[2]*f2))
        pygame.draw.line(pantalla, c, (0, y + sy), (ANCHO, y + sy))
    for e in estrellas_fondo:
        b = e["brillo"]
        pygame.draw.circle(pantalla, (b, b, b),
                           (int(e["x"]), int(e["y"]) + sy),
                           max(1, int(e["r"])))
    for nb in nebulosas:
        nx = int(nb["x"] - camera_x * 0.05) % (ANCHO + 400) - 200
        ny = nb["y"] + sy
        s  = pygame.Surface((nb["radio"] * 2, nb["radio"] * 2), pygame.SRCALPHA)
        r, g, b, a = nb["color"]
        pygame.draw.circle(s, (r, g, b, a), (nb["radio"], nb["radio"]), nb["radio"])
        pantalla.blit(s, (nx - nb["radio"], ny - nb["radio"]))
    for n in nubes_lejanas:
        nx = int(n["x"] - camera_x * 0.10) % (ANCHO + 300) - 150
        pygame.draw.ellipse(pantalla, (180, 195, 240), (nx, n["y"] + sy, n["ancho"], 18))
    for n in nubes_medias:
        nx = int(n["x"] - camera_x * 0.25) % (ANCHO + 300) - 150
        pygame.draw.ellipse(pantalla, (140, 160, 220), (nx, n["y"] + sy, n["ancho"], 15))
    for n in nubes_cercanas:
        nx = int(n["x"] - camera_x * 0.50) % (ANCHO + 200) - 100
        pygame.draw.ellipse(pantalla, (100, 120, 190), (nx, n["y"] + sy, n["ancho"], 12))

def fondo_menu():
    degradado(pantalla, FONDO_MENU_TOP, FONDO_MENU_BOTTOM)
    t = pygame.time.get_ticks()
    for e in estrellas_fondo:
        p = int(abs(math.sin(t * 0.001 + e["x"] * 0.05)) * 255)
        pygame.draw.circle(pantalla, (p, p, p),
                           (int(e["x"]), int(e["y"])),
                           max(1, int(e["r"] * (0.6 + 0.4 * p / 255))))

_moneda_frame = 0
_moneda_timer = 0

def dibujar_jugador_en(jrect, jvx, jvy, j_en_suelo, j_dashing, j_dir, j_invul,
                        j_anim_frame, pu_vel, pu_esc, color_base=None, sy=0):
    jx = jrect.x - camera_x
    jy = jrect.y + sy
    if j_invul > 0 and (j_invul % 10 >= 5):
        return
    if j_dashing:
        key = "jugador_dash"
    elif not j_en_suelo:
        key = "jugador_jump"
    elif jvx != 0:
        key = f"jugador_walk{j_anim_frame + 1}"
    else:
        key = "jugador_idle"
    img = sprites.get(key, (ANCHO_JUGADOR, ALTO_JUGADOR))
    if img:
        if j_dir == -1:
            img = pygame.transform.flip(img, True, False)
        pantalla.blit(img, (jx, jy))
    else:
        col = color_base if color_base else (BTN_AZUL_NEON if j_dashing else AMARILLO_PER)
        pygame.draw.rect(pantalla, col,   (jx, jy, jrect.width, jrect.height), 0, 4)
        pygame.draw.rect(pantalla, NEGRO, (jx, jy, jrect.width, jrect.height), 2, 4)
        ox = 30 if j_dir == 1 else 12
        pygame.draw.circle(pantalla, NEGRO, (jx + ox, jy + 18), 4)
    if pu_vel > 0:
        t   = pygame.time.get_ticks()
        a   = int(100 + 60 * math.sin(t * 0.01))
        s   = pygame.Surface((jrect.width + 16, jrect.height + 16), pygame.SRCALPHA)
        pygame.draw.rect(s, (*COLOR_PU_VEL, a),
                         (0, 0, jrect.width + 16, jrect.height + 16), 3, 8)
        pantalla.blit(s, (jx - 8, jy - 8))
    if pu_esc:
        t   = pygame.time.get_ticks()
        a   = int(120 + 80 * math.sin(t * 0.008))
        s   = pygame.Surface((jrect.width + 20, jrect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(s, (*COLOR_PU_ESCUDO, a),
                         (0, 0, jrect.width + 20, jrect.height + 20), 4, 10)
        pantalla.blit(s, (jx - 10, jy - 10))
    if j_invul > 80:
        s = pygame.Surface((jrect.width, jrect.height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 160))
        pantalla.blit(s, (jx, jy))

def dibujar_enemigo(e, sy):
    ex = e["rect"].x - camera_x
    ey = e["rect"].y + sy
    if not (-40 < ex < ANCHO + 40):
        return
    img = sprites.get("enemigo", (35, 35))
    if img:
        fi = img if e["dir"] == 1 else pygame.transform.flip(img, True, False)
        pantalla.blit(fi, (ex, ey))
    else:
        pygame.draw.rect(pantalla, COLOR_ENEMIGO, (ex, ey, e["rect"].width, e["rect"].height), 0, 6)
        pygame.draw.rect(pantalla, NEGRO,          (ex, ey, e["rect"].width, e["rect"].height), 2, 6)
        lx = (ex + 20, ey + 10, ex + 32, ey + 14) if e["dir"] == 1 else (ex + 15, ey + 10, ex + 3, ey + 14)
        pygame.draw.line(pantalla, BLANCO, (lx[0], lx[1]), (lx[2], lx[3]), 3)
        pygame.draw.circle(pantalla, NEGRO,
                           (ex + 26, ey + 18) if e["dir"] == 1 else (ex + 9, ey + 18), 3)

def dibujar_moneda(m, sy):
    global _moneda_frame, _moneda_timer
    if not m["activa"]:
        return
    mx = m["rect"].x - camera_x
    my = m["rect"].y + sy
    if not (-20 < mx < ANCHO + 20):
        return
    _moneda_timer += 1
    if _moneda_timer >= 12:
        _moneda_frame = (_moneda_frame + 1) % 2
        _moneda_timer = 0
    img = sprites.get(f"moneda{_moneda_frame + 1}", (18, 18))
    if img:
        pantalla.blit(img, (mx, my))
    else:
        pygame.draw.circle(pantalla, ORO_MONEDA, (mx + 9, my + 9), 9)

def dibujar_pantalla_ranking():
    degradado(pantalla, FONDO_MENU_TOP, FONDO_MENU_BOTTOM)
    t = pygame.time.get_ticks()
    for e in estrellas_fondo:
        p = int(abs(math.sin(t * 0.001 + e["x"] * 0.05)) * 255)
        pygame.draw.circle(pantalla, (p, p, p),
                           (int(e["x"]), int(e["y"])),
                           max(1, int(e["r"])))
    tr = fuente_grande.render("RANKING TOP 10", True, AMARILLO_PER)
    pantalla.blit(tr, (ANCHO // 2 - tr.get_width() // 2, 40))
    pygame.draw.line(pantalla, AMARILLO_PER, (ANCHO // 2 - 250, 100), (ANCHO // 2 + 250, 100), 2)
    lista = cargar_ranking()
    if not lista:
        ti = fuente.render("Aun no hay puntajes guardados.", True, GRIS_CLARO)
        pantalla.blit(ti, (ANCHO // 2 - ti.get_width() // 2, 280))
    else:
        col_medallas = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
        medallas_str = ["1ro", "2do", "3ro"]
        for i, entrada in enumerate(lista[:10]):
            y_fila   = 120 + i * 42
            fila_col = AMARILLO_PER if i == 0 else GRIS_CLARO
            if i < 3:
                med = fuente.render(medallas_str[i], True, col_medallas[i])
                pantalla.blit(med, (ANCHO // 2 - 320, y_fila))
            pygame.draw.rect(pantalla, (30, 30, 60),
                             (ANCHO // 2 - 280, y_fila - 2, 560, 36), 0, 6)
            num = fuente_hud.render(f"{i+1:2}.", True, fila_col)
            nom = fuente_hud.render(entrada.get("nombre", "???")[:12], True, fila_col)
            pts = fuente_hud.render(f"{entrada['puntos']:>8} pts", True, fila_col)
            mod = fuente_small.render(entrada.get("modo", "?"), True, (150, 200, 255))
            pantalla.blit(num, (ANCHO // 2 - 270, y_fila))
            pantalla.blit(nom, (ANCHO // 2 - 230, y_fila))
            pantalla.blit(pts, (ANCHO // 2 + 80,  y_fila))
            pantalla.blit(mod, (ANCHO // 2 + 210, y_fila + 6))
    btn_rank_volver.dibujar(pantalla)

def dibujar_gameover():
    pantalla.fill(color_fondo_gameover)
    go  = fuente_grande.render(texto_gameover, True, BLANCO)
    pantalla.blit(go, (ANCHO // 2 - go.get_width() // 2, ALTO // 4))
    pts = fuente_grande.render(f"PUNTUACION: {score} PTS", True, AMARILLO_PER)
    pantalla.blit(pts, (ANCHO // 2 - pts.get_width() // 2, ALTO // 4 + 80))
    sub = fuente_hud.render(
        f"Monedas: {monedas_recogidas}  |  Modo: {nombre_dificultad_actual}",
        True, GRIS_CLARO)
    pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2, ALTO // 4 + 145))
    if ingresando_nombre:
        pygame.draw.rect(pantalla, (30, 30, 70),   (ANCHO // 2 - 260, ALTO // 2 - 10, 520, 110), 0, 10)
        pygame.draw.rect(pantalla, AMARILLO_PER,   (ANCHO // 2 - 260, ALTO // 2 - 10, 520, 110), 3, 10)
        lbl = fuente_hud.render("Ingresa tu nombre para el ranking:", True, BLANCO)
        pantalla.blit(lbl, (ANCHO // 2 - lbl.get_width() // 2, ALTO // 2 + 2))
        cursor = "|" if pygame.time.get_ticks() % 800 < 400 else ""
        ni = fuente_grande.render(nombre_input + cursor, True, AMARILLO_PER)
        pantalla.blit(ni, (ANCHO // 2 - ni.get_width() // 2, ALTO // 2 + 40))
        hint = fuente_small.render("ENTER para confirmar", True, (180, 180, 180))
        pantalla.blit(hint, (ANCHO // 2 - hint.get_width() // 2, ALTO // 2 + 92))
    else:
        btn_go_menu.dibujar(pantalla)
        hr = fuente_small.render("(Tu puntaje ya fue guardado)", True, (150, 200, 150))
        pantalla.blit(hr, (ANCHO // 2 - hr.get_width() // 2, ALTO // 2 + 10))

def dibujar_timer_hud():
    if not modo_reloj_activo:
        return
    seg  = tiempo_restante // FPS
    mseg = (tiempo_restante % FPS) * 100 // FPS
    if seg > 30:   color_t = COLOR_FACIL
    elif seg > 10: color_t = COLOR_NORMAL
    else:          color_t = COLOR_DIFICIL
    txt_t = fuente_hud.render(f"  {seg:02}:{mseg:02}", True, color_t)
    rx    = ANCHO // 2 - txt_t.get_width() // 2 - 12
    pygame.draw.rect(pantalla, GRIS_OSCURO, (rx, 14, txt_t.get_width() + 24, 34), 0, 8)
    pygame.draw.rect(pantalla, color_t,     (rx, 14, txt_t.get_width() + 24, 34), 2, 8)
    pantalla.blit(txt_t, (rx + 12, 20))
    ratio = tiempo_restante / (TIEMPO_RELOJ_SEG * FPS)
    bw    = 300
    bx    = ANCHO // 2 - bw // 2
    pygame.draw.rect(pantalla, GRIS_OSCURO, (bx, 52, bw,          8), 0, 4)
    pygame.draw.rect(pantalla, color_t,     (bx, 52, int(bw*ratio), 8), 0, 4)

def dibujar_hud_j2():
    if not modo_2p:
        return
    if j2_muerto:
        li = fuente_small.render("J2: ELIMINADO", True, COLOR_DIFICIL)
        pantalla.blit(li, (ANCHO - 200, 65))
        return
    corazones(pantalla, 35, 72, vidas2, max_vidas_hud)
    li = fuente_small.render("J2", True, COLOR_J2)
    pantalla.blit(li, (12, 65))

# ══════════════════════════════════════════════════════════════════════════════
# ARRANQUE
# ══════════════════════════════════════════════════════════════════════════════
reproducir_musica("menu")

# ══════════════════════════════════════════════════════════════════════════════
# BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
while True:
    reloj.tick(FPS)
    eventos = pygame.event.get()

    sy = 0
    if duracion_temblor > 0:
        duracion_temblor -= 1
        sy = random.randint(-intensidad_temblor, intensidad_temblor)

    for ev in eventos:
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
            pantalla_completa = not pantalla_completa
            if pantalla_completa:
                info = pygame.display.Info()
                pantalla_real = pygame.display.set_mode(
                    (info.current_w, info.current_h), pygame.FULLSCREEN)
            else:
                pantalla_real = pygame.display.set_mode((ANCHO_JUEGO, ALTO_JUEGO))

        if estado_actual == ESTADO_CONFIG:
            changed_mm  = slider_mm.scan(ev)
            changed_mj  = slider_mj.scan(ev)
            changed_sfx = slider_sfx.scan(ev)
            if changed_mm:
                vol_musica_menu = slider_mm.valor
            if changed_mj:
                vol_musica_juego = slider_mj.valor
                pygame.mixer.music.set_volume(vol_musica_juego)
            if changed_sfx:
                vol_efectos_sfx = slider_sfx.valor
            # ESC también cierra config
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                estado_actual = ESTADO_MENU

        if estado_actual == ESTADO_MENU:
            if   btn_jugar.clicado(ev):        estado_actual = ESTADO_DIFICULTAD
            elif btn_config.clicado(ev):        estado_actual = ESTADO_CONFIG
            elif btn_ranking_menu.clicado(ev):  estado_actual = ESTADO_RANKING
            elif btn_salir.clicado(ev):         pygame.quit(); sys.exit()

        elif estado_actual == ESTADO_DIFICULTAD:
            if   btn_facil.clicado(ev):   iniciar_partida("facil");    estado_actual = ESTADO_JUEGO
            elif btn_normal.clicado(ev):  iniciar_partida("normal");   estado_actual = ESTADO_JUEGO
            elif btn_dificil.clicado(ev): iniciar_partida("dificil");  estado_actual = ESTADO_JUEGO
            elif btn_inf.clicado(ev):     iniciar_partida("infinito"); estado_actual = ESTADO_JUEGO
            elif btn_reloj.clicado(ev):   iniciar_partida("reloj");    estado_actual = ESTADO_JUEGO
            elif btn_volver.clicado(ev):  estado_actual = ESTADO_MENU

        elif estado_actual == ESTADO_CONFIG:
            if btn_cfg_ok.clicado(ev):
                estado_actual = ESTADO_MENU

        elif estado_actual == ESTADO_RANKING:
            if btn_rank_volver.clicado(ev):
                estado_actual = ESTADO_MENU

        elif estado_actual == ESTADO_PAUSA:
            if btn_reanudar.clicado(ev):
                estado_actual = ESTADO_JUEGO
                pygame.mixer.music.unpause()
            elif btn_reiniciar.clicado(ev):
                iniciar_partida(dificultad_guardada)
                estado_actual = ESTADO_JUEGO
            elif btn_p_salir.clicado(ev):
                estado_actual = ESTADO_MENU
                reproducir_musica("menu")
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_p, pygame.K_ESCAPE):
                estado_actual = ESTADO_JUEGO
                pygame.mixer.music.unpause()

        elif estado_actual == ESTADO_GAMEOVER:
            if ingresando_nombre:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN and nombre_input.strip():
                        agregar_a_ranking(nombre_input.strip(), score, dificultad_guardada)
                        ingresando_nombre = False
                    elif ev.key == pygame.K_BACKSPACE:
                        nombre_input = nombre_input[:-1]
                    elif len(nombre_input) < 12 and ev.unicode.isprintable():
                        nombre_input += ev.unicode
            else:
                if btn_go_menu.clicado(ev):
                    estado_actual = ESTADO_MENU
                    reproducir_musica("menu")

        if estado_actual == ESTADO_JUEGO and not meta_alcanzada:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_p, pygame.K_ESCAPE):
                    estado_actual = ESTADO_PAUSA
                    pygame.mixer.music.pause()
                    vel_x = 0
                    continue
                if ev.key == pygame.K_LEFT:
                    vel_x = -VELOCIDAD; direccion_mirada = -1
                if ev.key == pygame.K_RIGHT:
                    vel_x =  VELOCIDAD; direccion_mirada =  1
                if ev.key == pygame.K_SPACE:
                    if en_suelo:
                        vel_y = SALTO; en_suelo = False
                        saltos_realizados = 1
                        part_polvo(jugador.x, jugador.y)
                    elif saltos_realizados < MAX_SALTOS_PERMITIDOS:
                        vel_y = SALTO; saltos_realizados += 1
                        part_polvo(jugador.x, jugador.y)
                if ev.key == pygame.K_e and not esta_dashing:
                    now = pygame.time.get_ticks()
                    if now - ultimo_dash_tiempo >= DASH_COOLDOWN_MS:
                        esta_dashing          = True
                        dash_frames_restantes = DASH_DURACION_FRAMES
                        ultimo_dash_tiempo    = now
                        activar_temblor(5, 4)
            if ev.type == pygame.KEYUP:
                if ev.key == pygame.K_LEFT  and vel_x < 0: vel_x = 0
                if ev.key == pygame.K_RIGHT and vel_x > 0: vel_x = 0
            if modo_2p and not j2_muerto:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_a: vel_x2 = -VELOCIDAD; direccion_mirada2 = -1
                    if ev.key == pygame.K_d: vel_x2 =  VELOCIDAD; direccion_mirada2 =  1
                    if ev.key == pygame.K_w:
                        if en_suelo2:
                            vel_y2 = SALTO; en_suelo2 = False
                            saltos_realizados2 = 1
                            if jugador2: part_polvo(jugador2.x, jugador2.y)
                        elif saltos_realizados2 < MAX_SALTOS_PERMITIDOS:
                            vel_y2 = SALTO; saltos_realizados2 += 1
                    if ev.key == pygame.K_f and not esta_dashing2:
                        now = pygame.time.get_ticks()
                        if now - ultimo_dash2 >= DASH_COOLDOWN_MS:
                            esta_dashing2 = True
                            dash_frames2  = DASH_DURACION_FRAMES
                            ultimo_dash2  = now
                            activar_temblor(5, 4)
                if ev.type == pygame.KEYUP:
                    if ev.key == pygame.K_a and vel_x2 < 0: vel_x2 = 0
                    if ev.key == pygame.K_d and vel_x2 > 0: vel_x2 = 0

    # ─────────────────────────────────────────────────────────────────────────
    # LÓGICA DE JUEGO
    # ─────────────────────────────────────────────────────────────────────────
    if estado_actual == ESTADO_JUEGO:
        actualizar_particulas()
        actualizar_textos_flotantes()
        muro_pinchos_x += muro_pinchos_vel

        if modo_reloj_activo and not meta_alcanzada:
            tiempo_restante -= 1
            if tiempo_restante <= 0:
                tiempo_restante      = 0
                texto_gameover       = "¡SE ACABO EL TIEMPO!"
                color_fondo_gameover = (80, 0, 0)
                ingresando_nombre    = True
                nombre_input         = ""
                estado_actual        = ESTADO_GAMEOVER

        vel_actual = VELOCIDAD
        if pu_velocidad_timer > 0:
            pu_velocidad_timer -= 1
            vel_actual = int(VELOCIDAD * 1.65)

        if jugador and dificultad_guardada in ("infinito", "reloj", "2p") and jugador.x > ultimo_x_generado - 2000:
            agregar_tramo_pregunta()

        if boss and not boss_activado and not boss["muerto"]:
            if jugador and jugador.x > boss["x"] - 600:
                boss_activado = True
                agregar_texto_flotante(int(boss["x"]), int(boss["y"]) - 50, "¡¡BOSS!!", COLOR_BOSS)
                activar_temblor(40, 16)

        if meta_alcanzada:
            vel_x = 0
            if bandera_y < 460:
                bandera_y += 4
            else:
                bonus_tiempo = 0
                if modo_reloj_activo and tiempo_restante > 0:
                    bonus_tiempo  = (tiempo_restante // FPS) * 10
                    score        += bonus_tiempo
                    agregar_texto_flotante(jugador.centerx, jugador.y - 50,
                                          f"¡BONUS TIEMPO +{bonus_tiempo}!", COLOR_PU_VEL)
                if modo_2p and not j2_muerto and vidas > 0:
                    score += 500
                    agregar_texto_flotante(jugador.centerx, jugador.y - 80,
                                          "¡BONUS COOPERATIVO +500!", COLOR_FACIL)
                texto_gameover       = f"¡NIVEL COMPLETADO EN MODO {nombre_dificultad_actual}!"
                color_fondo_gameover = VERDE_SUELO_OSC
                ingresando_nombre    = True
                nombre_input         = ""
                estado_actual        = ESTADO_GAMEOVER

        if not meta_alcanzada and jugador:
            if invulnerable_frames > 0:
                invulnerable_frames -= 1

            if vel_x != 0 and en_suelo:
                anim_timer += 1
                if anim_timer >= 10:
                    anim_frame = (anim_frame + 1) % 2
                    anim_timer = 0
            else:
                anim_frame = anim_timer = 0

            if modo_2p and not j2_muerto:
                if vel_x2 != 0 and en_suelo2:
                    anim_timer2 += 1
                    if anim_timer2 >= 10:
                        anim_frame2 = (anim_frame2 + 1) % 2
                        anim_timer2 = 0
                else:
                    anim_frame2 = anim_timer2 = 0

            if esta_dashing:
                vel_x = direccion_mirada * DASH_FUERZA
                dash_frames_restantes -= 1
                particulas.append({
                    "x": jugador.centerx,
                    "y": jugador.centery + random.randint(-10, 10),
                    "vx": -direccion_mirada * 2, "vy": random.uniform(-1, 1),
                    "vida": 10, "color": BTN_AZUL_NEON,
                })
                if dash_frames_restantes <= 0:
                    esta_dashing = False
                    vel_x        = 0
                if boss and boss_activado and not boss["muerto"]:
                    rect_b = pygame.Rect(int(boss["x"]), int(boss["y"]), boss["ancho"], boss["alto"])
                    if jugador.colliderect(rect_b):
                        boss_recibir_golpe()

            for pm in plataformas_moviles:
                pm["angulo"] += pm["velocidad"]
                pm["rect"].y  = pm["y_inicial"] + int(math.sin(pm["angulo"]) * pm["rango"])

            for pi in plataformas_inestables:
                if pi["pisada"] and not pi["cayendo"]:
                    if pygame.time.get_ticks() - pi["tiempo_pisada"] > 700:
                        pi["cayendo"] = True
                if pi["cayendo"]:
                    pi["vel_caida"] += GRAVEDAD
                    pi["rect"].y    += int(pi["vel_caida"])

            for e in enemigos[:]:
                pr = e["plat_asociada"]
                e["rect"].x += e["vel"] * e["dir"]
                if e["dir"] ==  1 and e["rect"].right >= pr.right:
                    e["dir"] = -1; e["rect"].right = pr.right
                elif e["dir"] == -1 and e["rect"].left  <= pr.left:
                    e["dir"] =  1; e["rect"].left  = pr.left

                if jugador.colliderect(e["rect"]):
                    if vel_y > 0 and jugador.bottom - vel_y <= e["rect"].top + 15:
                        if e in enemigos: enemigos.remove(e)
                        vel_y = -12
                        agregar_texto_flotante(e["rect"].centerx, e["rect"].top - 10,
                                              f"+{150 * combo_multiplicador}", AMARILLO_PER)
                        score += 150 * combo_multiplicador
                        activar_temblor(8, 5)
                    elif esta_dashing:
                        part_explosion(e["rect"].centerx, e["rect"].top, COLOR_ENEMIGO, 20)
                        agregar_texto_flotante(e["rect"].centerx, e["rect"].top - 10,
                                              f"+{200 * combo_multiplicador}", AMARILLO_PER)
                        score += 200 * combo_multiplicador
                        if e in enemigos: enemigos.remove(e)
                        activar_temblor(6, 4)
                    elif invulnerable_frames <= 0:
                        _recibir_danio_jugador("UN ENEMIGO TE ELIMINO", COLOR_ENEMIGO)

                if (modo_2p and jugador2 and not j2_muerto
                        and e in enemigos and jugador2.colliderect(e["rect"])):
                    if vel_y2 > 0 and jugador2.bottom - vel_y2 <= e["rect"].top + 15:
                        if e in enemigos: enemigos.remove(e)
                        vel_y2 = -12
                        score += 150 * combo_multiplicador
                        activar_temblor(8, 5)
                    elif esta_dashing2:
                        if e in enemigos: enemigos.remove(e)
                        score += 200 * combo_multiplicador
                        activar_temblor(6, 4)
                    elif invulnerable2 <= 0:
                        _recibir_danio_j2()

            actualizar_enemigos_lava()
            actualizar_enemigos_proyectil()
            actualizar_boss()
            actualizar_powerups()
            actualizar_fisica_j2()

            for m in monedas:
                if m["activa"] and jugador.colliderect(m["rect"]):
                    m["activa"]         = False
                    monedas_recogidas  += 1
                    puntos              = 50 * combo_multiplicador
                    score              += puntos
                    agregar_texto_flotante(m["rect"].centerx, m["rect"].y - 10,
                                          f"+{puntos}", ORO_MONEDA)

            if not esta_dashing:
                keys = pygame.key.get_pressed()
                if   keys[pygame.K_LEFT]:  vel_x = -vel_actual; direccion_mirada = -1
                elif keys[pygame.K_RIGHT]: vel_x =  vel_actual; direccion_mirada =  1

            if modo_2p and not j2_muerto and not esta_dashing2:
                keys = pygame.key.get_pressed()
                if   keys[pygame.K_a]: vel_x2 = -vel_actual; direccion_mirada2 = -1
                elif keys[pygame.K_d]: vel_x2 =  vel_actual; direccion_mirada2 =  1

            jugador.x += vel_x

            for p in preguntas:
                if not p["respondida"] and jugador.colliderect(p["muro_bloqueo"]):
                    if vel_x > 0:
                        jugador.right = p["muro_bloqueo"].left

            if jugador.left < muro_pinchos_x:
                jugador.left = muro_pinchos_x
                if jugador.left < 0:
                    jugador.left = 0
            if dificultad_guardada not in ("infinito", "reloj", "2p"):
                if jugador.left < 0:
                    jugador.left = 0

            if (jugador.colliderect(pygame.Rect(muro_pinchos_x - 50, 0, 70, 700))
                    and invulnerable_frames <= 0):
                activar_temblor(30, 15)
                vidas              -= 1
                combo_multiplicador = 1
                invulnerable_frames = 90
                if vidas <= 0:
                    texto_gameover       = "LA PARED DE PINCHOS TE ALCANZO"
                    color_fondo_gameover = GRIS_OSCURO
                    ingresando_nombre    = True
                    nombre_input         = ""
                    estado_actual        = ESTADO_GAMEOVER
                else:
                    jugador.x = muro_pinchos_x + 120
                    jugador.y = checkpoint_y
                    vel_x = vel_y = 0

            vel_y      += GRAVEDAD
            jugador.y  += vel_y
            tocando     = False

            for p in plataformas:
                r = p["rect"]
                if jugador.colliderect(r) and vel_y >= 0 and jugador.bottom - vel_y <= r.top + 8:
                    jugador.bottom = r.top; vel_y = 0; tocando = True; saltos_realizados = 0
                    checkpoint_x   = r.x + 80
                    checkpoint_y   = r.top - ALTO_JUGADOR

            for pm in plataformas_moviles:
                r = pm["rect"]
                if jugador.colliderect(r) and vel_y >= 0 and jugador.bottom - vel_y <= r.top + 12:
                    jugador.bottom = r.top; vel_y = 0; tocando = True; saltos_realizados = 0
                    checkpoint_x   = r.x + 40
                    checkpoint_y   = r.top - ALTO_JUGADOR

            for pi in plataformas_inestables:
                r = pi["rect"]
                if (not pi["cayendo"] and jugador.colliderect(r)
                        and vel_y >= 0 and jugador.bottom - vel_y <= r.top + 10):
                    jugador.bottom = r.top; vel_y = 0; tocando = True; saltos_realizados = 0
                    if not pi["pisada"]:
                        pi["pisada"]        = True
                        pi["tiempo_pisada"] = pygame.time.get_ticks()

            for p in preguntas:
                cr = p["correcta_rect"]
                ir = p["incorrecta_rect"]
                if jugador.colliderect(cr) and vel_y >= 0 and jugador.bottom - vel_y <= cr.top + 8:
                    jugador.bottom = cr.top; vel_y = 0; tocando = True; saltos_realizados = 0
                    if not p["respondida"]:
                        p["respondida"] = True
                        pts = (250 if dificultad_guardada in ("infinito", "reloj") else 150) \
                              * combo_multiplicador
                        score              += pts
                        combo_multiplicador += 1
                        agregar_texto_flotante(cr.centerx, cr.top - 20, f"+{pts}", COLOR_FACIL)
                        checkpoint_x = cr.x + 80
                        checkpoint_y = cr.top - ALTO_JUGADOR
                if jugador.colliderect(ir) and vel_y >= 0 and jugador.bottom - vel_y <= ir.top + 8:
                    part_lava(jugador.centerx, jugador.bottom)
                    activar_temblor(20, 10)
                    vidas              -= 1
                    combo_multiplicador = 1
                    agregar_texto_flotante(ir.centerx, ir.top - 20, "INCORRECTO", COLOR_DIFICIL)
                    if dificultad_guardada in ("infinito", "reloj"):
                        muro_pinchos_vel = min(muro_pinchos_vel + 0.5, 8.0)
                    if vidas <= 0:
                        texto_gameover       = "RESPUESTA INCORRECTA"
                        color_fondo_gameover = ROJO_LAVA
                        ingresando_nombre    = True
                        nombre_input         = ""
                        estado_actual        = ESTADO_GAMEOVER
                    else:
                        jugador.x = checkpoint_x
                        jugador.y = checkpoint_y
                        vel_x = vel_y = 0

            en_suelo = tocando

            if lava and jugador.top >= lava.top - 5 and not en_suelo:
                part_lava(jugador.centerx, lava.top)
                activar_temblor(25, 12)
                vidas              -= 1
                combo_multiplicador = 1
                if vidas <= 0:
                    texto_gameover       = "TE CAISTE A LA LAVA"
                    color_fondo_gameover = (100, 10, 10)
                    ingresando_nombre    = True
                    nombre_input         = ""
                    estado_actual        = ESTADO_GAMEOVER
                else:
                    jugador.x = checkpoint_x
                    jugador.y = checkpoint_y
                    vel_x = vel_y = 0

        if jugador:
            if modo_2p and jugador2 and not j2_muerto:
                cam_obj = max(jugador.centerx, jugador2.centerx) - ANCHO // 2
            else:
                cam_obj = jugador.centerx - ANCHO // 2
            camera_x += (cam_obj - camera_x) * 0.08
            if camera_x < 0:
                camera_x = 0

    # ─────────────────────────────────────────────────────────────────────────
    # RENDERIZADO
    # ─────────────────────────────────────────────────────────────────────────
    if estado_actual in (ESTADO_JUEGO, ESTADO_PAUSA):
        fondo_juego(sy)

        if lava:
            pygame.draw.rect(pantalla, NARANJA_LAVA, (0, lava.y + sy, ANCHO, lava.height))
            pygame.draw.rect(pantalla, ROJO_LAVA,    (0, lava.y + 10 + sy, ANCHO, lava.height - 10))

        mr = muro_pinchos_x - camera_x
        if mr > -100:
            pygame.draw.rect(pantalla, muro_pinchos_color, (mr - 100, sy, 100, 660))
            for py_muro in range(0, 660, 30):
                if lava and py_muro + 30 <= lava.y:
                    pygame.draw.polygon(pantalla, (231, 76, 60), [
                        (mr,      py_muro + sy),
                        (mr + 22, py_muro + 15 + sy),
                        (mr,      py_muro + 30 + sy),
                    ])

        for p in preguntas:
            if not p["respondida"]:
                mx = p["muro_bloqueo"].x - camera_x
                if -20 < mx < ANCHO + 20:
                    pygame.draw.rect(pantalla, (255, 0, 100), (mx + 5, sy, 4, 660))

        for p  in plataformas:          dibujar_plat(p["rect"],  VERDE_SUELO,      VERDE_SUELO_OSC,  sy)
        for pm in plataformas_moviles:  dibujar_plat(pm["rect"], PLAT_MOVIL_COLOR, PLAT_MOVIL_OSC,   sy)
        for pi in plataformas_inestables:
            ct = PLAT_CAE_COLOR if not pi["pisada"] else (255, 60, 60)
            dibujar_plat(pi["rect"], ct, PLAT_CAE_OSC, sy)

        for e in enemigos: dibujar_enemigo(e, sy)
        dibujar_enemigos_lava(sy)
        dibujar_enemigos_proyectil(sy)
        dibujar_boss(sy)
        dibujar_powerups(sy)
        for m in monedas: dibujar_moneda(m, sy)

        for p in particulas:
            pygame.draw.rect(pantalla, p["color"],
                             (p["x"] - camera_x, p["y"] + sy, 5, 5))

        for p in preguntas:
            tx = p["texto_x"] - camera_x
            if -600 < tx < ANCHO + 200:
                ts = fuente.render(p["pregunta"], True, GRIS_OSCURO)
                pygame.draw.rect(pantalla, GRIS_CLARO,
                                 (tx - 15, 150 + sy, ts.get_width() + 30, 50), 0, 8)
                pantalla.blit(ts, (tx, 158 + sy))
                dibujar_plat(p["correcta_rect"],   AZUL_PLAT, AZUL_PLAT_OSC, sy)
                dibujar_plat(p["incorrecta_rect"],  AZUL_PLAT, AZUL_PLAT_OSC, sy)
                txt(p["correcta"],
                    p["correcta_rect"].x - camera_x + 20,
                    p["correcta_rect"].y - 45 + sy, GRIS_CLARO, fuente_small)
                txt(p["incorrecta"],
                    p["incorrecta_rect"].x - camera_x + 20,
                    p["incorrecta_rect"].y - 45 + sy, GRIS_CLARO, fuente_small)

        # J2
        if modo_2p and jugador2 and not j2_muerto:
            dibujar_jugador_en(jugador2, vel_x2, vel_y2, en_suelo2, esta_dashing2,
                               direccion_mirada2, invulnerable2,
                               anim_frame2, 0, False,
                               COLOR_J2, sy)
            lj2 = fuente_small.render("J2", True, COLOR_J2)
            pantalla.blit(lj2, (jugador2.x - camera_x, jugador2.y - 18 + sy))

        # J1
        if jugador:
            dibujar_jugador_en(jugador, vel_x, vel_y, en_suelo, esta_dashing,
                               direccion_mirada, invulnerable_frames,
                               anim_frame, pu_velocidad_timer, pu_escudo_activo,
                               None, sy)
            if modo_2p:
                lj1 = fuente_small.render("J1", True, AMARILLO_PER)
                pantalla.blit(lj1, (jugador.x - camera_x, jugador.y - 18 + sy))

        dibujar_textos_flotantes()

        hud_alto = 90 if modo_2p else 50
        pygame.draw.rect(pantalla, GRIS_CLARO, (15, 15, 900, hud_alto), 0, 8)
        pygame.draw.rect(pantalla, NEGRO,      (15, 15, 900, hud_alto), 2, 8)
        corazones(pantalla, 35, 40, vidas, max_vidas_hud)
        dibujar_hud_j2()

        cd   = max(0, 1000 - (pygame.time.get_ticks() - ultimo_dash_tiempo))
        dtxt = "DASH:LISTO" if cd == 0 else f"DASH:{round(cd/1000, 1)}s"
        hud  = (f"Modo:{nombre_dificultad_actual} | Pts:{score} | "
                f"Monedas:{monedas_recogidas} | x{combo_multiplicador} | {dtxt}")
        txt(hud, 160, 27, NEGRO, fuente_hud)
        dibujar_hud_powerups(pantalla)
        dibujar_timer_hud()

        if boss and boss_activado and not boss["muerto"]:
            if pygame.time.get_ticks() % 1200 < 600:
                bi = fuente_hud.render("DERROTA AL BOSS CON DASH (E)", True, COLOR_BOSS)
                pantalla.blit(bi, (ANCHO // 2 - bi.get_width() // 2, ALTO - 44))
        elif pygame.time.get_ticks() % 6000 < 3000 and cd == 0:
            tip = fuente_hud.render("¡Usa E para matar enemigos de la lava!", True, (255, 200, 50))
            pantalla.blit(tip, (ANCHO // 2 - tip.get_width() // 2, ALTO - 40))

        if modo_2p:
            c2 = fuente_small.render("J1: FLECHAS ESPACIO E  |  J2: WASD F", True, (180, 220, 255))
            pantalla.blit(c2, (ANCHO // 2 - c2.get_width() // 2, ALTO - 38))

        if estado_actual == ESTADO_PAUSA:
            s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            s.fill((0, 0, 0, 160))
            pantalla.blit(s, (0, 0))
            txt("PAUSA", ANCHO // 2 - 70, 140, BLANCO, fuente_grande)
            btn_reanudar.dibujar(pantalla)
            btn_reiniciar.dibujar(pantalla)
            btn_p_salir.dibujar(pantalla)

    elif estado_actual == ESTADO_MENU:
        fondo_menu()
        t  = pygame.time.get_ticks()
        gr = int(180 + 75 * math.sin(t * 0.002))
        gg = int(220 + 35 * math.sin(t * 0.003 + 1))
        ti = fuente_titulo.render("HISTORIA PLATFORMER", True, (gr, gg, 255))
        pantalla.blit(ti, (ANCHO // 2 - ti.get_width() // 2, 120))
        pygame.draw.line(pantalla, (100, 120, 255), (ANCHO//2-200, 210), (ANCHO//2+200, 210), 2)
        btn_jugar.dibujar(pantalla)
        btn_config.dibujar(pantalla)
        btn_ranking_menu.dibujar(pantalla)
        btn_salir.dibujar(pantalla)
        hi = fuente_hud.render(
            "FLECHAS MOVERSE  |  ESPACIO SALTAR  |  E DASH  |  P PAUSA",
            True, (100, 130, 200))
        pantalla.blit(hi, (ANCHO // 2 - hi.get_width() // 2, ALTO - 50))

    elif estado_actual == ESTADO_DIFICULTAD:
        fondo_menu()
        td = fuente_grande.render("SELECCIONA MODO", True, BLANCO)
        pantalla.blit(td, (ANCHO // 2 - td.get_width() // 2, 110))
        btn_facil.dibujar(pantalla)
        btn_normal.dibujar(pantalla)
        btn_dificil.dibujar(pantalla)
        btn_inf.dibujar(pantalla)
        btn_reloj.dibujar(pantalla)
        btn_volver.dibujar(pantalla)
        desc = {
            btn_facil:   "Preguntas simples · 3 vidas",
            btn_normal:  "Preguntas medias · Boss final",
            btn_dificil: "Preguntas dificiles · Boss agresivo",
            btn_inf:     "Sin fin · 1 vida · Muro rapido",
            btn_reloj:   f"Completa en {TIEMPO_RELOJ_SEG}s · Bonus por tiempo",
        }
        for b, d in desc.items():
            ds = fuente_small.render(d, True, (160, 180, 220))
            pantalla.blit(ds, (b.rect.right + 16, b.rect.centery - ds.get_height() // 2))

    elif estado_actual == ESTADO_CONFIG:
        # ── Fondo animado ──
        fondo_menu()

        # ── Panel central semitransparente ──
        panel_w, panel_h = 540, 420
        panel_x = ANCHO // 2 - panel_w // 2
        panel_y = _PNL_Y
        s_panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        s_panel.fill((15, 10, 40, 215))
        pantalla.blit(s_panel, (panel_x, panel_y))
        pygame.draw.rect(pantalla, BTN_AZUL_NEON,
                         (panel_x, panel_y, panel_w, panel_h), 2, 16)
        # Línea decorativa superior
        pygame.draw.line(pantalla, BTN_HOVER_MAGENTA,
                         (panel_x + 40, panel_y + 2),
                         (panel_x + panel_w - 40, panel_y + 2), 2)

        # ── Título dentro del panel ──
        tc = fuente_grande.render("OPCIONES DE AUDIO", True, BTN_AZUL_NEON)
        pantalla.blit(tc, (ANCHO // 2 - tc.get_width() // 2, panel_y + 22))
        pygame.draw.line(pantalla, (50, 80, 160),
                         (panel_x + 30, panel_y + 82),
                         (panel_x + panel_w - 30, panel_y + 82), 1)

        # ── Ícono de nota musical decorativo ──
        nota = fuente_grande.render("♪", True, (80, 120, 200))
        pantalla.blit(nota, (panel_x + 18, panel_y + 15))
        pantalla.blit(nota, (panel_x + panel_w - nota.get_width() - 18, panel_y + 15))

        # ── Sliders ──
        slider_mm.dibujar(pantalla)
        slider_mj.dibujar(pantalla)
        slider_sfx.dibujar(pantalla)

        # ── Botón guardar ──
        btn_cfg_ok.dibujar(pantalla)

        # ── Hint ESC ──
        hint = fuente_small.render("ESC o click en GUARDAR para volver", True, (100, 130, 180))
        pantalla.blit(hint, (ANCHO // 2 - hint.get_width() // 2,
                             btn_cfg_ok.rect.bottom + 12))

    elif estado_actual == ESTADO_RANKING:
        dibujar_pantalla_ranking()

    elif estado_actual == ESTADO_GAMEOVER:
        dibujar_gameover()

    if pantalla_completa:
        av, bv = pantalla_real.get_size()
        esc    = min(av / ANCHO_JUEGO, bv / ALTO_JUEGO)
        af, bf = int(ANCHO_JUEGO * esc), int(ALTO_JUEGO * esc)
        ps     = pygame.transform.scale(pantalla, (af, bf))
        pantalla_real.fill((0, 0, 0))
        pantalla_real.blit(ps, ((av - af) // 2, (bv - bf) // 2))
    else:
        pantalla_real.blit(pantalla, (0, 0))

    pygame.display.flip()