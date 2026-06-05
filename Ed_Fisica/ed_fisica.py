import pygame
import random
import sys
import math
import os
# ====================== RESOLVER RUTA (PyInstaller) ======================
def resolver_ruta(ruta_relativa):
    """ Obtiene la ruta absoluta de los recursos, compatible con PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)
# =========================================================================
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
# === VENTANA ===
ANCHO, ALTO = 1100, 720
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Camino a una Vida Saludable")
reloj = pygame.time.Clock()

# ---------------------------------------------------------------
# COLORES - paleta deportivo/moderna azul + naranja
# ---------------------------------------------------------------
BLANCO       = (255, 255, 255)
NEGRO        = (8,   12,  20)
GRIS_CLAR    = (200, 210, 225)
GRIS         = (130, 145, 165)
GRIS_OSC     = (70,  85, 105)
FONDO_OSC    = (10,  18,  38)
FONDO_MED    = (16,  28,  56)
FONDO_PANEL  = (20,  36,  68)

AZUL_PROF    = (14,  52, 138)
AZUL_VIF     = (28,  88, 210)
AZUL_CLAR    = (75, 155, 255)
AZUL_HIELO   = (175, 215, 255)

NARANJA_VIF  = (255, 115,  18)
NARANJA_CLAR = (255, 165,  65)
NARANJA_OSC  = (195,  75,   5)

COL_J1       = (28,  135, 255)
COL_J1_CLAR  = (100, 185, 255)
COL_J2       = (255,  88,  18)
COL_J2_CLAR  = (255, 160,  75)

COL_AVANZA    = (35,  195, 115)
COL_RETROCEDE = (215,  55,  55)
COL_PREGUNTA  = (55,  125, 235)
COL_NORMAL_A  = (26,   48,  88)
COL_NORMAL_B  = (32,   58, 105)
COL_BORDE     = (48,   78, 128)
COL_META      = (255, 198,   0)

AMARILLO     = (255, 205,  28)
VERDE_VIF    = (38,  205,  98)

# ---------------------------------------------------------------
# FUENTES - sin emojis, todas en Arial para maxima legibilidad
# ---------------------------------------------------------------
fuente_titulo  = pygame.font.SysFont("Arial", 46, bold=True)
fuente_grande  = pygame.font.SysFont("Arial", 32, bold=True)
fuente_med     = pygame.font.SysFont("Arial", 24, bold=True)
fuente_normal  = pygame.font.SysFont("Arial", 20)
fuente_peque   = pygame.font.SysFont("Arial", 15)
fuente_num     = pygame.font.SysFont("Arial", 13, bold=True)


# MUSICA
# Archivos deben estar dentro de la carpeta "ed_fisica/"
#   musica_menu.mp3  (o .ogg / .wav)
#   musica_juego.mp3 (o .ogg / .wav)
# ---------------------------------------------------------------
def _buscar_audio(nombre_base):
    for ext in [".mp3", ".ogg", ".wav", ".flac"]:
        ruta = resolver_ruta(f"ed_fisica/{nombre_base}{ext}")
        if os.path.isfile(ruta):
            return ruta
    return None

MUSICA_MENU_PATH  = _buscar_audio("musica_menu")
MUSICA_JUEGO_PATH = _buscar_audio("musica_juego")


class GestorMusica:
    def __init__(self):
        self.modo_actual  = None
        self.activa       = True
        self.volumen      = 0.5
        self.usa_archivo  = False
        # Melodia procedural de respaldo
        self.notas_menu  = [392,440,494,523,494,523,587,523,
                            440,392,349,392,440,494,440,392]
        self.notas_juego = [523,587,659,698,659,587,523,494,
                            440,494,523,587,523,494,440,392]
        self.idx_nota = 0
        self.ultimo   = 0
        self.intervalo = 380

    def cambiar_modo(self, modo):
        if modo == self.modo_actual:
            return
        self.modo_actual = modo
        self.idx_nota    = 0
        if not self.activa:
            return
        ruta = None
        if modo == "menu"  and MUSICA_MENU_PATH:
            ruta = MUSICA_MENU_PATH
        if modo == "juego" and MUSICA_JUEGO_PATH:
            ruta = MUSICA_JUEGO_PATH
        if ruta:
            try:
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.set_volume(self.volumen)
                pygame.mixer.music.play(-1)
                self.usa_archivo = True
                return
            except Exception:
                pass
        self.usa_archivo = False
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def update_procedural(self, ahora):
        if not self.activa or self.usa_archivo:
            return
        if ahora - self.ultimo < self.intervalo:
            return
        self.ultimo = ahora
        notas = self.notas_menu if self.modo_actual == "menu" else self.notas_juego
        freq  = notas[self.idx_nota % len(notas)]
        dur   = 0.28 if self.idx_nota % 4 != 2 else 0.15
        snd   = _gen_tono(freq, dur, self.volumen * 0.2, "sine")
        snd.play()
        self.idx_nota += 1

    def set_volumen(self, v):
        self.volumen = max(0.0, min(1.0, v))
        if self.usa_archivo:
            try:
                pygame.mixer.music.set_volume(self.volumen)
            except Exception:
                pass

    def toggle(self):
        self.activa = not self.activa
        if not self.activa:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            self.usa_archivo = False
        else:
            m = self.modo_actual
            self.modo_actual = None
            self.cambiar_modo(m)


gestor_musica = GestorMusica()

# ---------------------------------------------------------------
# SPRITES
# Coloca en la misma carpeta del script:
#   sprite_j1.png  -> ficha Jugador 1
#   sprite_j2.png  -> ficha Jugador 2
# ---------------------------------------------------------------
def _cargar_sprite(nombre):
    for ext in [".png", ".jpg", ".bmp"]:
        ruta = resolver_ruta(f"ed_fisica/{nombre}{ext}")
        if os.path.isfile(ruta):
            try:
                return pygame.image.load(ruta).convert_alpha()
            except Exception:
                pass
    return None


SPRITE_J1_ORIG = _cargar_sprite("sprite_j1")
SPRITE_J2_ORIG = _cargar_sprite("sprite_j2")

# ---------------------------------------------------------------
# SONIDOS SINTETICOS
# ---------------------------------------------------------------
def _gen_tono(freq=440, dur=0.15, vol=0.35, forma="sine", fade=True):
    sr = 44100
    n  = int(sr * dur)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sr
        if forma == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif forma == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            v = 2 * (t * freq - math.floor(t * freq + 0.5))
        e = (1.0 - (i/n)**0.5) if fade else 1.0
        s = max(-32768, min(32767, int(v * e * vol * 32767)))
        buf[i*2]   = s & 0xFF
        buf[i*2+1] = (s >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

def _gen_acorde(freqs, dur=0.3, vol=0.3):
    sr = 44100
    n  = int(sr * dur)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sr
        v = sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs)
        e = 1.0 - (i/n)
        s = max(-32768, min(32767, int(v * e * vol * 32767)))
        buf[i*2]   = s & 0xFF
        buf[i*2+1] = (s >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

SND_DADO       = _gen_tono(300, 0.12, 0.4, "square")
SND_MOVER      = _gen_tono(523, 0.10, 0.3)
SND_AVANZA     = _gen_acorde([523, 659, 784], 0.35, 0.4)
SND_RETROCEDE  = _gen_tono(200, 0.25, 0.4, "square")
SND_PREGUNTA   = _gen_tono(660, 0.15, 0.3)
SND_CORRECTO   = _gen_acorde([523, 659, 784, 1047], 0.5, 0.45)
SND_INCORRECTO = _gen_tono(150, 0.3, 0.4, "square")
SND_VICTORIA   = _gen_acorde([523, 659, 784, 1047, 1319], 0.8, 0.5)
SND_CLICK      = _gen_tono(500, 0.06, 0.2)

# ---------------------------------------------------------------
# SLIDER DE VOLUMEN
# ---------------------------------------------------------------
class SliderVolumen:
    def __init__(self, x, y, ancho=160):
        self.x     = x
        self.y     = y
        self.ancho = ancho
        self.valor = gestor_musica.volumen
        self.arrastrando = False

    def dibujar(self, surf):
        cy = self.y + 10
        lbl = fuente_peque.render("VOLUMEN", True, GRIS_CLAR)
        surf.blit(lbl, (self.x, self.y - 18))
        # Riel fondo
        pygame.draw.rect(surf, GRIS_OSC,  (self.x, cy-4, self.ancho, 8), border_radius=4)
        # Riel activo
        w = int(self.ancho * self.valor)
        pygame.draw.rect(surf, AZUL_VIF,  (self.x, cy-4, w, 8), border_radius=4)
        # Perilla
        px = self.x + w
        pygame.draw.circle(surf, BLANCO,    (px, cy), 10)
        pygame.draw.circle(surf, AZUL_CLAR, (px, cy), 10, 2)
        # Porcentaje
        pct = fuente_peque.render(f"{int(self.valor*100)}%", True, GRIS_CLAR)
        surf.blit(pct, (self.x + self.ancho + 8, cy - pct.get_height()//2))

    def manejar(self, ev):
        zona = pygame.Rect(self.x - 10, self.y - 12, self.ancho + 30, 44)
        if ev.type == pygame.MOUSEBUTTONDOWN and zona.collidepoint(ev.pos):
            self.arrastrando = True
            self._set(ev.pos[0])
        elif ev.type == pygame.MOUSEBUTTONUP:
            self.arrastrando = False
        elif ev.type == pygame.MOUSEMOTION and self.arrastrando:
            self._set(ev.pos[0])

    def _set(self, mx):
        self.valor = max(0.0, min(1.0, (mx - self.x) / self.ancho))
        gestor_musica.set_volumen(self.valor)

# ---------------------------------------------------------------
# TABLERO
# ---------------------------------------------------------------
TOTAL_CASILLAS = 36
COLS  = 12
FILAS = 3
ORIG_X = 48
ORIG_Y = 215
TAM_C  = 72

def calcular_casillas():
    pos = []
    for fila in range(FILAS):
        y = ORIG_Y + fila * (TAM_C + 6)
        rango = range(COLS) if fila % 2 == 0 else range(COLS-1, -1, -1)
        for col in rango:
            pos.append((ORIG_X + col * (TAM_C + 4), y))
    return pos

CASILLAS_POS = calcular_casillas()

ESPECIALES = {}
for c in [5, 12, 20, 27]:
    ESPECIALES[c] = ("avanza", 3, "Ejercicio extra! +3")
for c in [8, 16, 24, 31]:
    ESPECIALES[c] = ("retrocede", 3, "Lesion! -3")
for c in [3, 7, 11, 15, 19, 23, 28, 32]:
    ESPECIALES[c] = ("pregunta", 0, "Pregunta!")

# ---------------------------------------------------------------
# PREGUNTAS (sin caracteres especiales para mejor legibilidad)
# ---------------------------------------------------------------
PREGUNTAS = [
    {"pregunta": "Cuantos minutos de ejercicio diario recomienda la OMS?",
     "opciones": ["15 minutos", "30 minutos", "60 minutos", "90 minutos"],
     "correcta": 1,
     "feedback": "La OMS recomienda 30 minutos de actividad moderada diaria."},
    {"pregunta": "Cuantos vasos de agua se recomienda beber al dia?",
     "opciones": ["4 vasos", "6 vasos", "8 vasos", "12 vasos"],
     "correcta": 2,
     "feedback": "Se recomiendan 8 vasos (aprox. 2 litros) al dia."},
    {"pregunta": "Que ejercicio fortalece mas el corazon?",
     "opciones": ["Yoga", "Pesas", "Cardio aerobico", "Stretching"],
     "correcta": 2,
     "feedback": "El cardio aerobico como correr o nadar fortalece el corazon."},
    {"pregunta": "Cuantas horas de sueno necesita un adolescente?",
     "opciones": ["5-6 horas", "7-8 horas", "8-10 horas", "11-12 horas"],
     "correcta": 2,
     "feedback": "Los adolescentes necesitan entre 8 y 10 horas de sueno."},
    {"pregunta": "Cual es la principal fuente de energia del cuerpo?",
     "opciones": ["Proteinas", "Grasas", "Carbohidratos", "Vitaminas"],
     "correcta": 2,
     "feedback": "Los carbohidratos son el combustible principal del cuerpo."},
    {"pregunta": "Cual es el musculo mas grande del cuerpo humano?",
     "opciones": ["Biceps", "Pectoral", "Gluteo mayor", "Cuadriceps"],
     "correcta": 2,
     "feedback": "El gluteo mayor es el musculo mas grande del cuerpo."},
    {"pregunta": "Que deporte trabaja mas grupos musculares simultaneamente?",
     "opciones": ["Golf", "Natacion", "Tenis de mesa", "Dardos"],
     "correcta": 1,
     "feedback": "La natacion trabaja casi todos los musculos del cuerpo."},
    {"pregunta": "Cuanto tiempo antes de ejercitarse se recomienda comer?",
     "opciones": ["5 minutos", "30 minutos", "1 a 2 horas", "4 horas"],
     "correcta": 2,
     "feedback": "Lo ideal es comer entre 1 y 2 horas antes para tener energia."},
    {"pregunta": "Que mide el Indice de Masa Corporal (IMC)?",
     "opciones": ["Fuerza muscular", "Peso / altura al cuadrado",
                  "Porcentaje de grasa", "Frecuencia cardiaca"],
     "correcta": 1,
     "feedback": "El IMC es el peso en kg dividido por la altura en metros al cuadrado."},
    {"pregunta": "Cual de estas actividades NO es aerobica?",
     "opciones": ["Correr", "Nadar", "Ciclismo", "Levantar pesas"],
     "correcta": 3,
     "feedback": "Levantar pesas es un ejercicio anaerobico."},
    {"pregunta": "Frecuencia cardiaca maxima aproximada a los 20 anos?",
     "opciones": ["150 lpm", "180 lpm", "200 lpm", "220 lpm"],
     "correcta": 2,
     "feedback": "La formula es 220 menos la edad. A los 20 anos = 200 lpm."},
    {"pregunta": "Que vitamina produce el cuerpo con la luz solar?",
     "opciones": ["Vitamina A", "Vitamina B12", "Vitamina C", "Vitamina D"],
     "correcta": 3,
     "feedback": "La vitamina D se sintetiza en la piel con la exposicion solar."},
]

# ---------------------------------------------------------------
# PEONES POR CODIGO
# ---------------------------------------------------------------
def _dibujar_peon(surf, cx, cy_base, col_base, col_clar, col_borde, escala=1.0):
    r   = max(1, int(10 * escala))
    bw  = max(2, int(26 * escala))
    bh  = max(2, int(8  * escala))
    cuw = max(2, int(8  * escala))
    cuh = max(2, int(6  * escala))
    cow = max(2, int(18 * escala))
    coh = max(2, int(10 * escala))
    # Sombra base
    sh = pygame.Surface((bw+6, 5), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0,0,0,65), (0, 0, bw+6, 5))
    surf.blit(sh, (cx-(bw+6)//2, cy_base-2))
    # Base
    pygame.draw.rect(surf, col_borde,
                     pygame.Rect(cx-bw//2, cy_base-bh, bw, bh), border_radius=3)
    pygame.draw.rect(surf, col_base,
                     pygame.Rect(cx-bw//2+2, cy_base-bh+1, bw-4, bh-2), border_radius=3)
    # Cuerpo
    coy = cy_base - bh - coh
    pygame.draw.rect(surf, col_borde,
                     pygame.Rect(cx-cow//2, coy, cow, coh), border_radius=3)
    pygame.draw.rect(surf, col_base,
                     pygame.Rect(cx-cow//2+2, coy+1, cow-4, coh-2), border_radius=2)
    # Cuello
    cuy = coy - cuh
    pygame.draw.rect(surf, col_borde,
                     pygame.Rect(cx-cuw//2, cuy, cuw, cuh), border_radius=2)
    pygame.draw.rect(surf, col_base,
                     pygame.Rect(cx-cuw//2+1, cuy+1, cuw-2, cuh-2), border_radius=2)
    # Cabeza
    hcy = cuy - r
    pygame.draw.circle(surf, col_borde, (cx, hcy), r+1)
    pygame.draw.circle(surf, col_base,  (cx, hcy), r)
    pygame.draw.circle(surf, col_clar,
                       (cx - max(1,r//3), hcy - max(1,r//3)), max(1,r//3))

# ---------------------------------------------------------------
# ESTADO DEL JUEGO
# ---------------------------------------------------------------
class EstadoJuego:
    def __init__(self):
        self.modo_un_jugador = False
        self.reset()

    def reset(self):
        self.pos             = [0, 0]
        self.turno           = 0
        self.dado_val        = None
        self.dado_anim       = 0
        self.mensaje         = ""
        self.sub_mensaje     = ""
        self.ganador         = None
        self.scores          = [0, 0]
        self.pregunta_activa = None
        self.esperando_resp  = False
        self.resultado_resp  = None
        self.show_resultado  = 0
        self.dado_resultado  = None
        self.bloqueado       = False
        self.historial       = []
        self.ia_timer        = 0
        self.ia_respondiendo = False
        self.ia_resp_idx     = None
        self._ia_delay       = None

estado = EstadoJuego()

# ---------------------------------------------------------------
# DADO
# ---------------------------------------------------------------
PUNTOS_DADO = {
    1: [(0.5,0.5)],
    2: [(0.28,0.28),(0.72,0.72)],
    3: [(0.28,0.28),(0.5,0.5),(0.72,0.72)],
    4: [(0.28,0.28),(0.72,0.28),(0.28,0.72),(0.72,0.72)],
    5: [(0.28,0.28),(0.72,0.28),(0.5,0.5),(0.28,0.72),(0.72,0.72)],
    6: [(0.28,0.22),(0.72,0.22),(0.28,0.5),(0.72,0.5),(0.28,0.78),(0.72,0.78)],
}

def dibujar_dado(x, y, tam, valor, animando=False):
    pygame.draw.rect(pantalla, (0,0,0), (x+4, y+5, tam, tam), border_radius=12)
    if animando:
        fase = (pygame.time.get_ticks() // 80) % 2
        cd   = AZUL_PROF if fase == 0 else AZUL_VIF
        pygame.draw.rect(pantalla, cd, (x, y, tam, tam), border_radius=12)
        pygame.draw.rect(pantalla, AZUL_CLAR, (x, y, tam, tam), 2, border_radius=12)
        q = fuente_grande.render("?", True, AZUL_HIELO)
        pantalla.blit(q, (x+tam//2-q.get_width()//2, y+tam//2-q.get_height()//2))
        return
    pygame.draw.rect(pantalla, BLANCO,   (x, y, tam, tam), border_radius=12)
    pygame.draw.rect(pantalla, AZUL_VIF, (x, y, tam, tam), 3, border_radius=12)
    if valor and valor in PUNTOS_DADO:
        for rx, ry in PUNTOS_DADO[valor]:
            pygame.draw.circle(pantalla, AZUL_PROF,
                               (x+int(rx*tam), y+int(ry*tam)), tam//9)

# ---------------------------------------------------------------
# FICHA EN TABLERO
# ---------------------------------------------------------------
def dibujar_ficha_tablero(x, y, jugador):
    offset_x = -7 if jugador == 0 else 7
    bounce   = int(3 * abs(math.sin(pygame.time.get_ticks()/350 + jugador * math.pi)))
    cx = x + TAM_C//2 + offset_x
    cy = y + TAM_C - 5 - bounce

    sprite = SPRITE_J1_ORIG if jugador == 0 else SPRITE_J2_ORIG
    if sprite:
        ts  = TAM_C - 12
        img = pygame.transform.smoothscale(sprite, (ts, ts))
        pantalla.blit(img, (cx - ts//2, cy - ts))
    else:
        cb  = COL_J1      if jugador == 0 else COL_J2
        cc  = COL_J1_CLAR if jugador == 0 else COL_J2_CLAR
        cbo = AZUL_PROF   if jugador == 0 else NARANJA_OSC
        s   = pygame.Surface((TAM_C, TAM_C), pygame.SRCALPHA)
        _dibujar_peon(s, TAM_C//2+offset_x, TAM_C-5-bounce, cb, cc, cbo, 1.1)
        lbl = fuente_num.render("J1" if jugador==0 else "J2", True, BLANCO)
        s.blit(lbl, (TAM_C//2+offset_x - lbl.get_width()//2, TAM_C-5-bounce-48))
        pantalla.blit(s, (x, y))

# ---------------------------------------------------------------
# TABLERO
# ---------------------------------------------------------------
ICONO_CASILLA = {"avanza": "+", "retrocede": "-", "pregunta": "?"}
COLOR_TIPO    = {"avanza": COL_AVANZA, "retrocede": COL_RETROCEDE, "pregunta": COL_PREGUNTA}

def dibujar_tablero():
    mar = 10
    aw  = COLS * (TAM_C+4) + mar
    ah  = FILAS * (TAM_C+6) + mar*2
    pygame.draw.rect(pantalla, (8,22,52),
                     (ORIG_X-mar, ORIG_Y-mar, aw, ah), border_radius=14)
    pygame.draw.rect(pantalla, AZUL_VIF,
                     (ORIG_X-mar, ORIG_Y-mar, aw, ah), 2, border_radius=14)

    for i, (x, y) in enumerate(CASILLAS_POS):
        es_meta = (i == TOTAL_CASILLAS-1)
        if es_meta:
            col = COL_META
        elif i in ESPECIALES:
            col = COLOR_TIPO[ESPECIALES[i][0]]
        else:
            col = COL_NORMAL_A if i%2==0 else COL_NORMAL_B

        pygame.draw.rect(pantalla, (0,0,0),
                         (x+2, y+3, TAM_C-2, TAM_C-2), border_radius=7)
        pygame.draw.rect(pantalla, col,
                         (x, y, TAM_C-2, TAM_C-2), border_radius=7)
        borde = AMARILLO if es_meta else COL_BORDE
        pygame.draw.rect(pantalla, borde,
                         (x, y, TAM_C-2, TAM_C-2), 1, border_radius=7)

        col_n = NEGRO if es_meta else GRIS_CLAR
        n = fuente_num.render(str(i+1), True, col_n)
        pantalla.blit(n, (x+3, y+2))

        if es_meta:
            ic = fuente_grande.render("*", True, NEGRO)
            pantalla.blit(ic, (x+TAM_C//2-ic.get_width()//2-1,
                                y+TAM_C//2-ic.get_height()//2+3))
        elif i in ESPECIALES:
            sym = ICONO_CASILLA[ESPECIALES[i][0]]
            col_ic = BLANCO if ESPECIALES[i][0]!="retrocede" else (255,215,215)
            ic = fuente_grande.render(sym, True, col_ic)
            pantalla.blit(ic, (x+TAM_C//2-ic.get_width()//2,
                                y+TAM_C//2-ic.get_height()//2+4))

# ---------------------------------------------------------------
# PANEL LATERAL
# ---------------------------------------------------------------
def dibujar_panel(slider):
    px = ORIG_X + COLS*(TAM_C+4) + 18
    py = ORIG_Y - 10
    pw = ANCHO - px - 14
    ph = FILAS*(TAM_C+6) + 20

    pygame.draw.rect(pantalla, FONDO_PANEL, (px, py, pw, ph), border_radius=14)
    pygame.draw.rect(pantalla, AZUL_VIF,    (px, py, pw, ph), 2, border_radius=14)

    tit = fuente_med.render("JUGADORES", True, NARANJA_CLAR)
    pantalla.blit(tit, (px+pw//2-tit.get_width()//2, py+10))
    pygame.draw.line(pantalla, AZUL_VIF, (px+10, py+42), (px+pw-10, py+42), 1)

    nombres = ["Jugador 1", "IA (Rival)" if estado.modo_un_jugador else "Jugador 2"]

    for i in range(2):
        oy       = py + 52 + i*125
        col_j    = COL_J1_CLAR if i==0 else COL_J2_CLAR
        es_turno = (estado.turno == i)
        if es_turno and i==0:
            bg = (28,58,108)
        elif es_turno and i==1:
            bg = (78,33,8)
        else:
            bg = (16,30,55)
        pygame.draw.rect(pantalla, bg,    (px+6, oy-3, pw-12, 110), border_radius=10)
        if es_turno:
            pygame.draw.rect(pantalla, col_j, (px+6, oy-3, pw-12, 110), 2, border_radius=10)

        # Mini ficha
        sp = SPRITE_J1_ORIG if i==0 else SPRITE_J2_ORIG
        if sp:
            mini = pygame.transform.smoothscale(sp, (38, 38))
            pantalla.blit(mini, (px+8, oy+5))
        else:
            cb  = COL_J1      if i==0 else COL_J2
            cc  = COL_J1_CLAR if i==0 else COL_J2_CLAR
            cbo = AZUL_PROF   if i==0 else NARANJA_OSC
            ps  = pygame.Surface((40, 50), pygame.SRCALPHA)
            _dibujar_peon(ps, 20, 46, cb, cc, cbo, 0.9)
            pantalla.blit(ps, (px+6, oy+3))

        ns = fuente_normal.render(nombres[i], True, col_j)
        pantalla.blit(ns, (px+52, oy+8))

        cs = fuente_peque.render(f"Casilla: {estado.pos[i]+1} / {TOTAL_CASILLAS}", True, GRIS_CLAR)
        pantalla.blit(cs, (px+12, oy+36))
        ps2 = fuente_peque.render(f"Puntos:  {estado.scores[i]}", True, AMARILLO)
        pantalla.blit(ps2, (px+12, oy+56))

        progreso = estado.pos[i] / (TOTAL_CASILLAS-1)
        bw = pw - 28
        pygame.draw.rect(pantalla, (28,38,68), (px+12, oy+80, bw, 10), border_radius=5)
        if progreso > 0:
            pygame.draw.rect(pantalla, col_j,
                             (px+12, oy+80, int(bw*progreso), 10), border_radius=5)
        pygame.draw.rect(pantalla, AZUL_VIF, (px+12, oy+80, bw, 10), 1, border_radius=5)

        if es_turno:
            fch = fuente_med.render("<", True, NARANJA_CLAR)
            pantalla.blit(fch, (px+pw-24, oy+14))

    # Dado
    dibujar_dado(px+pw//2-35, py+ph-112, 70, estado.dado_val,
                 animando=(estado.dado_anim > 0))

    # Slider de volumen
    if slider:
        slider.x = px + 8
        slider.y = py + ph + 36
        slider.ancho = pw - 50
        slider.dibujar(pantalla)

    # Leyenda
    ley_y = py + ph + 10
    for col_l, lbl_txt in [
        (COL_AVANZA,    "+  Avanza 3"),
        (COL_RETROCEDE, "-  Retrocede 3"),
        (COL_PREGUNTA,  "?  Pregunta +2pts"),
    ]:
        pygame.draw.rect(pantalla, col_l, (px+6, ley_y+2, 12, 12), border_radius=3)
        t = fuente_peque.render(lbl_txt, True, GRIS_CLAR)
        pantalla.blit(t, (px+22, ley_y))
        ley_y += 20

# ---------------------------------------------------------------
# BOTON TIRAR DADO
# ---------------------------------------------------------------
BOTON_DADO = pygame.Rect(ORIG_X, ORIG_Y + FILAS*(TAM_C+6) + 16, 295, 52)

def dibujar_boton_dado():
    es_ia  = estado.modo_un_jugador and estado.turno == 1
    desact = estado.bloqueado or estado.esperando_resp or estado.ganador or es_ia
    if desact:
        col = (35, 50, 78)
    else:
        hover = BOTON_DADO.collidepoint(pygame.mouse.get_pos())
        col   = (38, 135, 255) if hover else (22, 96, 205)

    pygame.draw.rect(pantalla, (0,0,0), (BOTON_DADO.x+3, BOTON_DADO.y+4,
                                          BOTON_DADO.w, BOTON_DADO.h), border_radius=13)
    pygame.draw.rect(pantalla, col, BOTON_DADO, border_radius=13)
    bc = tuple(min(255, c+50) for c in col)
    pygame.draw.rect(pantalla, bc, BOTON_DADO, 2, border_radius=13)

    lbl = "Jugador 1" if estado.turno==0 else ("IA" if estado.modo_un_jugador else "Jugador 2")
    tc  = GRIS if desact else BLANCO
    t   = fuente_normal.render(f"Tirar dado  -  {lbl}", True, tc)
    pantalla.blit(t, (BOTON_DADO.centerx-t.get_width()//2,
                       BOTON_DADO.centery-t.get_height()//2))

# ---------------------------------------------------------------
# MENSAJE E HISTORIAL
# ---------------------------------------------------------------
def dibujar_mensaje():
    if estado.mensaje:
        t = fuente_med.render(estado.mensaje, True, BLANCO)
        pantalla.blit(t, (ORIG_X, 150))
    if estado.sub_mensaje:
        s = fuente_normal.render(estado.sub_mensaje, True, NARANJA_CLAR)
        pantalla.blit(s, (ORIG_X, 180))

def dibujar_historial():
    hx = ORIG_X
    hy = ORIG_Y + FILAS*(TAM_C+6) + 80
    tit = fuente_peque.render("ULTIMAS JUGADAS:", True, AZUL_CLAR)
    pantalla.blit(tit, (hx, hy))
    for k, ent in enumerate(estado.historial[-4:]):
        t = fuente_peque.render(f"  {ent}", True, GRIS_CLAR)
        pantalla.blit(t, (hx, hy+20+k*18))

# ---------------------------------------------------------------
# VENTANA PREGUNTA
# ---------------------------------------------------------------
def dibujar_pregunta():
    if not estado.esperando_resp:
        return []
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 4, 18, 178))
    pantalla.blit(overlay, (0, 0))

    wx, wy, ww, wh = 95, 75, ANCHO-190, ALTO-150
    pygame.draw.rect(pantalla, (0,0,0), (wx+6, wy+6, ww, wh), border_radius=20)
    pygame.draw.rect(pantalla, FONDO_MED, (wx, wy, ww, wh), border_radius=20)
    pygame.draw.rect(pantalla, AZUL_VIF,  (wx, wy, ww, wh), 3, border_radius=20)

    # Header coloreado segun jugador
    col_hdr = COL_J1 if estado.turno==0 else COL_J2
    pygame.draw.rect(pantalla, col_hdr, (wx, wy, ww, 58), border_radius=20)
    pygame.draw.rect(pantalla, col_hdr, (wx, wy+38, ww, 20))

    nombre_j = "JUGADOR 1" if estado.turno==0 else \
               ("IA" if estado.modo_un_jugador else "JUGADOR 2")
    hdr = fuente_med.render(f"RESPONDE {nombre_j}", True, BLANCO)
    pantalla.blit(hdr, (wx+ww//2-hdr.get_width()//2, wy+16))

    # Mini peon en header
    sp_hdr = SPRITE_J1_ORIG if estado.turno==0 else SPRITE_J2_ORIG
    if sp_hdr:
        mini = pygame.transform.smoothscale(sp_hdr, (40, 40))
        pantalla.blit(mini, (wx+16, wy+9))
    else:
        cb  = COL_J1      if estado.turno==0 else COL_J2
        cc  = COL_J1_CLAR if estado.turno==0 else COL_J2_CLAR
        cbo = AZUL_PROF   if estado.turno==0 else NARANJA_OSC
        sh  = pygame.Surface((38, 46), pygame.SRCALPHA)
        _dibujar_peon(sh, 19, 42, cb, cc, cbo, 0.9)
        pantalla.blit(sh, (wx+14, wy+8))

    # Pregunta con wrap
    pq = estado.pregunta_activa
    palabras = pq["pregunta"].split()
    lineas, lin = [], ""
    for p in palabras:
        prueba = (lin+" "+p).strip()
        if fuente_normal.size(prueba)[0] < ww-70:
            lin = prueba
        else:
            if lin: lineas.append(lin)
            lin = p
    if lin: lineas.append(lin)

    qy = wy + 72
    for line in lineas:
        ls = fuente_normal.render(line, True, BLANCO)
        pantalla.blit(ls, (wx+32, qy))
        qy += 26

    # Opciones
    bw_op = ww - 76
    botones = []
    for k, op in enumerate(pq["opciones"]):
        by = wy + 152 + k*64
        bx = wx + 38
        br = pygame.Rect(bx, by, bw_op, 50)
        botones.append(br)

        if estado.resultado_resp is not None:
            if k == pq["correcta"]:
                cb_op, cbo_op = (28,155,75), VERDE_VIF
            elif estado.resultado_resp is False and k != pq["correcta"]:
                cb_op, cbo_op = (135,28,28), (215,58,58)
            else:
                cb_op, cbo_op = (22,42,80), AZUL_VIF
        else:
            hover  = br.collidepoint(pygame.mouse.get_pos())
            col_jh = COL_J1_CLAR if estado.turno==0 else COL_J2_CLAR
            cb_op  = (28,78,158) if hover else (18,44,88)
            cbo_op = col_jh if hover else AZUL_VIF

        pygame.draw.rect(pantalla, (0,0,0), (bx+2, by+3, bw_op, 50), border_radius=9)
        pygame.draw.rect(pantalla, cb_op,   br, border_radius=9)
        pygame.draw.rect(pantalla, cbo_op,  br, 2, border_radius=9)

        pygame.draw.rect(pantalla, col_hdr, (bx+8, by+9, 30, 30), border_radius=5)
        letra = fuente_normal.render(["A","B","C","D"][k], True, BLANCO)
        pantalla.blit(letra, (bx+8+15-letra.get_width()//2, by+13))

        op_t = fuente_normal.render(op, True, BLANCO)
        pantalla.blit(op_t, (bx+46, by+13))

    # Resultado
    if estado.resultado_resp is not None:
        rc  = (75,250,125) if estado.resultado_resp else (255,85,85)
        rt  = "CORRECTO!  +2 puntos" if estado.resultado_resp else "INCORRECTO"
        rs  = fuente_grande.render(rt, True, rc)
        pantalla.blit(rs, (wx+ww//2-rs.get_width()//2, wy+wh-74))
        fd  = fuente_peque.render(pq["feedback"], True, NARANJA_CLAR)
        pantalla.blit(fd, (wx+ww//2-fd.get_width()//2, wy+wh-40))

    return botones

# ---------------------------------------------------------------
# IA
# ---------------------------------------------------------------
def ia_pensar():
    estado.ia_respondiendo = True
    estado.ia_timer = 85
    pq = estado.pregunta_activa
    if random.random() < 0.75:
        estado.ia_resp_idx = pq["correcta"]
    else:
        malas = [i for i in range(4) if i != pq["correcta"]]
        estado.ia_resp_idx = random.choice(malas)

# ---------------------------------------------------------------
# LOGICA
# ---------------------------------------------------------------
def tirar_dado():
    if estado.bloqueado or estado.esperando_resp or estado.ganador:
        return
    SND_DADO.play()
    val = random.randint(1, 6)
    estado.dado_val      = val
    estado.dado_anim     = 28
    estado.dado_resultado = val
    estado.bloqueado     = True

def aplicar_movimiento():
    j    = estado.turno
    val  = estado.dado_resultado
    nueva = min(estado.pos[j] + val, TOTAL_CASILLAS-1)
    estado.pos[j] = nueva
    SND_MOVER.play()
    nj = "J1" if j==0 else "J2"
    estado.historial.append(f"{nj}: saco {val} -> casilla {nueva+1}")

    nombre = "Jugador 1" if j==0 else ("IA" if estado.modo_un_jugador else "Jugador 2")

    if nueva == TOTAL_CASILLAS-1:
        estado.mensaje = f"{nombre} llego a la META!"
        return "victoria"

    if nueva in ESPECIALES:
        tipo, cant, desc = ESPECIALES[nueva]
        estado.sub_mensaje = desc
        if tipo == "avanza":
            SND_AVANZA.play()
            estado.pos[j] = min(nueva+cant, TOTAL_CASILLAS-1)
            estado.mensaje = f"{nombre}: {desc}"
            estado.historial.append(f"  Avanza a casilla {estado.pos[j]+1}")
            if estado.pos[j] == TOTAL_CASILLAS-1:
                return "victoria"
        elif tipo == "retrocede":
            SND_RETROCEDE.play()
            estado.pos[j] = max(nueva-cant, 0)
            estado.mensaje = f"{nombre}: {desc}"
            estado.historial.append(f"  Retrocede a casilla {estado.pos[j]+1}")
        elif tipo == "pregunta":
            SND_PREGUNTA.play()
            estado.pregunta_activa = random.choice(PREGUNTAS)
            estado.esperando_resp  = True
            estado.resultado_resp  = None
            estado.mensaje = f"Pregunta para {nombre}!"
            if estado.modo_un_jugador and j==1:
                ia_pensar()
            return "pregunta"
    else:
        estado.mensaje     = f"{nombre} avanzo {val} casillas"
        estado.sub_mensaje = ""

    estado.turno     = 1 - j
    estado.bloqueado = False
    return "ok"

def responder_pregunta(idx):
    pq = estado.pregunta_activa
    correcto = (idx == pq["correcta"])
    estado.resultado_resp = correcto
    if correcto:
        SND_CORRECTO.play()
        estado.scores[estado.turno] += 2
        estado.historial.append("  Respuesta correcta (+2 pts)")
    else:
        SND_INCORRECTO.play()
        estado.historial.append("  Respuesta incorrecta")
    estado.show_resultado = 150

# ---------------------------------------------------------------
# FONDO JUEGO
# ---------------------------------------------------------------
def dibujar_fondo_juego():
    for yp in range(ALTO):
        t = yp/ALTO
        c = (int(FONDO_OSC[0]*(1-t)+FONDO_MED[0]*t),
              int(FONDO_OSC[1]*(1-t)+FONDO_MED[1]*t),
              int(FONDO_OSC[2]*(1-t)+FONDO_MED[2]*t))
        pygame.draw.line(pantalla, c, (0,yp), (ANCHO,yp))
    pygame.draw.rect(pantalla, AZUL_PROF, (0, 0, ANCHO, 132))
    pygame.draw.rect(pantalla, NARANJA_VIF, (0, 130, ANCHO, 4))

    somb = fuente_grande.render("CAMINO A UNA VIDA SALUDABLE", True, (0,18,55))
    titu = fuente_grande.render("CAMINO A UNA VIDA SALUDABLE", True, BLANCO)
    pantalla.blit(somb, (ANCHO//2-somb.get_width()//2+2, 24))
    pantalla.blit(titu, (ANCHO//2-titu.get_width()//2,   22))

    col_t = COL_J1_CLAR if estado.turno==0 else COL_J2_CLAR
    nombre_t = "Jugador 1" if estado.turno==0 else \
               ("IA" if estado.modo_un_jugador else "Jugador 2")
    sub = fuente_normal.render(f"Turno: {nombre_t}", True, col_t)
    pantalla.blit(sub, (ANCHO//2-sub.get_width()//2, 80))

# ---------------------------------------------------------------
# PANTALLA CARGA
# ---------------------------------------------------------------
def pantalla_carga():
    pasos = ["Inicializando tablero...", "Cargando preguntas...",
             "Generando sonidos...", "Preparando fichas...", "Listo!"]
    for i, paso in enumerate(pasos):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        for yp in range(ALTO):
            t = yp/ALTO
            c = (int(8+8*t), int(14+16*t), int(32+18*t))
            pygame.draw.line(pantalla, c, (0,yp), (ANCHO,yp))

        t_seg = pygame.time.get_ticks()/1000
        radio = int(62 + 7*math.sin(t_seg*3))
        pygame.draw.circle(pantalla, AZUL_PROF,  (ANCHO//2, 195), radio+5)
        pygame.draw.circle(pantalla, AZUL_VIF,   (ANCHO//2, 195), radio)
        pygame.draw.circle(pantalla, AZUL_CLAR,  (ANCHO//2, 195), radio-15, 3)

        cx, cy = ANCHO//2, 195
        ta = t_seg * 4
        lo = int(10*math.sin(ta))
        ao = int(8*math.sin(ta+math.pi))
        pygame.draw.circle(pantalla, AMARILLO, (cx, cy-26), 12)
        pygame.draw.circle(pantalla, NEGRO,    (cx, cy-26), 12, 2)
        pygame.draw.line(pantalla, BLANCO, (cx, cy-14), (cx, cy+16), 4)
        pygame.draw.line(pantalla, BLANCO, (cx, cy-4),  (cx-16+ao, cy+11), 3)
        pygame.draw.line(pantalla, BLANCO, (cx, cy-4),  (cx+16-ao, cy+4),  3)
        pygame.draw.line(pantalla, BLANCO, (cx, cy+16), (cx-13, cy+32+lo), 3)
        pygame.draw.line(pantalla, BLANCO, (cx, cy+16), (cx+13, cy+32-lo), 3)

        tit = fuente_titulo.render("CAMINO A UNA VIDA SALUDABLE", True, AZUL_CLAR)
        pantalla.blit(tit, (ANCHO//2-tit.get_width()//2, 290))
        sub = fuente_normal.render("Juego de Educacion Fisica", True, NARANJA_CLAR)
        pantalla.blit(sub, (ANCHO//2-sub.get_width()//2, 344))

        prog = (i+1)/len(pasos)
        pygame.draw.rect(pantalla, (28,46,88), (200,398,700,20), border_radius=10)
        pygame.draw.rect(pantalla, NARANJA_VIF, (200,398,int(700*prog),20), border_radius=10)
        pygame.draw.rect(pantalla, AZUL_CLAR,   (200,398,700,20), 2, border_radius=10)
        pt = fuente_normal.render(paso, True, AZUL_HIELO)
        pantalla.blit(pt, (ANCHO//2-pt.get_width()//2, 430))
        pp = fuente_med.render(f"{int(prog*100)}%", True, NARANJA_CLAR)
        pantalla.blit(pp, (ANCHO//2-pp.get_width()//2, 462))

        pygame.display.flip()
        pygame.time.wait(430)

# ---------------------------------------------------------------
# MENU PRINCIPAL
# ---------------------------------------------------------------
def menu_principal():
    slider = SliderVolumen(ANCHO//2-120, 510, 240)
    slider.valor = gestor_musica.volumen

    boton_1p    = pygame.Rect(ANCHO//2-155, 300, 310, 60)
    boton_2p    = pygame.Rect(ANCHO//2-155, 374, 310, 60)
    boton_musica= pygame.Rect(ANCHO//2-155, 448, 310, 54)
    boton_salir = pygame.Rect(ANCHO//2-155, 558, 310, 50)

    estrellas = [(random.randint(0,ANCHO), random.randint(0,ALTO),
                  random.uniform(0.3,1.5), random.randint(1,3)) for _ in range(55)]

    gestor_musica.cambiar_modo("menu")

    def _btn(rect, texto, cb, ch):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        col   = ch if hover else cb
        borde = tuple(min(255, c+55) for c in col)
        pygame.draw.rect(pantalla, (0,0,0), (rect.x+3,rect.y+4,rect.w,rect.h), border_radius=13)
        pygame.draw.rect(pantalla, col,   rect, border_radius=13)
        pygame.draw.rect(pantalla, borde, rect, 2, border_radius=13)
        ts = fuente_med.render(texto, True, BLANCO)
        pantalla.blit(ts, (rect.centerx-ts.get_width()//2,
                           rect.centery-ts.get_height()//2))

    while True:
        ahora = pygame.time.get_ticks()
        gestor_musica.update_procedural(ahora)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            slider.manejar(ev)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if boton_1p.collidepoint(ev.pos):
                    SND_CLICK.play()
                    estado.modo_un_jugador = True
                    return
                if boton_2p.collidepoint(ev.pos):
                    SND_CLICK.play()
                    estado.modo_un_jugador = False
                    return
                if boton_musica.collidepoint(ev.pos):
                    SND_CLICK.play()
                    gestor_musica.toggle()
                if boton_salir.collidepoint(ev.pos):
                    pygame.quit(); sys.exit()

        for yp in range(ALTO):
            t = yp/ALTO
            c = (int(8*(1-t)+5*t), int(15*(1-t)+10*t), int(38*(1-t)+22*t))
            pygame.draw.line(pantalla, c, (0,yp), (ANCHO,yp))

        for sx,sy,br,rad in estrellas:
            al = int(100 + 80*math.sin(ahora/800+sx))
            pygame.draw.circle(pantalla, (al,al,min(255,al+50)), (int(sx),int(sy)), rad)

        # Panel titulo
        pw_t, ph_t = 720, 118
        px_t = ANCHO//2 - pw_t//2
        py_t = 52
        pygame.draw.rect(pantalla, (14,32,78), (px_t,py_t,pw_t,ph_t), border_radius=18)
        pygame.draw.rect(pantalla, AZUL_VIF,   (px_t,py_t,pw_t,ph_t), 2, border_radius=18)
        pygame.draw.rect(pantalla, NARANJA_VIF,
                         (px_t+10, py_t+ph_t-6, pw_t-20, 4), border_radius=2)

        oy_t = int(5*math.sin(ahora/1000*1.8))
        somb = fuente_titulo.render("CAMINO A UNA VIDA SALUDABLE", True, (0,28,78))
        titu = fuente_titulo.render("CAMINO A UNA VIDA SALUDABLE", True, BLANCO)
        pantalla.blit(somb, (ANCHO//2-somb.get_width()//2+2, py_t+14))
        pantalla.blit(titu, (ANCHO//2-titu.get_width()//2,   py_t+12+oy_t))
        sub_t = fuente_normal.render("Juego de Educacion Fisica", True, NARANJA_CLAR)
        pantalla.blit(sub_t, (ANCHO//2-sub_t.get_width()//2, py_t+76))

        # Peones decorativos
        ps1 = pygame.Surface((56, 76), pygame.SRCALPHA)
        ps2 = pygame.Surface((56, 76), pygame.SRCALPHA)
        sp1 = SPRITE_J1_ORIG
        sp2 = SPRITE_J2_ORIG
        if sp1:
            i1 = pygame.transform.smoothscale(sp1, (56,56))
            ps1.blit(i1, (0,20))
        else:
            _dibujar_peon(ps1, 28, 70, COL_J1, COL_J1_CLAR, AZUL_PROF, 1.4)
        if sp2:
            i2 = pygame.transform.smoothscale(sp2, (56,56))
            ps2.blit(i2, (0,20))
        else:
            _dibujar_peon(ps2, 28, 70, COL_J2, COL_J2_CLAR, NARANJA_OSC, 1.4)
        pantalla.blit(ps1, (ANCHO//2-75, 186))
        pantalla.blit(ps2, (ANCHO//2+20, 186))
        lj1 = fuente_peque.render("J1", True, COL_J1_CLAR)
        lj2 = fuente_peque.render("J2", True, COL_J2_CLAR)
        pantalla.blit(lj1, (ANCHO//2-75+28-lj1.get_width()//2, 268))
        pantalla.blit(lj2, (ANCHO//2+20+28-lj2.get_width()//2, 268))

        _btn(boton_1p,     "1 JUGADOR  (vs IA)",    (18,112,215), (36,145,255))
        _btn(boton_2p,     "2 JUGADORES",            (175,75,8),   (225,108,18))
        _btn(boton_musica, "MUSICA: ON" if gestor_musica.activa else "MUSICA: OFF",
                           (55,75,138), (78,108,178))
        _btn(boton_salir,  "SALIR",                  (118,28,28),  (165,48,48))

        slider.dibujar(pantalla)

        # Info archivos en la parte inferior
        info = [
            "MUSICA: coloca  musica_menu.mp3  y  musica_juego.mp3  junto al script",
            "SPRITES: coloca  sprite_j1.png  y  sprite_j2.png  junto al script",
        ]
        iy = 614
        for il in info:
            it = fuente_peque.render(il, True, GRIS_OSC)
            pantalla.blit(it, (ANCHO//2-it.get_width()//2, iy))
            iy += 18

        pygame.display.flip()
        reloj.tick(60)

# ---------------------------------------------------------------
# PANTALLA VICTORIA
# ---------------------------------------------------------------
def pantalla_victoria(ganador):
    estado.ganador = ganador
    SND_VICTORIA.play()
    gestor_musica.cambiar_modo("menu")
    t0 = pygame.time.get_ticks()
    confeti = [(random.randint(0,ANCHO), random.randint(-60,0),
                random.uniform(-2.5,2.5), random.uniform(2,7),
                random.choice([AMARILLO,AZUL_CLAR,NARANJA_CLAR,VERDE_VIF,(255,80,160),(0,200,230)]),
                random.randint(5,14))
               for _ in range(90)]

    boton_menu  = pygame.Rect(ANCHO//2-215, 534, 192, 52)
    boton_nuevo = pygame.Rect(ANCHO//2+22,  534, 192, 52)
    slider_v    = SliderVolumen(ANCHO//2-100, 610, 200)
    slider_v.valor = gestor_musica.volumen

    def _btn2(rect, texto, cb, ch):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        col   = ch if hover else cb
        borde = tuple(min(255, c+55) for c in col)
        pygame.draw.rect(pantalla, (0,0,0), (rect.x+3,rect.y+4,rect.w,rect.h), border_radius=12)
        pygame.draw.rect(pantalla, col,   rect, border_radius=12)
        pygame.draw.rect(pantalla, borde, rect, 2, border_radius=12)
        ts = fuente_normal.render(texto, True, BLANCO)
        pantalla.blit(ts, (rect.centerx-ts.get_width()//2,
                           rect.centery-ts.get_height()//2))

    while True:
        ahora = pygame.time.get_ticks()
        t_seg = (ahora-t0)/1000
        gestor_musica.update_procedural(ahora)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            slider_v.manejar(ev)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if boton_menu.collidepoint(ev.pos):
                    estado.reset()
                    return "menu"
                if boton_nuevo.collidepoint(ev.pos):
                    estado.reset()
                    return "juego"

        for yp in range(ALTO):
            t = yp/ALTO
            c = (int(8*(1-t)+5*t),int(15*(1-t)+10*t),int(38*(1-t)+22*t))
            pygame.draw.line(pantalla, c, (0,yp),(ANCHO,yp))

        nuevos = []
        for cx,cy,vx,vy,col,r in confeti:
            pygame.draw.circle(pantalla, col, (int(cx),int(cy)), r)
            ncy = cy + vy
            nuevos.append(((cx+vx)%ANCHO, ncy, vx, vy, col, r))
            if ncy > ALTO+20:
                nuevos[-1] = (random.randint(0,ANCHO), -30, vx, vy, col, r)
        confeti = nuevos

        pw, ph = 580, 330
        ppx, ppy = ANCHO//2-pw//2, ALTO//2-ph//2-52
        pulse = int(4*math.sin(t_seg*5))
        col_g = COL_J1 if ganador==0 else COL_J2
        pygame.draw.rect(pantalla, (0,0,0),
                         (ppx-pulse+4, ppy-pulse+5, pw+pulse*2, ph+pulse*2), border_radius=24)
        pygame.draw.rect(pantalla, FONDO_PANEL,
                         (ppx-pulse, ppy-pulse, pw+pulse*2, ph+pulse*2), border_radius=24)
        pygame.draw.rect(pantalla, col_g,
                         (ppx-pulse, ppy-pulse, pw+pulse*2, ph+pulse*2), 3, border_radius=24)

        est = fuente_titulo.render("*", True, AMARILLO)
        pantalla.blit(est, (ANCHO//2-est.get_width()//2, ppy+12))

        nombre_g = "Jugador 1" if ganador==0 else ("IA" if estado.modo_un_jugador else "Jugador 2")
        gt = fuente_titulo.render(f"{nombre_g} GANO!", True, AMARILLO)
        pantalla.blit(gt, (ANCHO//2-gt.get_width()//2, ppy+75))

        sp_g = SPRITE_J1_ORIG if ganador==0 else SPRITE_J2_ORIG
        if sp_g:
            img_g = pygame.transform.smoothscale(sp_g, (72,72))
            pantalla.blit(img_g, (ANCHO//2-36, ppy+150))
        else:
            cb_g  = COL_J1      if ganador==0 else COL_J2
            cc_g  = COL_J1_CLAR if ganador==0 else COL_J2_CLAR
            cbo_g = AZUL_PROF   if ganador==0 else NARANJA_OSC
            ps_g  = pygame.Surface((80,90), pygame.SRCALPHA)
            _dibujar_peon(ps_g, 40, 84, cb_g, cc_g, cbo_g, 1.85)
            pantalla.blit(ps_g, (ANCHO//2-40, ppy+140))

        pts_t = fuente_normal.render(f"Puntos: {estado.scores[ganador]}", True, NARANJA_CLAR)
        pantalla.blit(pts_t, (ANCHO//2-pts_t.get_width()//2, ppy+252))

        _btn2(boton_menu,  "< Menu",        (28,78,158),(45,110,215))
        _btn2(boton_nuevo, "Nuevo juego",   (165,68,8), (215,98,18))
        slider_v.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(60)

# ---------------------------------------------------------------
# BUCLE PRINCIPAL DEL JUEGO
# ---------------------------------------------------------------
def juego_loop():
    estado.reset()
    gestor_musica.cambiar_modo("juego")
    botones_pregunta = []
    slider = SliderVolumen(0, 0, 160)
    slider.valor = gestor_musica.volumen

    while True:
        ahora = pygame.time.get_ticks()
        gestor_musica.update_procedural(ahora)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            slider.manejar(ev)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "menu"
                if ev.key == pygame.K_m:
                    gestor_musica.toggle()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                es_ia = estado.modo_un_jugador and estado.turno==1
                if BOTON_DADO.collidepoint(ev.pos) and not es_ia:
                    tirar_dado()
                if estado.esperando_resp and estado.resultado_resp is None and not es_ia:
                    for k, br in enumerate(botones_pregunta):
                        if br.collidepoint(ev.pos):
                            responder_pregunta(k)

        # IA tirar dado
        if estado.modo_un_jugador and estado.turno==1 \
                and not estado.bloqueado and not estado.esperando_resp and not estado.ganador:
            if estado._ia_delay is None:
                estado._ia_delay = ahora + 900
            elif ahora >= estado._ia_delay:
                estado._ia_delay = None
                tirar_dado()

        # IA responder
        if estado.modo_un_jugador and estado.turno==1 \
                and estado.esperando_resp and estado.resultado_resp is None \
                and estado.ia_respondiendo:
            estado.ia_timer -= 1
            if estado.ia_timer <= 0:
                estado.ia_respondiendo = False
                responder_pregunta(estado.ia_resp_idx)

        # Animacion dado
        if estado.dado_anim > 0:
            estado.dado_anim -= 1
            if estado.dado_anim == 0:
                resultado = aplicar_movimiento()
                if resultado == "victoria":
                    return pantalla_victoria(estado.turno)

        # Cerrar pregunta
        if estado.show_resultado > 0:
            estado.show_resultado -= 1
            if estado.show_resultado == 0:
                estado.esperando_resp  = False
                estado.pregunta_activa = None
                estado.resultado_resp  = None
                estado.turno           = 1 - estado.turno
                estado.bloqueado       = False

        # DIBUJAR
        dibujar_fondo_juego()
        dibujar_tablero()
        for i in range(2):
            p = estado.pos[i]
            if p < len(CASILLAS_POS):
                x, y = CASILLAS_POS[p]
                dibujar_ficha_tablero(x, y, i)
        dibujar_panel(slider)
        dibujar_boton_dado()
        dibujar_mensaje()
        dibujar_historial()

        hint = fuente_peque.render("ESC: Menu   M: Musica", True, GRIS_OSC)
        pantalla.blit(hint, (ANCHO-hint.get_width()-12, ALTO-20))

        if estado.esperando_resp:
            botones_pregunta = dibujar_pregunta() or []

        pygame.display.flip()
        reloj.tick(60)

# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
def main():
    pantalla_carga()
    destino = "menu"
    while True:
        if destino == "menu":
            menu_principal()
            destino = "juego"
        elif destino == "juego":
            destino = juego_loop()
            if destino is None:
                destino = "menu"

if __name__ == "__main__":
    main()