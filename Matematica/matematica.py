import pygame
import random
import time
import sys
import os
import json
import math


try:
    import cv2
    CV2_DISPONIBLE = True
except ImportError:
    CV2_DISPONIBLE = False

# ══════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════
ANCHO, ALTO = 1280, 800
FPS = 60

# Paleta: dark academia / pizarrón moderno
C_FONDO        = (8,   12,  24)
C_PANEL        = (14,  20,  38)
C_PANEL2       = (20,  28,  52)
C_BORDE        = (40,  55,  100)
C_BORDE_LUZ    = (80,  120, 220)
C_TEXTO        = (230, 235, 255)
C_TEXTO2       = (140, 150, 185)
C_TEXTO3       = (80,  90,  130)
C_BLANCO       = (255, 255, 255)
C_NEGRO        = (0,   0,   0)

C_VERDE        = (50,  220, 120)
C_VERDE_OSC    = (20,  140, 70)
C_ROJO         = (240, 70,  70)
C_ROJO_OSC     = (160, 30,  30)
C_AMARILLO     = (255, 210, 50)
C_AMARILLO_OSC = (180, 140, 10)
C_AZUL         = (60,  140, 255)
C_AZUL_OSC     = (30,  80,  180)
C_NARANJA      = (255, 140, 40)
C_NARANJA_OSC  = (180, 80,  10)
C_PURPURA      = (170, 90,  255)
C_CIAN         = (50,  220, 220)
C_ROSA         = (255, 90,  180)

# Niveles de dificultad
NIVELES = ["Fácil", "Normal", "Difícil", "Extremo"]

# Operaciones disponibles
OPERACIONES = ["+", "-", "×", "÷", "²", "√", "%"]

# ══════════════════════════════════════════════════════════════════════
# PYGAME INIT
# ══════════════════════════════════════════════════════════════════════
pygame.init()
pygame.mixer.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("MathFlash 3.0 ⚡")
reloj = pygame.time.Clock()

# Fuentes — intentamos fuentes más llamativas
def _fuente(nombre, tamaño, bold=False):
    for n in [nombre, "Segoe UI", "DejaVu Sans", "Arial"]:
        try:
            f = pygame.font.SysFont(n, tamaño, bold=bold)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.SysFont(None, tamaño, bold=bold)

F_TITULO    = _fuente("Impact",       72, bold=False)
F_GRANDE    = _fuente("Impact",       52)
F_SUBTITULO = _fuente("Segoe UI",     36, bold=True)
F_NORMAL    = _fuente("Segoe UI",     26, bold=True)
F_CHICA     = _fuente("Segoe UI",     20)
F_MINI      = _fuente("Segoe UI",     15)
F_HUD       = _fuente("Consolas",     22, bold=True)
F_MONO      = _fuente("Consolas",     42, bold=True)
F_MONO_G    = _fuente("Consolas",     60, bold=True)

# ══════════════════════════════════════════════════════════════════════
# ESTADO GLOBAL
# ══════════════════════════════════════════════════════════════════════
volumen_global = 0.6

# ══════════════════════════════════════════════════════════════════════
# UTILIDADES GENERALES
# ══════════════════════════════════════════════════════════════════════
# ====================== RESOLVER RUTA (PyInstaller) ======================
def resolver_ruta(ruta_relativa):
    """ Obtiene la ruta absoluta de los recursos, compatible con PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)
# =========================================================================


def reproducir_musica(archivo):
    pygame.mixer.music.stop()
    try:
        # Intentos con diferentes rutas
        for ruta_intento in [
            resolver_ruta(f"matematica/{archivo}"),
            resolver_ruta(archivo),
            resolver_ruta(f"Matematica/{archivo}"),
        ]:
            if os.path.exists(ruta_intento):
                pygame.mixer.music.load(ruta_intento)
                pygame.mixer.music.set_volume(volumen_global)
                pygame.mixer.music.play(-1)
                print(f"[Música] ✅ Reproduciendo: {ruta_intento}")
                return
        print(f"[Música] ❌ No encontrado: {archivo}")
    except Exception as e:
        print(f"[Música] Error: {e}")


def overlay(alpha=160):
    s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    pantalla.blit(s, (0, 0))


def rect_redondeado_alfa(surf, color, rect, radio=12, alpha=200):
    """Dibuja un rectángulo redondeado semitransparente."""
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, rect.width, rect.height), border_radius=radio)
    surf.blit(s, rect.topleft)


def texto_con_sombra(surf, texto, fuente, color, pos, sombra_offset=2, sombra_alpha=120):
    so = fuente.render(texto, True, (0, 0, 0))
    so.set_alpha(sombra_alpha)
    surf.blit(so, (pos[0] + sombra_offset, pos[1] + sombra_offset))
    surf.blit(fuente.render(texto, True, color), pos)


def centrado(surf, texto, fuente, color, y, sombra=True):
    r = fuente.render(texto, True, color)
    x = ANCHO // 2 - r.get_width() // 2
    if sombra:
        so = fuente.render(texto, True, (0, 0, 0))
        so.set_alpha(100)
        surf.blit(so, (x + 2, y + 2))
    surf.blit(r, (x, y))


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ══════════════════════════════════════════════════════════════════════
# PARTÍCULAS Y EFECTOS
# ══════════════════════════════════════════════════════════════════════
class Particula:
    __slots__ = ["x", "y", "vx", "vy", "vida", "vida_max", "color", "r", "tipo"]

    def __init__(self, x, y, color, tipo="chispa"):
        self.x = float(x)
        self.y = float(y)
        self.tipo = tipo
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 8) if tipo == "chispa" else random.uniform(1, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - (3 if tipo == "chispa" else 1)
        self.vida = random.randint(30, 70)
        self.vida_max = self.vida
        self.color = color
        self.r = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.18
        self.vx *= 0.97
        self.vida -= 1

    def draw(self, surf):
        t = self.vida / self.vida_max
        alpha = int(255 * t)
        r = max(1, int(self.r * t))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r + 1, r + 1), r)
        surf.blit(s, (int(self.x) - r - 1, int(self.y) - r - 1))


particulas: list[Particula] = []


def explotar(x, y, color, n=30, tipo="chispa"):
    for _ in range(n):
        particulas.append(Particula(x, y, color, tipo))


def actualizar_particulas():
    for p in particulas[:]:
        p.update()
        p.draw(pantalla)
        if p.vida <= 0:
            particulas.remove(p)


# ══════════════════════════════════════════════════════════════════════
# ESTRELLAS DE FONDO
# ══════════════════════════════════════════════════════════════════════
class Estrella:
    def __init__(self):
        self.x = random.uniform(0, ANCHO)
        self.y = random.uniform(0, ALTO)
        self.r = random.uniform(0.5, 2.0)
        self.brillo = random.uniform(0.3, 1.0)
        self.vel_brillo = random.uniform(0.005, 0.02) * random.choice([-1, 1])

    def update(self):
        self.brillo += self.vel_brillo
        if self.brillo > 1.0 or self.brillo < 0.2:
            self.vel_brillo *= -1

    def draw(self, surf):
        c = int(self.brillo * 180)
        pygame.draw.circle(surf, (c, c, min(255, c + 60)), (int(self.x), int(self.y)), int(self.r))


estrellas_bg = [Estrella() for _ in range(120)]


def dibujar_fondo_espacio(t=0):
    pantalla.fill(C_FONDO)
    for e in estrellas_bg:
        e.update()
        e.draw(pantalla)
    # Nebulosa decorativa
    for i, (cx, cy, cr, col) in enumerate([
        (200, 150, 200, (30, 20, 80)),
        (1000, 600, 180, (20, 50, 40)),
        (600, 400, 250, (40, 15, 60)),
    ]):
        oy = int(math.sin(t * 0.01 + i) * 15)
        s = pygame.Surface((cr * 2, cr * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, 60), (cr, cr), cr)
        pantalla.blit(s, (cx - cr, cy + oy - cr))


# ══════════════════════════════════════════════════════════════════════
# VIDEO FONDO (opcional)
# ══════════════════════════════════════════════════════════════════════
class VideoFondo:
    def __init__(self, ruta):
        self.cap = None
        self.activo = False
        if CV2_DISPONIBLE:
            ruta_abs = resolver_ruta(ruta)
            if os.path.exists(ruta_abs):
                self.cap = cv2.VideoCapture(ruta_abs)
                self.activo = self.cap.isOpened()

    def obtener_frame(self):
        if not self.activo or self.cap is None:
            return None
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (ANCHO, ALTO))
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    def liberar(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()


video_menu = VideoFondo("matematica/fondo.mp4")

# ══════════════════════════════════════════════════════════════════════
# RANKING
# ══════════════════════════════════════════════════════════════════════
RUTA_RANKING = resolver_ruta("matematica/ranking.json")


def cargar_ranking():
    try:
        if os.path.exists(RUTA_RANKING):
            with open(RUTA_RANKING, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return []


def guardar_ranking(ranking):
    try:
        d = os.path.dirname(RUTA_RANKING)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(RUTA_RANKING, "w", encoding="utf-8") as f:
            json.dump(ranking, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Advertencia ranking: {e}")


def agregar_al_ranking(nombre, puntos, aciertos, errores, racha_max, calificacion, nivel):
    r = cargar_ranking()
    r.append({
        "nombre":      nombre,
        "puntos":      puntos,
        "aciertos":    aciertos,
        "errores":     errores,
        "racha_max":   racha_max,
        "calificacion": round(calificacion, 1),
        "nivel":       nivel,
        "fecha":       time.strftime("%d/%m/%Y %H:%M"),
    })
    r.sort(key=lambda x: x["puntos"], reverse=True)
    r = r[:15]
    guardar_ranking(r)
    return r


# ══════════════════════════════════════════════════════════════════════
# COMPONENTES UI
# ══════════════════════════════════════════════════════════════════════
class Boton:
    def __init__(self, texto, x, y, ancho, alto, color, color_txt=None,
                 fuente=None, icono=""):
        self.texto     = texto
        self.icono     = icono
        self.rect      = pygame.Rect(x, y, ancho, alto)
        self.color     = color
        self.color_txt = color_txt or C_BLANCO
        self.fuente    = fuente or F_NORMAL
        self._pulso    = 0.0

    def _color_actual(self):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        if hover:
            return tuple(min(c + 40, 255) for c in self.color)
        return self.color

    def dibujar(self, surf):
        c = self._color_actual()
        # Sombra
        sombra = pygame.Surface((self.rect.w, self.rect.h + 4), pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 80), (3, 5, self.rect.w, self.rect.h), border_radius=10)
        surf.blit(sombra, (self.rect.x, self.rect.y))
        # Fondo
        pygame.draw.rect(surf, c, self.rect, border_radius=10)
        # Borde luminoso
        borde = tuple(min(v + 80, 255) for v in self.color)
        pygame.draw.rect(surf, borde, self.rect, 2, border_radius=10)
        # Texto
        label = (self.icono + "  " + self.texto).strip() if self.icono else self.texto
        s = self.fuente.render(label, True, self.color_txt)
        surf.blit(s, s.get_rect(center=self.rect.center))

    def clickeado(self, pos):
        return self.rect.collidepoint(pos)


class SliderVolumen:
    def __init__(self, x, y, ancho):
        self.rect     = pygame.Rect(x, y, ancho, 10)
        self.valor    = volumen_global
        self.w_knob   = 22
        self._drag    = False

    @property
    def _knob_x(self):
        return self.rect.x + int(self.valor * (self.rect.w - self.w_knob))

    def dibujar(self, surf):
        # Track
        pygame.draw.rect(surf, C_PANEL2, self.rect, border_radius=5)
        # Fill
        fw = int(self.valor * self.rect.w)
        if fw > 0:
            pygame.draw.rect(surf, C_AZUL,
                             pygame.Rect(self.rect.x, self.rect.y, fw, self.rect.h),
                             border_radius=5)
        pygame.draw.rect(surf, C_BORDE_LUZ, self.rect, 1, border_radius=5)
        # Knob
        kr = pygame.Rect(self._knob_x, self.rect.y - 6, self.w_knob, self.rect.h + 12)
        pygame.draw.rect(surf, C_BLANCO, kr, border_radius=6)
        # Porcentaje
        pct = F_CHICA.render(f"{int(self.valor * 100)}%", True, C_TEXTO2)
        surf.blit(pct, (self.rect.right + 14, self.rect.y - 4))

    def manejar(self, ev):
        global volumen_global
        kr = pygame.Rect(self._knob_x, self.rect.y - 6, self.w_knob, self.rect.h + 12)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if kr.collidepoint(ev.pos) or self.rect.collidepoint(ev.pos):
                self._drag = True
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self._drag = False
        elif ev.type == pygame.MOUSEMOTION and self._drag:
            nx = max(self.rect.x, min(ev.pos[0], self.rect.right - self.w_knob))
            self.valor = (nx - self.rect.x) / max(1, self.rect.w - self.w_knob)
            volumen_global = self.valor
            pygame.mixer.music.set_volume(volumen_global)


class SelectorFila:
    """Selector de opción única en fila horizontal."""

    def __init__(self, titulo, opciones, y, x0=300, espaciado=170, ancho_op=155, alto_op=44):
        self.titulo    = titulo
        self.opciones  = opciones
        self.y         = y
        self.sel       = opciones[0]
        self.rects     = {}
        for i, op in enumerate(opciones):
            self.rects[op] = pygame.Rect(x0 + i * espaciado, y, ancho_op, alto_op)

    def dibujar(self, surf):
        lbl = F_HUD.render(self.titulo, True, C_TEXTO2)
        surf.blit(lbl, (50, self.y + 10))
        for op, rect in self.rects.items():
            activa = op == self.sel
            hover  = rect.collidepoint(pygame.mouse.get_pos()) and not activa
            if activa:
                pygame.draw.rect(surf, C_AZUL_OSC, rect, border_radius=8)
                pygame.draw.rect(surf, C_BORDE_LUZ, rect, 2, border_radius=8)
                c_txt = C_BLANCO
            elif hover:
                pygame.draw.rect(surf, C_PANEL2, rect, border_radius=8)
                pygame.draw.rect(surf, C_BORDE, rect, 2, border_radius=8)
                c_txt = C_TEXTO
            else:
                pygame.draw.rect(surf, C_PANEL, rect, border_radius=8)
                pygame.draw.rect(surf, C_BORDE, rect, 1, border_radius=8)
                c_txt = C_TEXTO3
            s = F_CHICA.render(str(op), True, c_txt)
            surf.blit(s, s.get_rect(center=rect.center))

    def click(self, pos):
        for op, rect in self.rects.items():
            if rect.collidepoint(pos):
                self.sel = op
                return True
        return False


class SelectorMulti:
    """Selector de múltiples opciones (toggle)."""

    def __init__(self, titulo, opciones, y, x0=300, espaciado=110, ancho_op=95, alto_op=44):
        self.titulo    = titulo
        self.opciones  = opciones
        self.y         = y
        self.activas   = {opciones[0]}
        self.rects     = {}
        for i, op in enumerate(opciones):
            self.rects[op] = pygame.Rect(x0 + i * espaciado, y, ancho_op, alto_op)

    def dibujar(self, surf):
        lbl = F_HUD.render(self.titulo, True, C_TEXTO2)
        surf.blit(lbl, (50, self.y + 10))
        for op, rect in self.rects.items():
            activa = op in self.activas
            hover  = rect.collidepoint(pygame.mouse.get_pos()) and not activa
            if activa:
                pygame.draw.rect(surf, C_VERDE_OSC, rect, border_radius=8)
                pygame.draw.rect(surf, C_VERDE, rect, 2, border_radius=8)
                c_txt = C_BLANCO
            elif hover:
                pygame.draw.rect(surf, C_PANEL2, rect, border_radius=8)
                pygame.draw.rect(surf, C_BORDE, rect, 2, border_radius=8)
                c_txt = C_TEXTO
            else:
                pygame.draw.rect(surf, C_PANEL, rect, border_radius=8)
                pygame.draw.rect(surf, C_BORDE, rect, 1, border_radius=8)
                c_txt = C_TEXTO3
            s = F_CHICA.render(str(op), True, c_txt)
            surf.blit(s, s.get_rect(center=rect.center))

    def click(self, pos):
        for op, rect in self.rects.items():
            if rect.collidepoint(pos):
                if op in self.activas and len(self.activas) > 1:
                    self.activas.discard(op)
                else:
                    self.activas.add(op)
                return True
        return False

    def lista(self):
        return [op for op in self.opciones if op in self.activas]


# ══════════════════════════════════════════════════════════════════════
# MOTOR MATEMÁTICO MEJORADO
# ══════════════════════════════════════════════════════════════════════

RANGOS = {
    "Fácil":   (10,  20,  5),   # (max_a, max_b, max_div)
    "Normal":  (50,  50,  12),
    "Difícil": (200, 150, 25),
    "Extremo": (999, 500, 50),
}

PTS_NIVEL = {"Fácil": 10, "Normal": 20, "Difícil": 40, "Extremo": 80}
PEN_NIVEL = {"Fácil": 5,  "Normal": 15, "Difícil": 30, "Extremo": 50}


def _fmt(n):
    """Formatea entero eliminando .0"""
    return str(int(n)) if isinstance(n, float) and n == int(n) else str(n)


def generar_operacion(dificultad, operaciones_sel, conjunto):
    """
    Devuelve (texto_pregunta, respuesta_str, valor_pts_extra).
    valor_pts_extra: las operaciones difíciles valen más.
    """
    op = random.choice(operaciones_sel)
    rmax_a, rmax_b, rmax_div = RANGOS[dificultad]

    # Conjuntos numéricos
    if conjunto == "Enteros":
        signo_a = random.choice([-1, 1])
        signo_b = random.choice([-1, 1])
    else:
        signo_a = signo_b = 1

    a = signo_a * random.randint(2, rmax_a)
    b = signo_b * random.randint(2, rmax_b)

    pts_extra = 0

    if op == "+":
        res = a + b
        texto = f"{a} + {b}"

    elif op == "-":
        if conjunto == "Naturales" and a < b:
            a, b = b, a
        res = a - b
        texto = f"{a} - {b}"

    elif op == "×":
        # Multiplicación: usar rangos más moderados
        a = signo_a * random.randint(2, min(rmax_a, 30 if dificultad in ("Fácil", "Normal") else 99))
        b = signo_b * random.randint(2, min(rmax_b, 30 if dificultad in ("Fácil", "Normal") else 99))
        res = a * b
        texto = f"{a} × {b}"
        pts_extra = 5

    elif op == "÷":
        # División exacta siempre
        divisor = random.randint(2, min(abs(b) or 2, rmax_div))
        a = divisor * random.randint(2, rmax_div)
        if conjunto == "Enteros":
            a *= signo_a
        res = a // divisor
        texto = f"{a} ÷ {divisor}"
        pts_extra = 5

    elif op == "²":
        base = random.randint(2, min(30, rmax_a // 3 + 2))
        if conjunto == "Enteros":
            base *= signo_a
        res = base * base
        texto = f"{base}²"
        pts_extra = 10

    elif op == "√":
        # Raíz cuadrada perfecta
        base = random.randint(2, min(30, rmax_a // 3 + 2))
        res  = base
        texto = f"√{base * base}"
        pts_extra = 10

    elif op == "%":
        # Módulo
        divisor = random.randint(2, min(20, rmax_div))
        a = random.randint(divisor + 1, rmax_a)
        res = a % divisor
        texto = f"{a} mod {divisor}"
        pts_extra = 8

    else:
        # Fallback suma
        res = a + b
        texto = f"{a} + {b}"
        op = "+"

    return texto, _fmt(res), pts_extra


def escalar_dificultad_automatica(dificultad, racha_aciertos, racha_errores):
    """
    Sube si hay 5 aciertos seguidos; baja si hay 3 errores seguidos.
    """
    idx = NIVELES.index(dificultad)
    if racha_aciertos >= 5 and idx < len(NIVELES) - 1:
        return NIVELES[idx + 1], True, False
    if racha_errores >= 3 and idx > 0:
        return NIVELES[idx - 1], False, True
    return dificultad, False, False


# ══════════════════════════════════════════════════════════════════════
# DIÁLOGO CONFIRMACIÓN
# ══════════════════════════════════════════════════════════════════════
def dialogo_confirmacion(fondo_capturado):
    ancho_d, alto_d = 500, 240
    rd = pygame.Rect((ANCHO - ancho_d) // 2, (ALTO - alto_d) // 2, ancho_d, alto_d)
    btn_si = Boton("Sí, salir",      rd.x + 50,  rd.y + 150, 160, 52, C_ROJO_OSC)
    btn_no = Boton("No, continuar",  rd.x + 285, rd.y + 150, 170, 52, C_VERDE_OSC)

    while True:
        reloj.tick(FPS)
        pantalla.blit(fondo_capturado, (0, 0))
        overlay(180)

        rect_redondeado_alfa(pantalla, C_PANEL, rd, 16, 240)
        pygame.draw.rect(pantalla, C_BORDE_LUZ, rd, 2, border_radius=16)

        centrado(pantalla, "¿Salir de la partida?", F_SUBTITULO, C_BLANCO, rd.y + 35)
        centrado(pantalla, "Perderás todo el progreso de esta ronda.",
                 F_CHICA, C_TEXTO2, rd.y + 88)

        btn_si.dibujar(pantalla)
        btn_no.dibujar(pantalla)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                video_menu.liberar(); pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_n):
                    return False
                if ev.key in (pygame.K_RETURN, pygame.K_y):
                    return True
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_si.clickeado(ev.pos):  return True
                if btn_no.clickeado(ev.pos):  return False


# ══════════════════════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════════════════════
def menu_principal():
    if not pygame.mixer.music.get_busy():
        reproducir_musica("Fondo_Musical.mp3")

    bw, bh = 300, 58
    xc = ANCHO // 2 - bw // 2
    btn_jugar   = Boton("Jugar",          xc, 330, bw, bh, C_VERDE_OSC,  )
    btn_ranking = Boton("Clasificación",  xc, 405, bw, bh, C_AZUL_OSC,   )
    btn_config  = Boton("Configuración",  xc, 480, bw, bh, C_NARANJA_OSC, )
    btn_salir   = Boton("Salir",          xc, 555, bw, bh, C_ROJO_OSC,   )
    t = 0

    while True:
        reloj.tick(FPS)
        t += 1

        frame = video_menu.obtener_frame()
        if frame:
            pantalla.blit(frame, (0, 0))
            overlay(80)
        else:
            dibujar_fondo_espacio(t)

        # Título pulsante
        escala = 1 + 0.015 * math.sin(t * 0.05)
        surf_t = F_TITULO.render("MATHFLASH", True, C_AMARILLO)
        sw = int(surf_t.get_width() * escala)
        sh = int(surf_t.get_height() * escala)
        sc = pygame.transform.smoothscale(surf_t, (sw, sh))
        pantalla.blit(sc, (ANCHO // 2 - sw // 2, 100))

        surf_v = F_CHICA.render("3.0  ⚡  El desafío matemático definitivo", True, C_TEXTO2)
        pantalla.blit(surf_v, (ANCHO // 2 - surf_v.get_width() // 2, 195))

        # Línea decorativa
        py = 230
        for dx in range(-300, 301):
            c = int(abs(math.sin((dx + t * 2) * 0.02)) * 180)
            pygame.draw.line(pantalla, (c // 3, c // 2, c), (ANCHO // 2 + dx, py), (ANCHO // 2 + dx, py), 1)

        btn_jugar.dibujar(pantalla)
        btn_ranking.dibujar(pantalla)
        btn_config.dibujar(pantalla)
        btn_salir.dibujar(pantalla)

        # Versión
        ver = F_MINI.render("v3.0 — Todos los derechos reservados", True, C_TEXTO3)
        pantalla.blit(ver, (ANCHO // 2 - ver.get_width() // 2, ALTO - 24))

        actualizar_particulas()
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                video_menu.liberar(); pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                video_menu.liberar(); pygame.quit(); sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_jugar.clickeado(ev.pos):
                    explotar(btn_jugar.rect.centerx, btn_jugar.rect.centery, C_VERDE, 20)
                    return "PREPARACION"
                if btn_ranking.clickeado(ev.pos):  return "RANKING"
                if btn_config.clickeado(ev.pos):   return "CONFIGURACION"
                if btn_salir.clickeado(ev.pos):
                    video_menu.liberar(); pygame.quit(); sys.exit()


# ══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════
def pantalla_configuracion():
    slider = SliderVolumen(ANCHO // 2 - 220, ALTO // 2, 440)
    btn_v  = Boton("Volver", ANCHO // 2 - 100, ALTO - 120, 200, 52, C_AZUL_OSC)
    t = 0

    while True:
        reloj.tick(FPS)
        t += 1
        dibujar_fondo_espacio(t)

        centrado(pantalla, "Configuración", F_TITULO, C_AMARILLO, 80)
        centrado(pantalla, "Volumen de música", F_SUBTITULO, C_TEXTO, 200)

        slider.dibujar(pantalla)
        btn_v.dibujar(pantalla)

        # Visualizador de volumen
        barras = 24
        for i in range(barras):
            h = int(20 + 40 * abs(math.sin((i + t * 0.3) * 0.4)) * slider.valor)
            c = lerp_color(C_AZUL, C_CIAN, i / barras)
            bx = ANCHO // 2 - barras * 9 + i * 18
            pygame.draw.rect(pantalla, c, (bx, ALTO // 2 + 60, 12, h), border_radius=3)

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                video_menu.liberar(); pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return "MENU"
            slider.manejar(ev)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_v.clickeado(ev.pos):
                    return "MENU"


# ══════════════════════════════════════════════════════════════════════
# RANKING
# ══════════════════════════════════════════════════════════════════════
def pantalla_ranking():
    ranking = cargar_ranking()
    btn_v   = Boton("Volver", ANCHO // 2 - 100, ALTO - 75, 200, 50, C_AZUL_OSC)
    btn_bor = Boton("Borrar ranking", 30, ALTO - 75, 190, 50, C_ROJO_OSC, fuente=F_CHICA)
    scroll  = 0
    t = 0

    colores_pos = [C_AMARILLO, (192, 192, 192), (205, 127, 50)] + [C_TEXTO] * 12

    while True:
        reloj.tick(FPS)
        t += 1
        dibujar_fondo_espacio(t)

        centrado(pantalla, " CLASIFICACIÓN ", F_TITULO, C_AMARILLO, 30)

        if not ranking:
            centrado(pantalla, "¡Aún no hay partidas registradas!", F_SUBTITULO, C_TEXTO2, ALTO // 2 - 30)
        else:
            encabs = ["#", "Jugador", "Puntos", "Aciertos", "Errores", "Racha", "Nota", "Nivel", "Fecha"]
            xs     = [40, 100, 310, 440, 545, 645, 735, 820, 960]
            y_enc  = 120
            for j, enc in enumerate(encabs):
                s = F_HUD.render(enc, True, C_AMARILLO)
                pantalla.blit(s, (xs[j], y_enc))
            pygame.draw.line(pantalla, C_BORDE_LUZ, (30, 148), (ANCHO - 30, 148), 1)

            for i, ent in enumerate(ranking[scroll: scroll + 12]):
                idx_real = i + scroll
                y = 158 + i * 40
                col = colores_pos[idx_real]
                # Fondo alterno
                if i % 2 == 0:
                    rect_redondeado_alfa(pantalla, C_PANEL, pygame.Rect(30, y - 4, ANCHO - 60, 36), 6, 80)

                datos = [
                    str(idx_real + 1),
                    ent.get("nombre", "???")[:14],
                    str(ent.get("puntos", 0)),
                    str(ent.get("aciertos", 0)),
                    str(ent.get("errores", 0)),
                    str(ent.get("racha_max", "-")),
                    f"{ent.get('calificacion', 0):.1f}",
                    ent.get("nivel", "-"),
                    ent.get("fecha", "-")[:10],
                ]
                for j, dato in enumerate(datos):
                    s = F_CHICA.render(dato, True, col)
                    pantalla.blit(s, (xs[j], y))

        btn_v.dibujar(pantalla)
        btn_bor.dibujar(pantalla)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                video_menu.liberar(); pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:   return "MENU"
                if ev.key == pygame.K_DOWN:     scroll = min(scroll + 1, max(0, len(ranking) - 12))
                if ev.key == pygame.K_UP:       scroll = max(0, scroll - 1)
            elif ev.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(scroll - ev.y, max(0, len(ranking) - 12)))
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_v.clickeado(ev.pos):   return "MENU"
                if btn_bor.clickeado(ev.pos):
                    guardar_ranking([])
                    ranking = []


# ══════════════════════════════════════════════════════════════════════
# PREPARACIÓN
# ══════════════════════════════════════════════════════════════════════
def pantalla_preparacion():
    fila_dif  = SelectorFila("Dificultad inicial:",
                             NIVELES, 180, 300, 185, 170)
    fila_tpo  = SelectorFila("Duración:",
                             ["1:00", "1:30", "2:00", "3:00", "5:00"],
                             260, 290, 165, 150)
    fila_conj = SelectorFila("Conjunto numérico:",
                             ["Naturales", "Enteros"],
                             340, 290, 220, 205)
    fila_ops  = SelectorMulti("Operaciones:",
                              OPERACIONES, 420, 290, 115, 100)
    fila_auto = SelectorFila("Dificultad progresiva:",
                             ["Activada", "Desactivada"],
                             500, 315, 250, 230)

    btn_play  = Boton("  COMENZAR", ANCHO // 2 - 170, ALTO - 100, 340, 62,
                      C_VERDE_OSC, fuente=F_SUBTITULO)
    btn_back  = Boton(" Volver",   40, ALTO - 85, 150, 48, C_AZUL_OSC, fuente=F_CHICA)
    t = 0

    while True:
        reloj.tick(FPS)
        t += 1
        dibujar_fondo_espacio(t)

        # Panel central
        panel = pygame.Rect(20, 60, ANCHO - 40, ALTO - 140)
        rect_redondeado_alfa(pantalla, C_PANEL, panel, 16, 210)
        pygame.draw.rect(pantalla, C_BORDE, panel, 1, border_radius=16)

        centrado(pantalla, "Configurar partida", F_SUBTITULO, C_AMARILLO, 80)
        pygame.draw.line(pantalla, C_BORDE, (80, 125), (ANCHO - 80, 125), 1)

        fila_dif.dibujar(pantalla)
        fila_tpo.dibujar(pantalla)
        fila_conj.dibujar(pantalla)
        fila_ops.dibujar(pantalla)
        fila_auto.dibujar(pantalla)

        # Resumen selección
        ops_sel = fila_ops.lista()
        res_txt = F_MINI.render(
            f"Operaciones activas: {', '.join(ops_sel)}  |  Conjunto: {fila_conj.sel}",
            True, C_CIAN)
        pantalla.blit(res_txt, (50, 590))

        btn_play.dibujar(pantalla)
        btn_back.dibujar(pantalla)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                video_menu.liberar(); pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return "MENU", None
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                fila_dif.click(ev.pos)
                fila_tpo.click(ev.pos)
                fila_conj.click(ev.pos)
                fila_ops.click(ev.pos)
                fila_auto.click(ev.pos)
                if btn_back.clickeado(ev.pos):
                    return "MENU", None
                if btn_play.clickeado(ev.pos):
                    if not fila_ops.lista():
                        continue   # No permitir iniciar sin operaciones
                    mins, segs = map(int, fila_tpo.sel.split(":"))
                    cfg = {
                        "dificultad":  fila_dif.sel,
                        "tiempo":      mins * 60 + segs,
                        "operaciones": fila_ops.lista(),
                        "conjunto":    fila_conj.sel,
                        "adaptativa":  fila_auto.sel == "Activada",
                    }
                    return "JUEGO", cfg


# ══════════════════════════════════════════════════════════════════════
# JUEGO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════

# Logros
LOGROS = {
    "primer_acierto":    {"nombre": "¡Primera sangre!",   "desc": "Primer acierto",        "color": C_VERDE},
    "racha_5":           {"nombre": "En racha x5",         "desc": "5 aciertos seguidos",   "color": C_AMARILLO},
    "racha_10":          {"nombre": "Imparable x10",       "desc": "10 aciertos seguidos",  "color": C_NARANJA},
    "racha_20":          {"nombre": "LEGENDARIO x20",      "desc": "20 aciertos seguidos",  "color": C_PURPURA},
    "sube_dificultad":   {"nombre": "Más difícil",         "desc": "Subiste de dificultad", "color": C_CIAN},
    "velocidad":         {"nombre": "¡Velocista!",         "desc": "Respuesta en < 3 seg",  "color": C_ROSA},
    "sin_errores_10":    {"nombre": "Perfección",          "desc": "10 aciertos sin error", "color": C_AMARILLO},
}


def pantalla_juego(config):
    reproducir_musica("Jugar_Musica.mp3")

    # Fondo del juego
    try:
        fondo_img = pygame.image.load(resolver_ruta("pizarron.jpg"))
        fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))
    except pygame.error:
        fondo_img = None

    # Estado del juego
    dificultad      = config["dificultad"]
    tiempo_total    = float(config["tiempo"])
    tiempo_rest     = tiempo_total
    ops             = config["operaciones"]
    conjunto        = config["conjunto"]
    adaptativa      = config["adaptativa"]

    vidas           = 3
    puntos          = 0
    aciertos        = 0
    errores         = 0
    racha           = 0
    racha_max       = 0
    racha_errores   = 0
    sin_error_count = 0      # para logro sin errores
    tiempos_resp    = []
    logros_ganados  = set()

    entrada         = ""
    op_txt, res_ok, pts_extra = generar_operacion(dificultad, ops, conjunto)
    t_inicio_preg   = time.time()

    # Feedback
    msg_feedback   = ""
    color_feedback = C_ROJO
    t_fb_fin       = 0

    # Notificación de logro
    logro_notif       = None
    t_logro_fin       = 0

    # Barra de progreso de racha
    racha_para_subir = 5

    # Animación de número de pregunta
    num_pregunta = 0

    # Efectos de nivel
    notif_nivel    = ""
    t_nivel_fin    = 0

    t = 0

    def mostrar_logro(clave):
        nonlocal logro_notif, t_logro_fin
        if clave not in logros_ganados:
            logros_ganados.add(clave)
            logro_notif = LOGROS[clave]
            t_logro_fin = time.time() + 3.0

    def nueva_pregunta():
        nonlocal op_txt, res_ok, pts_extra, t_inicio_preg, entrada, num_pregunta
        op_txt, res_ok, pts_extra = generar_operacion(dificultad, ops, conjunto)
        t_inicio_preg = time.time()
        entrada = ""
        num_pregunta += 1

    nueva_pregunta()
    num_pregunta = 1

    RECT_INPUT = pygame.Rect(ANCHO // 2 - 240, ALTO // 2 + 40, 480, 72)

    while True:
        dt = reloj.tick(FPS) / 1000.0
        tiempo_rest = max(0.0, tiempo_rest - dt)
        t += 1

        # ── Dibujo ──────────────────────────────────────────────────
        if fondo_img:
            pantalla.blit(fondo_img, (0, 0))
            overlay(100)
        else:
            dibujar_fondo_espacio(t)

        # HUD superior — panel oscuro
        hud_rect = pygame.Rect(0, 0, ANCHO, 70)
        rect_redondeado_alfa(pantalla, C_PANEL, hud_rect, 0, 220)

        # Tiempo (barra + texto)
        prog_t = tiempo_rest / tiempo_total
        color_tiempo = C_VERDE if prog_t > 0.5 else (C_AMARILLO if prog_t > 0.25 else C_ROJO)
        pygame.draw.rect(pantalla, C_PANEL2, (0, 60, ANCHO, 10))
        pygame.draw.rect(pantalla, color_tiempo, (0, 60, int(ANCHO * prog_t), 10))
        t_txt = F_HUD.render(f"⏱  {int(tiempo_rest)}s", True, color_tiempo)
        pantalla.blit(t_txt, (20, 18))

        # Puntos
        pt_txt = F_HUD.render(f"⭐ {puntos} pts", True, C_AMARILLO)
        pantalla.blit(pt_txt, (ANCHO // 2 - pt_txt.get_width() // 2, 18))

        # Racha
        if racha > 0:
            r_col = C_NARANJA if racha >= 5 else C_CIAN
            r_txt = F_HUD.render(f" ×{racha}", True, r_col)
            pantalla.blit(r_txt, (ANCHO - r_txt.get_width() - 200, 18))

        # Dificultad
        d_txt = F_MINI.render(dificultad, True, C_TEXTO2)
        pantalla.blit(d_txt, (ANCHO - d_txt.get_width() - 20, 8))

        # Vidas (corazones)
        for v in range(3):
            cx = ANCHO - 100 + v * 32 - 10
            col_v = C_ROJO if v < vidas else (60, 30, 30)
            pygame.draw.circle(pantalla, col_v, (cx, 42), 10)

        # Aciertos / errores
        ae_txt = F_MINI.render(f"✔ {aciertos}   ✖ {errores}", True, C_TEXTO2)
        pantalla.blit(ae_txt, (ANCHO - ae_txt.get_width() - 20, 50))

        # Barra de racha hacia siguiente nivel
        if adaptativa:
            prog_racha = min(racha / racha_para_subir, 1.0)
            pygame.draw.rect(pantalla, C_PANEL2, (20, 70, 300, 6))
            pygame.draw.rect(pantalla, C_PURPURA, (20, 70, int(300 * prog_racha), 6))
            rn_txt = F_MINI.render(f"Próx. nivel: {racha}/{racha_para_subir}", True, C_TEXTO3)
            pantalla.blit(rn_txt, (20, 76))

        # ── Operación central ────────────────────────────────────────
        pygame.draw.rect(pantalla, C_PANEL, (ANCHO // 2 - 350, ALTO // 2 - 180, 700, 90),
                         border_radius=12)
        pygame.draw.rect(pantalla, C_BORDE_LUZ, (ANCHO // 2 - 350, ALTO // 2 - 180, 700, 90),
                         2, border_radius=12)

        op_surf = F_MONO_G.render(op_txt, True, C_BLANCO)
        pantalla.blit(op_surf, op_surf.get_rect(center=(ANCHO // 2, ALTO // 2 - 135)))

        # Etiqueta pregunta
        pq_txt = F_MINI.render(f"Pregunta #{num_pregunta}", True, C_TEXTO3)
        pantalla.blit(pq_txt, (ANCHO // 2 - pq_txt.get_width() // 2, ALTO // 2 - 182))

        # Hint de tipo de operación
        hint_txt = F_MINI.render(f"Conjunto: {conjunto}  |  Operaciones: {', '.join(ops)}", True, C_TEXTO3)
        pantalla.blit(hint_txt, (hint_txt.get_rect(centerx=ANCHO // 2).x, ALTO // 2 - 70))

        # Barra de entrada
        pulso = int(abs(math.sin(t * 0.05)) * 20)
        col_borde_input = tuple(min(c + pulso, 255) for c in C_BORDE_LUZ)
        pygame.draw.rect(pantalla, (25, 30, 55), RECT_INPUT, border_radius=12)
        pygame.draw.rect(pantalla, col_borde_input, RECT_INPUT, 3, border_radius=12)
        inp_surf = F_MONO.render(entrada + ("▌" if t % 60 < 30 else " "), True, C_BLANCO)
        pantalla.blit(inp_surf, inp_surf.get_rect(center=RECT_INPUT.center))

        ayuda = F_MINI.render("Escribí la respuesta y pulsá  Enter", True, C_TEXTO3)
        pantalla.blit(ayuda, ayuda.get_rect(centerx=ANCHO // 2, y=RECT_INPUT.bottom + 8))

        # ── Feedback ─────────────────────────────────────────────────
        if msg_feedback and time.time() < t_fb_fin:
            alpha = min(255, int((t_fb_fin - time.time()) / 0.3 * 255))
            fb_surf = F_NORMAL.render(msg_feedback, True, color_feedback)
            fb_surf.set_alpha(alpha)
            pantalla.blit(fb_surf, fb_surf.get_rect(center=(ANCHO // 2, RECT_INPUT.bottom + 55)))

        # ── Notificación de logro ─────────────────────────────────────
        if logro_notif and time.time() < t_logro_fin:
            t_restante = t_logro_fin - time.time()
            alpha = min(255, int(t_restante / 0.5 * 255))
            log_rect = pygame.Rect(ANCHO - 380, 90, 360, 70)
            rect_redondeado_alfa(pantalla, logro_notif["color"], log_rect, 10, 180)
            pygame.draw.rect(pantalla, logro_notif["color"], log_rect, 2, border_radius=10)
            s1 = F_NORMAL.render(f"🏆 {logro_notif['nombre']}", True, C_BLANCO)
            s2 = F_MINI.render(logro_notif["desc"], True, C_BLANCO)
            s1.set_alpha(alpha); s2.set_alpha(alpha)
            pantalla.blit(s1, (log_rect.x + 10, log_rect.y + 8))
            pantalla.blit(s2, (log_rect.x + 10, log_rect.y + 42))

        # ── Notificación cambio de nivel ──────────────────────────────
        if notif_nivel and time.time() < t_nivel_fin:
            alpha = min(255, int((t_nivel_fin - time.time()) / 0.4 * 255))
            nv_surf = F_SUBTITULO.render(notif_nivel, True, C_CIAN)
            nv_surf.set_alpha(alpha)
            pantalla.blit(nv_surf, nv_surf.get_rect(center=(ANCHO // 2, ALTO - 120)))

        actualizar_particulas()
        pygame.display.flip()

        # ── Condiciones de fin ────────────────────────────────────────
        if vidas <= 0 or tiempo_rest <= 0:
            break

        # ── Eventos ───────────────────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                video_menu.liberar(); pygame.quit(); sys.exit()

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    cap = pantalla.copy()
                    if dialogo_confirmacion(cap):
                        reproducir_musica("Fondo_Musical.mp3")
                        return "MENU", None

                elif ev.key == pygame.K_BACKSPACE:
                    entrada = entrada[:-1]

                elif ev.key == pygame.K_RETURN and entrada.strip():
                    t_empl = time.time() - t_inicio_preg
                    tiempos_resp.append(t_empl)
                    resp = entrada.strip()

                    if resp == res_ok:
                        # ── CORRECTO ──────────────────────────────────
                        aciertos       += 1
                        racha          += 1
                        racha_errores   = 0
                        racha_max       = max(racha_max, racha)
                        sin_error_count += 1

                        ganados = PTS_NIVEL[dificultad] + pts_extra
                        # Multiplicador de racha
                        mult = 1 + (racha - 1) * 0.1
                        ganados = int(ganados * min(mult, 3.0))
                        # Bonus velocidad
                        bonus_vel = 10 if t_empl < 3 else (5 if t_empl < 6 else 0)
                        ganados  += bonus_vel
                        puntos   += ganados

                        # Tiempo bonus
                        tiempo_rest = min(tiempo_rest + 4, tiempo_total + 60)

                        msg_feedback   = f"+{ganados} pts" + (f"  [×{mult:.1f} racha]" if racha > 1 else "") + (f"  [+velocidad]" if bonus_vel else "")
                        color_feedback = C_VERDE
                        t_fb_fin       = time.time() + 1.5

                        # Efectos visuales
                        explotar(RECT_INPUT.centerx, RECT_INPUT.centery, C_VERDE, 25)

                        # Logros
                        if aciertos == 1:
                            mostrar_logro("primer_acierto")
                        if racha >= 5:
                            mostrar_logro("racha_5")
                        if racha >= 10:
                            mostrar_logro("racha_10")
                        if racha >= 20:
                            mostrar_logro("racha_20")
                        if bonus_vel and t_empl < 3:
                            mostrar_logro("velocidad")
                        if sin_error_count >= 10:
                            mostrar_logro("sin_errores_10")

                        # Dificultad adaptativa
                        if adaptativa:
                            nueva_dif, subio, bajo = escalar_dificultad_automatica(
                                dificultad, racha, racha_errores)
                            if subio:
                                notif_nivel = f"⬆  Dificultad: {nueva_dif}"
                                t_nivel_fin = time.time() + 2.5
                                racha = 0
                                mostrar_logro("sube_dificultad")
                                explotar(ANCHO // 2, ALTO // 2, C_PURPURA, 40)
                            elif bajo:
                                notif_nivel = f"⬇  Dificultad: {nueva_dif}"
                                t_nivel_fin = time.time() + 2.5
                            dificultad = nueva_dif

                        nueva_pregunta()

                    else:
                        # ── INCORRECTO ───────────────────────────────
                        errores       += 1
                        racha          = 0
                        racha_errores += 1
                        sin_error_count = 0

                        pen = PEN_NIVEL[dificultad]
                        if puntos >= pen:
                            puntos -= pen
                            msg_extra = f"(-{pen} pts)"
                        else:
                            puntos = 0
                            vidas -= 1
                            msg_extra = "(-1 vida)"
                            explotar(RECT_INPUT.centerx, RECT_INPUT.centery, C_ROJO, 30)

                        # Penalización de tiempo
                        tiempo_rest = max(0.0, tiempo_rest - 5)

                        msg_feedback   = f"✖  Respuesta: {res_ok}  {msg_extra}"
                        color_feedback = C_ROJO
                        t_fb_fin       = time.time() + 3.0

                        # Dificultad adaptativa bajada
                        if adaptativa:
                            nueva_dif, _, bajo = escalar_dificultad_automatica(
                                dificultad, racha, racha_errores)
                            if bajo:
                                notif_nivel = f"⬇  Dificultad: {nueva_dif}"
                                t_nivel_fin = time.time() + 2.5
                            dificultad = nueva_dif

                        entrada = ""
                        op_txt, res_ok, pts_extra = generar_operacion(dificultad, ops, conjunto)
                        t_inicio_preg = time.time()

                else:
                    c = ev.unicode
                    # Permitir: dígitos, signo negativo al inicio, punto, i y + para complejos
                    if conjunto == "Complejos":
                        permitidos = "0123456789-+i."
                    else:
                        permitidos = "0123456789-"
                    if c in permitidos and len(entrada) < 18:
                        # Solo un signo negativo al inicio
                        if c == "-" and ("-" in entrada or len(entrada) > 0 and entrada[-1] in "-+"):
                            pass
                        else:
                            entrada += c

    # ── Calcular calificación ─────────────────────────────────────────
    total   = aciertos + errores
    calific = 1.0 if total == 0 else max(1.0, 1.0 + (aciertos / total) * 9.0)

    return "GAMEOVER", {
        "aciertos":    aciertos,
        "errores":     errores,
        "puntos":      puntos,
        "racha_max":   racha_max,
        "tiempos":     tiempos_resp,
        "calificacion": calific,
        "dificultad":  dificultad,
        "logros":      list(logros_ganados),
        "total_preguntas": num_pregunta - 1,
    }


# ══════════════════════════════════════════════════════════════════════
# INGRESAR NOMBRE
# ══════════════════════════════════════════════════════════════════════
def pantalla_ingresar_nombre(puntos):
    nombre   = ""
    barra_r  = pygame.Rect(ANCHO // 2 - 220, ALTO // 2 + 10, 440, 62)
    btn_guar = Boton("Guardar puntaje", ANCHO // 2 - 200, ALTO // 2 + 110, 190, 52, C_VERDE_OSC)
    btn_omit = Boton("Omitir",          ANCHO // 2 + 15,  ALTO // 2 + 110, 190, 52, (80, 80, 100))
    t = 0

    while True:
        reloj.tick(FPS)
        t += 1
        dibujar_fondo_espacio(t)

        panel = pygame.Rect(ANCHO // 2 - 300, ALTO // 2 - 160, 600, 360)
        rect_redondeado_alfa(pantalla, C_PANEL, panel, 16, 230)
        pygame.draw.rect(pantalla, C_BORDE_LUZ, panel, 2, border_radius=16)

        centrado(pantalla, "¡Partida terminada!", F_SUBTITULO, C_AMARILLO, ALTO // 2 - 140)
        centrado(pantalla, f"Puntaje: {puntos} pts", F_GRANDE, C_BLANCO, ALTO // 2 - 88)
        centrado(pantalla, "Ingresá tu nombre para el ranking:", F_CHICA, C_TEXTO2, ALTO // 2 - 34)

        # Input
        pygame.draw.rect(pantalla, (20, 26, 50), barra_r, border_radius=10)
        pygame.draw.rect(pantalla, C_AZUL, barra_r, 2, border_radius=10)
        ns = F_SUBTITULO.render(nombre + ("▌" if t % 60 < 30 else " "), True, C_BLANCO)
        pantalla.blit(ns, ns.get_rect(center=barra_r.center))

        btn_guar.dibujar(pantalla)
        btn_omit.dibujar(pantalla)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                video_menu.liberar(); pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                elif ev.key == pygame.K_RETURN and nombre.strip():
                    return nombre.strip()
                elif ev.key == pygame.K_ESCAPE:
                    return None
                elif ev.unicode.isprintable() and len(nombre) < 18:
                    nombre += ev.unicode
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_guar.clickeado(ev.pos) and nombre.strip():
                    return nombre.strip()
                if btn_omit.clickeado(ev.pos):
                    return None


# ══════════════════════════════════════════════════════════════════════
# GAME OVER / RESULTADOS
# ══════════════════════════════════════════════════════════════════════
def pantalla_game_over(stats):
    pygame.mixer.music.stop()

    aciertos    = stats["aciertos"]
    errores     = stats["errores"]
    puntos      = stats["puntos"]
    racha_max   = stats["racha_max"]
    tiempos     = stats["tiempos"]
    calific     = stats["calificacion"]
    dificultad  = stats["dificultad"]
    logros      = stats["logros"]
    total_preg  = stats["total_preguntas"]

    vel_prom = (sum(tiempos) / len(tiempos)) if tiempos else 0.0
    precision = (aciertos / max(1, total_preg)) * 100

    nombre = pantalla_ingresar_nombre(puntos)
    if nombre:
        agregar_al_ranking(nombre, puntos, aciertos, errores, racha_max, calific, dificultad)

    btn_menu   = Boton("Menú principal",   ANCHO // 2 - 350, ALTO - 105, 250, 58, C_VERDE_OSC)
    btn_revan  = Boton("Revancha",         ANCHO // 2 - 80,  ALTO - 105, 200, 58, C_AZUL_OSC)
    btn_rank   = Boton("Clasificación",    ANCHO // 2 + 140, ALTO - 105, 220, 58, C_NARANJA_OSC)

    # Color nota
    def color_nota(c):
        if c >= 8:   return C_VERDE
        if c >= 6:   return C_AMARILLO
        if c >= 4:   return C_NARANJA
        return C_ROJO

    # Grado descriptivo
    def grado(c):
        if c >= 9:   return "¡EXCEPCIONAL!"
        if c >= 8:   return "Sobresaliente"
        if c >= 7:   return "Notable"
        if c >= 6:   return "Aprobado"
        if c >= 4:   return "Insuficiente"
        return "¡Seguí practicando!"

    t = 0
    while True:
        reloj.tick(FPS)
        t += 1
        dibujar_fondo_espacio(t)
        if t % 10 == 0:
            explotar(random.randint(100, ANCHO - 100),
                     random.randint(80, ALTO - 200),
                     random.choice([C_AMARILLO, C_VERDE, C_CIAN, C_PURPURA]), 8, "circulo")

        # Panel principal
        panel = pygame.Rect(60, 20, ANCHO - 120, ALTO - 140)
        rect_redondeado_alfa(pantalla, C_PANEL, panel, 20, 230)
        pygame.draw.rect(pantalla, C_BORDE_LUZ, panel, 2, border_radius=20)

        centrado(pantalla, "RESULTADO FINAL", F_TITULO, C_AMARILLO, 35)

        # Nota grande
        nota_str = f"{calific:.1f}"
        nota_surf = F_TITULO.render(nota_str + " / 10", True, color_nota(calific))
        pantalla.blit(nota_surf, nota_surf.get_rect(center=(ANCHO // 2, 140)))
        grd_s = F_SUBTITULO.render(grado(calific), True, color_nota(calific))
        pantalla.blit(grd_s, grd_s.get_rect(center=(ANCHO // 2, 198)))

        # Línea divisora
        pygame.draw.line(pantalla, C_BORDE, (120, 226), (ANCHO - 120, 226), 1)

        # Estadísticas en grilla 2x3
               # Estadísticas en grilla 2x3 - CENTRADO
        stats_items = [
            ("Puntuación",       f"{puntos} pts",             C_AMARILLO),
            ("Aciertos",         str(aciertos),               C_VERDE),
            ("Errores",          str(errores),                C_ROJO),
            ("Racha máxima",     f"×{racha_max}",             C_NARANJA),
            ("Precisión",        f"{precision:.1f}%",         C_CIAN),
            ("Vel. promedio",    f"{vel_prom:.1f}s / preg",   C_TEXTO),
        ]

        # Posiciones centradas (mejor distribución en pantalla 1280px)
        cols = [210, 640, 1070]   # ← Corregido y centrado
        rows = [255, 355]
        for i, (etiq, val, col) in enumerate(stats_items):
            cx = cols[i % 3]
            cy = rows[i // 3]
            # Caja stat
            sr = pygame.Rect(cx - 130, cy - 10, 260, 80)
            rect_redondeado_alfa(pantalla, C_PANEL2, sr, 10, 200)
            pygame.draw.rect(pantalla, col, sr, 1, border_radius=10)
            e_s = F_MINI.render(etiq, True, C_TEXTO2)
            v_s = F_NORMAL.render(val, True, col)
            pantalla.blit(e_s, e_s.get_rect(center=(cx, cy + 10)))
            pantalla.blit(v_s, v_s.get_rect(center=(cx, cy + 45)))

        # Logros
        pygame.draw.line(pantalla, C_BORDE, (120, 458), (ANCHO - 120, 458), 1)
        centrado(pantalla, "Logros obtenidos", F_HUD, C_TEXTO2, 466)
        if logros:
            for j, clave in enumerate(logros[:6]):
                ldata = LOGROS.get(clave)
                if ldata:
                    lx = 120 + j * 180
                    ls = F_MINI.render(ldata["nombre"], True, ldata["color"])
                    pantalla.blit(ls, (lx, 492))
        else:
            s = F_MINI.render("Ninguno — ¡volvé a intentarlo!", True, C_TEXTO3)
            pantalla.blit(s, s.get_rect(centerx=ANCHO // 2, y=492))

        btn_menu.dibujar(pantalla)
        btn_revan.dibujar(pantalla)
        btn_rank.dibujar(pantalla)

        actualizar_particulas()
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                video_menu.liberar(); pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                reproducir_musica("Fondo_Musical.mp3")
                return "MENU"
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_menu.clickeado(ev.pos):
                    reproducir_musica("Fondo_Musical.mp3")
                    return "MENU"
                if btn_revan.clickeado(ev.pos):
                    return "PREPARACION"
                if btn_rank.clickeado(ev.pos):
                    return "RANKING"


# ══════════════════════════════════════════════════════════════════════
# BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════
def main():
    estado         = "MENU"
    config_partida = None
    stats_partida  = None

    while True:
        if estado == "MENU":
            estado = menu_principal()

        elif estado == "CONFIGURACION":
            estado = pantalla_configuracion()

        elif estado == "RANKING":
            estado = pantalla_ranking()

        elif estado == "PREPARACION":
            estado, cfg = pantalla_preparacion()
            if cfg:
                config_partida = cfg

        elif estado == "JUEGO":
            if config_partida is None:
                estado = "PREPARACION"
                continue
            estado, stats = pantalla_juego(config_partida)
            if stats:
                stats_partida = stats

        elif estado == "GAMEOVER":
            if stats_partida is None:
                estado = "MENU"
                continue
            estado = pantalla_game_over(stats_partida)
            stats_partida = None   # limpiar para la próxima partida

        else:
            estado = "MENU"


if __name__ == "__main__":
    main()