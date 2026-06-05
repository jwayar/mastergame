"""
╔══════════════════════════════════════════════════════╗
║          DEFENSOR DE INTERNET  v3.3                  ║
║  Proyecto educativo de ciberseguridad con pygame     ╚══════════════════════════════════════════════════════╝

Todos los archivos (sprites, sonidos, música) van en la
MISMA carpeta que este .py:

  escudo.png          (130x28)
  boss.png            (180x70)
  fondo_menu.png      (900x620)
  fondo_juego.png     (900x620)
  acierto.wav
  error.wav
  nivel.wav
  boss.wav
  musica_menu.ogg
  musica_juego.ogg

Si falta alguno, el juego usa gráficos/sonidos generados.
"""

import pygame
import random
import sys
import json
import os
import math

# ====================== RESOLVER RUTA (PyInstaller) ======================
def resolver_ruta(ruta_relativa):
    """ Obtiene la ruta absoluta de los recursos, compatible con PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)
# =========================================================================

pygame.init()
pygame.mixer.init()

ANCHO, ALTO = 900, 620
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Defensor de Internet v3.3")
clock = pygame.time.Clock()

# ─── COLORES ─────────────────────────────────────────────────
NEGRO       = ( 10,  12,  28)
BLANCO      = (240, 242, 255)
AZUL        = ( 40, 130, 255)
AZUL_OSC    = ( 15,  55, 140)
AZUL_MED    = ( 25,  80, 180)
VERDE       = ( 35, 210,  90)
VERDE_OSC   = ( 12, 100,  45)
ROJO        = (230,  45,  55)
ROJO_OSC    = (100,  12,  18)
AMARILLO    = (255, 218,   0)
NARANJA     = (255, 148,  20)
GRIS        = ( 75,  78, 105)
GRIS_CLARO  = (155, 158, 185)
PURPURA     = (150,  65, 230)
CIAN        = (  0, 210, 235)
FONDO_JUEGO = ( 10,  12,  28)
FONDO_HUD   = ( 18,  20,  42)

# ─── FUENTES ─────────────────────────────────────────────────
fuente_titulo  = pygame.font.SysFont("consolas", 54, bold=True)
fuente_grande  = pygame.font.SysFont("consolas", 34, bold=True)
fuente_normal  = pygame.font.SysFont("consolas", 24, bold=True)
fuente_pequena = pygame.font.SysFont("consolas", 18)
fuente_mini    = pygame.font.SysFont("consolas", 14)

# ─── RUTAS ───────────────────────────────────────────────────
DIR = os.path.dirname(os.path.abspath(__file__))

# ─── RUTAS ───────────────────────────────────────────────────
def ruta(nombre):
    """ Ruta compatible con carpeta 'informatica' """
    return resolver_ruta(f"Informatica/{nombre}")

ARCHIVO_RANKING = ruta("ranking.json")

# ─── RANKING ─────────────────────────────────────────────────
def cargar_ranking():
    if os.path.exists(ARCHIVO_RANKING):
        try:
            with open(ARCHIVO_RANKING, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def guardar_ranking(nombre, puntaje):
    ranking = cargar_ranking()
    ranking.append({"nombre": nombre, "puntaje": puntaje})
    ranking.sort(key=lambda x: x["puntaje"], reverse=True)
    ranking = ranking[:10]
    with open(ARCHIVO_RANKING, "w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)
    return ranking

# ─── CARGA DE RECURSOS ───────────────────────────────────────
def cargar_imagen(nombre, tam):
    path = ruta(nombre)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, tam)
        except Exception as e:
            print(f"[imagen] Error cargando {nombre}: {e}")
    return None

def cargar_sonido(nombre):
    path = ruta(nombre)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"[sonido] Error cargando {nombre}: {e}")
    return None

def iniciar_musica(nombre, vol=0.45):
    path = ruta(nombre)
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[música] Error cargando {nombre}: {e}")
    else:
        print(f"[música] No encontrado: {nombre}")

def detener_musica():
    pygame.mixer.music.stop()

def reproducir(snd):
    if snd:
        snd.play()

# ─── CARGAR SPRITES ──────────────────────────────────────────
img_escudo      = cargar_imagen("escudo.png",      (130, 28))
img_boss        = cargar_imagen("boss.png",        (180, 70))
img_fondo_menu  = cargar_imagen("fondo_menu.png",  (ANCHO, ALTO))
img_fondo_juego = cargar_imagen("fondo_juego.png", (ANCHO, ALTO))

# ─── CARGAR SONIDOS ──────────────────────────────────────────
# Solo cargamos los que existen
snd_acierto = None
snd_error   = None
snd_nivel   = None
snd_boss    = None

# ─── DATOS DE OBJETOS ────────────────────────────────────────
OBJETOS_INFO = [
    {
        "id": "phishing", "texto": "PHISHING", "tipo": "amenaza",
        "emoji": "?", "color": ROJO, "color2": (180, 20, 30),
        "consejo": "Bloqueaste un PHISHING!",
        "detalle": "El phishing finge ser una empresa\npara robarte tus datos.\nNunca hagas clic en correos\nque pidan tu clave.",
    },
    {
        "id": "virus", "texto": "VIRUS", "tipo": "amenaza",
        "emoji": "X", "color": ROJO, "color2": (160, 15, 25),
        "consejo": "Eliminaste un VIRUS!",
        "detalle": "Un virus daña tu computadora\no roba tus archivos.\nUsa un antivirus y no\ndescargues programas raros.",
    },
    {
        "id": "link_falso", "texto": "LINK FALSO", "tipo": "amenaza",
        "emoji": "!", "color": NARANJA, "color2": (200, 100, 10),
        "consejo": "Bloqueaste un LINK FALSO!",
        "detalle": "Los links falsos te llevan a\npaginas que parecen reales.\nSiempre mira bien la direccion\nantes de ingresar datos.",
    },
    {
        "id": "password_debil", "texto": "CLAVE: 1234", "tipo": "amenaza",
        "emoji": "?", "color": NARANJA, "color2": (190, 95, 8),
        "consejo": "Contrasena debil bloqueada!",
        "detalle": "Una clave como '1234' es\nmuy facil de adivinar.\nUsa letras, numeros y simbolos.\nEjemplo: Mi@Casa#2024",
    },
    {
        "id": "correo_seguro", "texto": "CORREO OK", "tipo": "seguro",
        "emoji": "@", "color": VERDE, "color2": (15, 140, 55),
        "consejo": "Es un correo legitimo!",
        "detalle": "Un correo oficial viene de\ndirecciones conocidas.\nNunca te pide contrasenias.\nAprender a distinguirlos es clave.",
    },
    {
        "id": "web_segura", "texto": "WEB SEGURA", "tipo": "seguro",
        "emoji": "S", "color": VERDE, "color2": (12, 130, 50),
        "consejo": "Sitio confiable, no lo bloquees!",
        "detalle": "Una web segura empieza con\nhttps:// y tiene un candado.\nBusca siempre ese candado\nantes de ingresar datos!",
    },
    {
        "id": "actualizacion", "texto": "ACTUALIZAR", "tipo": "seguro",
        "emoji": "^", "color": AZUL, "color2": (20, 90, 200),
        "consejo": "Las actualizaciones te protegen!",
        "detalle": "Actualizar tus programas\ncierra agujeros de seguridad.\nSiempre acepta las actualizaciones\noficiales.",
    },
    {
        "id": "password_fuerte", "texto": "CLAVE OK", "tipo": "seguro",
        "emoji": "*", "color": CIAN, "color2": (0, 160, 185),
        "consejo": "Excelente contrasenia!",
        "detalle": "Una contrasenia fuerte tiene\nletras, numeros y simbolos.\nUsa una diferente para cada\ncuenta. Asi estas seguro!",
    },
]

PREGUNTAS_BOSS = [
    {
        "pregunta": "¿Qué es el Phishing?",
        "opciones": ["Es una forma de mejorar el internet",
                     "Es un mensaje falso que quiere robarte",
                     "Es un programa para limpiar la computadora",
                     "Es un juego en línea"],
        "correcta": 1,
        "explicacion": "El phishing es un truco donde alguien se hace pasar\npor un banco o una empresa para robarte tu clave."
    },
    {
        "pregunta": "¿Cuál es una buena contraseña?",
        "opciones": ["123456", "mipassword", "Perro2025!Casa#", "abc123"],
        "correcta": 2,
        "explicacion": "Una buena contraseña mezcla letras, números y símbolos\npara que sea difícil de adivinar."
    },
    {
        "pregunta": "¿Qué significa que una página tenga el candado cerrado?",
        "opciones": ["Que la página es más lenta",
                     "Que es una página segura",
                     "Que la página es gratis",
                     "Que la página es nueva"],
        "correcta": 1,
        "explicacion": "El candadito cerrado significa que la página es segura\ny tus datos están protegidos."
    },
    {
        "pregunta": "¿Para qué sirve un antivirus?",
        "opciones": ["Para ver videos más rápido",
                     "Para proteger la computadora de virus",
                     "Para descargar juegos",
                     "Para cambiar el color de la pantalla"],
        "correcta": 1,
        "explicacion": "El antivirus es como un guardia que protege tu computadora\nde programas malos."
    },
    {
        "pregunta": "¿Qué hacer si te llega un mensaje con un link de un desconocido?",
        "opciones": ["Hacer clic para ver qué es",
                     "Mandárselo a un amigo",
                     "No abrirlo y borrarlo",
                     "Responder preguntando quién es"],
        "correcta": 2,
        "explicacion": "Es mejor no abrir links de personas desconocidas,\npueden ser peligrosos."
    },
    {
        "pregunta": "¿Cuándo es bueno actualizar los programas de la computadora?",
        "opciones": ["Nunca hay que actualizarlos",
                     "Solo una vez por año",
                     "Cuando sale una actualización nueva",
                     "Solo cuando la computadora se rompe"],
        "correcta": 2,
        "explicacion": "Actualizar los programas ayuda a que tu computadora\nesté más protegida."
    },
]

# ─── HELPERS UI ──────────────────────────────────────────────
def dibujar_fondo_menu():
    """Dibuja el fondo del menú: imagen si existe, sino color sólido + degradado."""
    if img_fondo_menu:
        pantalla.blit(img_fondo_menu, (0, 0))
    else:
        pantalla.fill(NEGRO)
        # Degradado suave de arriba hacia abajo
        for y in range(ALTO):
            factor = y / ALTO
            r = int(NEGRO[0] + (AZUL_OSC[0] - NEGRO[0]) * factor * 0.6)
            g = int(NEGRO[1] + (AZUL_OSC[1] - NEGRO[1]) * factor * 0.6)
            b = int(NEGRO[2] + (AZUL_OSC[2] - NEGRO[2]) * factor * 0.6)
            pygame.draw.line(pantalla, (r, g, b), (0, y), (ANCHO, y))

def dibujar_fondo_juego():
    """Dibuja el fondo del juego: imagen si existe, sino color sólido."""
    if img_fondo_juego:
        pantalla.blit(img_fondo_juego, (0, 0))
    else:
        pantalla.fill(FONDO_JUEGO)

def dibujar_texto_centrado(texto, fuente, color, y, sombra=True):
    if sombra:
        s = fuente.render(texto, True, (0, 0, 0))
        pantalla.blit(s, (ANCHO//2 - s.get_width()//2 + 2, y + 2))
    surf = fuente.render(texto, True, color)
    pantalla.blit(surf, (ANCHO//2 - surf.get_width()//2, y))

def dibujar_barra(x, y, ancho, alto, progreso, color_lleno, color_vacio=GRIS, radio=5):
    pygame.draw.rect(pantalla, color_vacio, (x, y, ancho, alto), border_radius=radio)
    if progreso > 0:
        w = max(radio*2, int(ancho * min(progreso, 1.0)))
        pygame.draw.rect(pantalla, color_lleno, (x, y, w, alto), border_radius=radio)

def texto_ml(texto, fuente, color, x, y, gap=22):
    for linea in texto.split("\n"):
        s = fuente.render(linea, True, color)
        pantalla.blit(s, (x, y))
        y += gap

def boton_ui(rect, texto, color_fondo, color_texto=BLANCO, fuente=None):
    if fuente is None:
        fuente = fuente_normal
    mx, my = pygame.mouse.get_pos()
    encima = rect.collidepoint(mx, my)
    r = rect.height // 2
    base = tuple(min(c+40, 255) for c in color_fondo) if encima else color_fondo
    sombra_r = pygame.Rect(rect.x+3, rect.y+4, rect.width, rect.height)
    pygame.draw.rect(pantalla, (0,0,0), sombra_r, border_radius=r)
    pygame.draw.rect(pantalla, base, rect, border_radius=r)
    borde_col = tuple(min(c+80, 255) for c in color_fondo)
    pygame.draw.rect(pantalla, borde_col, rect, 2, border_radius=r)
    s = fuente.render(texto, True, color_texto)
    pantalla.blit(s, (rect.centerx - s.get_width()//2,
                      rect.centery - s.get_height()//2))
    return encima

# ─── PARTÍCULAS ──────────────────────────────────────────────
class Particula:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x     = random.uniform(0, ANCHO)
        self.y     = random.uniform(0, ALTO)
        self.vel_y = random.uniform(-0.3, -0.8)
        self.vel_x = random.uniform(-0.2, 0.2)
        self.r     = random.randint(1, 3)
        self.color = random.choice([CIAN, AZUL, AMARILLO, BLANCO, VERDE])

    def actualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y
        if self.y < -5:
            self.reset()
            self.y = ALTO + 5

    def dibujar(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.r)

particulas = [Particula() for _ in range(80)]

# ─── CONSTANTES DE JUEGO ─────────────────────────────────────
OBJ_W, OBJ_H         = 148, 44
OBJETOS_POR_NIVEL    = [1, 2, 2, 3, 3]
VEL_INICIAL          = 2.5
VEL_MAXIMA           = 5.5
SEP_VERTICAL_MIN     = 260
ESCUDO_W             = 130
VEL_JUGADOR          = 9
ALTO_HUD             = 92

# ─── OBJETO QUE CAE ──────────────────────────────────────────
class ObjetoJuego:
    CARRILES = [55, 215, 375, 535, 695]

    def __init__(self, vel=1.5, carriles_ocupados=None):
        self.info   = random.choice(OBJETOS_INFO)
        libres      = [c for c in self.CARRILES if c not in (carriles_ocupados or [])]
        if not libres:
            libres  = self.CARRILES
        self.carril = random.choice(libres)
        self.rect   = pygame.Rect(self.carril, -80, OBJ_W, OBJ_H)
        self.vel    = vel
        self.brillo = 0
        self.brillo_dir = 1

    @property
    def carril_x(self):
        return self.rect.x

    def actualizar(self):
        self.rect.y += self.vel
        self.brillo += self.brillo_dir * 3
        if self.brillo >= 60 or self.brillo <= 0:
            self.brillo_dir *= -1

    def dibujar(self):
        radio = OBJ_H // 2
        col   = self.info["color"]
        col2  = self.info.get("color2", col)

        sr = self.rect.move(3, 4)
        pygame.draw.rect(pantalla, (0,0,0), sr, border_radius=radio)
        pygame.draw.rect(pantalla, col2, self.rect, border_radius=radio)
        pygame.draw.rect(pantalla, col,  self.rect.inflate(-4,-4), border_radius=radio-2)

        brillo_surf = pygame.Surface((self.rect.width, self.rect.height//2), pygame.SRCALPHA)
        brillo_surf.fill((255,255,255, 18 + self.brillo//4))
        pantalla.blit(brillo_surf, self.rect.topleft)

        borde_col = tuple(min(c+60,255) for c in col)
        pygame.draw.rect(pantalla, borde_col, self.rect, 2, border_radius=radio)

        emoji = self.info.get("emoji", "")
        etxt  = fuente_pequena.render(f"{emoji} {self.info['texto']}", True, BLANCO)
        pantalla.blit(etxt, (self.rect.x + (self.rect.w - etxt.get_width())//2,
                              self.rect.y + (self.rect.h - etxt.get_height())//2))

        if self.info["tipo"] == "amenaza":
            et_col = ROJO;  et_txt = "! BLOQUEAR"
        else:
            et_col = VERDE; et_txt = "OK DEJAR PASAR"
        et = fuente_mini.render(et_txt, True, et_col)
        pantalla.blit(et, (self.rect.x + (self.rect.w - et.get_width())//2,
                           self.rect.y - 16))

# ─── PROYECTILES ─────────────────────────────────────────────
class ProyectilBoss:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x-8, y, 16, 16)
        self.vel  = 4
        self.ang  = 0

    def actualizar(self):
        self.rect.y += self.vel
        self.ang = (self.ang + 8) % 360

    def dibujar(self):
        cx, cy = self.rect.center
        for i in range(4):
            a  = math.radians(self.ang + i*90)
            px = cx + int(8*math.cos(a))
            py = cy + int(8*math.sin(a))
            pygame.draw.circle(pantalla, NARANJA, (px, py), 4)
        pygame.draw.circle(pantalla, ROJO, (cx, cy), 5)


class ProyectilJugador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x-5, y-12, 10, 20)
        self.vel  = 10

    def actualizar(self):
        self.rect.y -= self.vel

    def dibujar(self):
        pygame.draw.rect(pantalla, CIAN, self.rect, border_radius=5)
        pygame.draw.rect(pantalla, BLANCO, self.rect.inflate(-4,-4), border_radius=4)
        for i in range(1, 4):
            alpha_s = pygame.Surface((self.rect.width, 8), pygame.SRCALPHA)
            alpha_s.fill((*CIAN, max(0, 100 - i*30)))
            pantalla.blit(alpha_s, (self.rect.x, self.rect.bottom + i*6))

# ─── BOSS ────────────────────────────────────────────────────
class Boss:
    VIDA_MAX = 6

    def __init__(self):
        self.rect      = pygame.Rect(ANCHO//2 - 90, 50, 180, 70)
        self.vel       = 1.5
        self.dir       = 1
        self.vida      = self.VIDA_MAX
        self.fase      = 1
        self.proyectiles    = []
        self.timer_disparo  = 0
        self.pregunta_activa = False
        self.pregunta_idx   = 0
        self.preguntas      = random.sample(PREGUNTAS_BOSS, len(PREGUNTAS_BOSS))
        self.preg_actual    = None
        self.anim_golpe     = 0

    @property
    def vivo(self):
        return self.vida > 0

    def recibir_golpe(self):
        self.vida -= 1
        self.anim_golpe = 18
        if self.vida <= self.VIDA_MAX // 2:
            self.fase = 2
            self.vel  = 2.5

    def siguiente_pregunta(self):
        if self.pregunta_idx >= len(self.preguntas):
            self.preguntas    = random.sample(PREGUNTAS_BOSS, len(PREGUNTAS_BOSS))
            self.pregunta_idx = 0
        self.preg_actual     = self.preguntas[self.pregunta_idx]
        self.pregunta_idx   += 1
        self.pregunta_activa = True

    def actualizar(self):
        if self.pregunta_activa:
            return
        self.rect.x += self.vel * self.dir
        if self.rect.right >= ANCHO-20 or self.rect.left <= 20:
            self.dir *= -1
        if self.anim_golpe > 0:
            self.anim_golpe -= 1

        self.timer_disparo += 1
        intervalo = 90 if self.fase == 1 else 55
        if self.timer_disparo >= intervalo:
            self.timer_disparo = 0
            disparos = [self.rect.centerx] if self.fase == 1 else \
                       [self.rect.centerx-50, self.rect.centerx, self.rect.centerx+50]
            for dx in disparos:
                self.proyectiles.append(ProyectilBoss(dx, self.rect.bottom+5))
        for p in self.proyectiles[:]:
            p.actualizar()
            if p.rect.top > ALTO:
                self.proyectiles.remove(p)

    def dibujar(self):
        ox = random.randint(-3,3) if self.anim_golpe > 0 else 0
        color_b = ROJO if self.fase == 2 else PURPURA
        r = self.rect.move(ox, 0)
        pygame.draw.rect(pantalla, (0,0,0), r.move(4,6), border_radius=18)
        if img_boss:
            pantalla.blit(img_boss, r.topleft)
        else:
            pygame.draw.rect(pantalla, color_b, r, border_radius=16)
            inner = r.inflate(-6,-6)
            col2  = tuple(min(c+40,255) for c in color_b)
            pygame.draw.rect(pantalla, col2, inner, border_radius=14)
            oy = r.y + 22
            for ex in [r.x+45, r.x+125]:
                pygame.draw.circle(pantalla, AMARILLO, (ex, oy), 10)
                pygame.draw.circle(pantalla, NEGRO, (ex+(2 if self.fase==2 else 0), oy), 5)
            boca_col = ROJO if self.fase == 2 else NARANJA
            pygame.draw.rect(pantalla, boca_col, (r.x+55, r.y+46, 70, 12), border_radius=5)
            lbl = fuente_mini.render("HACKER SUPREMO", True, BLANCO)
            pantalla.blit(lbl, (r.centerx - lbl.get_width()//2, r.y-18))

        dibujar_barra(r.x, r.bottom+4, r.width, 8,
                      self.vida/self.VIDA_MAX, VERDE, ROJO_OSC, radio=4)
        lv = fuente_mini.render(f"Vida: {self.vida}/{self.VIDA_MAX}", True, BLANCO)
        pantalla.blit(lv, (r.centerx - lv.get_width()//2, r.bottom+14))
        for p in self.proyectiles:
            p.dibujar()

# ─── PANTALLA PREGUNTA BOSS ──────────────────────────────────
def pantalla_pregunta_boss(boss):
    preg    = boss.preg_actual
    opciones = preg["opciones"]

    btn_opciones = []
    for i in range(4):
        fila = i // 2; col_idx = i % 2
        bx = 160 + col_idx * 310
        by = 370 + fila * 80
        btn_opciones.append(pygame.Rect(bx, by, 280, 64))

    resultado      = None
    timer_resultado = 0
    DURACION       = 120

    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and resultado is None:
                for i, btn in enumerate(btn_opciones):
                    if btn.collidepoint(ev.pos):
                        resultado = (i == preg["correcta"])
                        timer_resultado = DURACION
            if ev.type == pygame.KEYDOWN and resultado is None:
                mapa = {pygame.K_1:0, pygame.K_2:1, pygame.K_3:2, pygame.K_4:3}
                if ev.key in mapa:
                    resultado = (mapa[ev.key] == preg["correcta"])
                    timer_resultado = DURACION

        if resultado is not None:
            timer_resultado -= 1
            if timer_resultado <= 0:
                boss.pregunta_activa = False
                return resultado

        # Fondo del juego antes del overlay
        dibujar_fondo_juego()

        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 10, 200))
        pantalla.blit(overlay, (0,0))

        caja = pygame.Rect(80, 100, ANCHO-160, 450)
        pygame.draw.rect(pantalla, FONDO_HUD, caja, border_radius=20)
        pygame.draw.rect(pantalla, PURPURA,   caja, 3, border_radius=20)

        dibujar_texto_centrado("PREGUNTA DEL HACKER!", fuente_grande, AMARILLO, 120)
        for i, linea in enumerate(preg["pregunta"].split("\n")):
            dibujar_texto_centrado(linea, fuente_normal, BLANCO, 185 + i*32)

        if resultado is None:
            hint = fuente_mini.render("Clic en la opcion o presiona 1 2 3 4", True, GRIS_CLARO)
            pantalla.blit(hint, (ANCHO//2 - hint.get_width()//2, 340))
            for i, btn in enumerate(btn_opciones):
                mx, my = pygame.mouse.get_pos()
                hover  = btn.collidepoint(mx, my)
                bg     = AZUL_MED if hover else AZUL_OSC
                pygame.draw.rect(pantalla, bg, btn, border_radius=14)
                pygame.draw.rect(pantalla, CIAN if hover else AZUL, btn, 2, border_radius=14)
                num = fuente_mini.render(str(i+1), True, AMARILLO)
                pantalla.blit(num, (btn.x+10, btn.centery - num.get_height()//2))
                for j, linea in enumerate(opciones[i].split("\n")):
                    t = fuente_pequena.render(linea, True, BLANCO)
                    pantalla.blit(t, (btn.x+35, btn.y+10+j*22))
        else:
            if resultado:
                dibujar_texto_centrado("CORRECTO! Golpeaste al hacker!", fuente_normal, VERDE, 360)
            else:
                dibujar_texto_centrado("INCORRECTO. El hacker te esquivo!", fuente_normal, ROJO, 360)
            for j, linea in enumerate(preg["explicacion"].split("\n")):
                dibujar_texto_centrado(linea, fuente_pequena, GRIS_CLARO, 410+j*22)
            dibujar_barra(ANCHO//2-100, 490, 200, 8,
                          timer_resultado/DURACION,
                          VERDE if resultado else ROJO, GRIS)

        pygame.display.flip()
        clock.tick(60)

    return False

# ─── MENÚ PRINCIPAL ──────────────────────────────────────────
def menu_principal():
    iniciar_musica("musica_menu.mp3")
    t = 0

    btn_jugar    = pygame.Rect(ANCHO//2-150, 290, 300, 58)
    btn_tutorial = pygame.Rect(ANCHO//2-150, 365, 300, 58)
    btn_ranking  = pygame.Rect(ANCHO//2-150, 440, 300, 58)
    btn_salir    = pygame.Rect(ANCHO//2-150, 515, 300, 58)

    circulos = [{"x": random.randint(50,ANCHO-50),
                 "y": random.randint(50,ALTO-50),
                 "r": random.randint(20,80),
                 "col": random.choice([AZUL,CIAN,PURPURA,VERDE]),
                 "vel": random.uniform(0.2,0.6),
                 "fase": random.uniform(0, math.pi*2)}
                for _ in range(12)]

    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_jugar.collidepoint(ev.pos):
                    detener_musica(); return "jugar"
                if btn_tutorial.collidepoint(ev.pos):
                    pantalla_tutorial()
                    iniciar_musica("musica_menu.mp3")
                if btn_ranking.collidepoint(ev.pos):
                    pantalla_ranking()
                if btn_salir.collidepoint(ev.pos):
                    pygame.quit(); sys.exit()

        t += 1

        # ── FONDO del menú ──
        dibujar_fondo_menu()

        for c in circulos:
            cy = c["y"] + math.sin(t*c["vel"]*0.05 + c["fase"])*18
            s  = pygame.Surface((c["r"]*2, c["r"]*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*c["col"], 22), (c["r"], c["r"]), c["r"])
            pantalla.blit(s, (c["x"]-c["r"], int(cy)-c["r"]))

        for p in particulas:
            p.actualizar(); p.dibujar(pantalla)

        for gx in range(0, ANCHO, 80):
            pygame.draw.line(pantalla, (*AZUL_OSC, 60), (gx,0), (gx,ALTO), 1)
        for gy in range(0, ALTO, 80):
            pygame.draw.line(pantalla, (*AZUL_OSC, 60), (0,gy), (ANCHO,gy), 1)

        escala = 1 + 0.025*math.sin(t*0.05)
        t1 = fuente_titulo.render("DEFENSOR", True, CIAN)
        t2 = fuente_titulo.render("DE INTERNET", True, AMARILLO)
        for surf, y_base in [(t1, 100), (t2, 160)]:
            sw = int(surf.get_width()*escala)
            sh = int(surf.get_height()*escala)
            scaled = pygame.transform.scale(surf, (sw, sh))
            sombra = pygame.transform.scale(surf, (sw, sh))
            sombra.set_alpha(80)
            pantalla.blit(sombra, (ANCHO//2-sw//2+4, y_base+4))
            pantalla.blit(scaled, (ANCHO//2-sw//2, y_base))

        sub = fuente_pequena.render("Aprende a protegerte en internet mientras juegas", True, GRIS_CLARO)
        pantalla.blit(sub, (ANCHO//2 - sub.get_width()//2, 230))
        pygame.draw.line(pantalla, CIAN,    (ANCHO//2-180, 262), (ANCHO//2+180, 262), 1)
        pygame.draw.line(pantalla, AMARILLO,(ANCHO//2-60,  268), (ANCHO//2+60,  268), 1)

        boton_ui(btn_jugar,    ">   JUGAR",        AZUL_OSC)
        boton_ui(btn_tutorial, "?   COMO JUGAR",   GRIS)
        boton_ui(btn_ranking,  "*   RANKING",      (70,55,8))
        boton_ui(btn_salir,    "X   SALIR",        ROJO_OSC)

        v = fuente_mini.render("v3.3  -  Proyecto Educativo de Ciberseguridad", True, GRIS)
        pantalla.blit(v, (ANCHO//2 - v.get_width()//2, ALTO-26))

        pygame.display.flip()
        clock.tick(60)

# ─── TUTORIAL ────────────────────────────────────────────────
def pantalla_tutorial():
    pasos = [
        ("MOVIMIENTO",
         "Usa las flechas <- -> del teclado\npara mover el ESCUDO de lado a lado.\n\nEl escudo es tu herramienta\npara bloquear amenazas."),
        ("AMENAZAS (ROJAS / NARANJAS)",
         "Los objetos rojos y naranjas son\npeligrosos: Phishing, Virus, Links falsos,\nContrasenias debiles.\nTocalos con el escudo para eliminarlos!"),
        ("OBJETOS SEGUROS (VERDES / AZULES)",
         "Los objetos verdes y azules son buenos:\nCorreos OK, webs seguras, actualizaciones.\nNO los toques o perderas puntos!\nLee bien la etiqueta de cada objeto."),
        ("NIVELES Y DIFICULTAD",
         "Bloquea 5 amenazas para subir de nivel.\nCada nivel los objetos caen mas rapido.\nHay 5 niveles en total!\nEntre niveles veras un resumen educativo."),
        ("EL BOSS FINAL (NIVEL 5)",
         "Aparece el HACKER SUPREMO.\nPresiona ESPACIO para dispararle.\nCuando lo golpees saldra una pregunta.\nResponde bien para hacerle danio!"),
        ("PUNTAJE Y VIDAS",
         "Bloquear amenaza:    +10 puntos\nDejar pasar amenaza: -1 vida (tienes 3)\nGolpear obj. seguro: -5 puntos\nDerrotar boss:       +100 puntos\n\nIntenta llegar al TOP 10!"),
    ]
    paso     = 0
    btn_sig  = pygame.Rect(620, 540, 180, 48)
    btn_ant  = pygame.Rect(100, 540, 180, 48)
    btn_ok   = pygame.Rect(ANCHO//2-90, 540, 180, 48)

    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_sig.collidepoint(ev.pos) and paso < len(pasos)-1: paso += 1
                elif btn_ant.collidepoint(ev.pos) and paso > 0:          paso -= 1
                elif btn_ok.collidepoint(ev.pos) and paso == len(pasos)-1: corriendo = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RIGHT and paso < len(pasos)-1: paso += 1
                elif ev.key == pygame.K_LEFT and paso > 0:           paso -= 1
                elif ev.key == pygame.K_ESCAPE:                       corriendo = False

        # ── FONDO del menú también en tutorial ──
        dibujar_fondo_menu()

        for p in particulas:
            p.actualizar(); p.dibujar(pantalla)

        caja = pygame.Rect(70, 70, ANCHO-140, 450)
        s = pygame.Surface(caja.size, pygame.SRCALPHA)
        s.fill((10,12,40,200))
        pantalla.blit(s, caja.topleft)
        pygame.draw.rect(pantalla, CIAN, caja, 2, border_radius=18)

        dibujar_texto_centrado("COMO SE JUEGA?", fuente_grande, CIAN, 90)
        titulo_p, desc_p = pasos[paso]
        dibujar_texto_centrado(titulo_p, fuente_normal, AMARILLO, 158)
        texto_ml(desc_p, fuente_pequena, BLANCO, 110, 210, gap=28)

        dibujar_barra(ANCHO//2-160, 465, 320, 8,
                      (paso+1)/len(pasos), CIAN, GRIS)
        pc = fuente_mini.render(f"Paso {paso+1} de {len(pasos)}", True, GRIS_CLARO)
        pantalla.blit(pc, (ANCHO//2 - pc.get_width()//2, 478))

        if paso > 0:                  boton_ui(btn_ant, "< ANTERIOR", AZUL_OSC)
        if paso < len(pasos)-1:       boton_ui(btn_sig, "SIGUIENTE >", AZUL_OSC)
        else:                          boton_ui(btn_ok,  "LISTO!",     VERDE_OSC)

        hint = fuente_mini.render("Flechas <- -> para navegar", True, GRIS)
        pantalla.blit(hint, (ANCHO//2 - hint.get_width()//2, 596))
        pygame.display.flip()
        clock.tick(60)

# ─── PANTALLA RANKING ────────────────────────────────────────
def pantalla_ranking():
    ranking    = cargar_ranking()
    btn_volver = pygame.Rect(ANCHO//2-90, 548, 180, 48)

    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_volver.collidepoint(ev.pos): corriendo = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                corriendo = False

        # ── FONDO del menú en ranking ──
        dibujar_fondo_menu()

        for p in particulas:
            p.actualizar(); p.dibujar(pantalla)

        caja = pygame.Rect(100, 55, ANCHO-200, 480)
        s    = pygame.Surface(caja.size, pygame.SRCALPHA)
        s.fill((10,12,40,210))
        pantalla.blit(s, caja.topleft)
        pygame.draw.rect(pantalla, AMARILLO, caja, 2, border_radius=18)

        dibujar_texto_centrado("* TOP 10 RANKING *", fuente_grande, AMARILLO, 75)

        if not ranking:
            dibujar_texto_centrado("Aun no hay puntajes guardados.",
                                   fuente_normal, GRIS_CLARO, 290)
        else:
            medallas  = ["[1]","[2]","[3]"] + ["   "]*7
            cols_pos  = [AMARILLO, GRIS_CLARO, NARANJA] + [BLANCO]*7
            for i, entry in enumerate(ranking[:10]):
                col   = cols_pos[i]
                y     = 138 + i*33
                linea = f"{medallas[i]}  #{i+1}   {entry['nombre'][:14]:<14}   {entry['puntaje']:>6}"
                t     = fuente_pequena.render(linea, True, col)
                pantalla.blit(t, (ANCHO//2 - t.get_width()//2, y))

        boton_ui(btn_volver, "< VOLVER", AZUL_OSC)
        pygame.display.flip()
        clock.tick(60)

# ─── INGRESO DE NOMBRE ───────────────────────────────────────
def pedir_nombre(puntaje):
    nombre = ""
    btn_ok = pygame.Rect(ANCHO//2-80, 400, 160, 50)

    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and nombre.strip():
                    corriendo = False
                elif ev.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                elif len(nombre) < 12 and ev.unicode.isprintable() and ev.unicode != "":
                    nombre += ev.unicode
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_ok.collidepoint(ev.pos) and nombre.strip():
                    corriendo = False

        # ── FONDO del menú en ingreso nombre ──
        dibujar_fondo_menu()

        for p in particulas:
            p.actualizar(); p.dibujar(pantalla)

        caja = pygame.Rect(190, 150, 520, 320)
        s    = pygame.Surface(caja.size, pygame.SRCALPHA)
        s.fill((10,12,40,210))
        pantalla.blit(s, caja.topleft)
        pygame.draw.rect(pantalla, CIAN, caja, 2, border_radius=18)

        dibujar_texto_centrado(f"PUNTAJE: {puntaje}", fuente_grande, AMARILLO, 175)
        dibujar_texto_centrado("Ingresa tu nombre:", fuente_normal, BLANCO, 248)

        campo = pygame.Rect(ANCHO//2-150, 298, 300, 48)
        pygame.draw.rect(pantalla, (25,30,65), campo, border_radius=14)
        pygame.draw.rect(pantalla, CIAN,       campo, 2, border_radius=14)
        cursor = "|" if pygame.time.get_ticks()%900 < 450 else ""
        nt = fuente_normal.render(nombre + cursor, True, BLANCO)
        pantalla.blit(nt, (campo.x+12, campo.y+10))

        if nombre.strip():
            boton_ui(btn_ok, "GUARDAR", VERDE_OSC)
        else:
            hint = fuente_mini.render("Escribe tu nombre para guardar", True, GRIS_CLARO)
            pantalla.blit(hint, (ANCHO//2 - hint.get_width()//2, 410))

        pygame.display.flip()
        clock.tick(60)

    return nombre.strip() or "Anonimo"

# ─── NIVEL COMPLETADO ────────────────────────────────────────
def pantalla_nivel_completado(nivel, resumen):
    btn_cont  = pygame.Rect(ANCHO//2-110, 534, 220, 50)
    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_cont.collidepoint(ev.pos): corriendo = False
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                corriendo = False

        # ── FONDO del juego en pantalla nivel ──
        dibujar_fondo_juego()

        for p in particulas:
            p.actualizar(); p.dibujar(pantalla)

        caja = pygame.Rect(70, 65, ANCHO-140, 460)
        s    = pygame.Surface(caja.size, pygame.SRCALPHA)
        s.fill((10,12,40,200))
        pantalla.blit(s, caja.topleft)
        pygame.draw.rect(pantalla, VERDE, caja, 2, border_radius=18)

        dibujar_texto_centrado(f"NIVEL {nivel} COMPLETADO", fuente_grande, VERDE, 85)
        dibujar_texto_centrado("Que aprendiste en este nivel?", fuente_normal, AMARILLO, 138)

        y = 192
        vistos = {}
        for info in resumen:
            if info["id"] not in vistos:
                vistos[info["id"]] = info
        for info in list(vistos.values())[:5]:
            icono = "!" if info["tipo"] == "amenaza" else "OK"
            col   = ROJO if info["tipo"] == "amenaza" else VERDE
            tit   = fuente_pequena.render(f"{icono}  {info['texto']}", True, col)
            pantalla.blit(tit, (110, y))
            det   = fuente_mini.render(info["detalle"].split("\n")[0], True, GRIS_CLARO)
            pantalla.blit(det, (130, y+22))
            y += 54
            if y > 490: break

        boton_ui(btn_cont, "SIGUIENTE NIVEL >", AZUL_OSC)
        pygame.display.flip()
        clock.tick(60)

# ─── PANTALLA FINAL ──────────────────────────────────────────
def pantalla_fin(puntaje, victoria=False):
    detener_musica()
    nombre  = pedir_nombre(puntaje)
    guardar_ranking(nombre, puntaje)
    ranking = cargar_ranking()

    btn_menu    = pygame.Rect(ANCHO//2-230, 510, 200, 52)
    btn_ranking = pygame.Rect(ANCHO//2+30,  510, 200, 52)

    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_menu.collidepoint(ev.pos):    return "menu"
                if btn_ranking.collidepoint(ev.pos): pantalla_ranking()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return "menu"

        # ── FONDO del menú en pantalla final ──
        dibujar_fondo_menu()

        for p in particulas:
            p.actualizar(); p.dibujar(pantalla)

        caja     = pygame.Rect(90, 65, ANCHO-180, 440)
        s        = pygame.Surface(caja.size, pygame.SRCALPHA)
        s.fill((10,12,40,210))
        pantalla.blit(s, caja.topleft)
        borde_col = VERDE if victoria else ROJO
        pygame.draw.rect(pantalla, borde_col, caja, 3, border_radius=18)

        if victoria:
            dibujar_texto_centrado("GANASTE!", fuente_grande, VERDE, 90)
            dibujar_texto_centrado("Derrotaste al Hacker Supremo!", fuente_normal, BLANCO, 155)
        else:
            dibujar_texto_centrado("GAME OVER", fuente_grande, ROJO, 90)
            dibujar_texto_centrado("El internet necesita mas defensores!", fuente_normal, BLANCO, 155)

        dibujar_texto_centrado(f"Jugador: {nombre}", fuente_normal, AMARILLO, 210)
        dibujar_texto_centrado(f"Puntaje: {puntaje}", fuente_grande, AMARILLO, 248)

        pygame.draw.line(pantalla, GRIS, (160,302),(ANCHO-160,302), 1)
        dibujar_texto_centrado("--- TOP 5 ---", fuente_pequena, GRIS_CLARO, 308)
        for i, entry in enumerate(ranking[:5]):
            col = AMARILLO if entry["nombre"] == nombre else BLANCO
            rt  = fuente_pequena.render(
                f"#{i+1}  {entry['nombre'][:10]:<10}  {entry['puntaje']:>6}", True, col)
            pantalla.blit(rt, (ANCHO//2 - rt.get_width()//2, 340 + i*28))

        boton_ui(btn_menu,    "<  MENU",    AZUL_OSC)
        boton_ui(btn_ranking, "*  RANKING", (70,55,8))
        pygame.display.flip()
        clock.tick(60)

# ─── HELPERS SPAWN ───────────────────────────────────────────
def _carriles_ocupados(objetos):
    return [obj.carril_x for obj in objetos]

def generar_objeto(vel, objetos):
    ocupados = _carriles_ocupados(objetos)
    for _ in range(15):
        nuevo = ObjetoJuego(vel, ocupados)
        colisiona = any(nuevo.rect.colliderect(obj.rect.inflate(10, SEP_VERTICAL_MIN))
                        for obj in objetos)
        if not colisiona:
            return nuevo
    return ObjetoJuego(vel)

def spawn_inicial(cant, vel):
    objetos     = []
    altura_zona = ALTO - ALTO_HUD
    franja      = max(SEP_VERTICAL_MIN, altura_zona // max(cant, 1))
    for i in range(cant):
        obj = generar_objeto(vel, objetos)
        obj.rect.y = -(i * franja) - random.randint(60, 140)
        objetos.append(obj)
    return objetos

# ─── DIBUJAR JUEGO ───────────────────────────────────────────
def _dibujar_juego(objetos, jugador, boss, boss_activo,
                   puntos, vidas, nivel, progreso_nivel,
                   mensaje, color_msg, timer_mensaje,
                   tooltip_txt, tooltip_col, tooltip_timer, t,
                   jugador_anim=0, disparos_jugador=None):

    # ── FONDO del juego ──
    dibujar_fondo_juego()

    for gx in range(0, ANCHO, 90):
        pygame.draw.line(pantalla, (20,22,45), (gx, ALTO_HUD), (gx, ALTO), 1)
    for gy in range(ALTO_HUD, ALTO, 80):
        pygame.draw.line(pantalla, (20,22,45), (0, gy), (ANCHO, gy), 1)

    if not boss_activo:
        for obj in objetos: obj.dibujar()
    else:
        if boss: boss.dibujar()
        if disparos_jugador:
            for d in disparos_jugador: d.dibujar()

    jx = jugador.x + (random.randint(-4,4) if jugador_anim > 0 else 0)
    jr = pygame.Rect(jx, jugador.y, jugador.width, jugador.height)

    if img_escudo:
        pantalla.blit(img_escudo, jr.topleft)
    else:
        brillo   = int(30*abs(math.sin(t*0.07)))
        base_col = tuple(min(c+brillo, 255) for c in AZUL)
        pygame.draw.rect(pantalla, base_col, jr, border_radius=14)
        borde_c  = CIAN if jugador_anim == 0 else ROJO
        pygame.draw.rect(pantalla, borde_c, jr, 2, border_radius=14)
        et = fuente_mini.render("< ESCUDO >", True, BLANCO)
        pantalla.blit(et, (jr.x + (jr.w - et.get_width())//2,
                           jr.y + (jr.h - et.get_height())//2))

    # HUD
    hud = pygame.Surface((ANCHO, ALTO_HUD), pygame.SRCALPHA)
    hud.fill((*FONDO_HUD, 230))
    pantalla.blit(hud, (0,0))
    pygame.draw.line(pantalla, CIAN, (0, ALTO_HUD), (ANCHO, ALTO_HUD), 2)

    pt = fuente_grande.render(f"{puntos:>6} pts", True, AMARILLO)
    pantalla.blit(pt, (18, 12))

    v_lbl = fuente_mini.render("VIDAS", True, GRIS_CLARO)
    pantalla.blit(v_lbl, (338, 8))
    for i in range(3):
        col_v = ROJO if i < vidas else GRIS
        hx    = 335 + i*46
        pygame.draw.rect(pantalla, col_v, (hx, 24, 38, 22), border_radius=11)
        if i < vidas:
            ht = fuente_mini.render("v", True, BLANCO)
            pantalla.blit(ht, (hx+10, 25))

    nv = fuente_normal.render(f"NVL {nivel}", True, CIAN)
    pantalla.blit(nv, (530, 12))

    lbl_prog = fuente_mini.render(
        f"Progreso nivel {nivel}" if nivel < 5 else "NIVEL BOSS!", True, GRIS_CLARO)
    pantalla.blit(lbl_prog, (640, 8))
    dibujar_barra(640, 30, 240, 14,
                  min(progreso_nivel, 1.0),
                  VERDE if nivel < 5 else ROJO, GRIS, radio=7)

    if timer_mensaje > 0:
        alpha   = min(255, timer_mensaje*5)
        msg_surf = fuente_pequena.render(mensaje, True, color_msg)
        bg_w    = msg_surf.get_width() + 28
        bg      = pygame.Surface((bg_w, 36), pygame.SRCALPHA)
        bg.fill((0,0,0, min(alpha,190)))
        mx      = ANCHO//2 - bg_w//2
        pantalla.blit(bg, (mx, ALTO-52))
        pygame.draw.rect(pantalla, color_msg, (mx, ALTO-52, bg_w, 36), 1, border_radius=8)
        msg_surf.set_alpha(alpha)
        pantalla.blit(msg_surf, (ANCHO//2 - msg_surf.get_width()//2, ALTO-46))

    if tooltip_timer > 0:
        alpha_t = min(230, tooltip_timer*4)
        tip_bg  = pygame.Surface((258, 114), pygame.SRCALPHA)
        tip_bg.fill((8,10,30, min(alpha_t,200)))
        ty = ALTO_HUD + 10
        pantalla.blit(tip_bg, (ANCHO-266, ty))
        pygame.draw.rect(pantalla, tooltip_col,
                         (ANCHO-266, ty, 258, 114), 1, border_radius=8)
        tit = fuente_mini.render("Sabias que...?", True, tooltip_col)
        pantalla.blit(tit, (ANCHO-258, ty+8))
        for i, l in enumerate(tooltip_txt.split("\n")[:4]):
            lt = fuente_mini.render(l, True, BLANCO)
            lt.set_alpha(alpha_t)
            pantalla.blit(lt, (ANCHO-258, ty+28+i*20))

    if t < 300:
        alpha_hint = max(0, 255 - max(0, t-240)*4)
        ht = fuente_mini.render("<- -> para mover el escudo", True, GRIS_CLARO)
        ht.set_alpha(alpha_hint)
        pantalla.blit(ht, (ANCHO//2 - ht.get_width()//2, ALTO-20))

# ─── LÓGICA PRINCIPAL ────────────────────────────────────────
def jugar():
    iniciar_musica("musica_juego.mp3")

    jugador  = pygame.Rect(ANCHO//2 - ESCUDO_W//2, ALTO-70, ESCUDO_W, 28)
    puntos   = 0
    vidas    = 3
    nivel    = 1
    amenazas_bloqueadas = 0
    AMENAZAS_POR_NIVEL  = 5

    vel_objetos = VEL_INICIAL
    max_obj     = OBJETOS_POR_NIVEL[0]
    objetos     = spawn_inicial(max_obj, vel_objetos)

    mensaje       = ""
    color_msg     = BLANCO
    timer_mensaje = 0
    tooltip_txt   = ""
    tooltip_col   = BLANCO
    tooltip_timer = 0
    TOOLTIP_DUR   = 210

    progreso_nivel = 0.0
    resumen_nivel  = []

    boss_activo    = False
    boss           = None
    boss_derrotado = False

    disparos_jugador = []
    cooldown_disparo = 0
    COOLDOWN_MAX     = 22

    jugador_anim = 0
    t = 0

    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "menu"
                if ev.key == pygame.K_SPACE:
                    if boss_activo and boss and not boss.pregunta_activa and cooldown_disparo == 0:
                        disparos_jugador.append(
                            ProyectilJugador(jugador.centerx, jugador.top))
                        cooldown_disparo = COOLDOWN_MAX

        t += 1

        teclas = pygame.key.get_pressed()
        dx = 0
        if teclas[pygame.K_LEFT]:  dx = -VEL_JUGADOR
        if teclas[pygame.K_RIGHT]: dx =  VEL_JUGADOR
        jugador.x = max(0, min(ANCHO - jugador.width, jugador.x + dx))
        if jugador_anim > 0: jugador_anim -= 1

        if cooldown_disparo > 0: cooldown_disparo -= 1
        if boss_activo and boss and not boss.pregunta_activa:
            if teclas[pygame.K_SPACE] and cooldown_disparo == 0:
                disparos_jugador.append(
                    ProyectilJugador(jugador.centerx, jugador.top))
                cooldown_disparo = COOLDOWN_MAX

        if not boss_activo:
            for obj in objetos[:]:
                obj.actualizar()

                for otro in objetos:
                    if otro is obj: continue
                    if obj.rect.colliderect(otro.rect.inflate(8,8)):
                        if obj.rect.y > otro.rect.y:
                            obj.rect.y = otro.rect.bottom + 12
                        else:
                            otro.rect.y = obj.rect.bottom + 12

                if jugador.colliderect(obj.rect):
                    info = obj.info
                    if info["id"] not in [r["id"] for r in resumen_nivel]:
                        resumen_nivel.append(info)

                    if info["tipo"] == "amenaza":
                        puntos += 10
                        amenazas_bloqueadas += 1
                        progreso_nivel = amenazas_bloqueadas / AMENAZAS_POR_NIVEL
                        mensaje       = f"+10  Amenaza bloqueada!"
                        color_msg     = VERDE
                        tooltip_txt   = info["detalle"]
                        tooltip_col   = VERDE
                        tooltip_timer = TOOLTIP_DUR
                        reproducir(snd_acierto)
                    else:
                        puntos        = max(0, puntos-5)
                        mensaje       = f"-5   Ese era seguro! No lo bloquees."
                        color_msg     = NARANJA
                        tooltip_txt   = info["detalle"]
                        tooltip_col   = NARANJA
                        tooltip_timer = TOOLTIP_DUR
                        jugador_anim  = 20
                        reproducir(snd_error)

                    timer_mensaje = 150
                    objetos.remove(obj)
                    nuevo = generar_objeto(vel_objetos, objetos)
                    nuevo.rect.y = random.randint(-320, -120)
                    objetos.append(nuevo)
                    continue

                if obj.rect.top > ALTO:
                    if obj.info["tipo"] == "amenaza":
                        vidas        -= 1
                        mensaje       = "Una amenaza paso! Cuidado!"
                        color_msg     = ROJO
                        timer_mensaje = 160
                        tooltip_txt   = obj.info["detalle"]
                        tooltip_col   = ROJO
                        tooltip_timer = TOOLTIP_DUR
                        jugador_anim  = 25
                        reproducir(snd_error)
                    objetos.remove(obj)
                    nuevo = generar_objeto(vel_objetos, objetos)
                    nuevo.rect.y = random.randint(-320, -120)
                    objetos.append(nuevo)

            if amenazas_bloqueadas >= AMENAZAS_POR_NIVEL * nivel and nivel < 5:
                reproducir(snd_nivel)
                pantalla_nivel_completado(nivel, resumen_nivel)
                nivel              += 1
                vel_objetos         = min(VEL_INICIAL + (nivel-1)*0.8, VEL_MAXIMA)
                max_obj             = OBJETOS_POR_NIVEL[nivel-1]
                amenazas_bloqueadas = 0
                progreso_nivel      = 0.0
                resumen_nivel       = []
                objetos             = spawn_inicial(max_obj, vel_objetos)

            if nivel == 5 and not boss_activo and not boss_derrotado:
                boss_activo = True
                boss        = Boss()
                objetos.clear()
                reproducir(snd_boss)
                mensaje       = "HACKER SUPREMO! Presiona ESPACIO para dispararle."
                color_msg     = ROJO
                timer_mensaje = 280
                disparos_jugador.clear()

        else:
            if boss:
                boss.actualizar()

                for d in disparos_jugador[:]:
                    d.actualizar()
                    if d.rect.bottom < ALTO_HUD:
                        disparos_jugador.remove(d)
                        continue
                    if d.rect.colliderect(boss.rect) and not boss.pregunta_activa:
                        disparos_jugador.remove(d)
                        boss.siguiente_pregunta()

                if boss.pregunta_activa:
                    _dibujar_juego(objetos, jugador, boss, boss_activo,
                                   puntos, vidas, nivel, progreso_nivel,
                                   mensaje, color_msg, timer_mensaje,
                                   tooltip_txt, tooltip_col, tooltip_timer, t,
                                   jugador_anim, disparos_jugador)
                    pygame.display.flip()
                    correcto = pantalla_pregunta_boss(boss)
                    if correcto:
                        boss.recibir_golpe()
                        puntos += 20
                        reproducir(snd_acierto)
                    else:
                        vidas = max(0, vidas-1)
                        reproducir(snd_error)
                        jugador_anim = 30
                    boss.pregunta_activa = False

                for p in boss.proyectiles[:]:
                    if jugador.colliderect(p.rect):
                        vidas        -= 1
                        boss.proyectiles.remove(p)
                        mensaje       = "Te golpeo el proyectil! Esquiva!"
                        color_msg     = ROJO
                        timer_mensaje = 120
                        jugador_anim  = 30
                        reproducir(snd_error)

                if not boss.vivo:
                    boss_activo    = False
                    boss_derrotado = True
                    puntos        += 100
                    return pantalla_fin(puntos, victoria=True)

        if vidas <= 0:
            return pantalla_fin(puntos, victoria=False)

        if timer_mensaje > 0: timer_mensaje -= 1
        if tooltip_timer > 0: tooltip_timer -= 1

        _dibujar_juego(objetos, jugador, boss, boss_activo,
                       puntos, vidas, nivel, progreso_nivel,
                       mensaje, color_msg, timer_mensaje,
                       tooltip_txt, tooltip_col, tooltip_timer, t,
                       jugador_anim, disparos_jugador)

        pygame.display.flip()
        clock.tick(60)

    return "menu"

# ─── MAIN ────────────────────────────────────────────────────
def main():
    estado = "menu"
    while True:
        if estado == "menu":
            estado = menu_principal()
        elif estado == "jugar":
            estado = jugar()
        else:
            estado = "menu"

if __name__ == "__main__":
    main()