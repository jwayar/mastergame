"""
╔══════════════════════════════════════════════════════╗
║              MATERGAME  - Menu Principal             ║
║         Launcher educativo para ninos 8-12           ║
╚══════════════════════════════════════════════════════╝
"""

import pygame
import sys
import os
import subprocess
import math
import random

# ── Resolver ruta (PyInstaller compatible) ────────────
def resolver_ruta(ruta_relativa):
    """Devuelve la ruta correcta tanto en desarrollo como en .exe compilado."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, ruta_relativa)

# ── Inicializar Pygame ────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ── Pantalla ──────────────────────────────────────────
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("MasterGame 🎮")
clock = pygame.time.Clock()

# ── Colores ───────────────────────────────────────────
BLANCO      = (255, 255, 255)
NEGRO       = (20,  20,  35)
FONDO_COL   = (30,  32,  50)
AMARILLO    = (255, 200,   0)
ROJO        = (230,  40,  40)
NARANJA     = (255, 120,   0)
MORADO      = (130,  50, 180)
VERDE_CLARO = (60,  200,  80)
ROSA        = (240, 100, 180)
CELESTE     = (80,  160, 240)
GRIS_CLARO  = (200, 205, 220)
GRIS_OSC    = (100, 105, 120)

# ── Fuentes ───────────────────────────────────────────
try:
    f_titulo  = pygame.font.SysFont("comicsansms", 48, bold=True)
    f_sub     = pygame.font.SysFont("comicsansms", 16)
    f_boton   = pygame.font.SysFont("comicsansms", 17, bold=True)
    f_mini    = pygame.font.SysFont("comicsansms", 13)
except Exception:
    f_titulo  = pygame.font.SysFont(None, 48, bold=True)
    f_sub     = pygame.font.SysFont(None, 16)
    f_boton   = pygame.font.SysFont(None, 17, bold=True)
    f_mini    = pygame.font.SysFont(None, 13)

# ── Materias ──────────────────────────────────────────
# Formato: (texto, color, ruta_icono, carpeta, nombre_exe)
MATERIAS = [
    ("Lengua",       AMARILLO,    "Lengua/IconoLen.png",        "Lengua",       "lengua.py"),
    ("Matematica",   ROJO,        "Matematica/IconoMat.png",    "Matematica",   "matematica.py"),
    ("Ed. Fisica",   NARANJA,     "Ed_Fisica/IconoEdF.png",     "Ed_Fisica",    "ed_fisica.py"),
    ("Geografia",    MORADO,      "Geografia/IconoGeo.png",     "Geografia",    "geografia.py"),
    ("Historia",     VERDE_CLARO, "Historia/IconoHist.png",     "Historia",     "historia.py"),
    ("Programacion", ROSA,        "Programacion/IconoProg.png", "Programacion", "aprende_python.py"),
    ("Informatica",  CELESTE,     "Informatica/IconoInf.png",   "Informatica",  "informatica.py"),
]

# ── Cargar iconos ─────────────────────────────────────
def cargar_icono(ruta):
    ruta_abs = resolver_ruta(ruta)
    if os.path.exists(ruta_abs):
        try:
            img = pygame.image.load(ruta_abs).convert_alpha()
            return pygame.transform.smoothscale(img, (36, 36))
        except Exception:
            pass
    return None

botones = []
for texto, color, ruta_icono, carpeta, exe in MATERIAS:
    botones.append({
        "texto":   texto,
        "color":   color,
        "carpeta": carpeta,
        "exe":     exe,
        "icono":   cargar_icono(ruta_icono),
        "rect":    None,
        "hover":   False,
        "anim":    0.0,
    })

# ── Cargar fondo (opcional) ───────────────────────────
def cargar_fondo():
    ruta = resolver_ruta("fondo_main.png")
    if os.path.exists(ruta):
        try:
            img = pygame.image.load(ruta).convert()
            return pygame.transform.scale(img, (ANCHO, ALTO))
        except Exception:
            pass
    return None

fondo_img = cargar_fondo()

# ── Partículas de fondo ───────────────────────────────
class Particula:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x   = random.uniform(0, ANCHO)
        self.y   = random.uniform(0, ALTO)
        self.r   = random.uniform(1, 3)
        self.vel = random.uniform(0.2, 0.8)
        self.col = random.choice([
            (255, 200, 80, 80), (100, 180, 255, 80),
            (200, 100, 255, 80), (80, 220, 120, 80),
        ])

    def update(self):
        self.y -= self.vel
        if self.y < -5:
            self.reset()
            self.y = ALTO + 5

    def draw(self):
        s = pygame.Surface((int(self.r * 2), int(self.r * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, self.col, (int(self.r), int(self.r)), int(self.r))
        pantalla.blit(s, (int(self.x - self.r), int(self.y - self.r)))

particulas = [Particula() for _ in range(50)]

# ── Dibujar fondo ─────────────────────────────────────
def dibujar_fondo(t):
    if fondo_img:
        pantalla.blit(fondo_img, (0, 0))
        # Overlay semitransparente para mejorar legibilidad
        ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        ov.fill((20, 20, 40, 160))
        pantalla.blit(ov, (0, 0))
    else:
        pantalla.fill(FONDO_COL)
        # Degradado sutil
        for y in range(0, ALTO, 4):
            alpha = int(30 * (1 - y / ALTO))
            s = pygame.Surface((ANCHO, 4), pygame.SRCALPHA)
            s.fill((60, 80, 140, alpha))
            pantalla.blit(s, (0, y))

    for p in particulas:
        p.update()
        p.draw()

# ── Lanzar juego ──────────────────────────────────────
def lanzar_juego(carpeta, archivo):
    """Lanza el .py con Python para pruebas, o el .exe si existe."""
    posibles = [
        resolver_ruta(os.path.join(carpeta, archivo)),
        resolver_ruta(archivo),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), carpeta, archivo),
    ]
    for ruta in posibles:
        if os.path.exists(ruta):
            try:
                # Si es .py lo lanza con el mismo intérprete Python
                if ruta.endswith(".py"):
                    subprocess.Popen([sys.executable, ruta], cwd=os.path.dirname(ruta))
                else:
                    subprocess.Popen([ruta], cwd=os.path.dirname(ruta))
                return True, ruta
            except Exception as e:
                return False, str(e)
    return False, "No encontrado"

# ── Mensaje flotante ──────────────────────────────────
mensaje_txt  = ""
mensaje_col  = BLANCO
mensaje_timer = 0

def mostrar_mensaje(txt, col=BLANCO, frames=120):
    global mensaje_txt, mensaje_col, mensaje_timer
    mensaje_txt   = txt
    mensaje_col   = col
    mensaje_timer = frames

# ── Layout botones: 2 columnas ────────────────────────
ANCHO_BTN  = 310
ALTO_BTN   = 62
RADIO_BTN  = 16
GAP_X      = 30
GAP_Y      = 16
COLS       = 2
START_X    = (ANCHO - COLS * ANCHO_BTN - GAP_X) // 2
START_Y    = 195

def calcular_rects():
    for i, b in enumerate(botones):
        col = i % COLS
        fila = i // COLS
        x = START_X + col * (ANCHO_BTN + GAP_X)
        y = START_Y + fila * (ALTO_BTN + GAP_Y)
        b["rect"] = pygame.Rect(x, y, ANCHO_BTN, ALTO_BTN)

calcular_rects()

def dibujar_boton(b, t):
    if b["rect"] is None:
        return

    mx, my = pygame.mouse.get_pos()
    over = b["rect"].collidepoint(mx, my)

    # Animación suave hover
    target = 1.0 if over else 0.0
    b["anim"] += (target - b["anim"]) * 0.18

    anim = b["anim"]
    rect = b["rect"].inflate(int(anim * 8), int(anim * 6))
    rect.center = b["rect"].center

    # Sombra
    sombra = pygame.Surface((rect.w + 6, rect.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, int(80 + anim * 60)),
                     (0, 0, rect.w + 6, rect.h + 8), border_radius=RADIO_BTN + 2)
    pantalla.blit(sombra, (rect.x - 2, rect.y + 5))

    # Color con brillo al hover
    r, g, bl = b["color"]
    factor = 1 + anim * 0.18
    col_final = (min(255, int(r * factor)), min(255, int(g * factor)), min(255, int(bl * factor)))

    pygame.draw.rect(pantalla, col_final, rect, border_radius=RADIO_BTN)

    # Borde brillante
    borde_alpha = int(100 + anim * 155)
    borde_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(borde_surf, (*BLANCO, borde_alpha),
                     (0, 0, rect.w, rect.h), 2, border_radius=RADIO_BTN)
    pantalla.blit(borde_surf, rect.topleft)

    # Círculo icono a la izquierda
    cx = rect.x + 36
    cy = rect.centery
    pygame.draw.circle(pantalla, (255, 255, 255, 200), (cx, cy), 26)
    circ_s = pygame.Surface((52, 52), pygame.SRCALPHA)
    pygame.draw.circle(circ_s, (255, 255, 255, 220), (26, 26), 26)
    pantalla.blit(circ_s, (cx - 26, cy - 26))

    if b["icono"]:
        pantalla.blit(b["icono"], (cx - 18, cy - 18))
    else:
        # Letra inicial como fallback
        letra = f_boton.render(b["texto"][0].upper(), True, b["color"])
        pantalla.blit(letra, (cx - letra.get_width() // 2, cy - letra.get_height() // 2))

    # Texto
    txt_s = f_boton.render(b["texto"].upper(), True, BLANCO)
    txt_x = rect.x + 74
    txt_y = rect.centery - txt_s.get_height() // 2
    # Sombra texto
    sombra_txt = f_boton.render(b["texto"].upper(), True, NEGRO)
    sombra_txt.set_alpha(80)
    pantalla.blit(sombra_txt, (txt_x + 1, txt_y + 1))
    pantalla.blit(txt_s, (txt_x, txt_y))

    # Flecha al hover
    if anim > 0.1:
        flecha_x = rect.right - 22
        flecha_y = rect.centery
        flecha_alpha = int(anim * 200)
        pts = [
            (flecha_x - 5, flecha_y - 7),
            (flecha_x + 5, flecha_y),
            (flecha_x - 5, flecha_y + 7),
        ]
        flecha_s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(flecha_s, (*BLANCO, flecha_alpha),
                            [(p[0] - flecha_x + 10, p[1] - flecha_y + 10) for p in pts])
        pantalla.blit(flecha_s, (flecha_x - 10, flecha_y - 10))

# ── Bucle principal ───────────────────────────────────
t = 0
ejecutando = True

while ejecutando:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            ejecutando = False

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                ejecutando = False

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            pos = pygame.mouse.get_pos()
            for b in botones:
                if b["rect"] and b["rect"].collidepoint(pos):
                    ok, info = lanzar_juego(b["carpeta"], b["exe"])
                    if ok:
                        mostrar_mensaje(f"Abriendo {b['texto']}...", VERDE_CLARO, 90)
                    else:
                        mostrar_mensaje(f"No se encontro {b['exe']}", ROJO, 150)

    t += 1
    if mensaje_timer > 0:
        mensaje_timer -= 1

    # ── Dibujo ──────────────────────────────────────
    dibujar_fondo(t)

    # Título con sombra y animación
    escala = 1 + 0.015 * math.sin(t * 0.05)
    titulo_surf = f_titulo.render("MasterGame", True, AMARILLO)
    tw = int(titulo_surf.get_width() * escala)
    th = int(titulo_surf.get_height() * escala)
    titulo_sc = pygame.transform.scale(titulo_surf, (tw, th))
    sombra_t = titulo_sc.copy()
    sombra_t.set_alpha(60)
    pantalla.blit(sombra_t, (ANCHO // 2 - tw // 2 + 3, 45 + 3))
    pantalla.blit(titulo_sc, (ANCHO // 2 - tw // 2, 45))

    # Subtítulo
    sub = f_sub.render("Elegí tu materia y empeza a jugar", True, GRIS_CLARO)
    pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2, 112))

    # Línea decorativa
    pygame.draw.line(pantalla, AMARILLO,
                     (ANCHO // 2 - 120, 135), (ANCHO // 2 + 120, 135), 2)

    # Botones
    for b in botones:
        dibujar_boton(b, t)

    # Mensaje de feedback
    if mensaje_timer > 0:
        alpha = min(255, mensaje_timer * 5)
        msg_s = f_boton.render(mensaje_txt, True, mensaje_col)
        bg_w  = msg_s.get_width() + 28
        bg_h  = 36
        bg    = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, min(alpha, 180)))
        px = ANCHO // 2 - bg_w // 2
        py = ALTO - 44
        pantalla.blit(bg, (px, py))
        pygame.draw.rect(pantalla, mensaje_col, (px, py, bg_w, bg_h), 1, border_radius=8)
        msg_s.set_alpha(alpha)
        pantalla.blit(msg_s, (ANCHO // 2 - msg_s.get_width() // 2, py + 8))

    # Versión
    ver = f_mini.render("MasterGame v1.0  |  ESC para salir", True, GRIS_OSC)
    pantalla.blit(ver, (ANCHO // 2 - ver.get_width() // 2, ALTO - 22))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()