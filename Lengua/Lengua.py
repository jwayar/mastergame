import math
import random
import sys
from enum import Enum, auto
from pathlib import Path
import os
import pygame
# ====================== RESOLVER RUTA (PyInstaller) ======================
def resolver_ruta(ruta_relativa):
    """ Obtiene la ruta absoluta de los recursos, compatible con PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)
# =========================================================================
from Question import (
    ROSCO_LETTERS,
    build_round_questions,
    normalize_text,
    parse_question_file,
)

# ==============================================================================
def ruta_asset(tipo: str, nombre: str):
    """ Ruta compatible con carpeta 'lengua' """
    return resolver_ruta(f"lengua/{tipo}/{nombre}")

# Para compatibilidad con el código existente
def ruta_sonido(nombre):
    return ruta_asset("sonidos", nombre)

def ruta_imagen(nombre):
    return ruta_asset("imagenes_usar", nombre)
# ==============================================================================

WIDTH, HEIGHT = 1440, 860
FPS = 60

COLOR_BG         = (10,  30,  80)
COLOR_PANEL      = (22,  48,  92)
COLOR_ACCENT     = (255, 196,   0)
COLOR_TEXT       = (245, 248, 255)
COLOR_MUTED      = (160, 180, 210)
COLOR_OK         = (46,  168,  92)
COLOR_FAIL       = (214,  62,  62)
COLOR_HOVER      = (255, 220,  80)
COLOR_FOCUS      = (255, 255, 255)
COLOR_ROSCO_IDLE = (30,  100, 200)
COLOR_ROSCO_OK   = (46,  168,  92)
COLOR_ROSCO_FAIL = (214,  62,  62)
COLOR_ROSCO_PASS = (100, 130, 175)
COLOR_ROSCO_ACT  = (240, 245, 255)
COLOR_GRAY_BG    = (80,   80,  80)
COLOR_GRAY_DARK  = (50,   50,  50)
COLOR_SLIDER_BG  = (40,   60, 110)
COLOR_SLIDER_FG  = (255, 196,   0)
COLOR_SLIDER_KN  = (255, 255, 255)


class GameMode(Enum):
    FREE  = auto()
    TIMED = auto()


class Screen(Enum):
    MAIN_MENU     = auto()
    MODE_MENU     = auto()
    SELECT_TIME   = auto()
    INSTRUCTIONS  = auto()
    PLAYING       = auto()
    THINKING_TIME = auto()
    PAUSED        = auto()
    FINISHED      = auto()
    SETTINGS      = auto()


# ── Slider de volumen ─────────────────────────────────────────────────────────
class VolumeSlider:
    """Barra deslizable horizontal, devuelve valor 0.0–1.0."""

    H = 14        # Grosor de la pista
    KR = 12       # Radio del knob

    def __init__(self, cx: int, cy: int, w: int, value: float, label: str):
        self.cx    = cx
        self.cy    = cy
        self.w     = w
        self.value = max(0.0, min(1.0, value))
        self.label = label
        self.dragging = False
        self.x0    = cx - w // 2
        self.x1    = cx + w // 2

    @property
    def knob_x(self) -> int:
        return self.x0 + int(self.value * self.w)

    def handle_event(self, ev: pygame.event.Event) -> bool:
        """Devuelve True si el valor cambió."""
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            kx = self.knob_x
            if math.hypot(ev.pos[0] - kx, ev.pos[1] - self.cy) <= self.KR + 6:
                self.dragging = True
                return False
            # Click directo en la pista
            if (self.x0 <= ev.pos[0] <= self.x1 and
                    abs(ev.pos[1] - self.cy) <= self.H + 4):
                self.dragging = True
                self._update_from_x(ev.pos[0])
                return True
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self.dragging = False
        elif ev.type == pygame.MOUSEMOTION and self.dragging:
            self._update_from_x(ev.pos[0])
            return True
        return False

    def _update_from_x(self, x: int) -> None:
        self.value = max(0.0, min(1.0, (x - self.x0) / self.w))

    def draw(self, surf: pygame.Surface, font: pygame.font.Font) -> None:
        # Etiqueta
        lbl = font.render(self.label, True, COLOR_TEXT)
        surf.blit(lbl, lbl.get_rect(midright=(self.x0 - 20, self.cy)))

        # Porcentaje
        pct = font.render(f"{int(self.value * 100)}%", True, COLOR_ACCENT)
        surf.blit(pct, pct.get_rect(midleft=(self.x1 + 20, self.cy)))

        # Pista
        track = pygame.Rect(self.x0, self.cy - self.H // 2, self.w, self.H)
        pygame.draw.rect(surf, COLOR_SLIDER_BG, track, border_radius=self.H)

        # Relleno
        fill_w = int(self.value * self.w)
        if fill_w > 0:
            fill = pygame.Rect(self.x0, self.cy - self.H // 2, fill_w, self.H)
            pygame.draw.rect(surf, COLOR_SLIDER_FG, fill, border_radius=self.H)

        # Knob
        kx = self.knob_x
        pygame.draw.circle(surf, COLOR_SLIDER_KN, (kx, self.cy), self.KR)
        pygame.draw.circle(surf, COLOR_SLIDER_FG, (kx, self.cy), self.KR, 3)


# ── Botón de menú ─────────────────────────────────────────────────────────────
class MenuButton:
    def __init__(self, rect: pygame.Rect, label: str, action: str):
        self.rect    = rect
        self.label   = label
        self.action  = action
        self.hovered = False
        self.focused = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if self.focused:
            border, fill, tc = COLOR_FOCUS, (40,  85, 150), COLOR_TEXT
        elif self.hovered:
            border, fill, tc = COLOR_HOVER, (55, 100, 165), (20, 30, 50)
        else:
            border, fill, tc = COLOR_ACCENT, COLOR_PANEL,   COLOR_TEXT
        pygame.draw.rect(surface, fill,   self.rect, border_radius=12)
        pygame.draw.rect(surface, border, self.rect, 3, border_radius=12)
        lbl = font.render(self.label, True, tc)
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


# ── Assets ────────────────────────────────────────────────────────────────────
class AssetManager:
    def __init__(self) -> None:
        self.logo_top:     pygame.Surface | None = None
        self.img_pensar:   pygame.Surface | None = None
        self.bg_menu:      pygame.Surface | None = None
        self.bg_seleccion: pygame.Surface | None = None
        self.bg_juego:     pygame.Surface | None = None

    def _safe_load(self, path: Path, size: tuple | None = None,
                   alpha: bool = False) -> pygame.Surface | None:
        if not path.is_file():
            return None
        img = pygame.image.load(str(path)).convert_alpha() if alpha \
              else pygame.image.load(str(path)).convert()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img

    def load(self) -> None:
        print("[Assets] Cargando imágenes...")

        for attr, names in [
            ("bg_menu",      ["Menu.png",   "fondo_menu.jpg",      "menu.jpg"]),
            ("bg_seleccion", ["menu_2.png", "fondo_seleccion.jpg", "menu2.jpg"]),
            ("bg_juego",     ["fondo_juego.jpg", "juego.jpg", "game.jpg"]),
        ]:
            for name in names:
                path = ruta_imagen(name)
                if os.path.exists(path):
                    try:
                        surf = self._safe_load(Path(path), (WIDTH, HEIGHT))
                        if surf:
                            setattr(self, attr, surf)
                            print(f"[Assets] ✅ {attr} cargado")
                            break
                    except:
                        pass

        # Logo
        for name in ["logo-borde.png", "logo.png"]:
            path = ruta_imagen(name)
            if os.path.exists(path):
                try:
                    raw = self._safe_load(Path(path), alpha=True)
                    if raw:
                        H = 140
                        w = int(raw.get_width() * H / raw.get_height())
                        self.logo_top = pygame.transform.smoothscale(raw, (w, H))
                        print(f"[Assets] ✅ Logo cargado")
                        break
                except:
                    pass

        # Imagen pensar
        for name in ["pensar.png", "pensar.jpg", "think.png"]:
            path = ruta_imagen(name)
            if os.path.exists(path):
                try:
                    raw = self._safe_load(Path(path), alpha=True)
                    if raw:
                        self.img_pensar = pygame.transform.smoothscale(raw, (400, 260))
                        print(f"[Assets] ✅ Imagen pensar cargada")
                        break
                except:
                    pass

# ── Audio ─────────────────────────────────────────────────────────────────────
class AudioManager:
    """
    Música: pygame.mixer.music  (canal dedicado, soporta MP3 largo sin problema)
    Efectos: pygame.mixer.Sound  (canales cortos: acierto / fallo)

    Archivos esperados en sonidos/:
        menu.mp3       → menú principal y modos
        juego.mp3      → durante la partida (volumen base)
        tension.mp3    → se activa al quedar ≤ 15 s
        acierto.mp3    → SFX acierto
        fallo.mp3      → SFX fallo
    """

    def __init__(self) -> None:
        self.enabled       = False
        self.current_track = ""          # "menu" | "juego" | "tension" | ""
        self.vol_music     = 0.65        # 0.0 – 1.0
        self.vol_sfx       = 0.80        # 0.0 – 1.0
        self.sfx_acierto: pygame.mixer.Sound | None = None
        self.sfx_fallo:   pygame.mixer.Sound | None = None
        # Rutas resueltas al hacer setup
        self._path: dict[str, str | None] = {
            "menu":    None,
            "juego":   None,
            "tension": None,
        }

    def _find(self, *names: str) -> str | None:
        for n in names:
            for ext in ["", ".mp3", ".ogg", ".wav"]:
                path = ruta_asset("sonidos", f"{n}{ext}")
                if os.path.exists(path):
                    print(f"[Audio] ✅ Encontrado: {n}{ext}")
                    return path
        print(f"[Audio] ❌ No encontrado: {names}")
        return None

    def setup(self) -> None:
        if not pygame.mixer.get_init():
            return
        self.enabled = True
        self._path["menu"]    = self._find("menu.mp3",    "musica_menu.mp3")
        self._path["juego"]   = self._find("juego.mp3",   "musica_juego.mp3")
        self._path["tension"] = self._find("tension.mp3", "musica_tension.mp3")

        sfx_ok   = self._find("acierto.mp3")
        sfx_fail = self._find("fallo.mp3")
        if sfx_ok:   self.sfx_acierto = pygame.mixer.Sound(sfx_ok)
        if sfx_fail: self.sfx_fallo   = pygame.mixer.Sound(sfx_fail)
        self._apply_sfx_vol()

    # ── Volumen ───────────────────────────────────────────────────────────────
    def set_vol_music(self, v: float) -> None:
        self.vol_music = max(0.0, min(1.0, v))
        pygame.mixer.music.set_volume(self.vol_music)

    def set_vol_sfx(self, v: float) -> None:
        self.vol_sfx = max(0.0, min(1.0, v))
        self._apply_sfx_vol()

    def _apply_sfx_vol(self) -> None:
        if self.sfx_acierto: self.sfx_acierto.set_volume(self.vol_sfx)
        if self.sfx_fallo:   self.sfx_fallo.set_volume(self.vol_sfx)

    # ── Reproducción ─────────────────────────────────────────────────────────
    def play_track(self, track: str) -> None:
        """Cambia la pista de música si es diferente a la actual."""
        if not self.enabled or self.current_track == track:
            return
        path = self._path.get(track)
        if not path:
            # Si no existe el archivo simplemente para la música
            pygame.mixer.music.stop()
            self.current_track = ""
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.vol_music)
        pygame.mixer.music.play(loops=-1)
        self.current_track = track

    def stop_all_music(self) -> None:
        if not self.enabled:
            return
        pygame.mixer.music.stop()
        self.current_track = ""

    def boost_to_tension(self) -> None:
        """Cambia a tension.mp3 cuando quedan ≤ 15 s."""
        if not self.enabled:
            return
        self.play_track("tension")

    def play_ok(self) -> None:
        if self.enabled and self.sfx_acierto:
            self.sfx_acierto.play()

    def play_fail(self) -> None:
        if self.enabled and self.sfx_fallo:
            self.sfx_fallo.play()


# ══════════════════════════════════════════════════════════════════════════════
class PasapalabraGame:

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()

        self.surf  = pygame.display.set_mode((WIDTH, HEIGHT),
                                             pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Pasapalabra — Edición Literatura y Lengua")
        self.clock = pygame.time.Clock()

        self.audio  = AudioManager(); self.audio.setup()
        self.assets = AssetManager(); self.assets.load()

        self._build_fonts()
        self._compute_layout()

        self.bank = parse_question_file()

        self.screen_id        = Screen.MAIN_MENU
        self.mode             = GameMode.FREE
        self.running          = True
        self.menu_focus       = 0
        self.selected_seconds = 100

        self.main_buttons     = self._build_main_menu()
        self.mode_buttons     = self._build_mode_menu()
        self.time_buttons     = self._build_time_menu()
        self.settings_buttons = self._build_settings_menu()
        self.pause_buttons    = self._build_pause_menu()
        self.active_buttons: list[MenuButton] = self.main_buttons

        # Sliders de configuración
        cx = WIDTH // 2
        self.slider_music = VolumeSlider(cx, 380, 500, self.audio.vol_music, "Música")
        self.slider_sfx   = VolumeSlider(cx, 480, 500, self.audio.vol_sfx,   "Efectos")

        self.rng = random.Random()
        self.music_fast_triggered = False
        self.reset_match()

    # ── Fuentes ───────────────────────────────────────────────────────────────
    def _build_fonts(self) -> None:
        def f(size: int, bold: bool = False) -> pygame.font.Font:
            return pygame.font.SysFont("segoeui", size, bold=bold)
        self.fn_title   = f(54, True)
        self.fn_menu    = f(30, True)
        self.fn_body    = f(26)
        self.fn_body_b  = f(26, True)
        self.fn_small   = f(22)
        self.fn_small_b = f(22, True)
        self.fn_caps    = f(16, True)
        self.fn_timer   = f(36, True)
        self.fn_big_ans = f(44, True)
        self.fn_rosco   = f(18, True)
        self.fn_hud_lbl = f(15, True)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _compute_layout(self) -> None:
        H_LOGO       = 140
        rosco_area_h = HEIGHT - H_LOGO
        rcx          = WIDTH  // 2
        rcy          = H_LOGO + rosco_area_h // 2

        self.rosco_radius  = int(rosco_area_h * 0.46)
        self.rosco_center  = (rcx, rcy)
        self.letter_radius = max(22, int(self.rosco_radius * 0.108))

        inner_r           = self.rosco_radius - self.letter_radius - 8
        self.inner_r      = inner_r
        panel_half_w      = int(inner_r * 0.70)
        self.panel_cx     = rcx
        self.panel_half_w = panel_half_w

        top = rcy - inner_r
        h2  = inner_r * 2
        self.y_pill       = top + int(h2 * 0.12)
        self.y_clue_start = top + int(h2 * 0.24)
        self.y_input      = top + int(h2 * 0.58)
        self.y_responder  = top + int(h2 * 0.72)
        self.y_paso       = top + int(h2 * 0.86)

        btn_w = 220; btn_h = 44
        self.rect_responder = pygame.Rect(rcx - btn_w//2,
                                          self.y_responder - btn_h//2, btn_w, btn_h)
        paso_w = 240; paso_h = 30
        self.rect_paso = pygame.Rect(rcx - paso_w//2,
                                     self.y_paso - paso_h//2, paso_w, paso_h)

        hud_y = H_LOGO // 2
        self.pause_center  = (28,  hud_y)
        self.pause_r       = 20
        self.timer_center  = (120, hud_y)
        self.timer_r       = 38
        self.ok_center     = (192, hud_y)
        self.ok_r          = 26
        self.hud_r         = 26
        self.hud_cx        = WIDTH - self.hud_r - 14
        self.hud_fail_y    = hud_y - 22
        self.hud_rest_y    = hud_y + 22
        self.hud_lbl_right = self.hud_cx - self.hud_r - 10
        self.continuar_rect = pygame.Rect(rcx - 120, rcy + 120, 240, 50)

    # ── Menús ─────────────────────────────────────────────────────────────────
    def _build_main_menu(self) -> list[MenuButton]:
        cx, y0 = WIDTH//2, 320
        return [
            MenuButton(pygame.Rect(cx-170, y0,     340, 58), "Jugar",         "play"),
            MenuButton(pygame.Rect(cx-170, y0+80,  340, 58), "Configuración", "settings"),
            MenuButton(pygame.Rect(cx-170, y0+160, 340, 58), "Salir",         "quit"),
        ]

    def _build_mode_menu(self) -> list[MenuButton]:
        cx, y0 = WIDTH//2, 320
        return [
            MenuButton(pygame.Rect(cx-210, y0,     420, 58), "Modo 1: Para Uno (75 s)", "mode_free"),
            MenuButton(pygame.Rect(cx-210, y0+80,  420, 58), "Modo 2: Contrareloj",     "mode_timed_panel"),
            MenuButton(pygame.Rect(cx-210, y0+175, 420, 50), "Volver al Menú",          "back_main"),
        ]

    def _build_time_menu(self) -> list[MenuButton]:
        cx = WIDTH // 2
        return [
            MenuButton(pygame.Rect(cx-160, HEIGHT//2 - 60,  320, 50), "75 Segundos",  "time_75"),
            MenuButton(pygame.Rect(cx-160, HEIGHT//2 + 5,   320, 50), "90 Segundos",  "time_90"),
            MenuButton(pygame.Rect(cx-160, HEIGHT//2 + 70,  320, 50), "95 Segundos",  "time_95"),
            MenuButton(pygame.Rect(cx-160, HEIGHT//2 + 135, 320, 50), "100 Segundos", "time_100"),
            MenuButton(pygame.Rect(cx-160, HEIGHT//2 + 210, 320, 48), "Volver atrás", "back_mode"),
        ]

    def _build_settings_menu(self) -> list[MenuButton]:
        cx = WIDTH // 2
        return [MenuButton(pygame.Rect(cx-170, 590, 340, 54), "Volver", "back_main")]

    def _build_pause_menu(self) -> list[MenuButton]:
        cx, y0 = WIDTH//2, HEIGHT//2 - 30
        return [
            MenuButton(pygame.Rect(cx-190, y0,    380, 54), "Continuar jugando", "resume"),
            MenuButton(pygame.Rect(cx-190, y0+74, 380, 54), "Volver al Inicio",  "back_main"),
        ]

    # ── Estado de partida ─────────────────────────────────────────────────────
    def reset_match(self) -> None:
        self.questions: dict               = {}
        self.letter_states: dict[str, str] = {L: "idle" for L in ROSCO_LETTERS}
        self.queue: list[str]              = list(ROSCO_LETTERS)
        self.queue_index                   = 0
        self.passed_pending: list[str]     = []
        self.revisit_used                  = False
        self.rosco_laps_done               = 0
        self.answer_buffer                 = ""
        self.feedback                      = ""
        self.feedback_timer                = 0
        self.time_left_ms                  = self.selected_seconds * 1000
        self.time_cap_ms                   = self.selected_seconds * 1000
        self.match_started_ms              = 0
        self.won                           = False
        self.wrong_overlay: dict | None    = None
        self.music_fast_triggered          = False

    def go_to_instructions(self, mode: GameMode) -> None:
        self.mode = mode
        if mode == GameMode.FREE:
            self.selected_seconds = 0
        self.reset_match()
        self.screen_id = Screen.INSTRUCTIONS

    def start_actual_match(self) -> None:
        self.rng              = random.Random()
        self.questions        = build_round_questions(self.bank, rng=self.rng)
        self.match_started_ms = pygame.time.get_ticks()
        self.screen_id        = Screen.PLAYING

    # ── Cola ──────────────────────────────────────────────────────────────────
    def current_letter(self) -> str | None:
        if self.queue_index < len(self.queue):
            return self.queue[self.queue_index]
        return None

    def advance_queue(self) -> None:
        self.queue_index += 1
        if self.queue_index >= len(self.queue):
            self._on_sequence_finished()

    def _on_sequence_finished(self) -> None:
        self.rosco_laps_done += 1
        if self.passed_pending:
            if self.mode == GameMode.TIMED and self.revisit_used:
                self._finish_game(True); return
            if self.mode == GameMode.TIMED:
                self.revisit_used = True
                self.time_cap_ms  = max(30_000, self.time_cap_ms - 20_000)
                self.time_left_ms = min(self.time_left_ms, self.time_cap_ms)
            self.queue          = list(self.passed_pending)
            self.passed_pending = []
            self.queue_index    = 0
            self.feedback       = "Repasando palabras pendientes..."
            self.feedback_timer = 120
        else:
            self._finish_game(True)

    def _finish_game(self, success: bool) -> None:
        self.won       = success
        self.screen_id = Screen.FINISHED
        self.audio.stop_all_music()

    # ── Respuestas ────────────────────────────────────────────────────────────
    def submit_answer(self) -> None:
        if self.wrong_overlay: return
        letter = self.current_letter()
        if not letter or letter not in self.questions: return
        q = self.questions[letter]
        if normalize_text(self.answer_buffer) == normalize_text(q.answer):
            self.mark_letter(letter, "ok")
            self.audio.play_ok()
            self.feedback       = "¡Correcto!"
            self.feedback_timer = 60
            self.answer_buffer  = ""
            self.advance_queue()
        else:
            self.mark_letter(letter, "fail")
            self.audio.play_fail()
            self.wrong_overlay = {"letter": letter, "answer": q.answer}
            self.answer_buffer = ""

    def dismiss_wrong_overlay(self) -> None:
        if not self.wrong_overlay: return
        self.wrong_overlay = None
        self.advance_queue()

    def paso_palabra(self) -> None:
        if self.wrong_overlay: return
        letter = self.current_letter()
        if not letter: return
        if letter not in self.passed_pending:
            self.passed_pending.append(letter)
        self.mark_letter(letter, "pass")
        self.answer_buffer = ""
        self.advance_queue()
        self.audio.stop_all_music()
        self.screen_id = Screen.THINKING_TIME

    def mark_letter(self, letter: str, state: str) -> None:
        self.letter_states[letter] = state

    def count_correct(self)   -> int:
        return sum(1 for s in self.letter_states.values() if s == "ok")
    def count_failed(self)    -> int:
        return sum(1 for s in self.letter_states.values() if s == "fail")
    def count_remaining(self) -> int:
        if self.queue_index >= len(self.queue): return 0
        return len(self.queue) - self.queue_index

    # ── Temporizador ──────────────────────────────────────────────────────────
    def tick_timer(self) -> None:
        if self.mode != GameMode.TIMED or self.screen_id != Screen.PLAYING:
            return
        now     = pygame.time.get_ticks()
        elapsed = now - self.match_started_ms
        self.match_started_ms = now
        self.time_left_ms    -= elapsed

        # Al llegar a 15 s cambia a tension.mp3
        if self.time_left_ms <= 15_000 and not self.music_fast_triggered:
            self.music_fast_triggered = True
            self.audio.boost_to_tension()

        if self.time_left_ms <= 0:
            self.time_left_ms = 0
            self._finish_game(False)

    def format_time(self) -> str:
        total = max(0, self.time_left_ms // 1000)
        m, s  = divmod(total, 60)
        return f"{m}:{s:02d}"

    # ── Navegación ────────────────────────────────────────────────────────────
    def set_menu(self, buttons: list[MenuButton], sid: Screen) -> None:
        self.active_buttons = buttons
        self.screen_id      = sid
        self.menu_focus     = 0
        for i, b in enumerate(buttons):
            b.focused = (i == 0)
            b.hovered = False

    def navigate_menu(self, delta: int) -> None:
        if not self.active_buttons: return
        self.active_buttons[self.menu_focus].focused = False
        self.menu_focus = (self.menu_focus + delta) % len(self.active_buttons)
        self.active_buttons[self.menu_focus].focused = True

    def activate_focused(self) -> None:
        if self.active_buttons:
            self._do_action(self.active_buttons[self.menu_focus].action)

    def _do_action(self, action: str) -> None:
        match action:
            case "quit":             self.running = False
            case "play":             self.set_menu(self.mode_buttons,     Screen.MODE_MENU)
            case "settings":         self.set_menu(self.settings_buttons, Screen.SETTINGS)
            case "back_main":        self.set_menu(self.main_buttons,     Screen.MAIN_MENU)
            case "back_mode":        self.set_menu(self.mode_buttons,     Screen.MODE_MENU)
            case "mode_free":
                self.selected_seconds = 75
                self.go_to_instructions(GameMode.TIMED)
            case "mode_timed_panel": self.set_menu(self.time_buttons, Screen.SELECT_TIME)
            case "time_75":
                self.selected_seconds = 75;  self.go_to_instructions(GameMode.TIMED)
            case "time_90":
                self.selected_seconds = 90;  self.go_to_instructions(GameMode.TIMED)
            case "time_95":
                self.selected_seconds = 95;  self.go_to_instructions(GameMode.TIMED)
            case "time_100":
                self.selected_seconds = 100; self.go_to_instructions(GameMode.TIMED)
            case "resume":
                self.screen_id = Screen.PLAYING
                self.match_started_ms = pygame.time.get_ticks()

    def _sync_hover(self) -> None:
        for i, b in enumerate(self.active_buttons):
            b.focused = (i == self.menu_focus)
            b.hovered = b.focused

    # ── Enrutamiento de audio ─────────────────────────────────────────────────
    def update_audio_routing(self) -> None:
        sid = self.screen_id
        if sid in (Screen.MAIN_MENU, Screen.MODE_MENU, Screen.SETTINGS):
            self.audio.play_track("menu")
        elif sid in (Screen.SELECT_TIME, Screen.INSTRUCTIONS):
            self.audio.play_track("menu")          # también usa menu.mp3
        elif sid == Screen.PLAYING:
            if not self.music_fast_triggered:
                self.audio.play_track("juego")
            # Si ya se activó tension, no tocar nada (ya está sonando)
        elif sid in (Screen.PAUSED, Screen.THINKING_TIME, Screen.FINISHED):
            self.audio.stop_all_music()

    # ── Bucle principal ───────────────────────────────────────────────────────
    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            mp = pygame.mouse.get_pos()
            self.update_audio_routing()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False

                elif ev.type == pygame.MOUSEMOTION:
                    if self.screen_id in (Screen.MAIN_MENU, Screen.MODE_MENU,
                                          Screen.SELECT_TIME, Screen.PAUSED):
                        for b in self.active_buttons:
                            b.hovered = b.contains(ev.pos)
                    # Sliders en Settings
                    if self.screen_id == Screen.SETTINGS:
                        changed_m = self.slider_music.handle_event(ev)
                        changed_s = self.slider_sfx.handle_event(ev)
                        if changed_m: self.audio.set_vol_music(self.slider_music.value)
                        if changed_s: self.audio.set_vol_sfx(self.slider_sfx.value)

                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    # Sliders primero en Settings
                    if self.screen_id == Screen.SETTINGS:
                        changed_m = self.slider_music.handle_event(ev)
                        changed_s = self.slider_sfx.handle_event(ev)
                        if changed_m: self.audio.set_vol_music(self.slider_music.value)
                        if changed_s: self.audio.set_vol_sfx(self.slider_sfx.value)
                    self._on_click(ev.pos)

                elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                    if self.screen_id == Screen.SETTINGS:
                        self.slider_music.handle_event(ev)
                        self.slider_sfx.handle_event(ev)

                elif ev.type == pygame.KEYDOWN:
                    self._on_key(ev.key)

                elif ev.type == pygame.TEXTINPUT:
                    if self.screen_id == Screen.PLAYING and not self.wrong_overlay:
                        if ev.text not in ("1", "2") and len(self.answer_buffer) < 48:
                            self.answer_buffer += ev.text.upper()

            if self.screen_id == Screen.PLAYING:
                self.tick_timer()
                if self.feedback_timer > 0:
                    self.feedback_timer -= 1

            self._draw(mp)
            pygame.display.flip()

        self.audio.stop_all_music()
        pygame.quit()

    def _on_click(self, pos: tuple[int, int]) -> None:
        sid = self.screen_id
        if sid in (Screen.MAIN_MENU, Screen.MODE_MENU, Screen.SELECT_TIME,
                   Screen.SETTINGS, Screen.PAUSED):
            for i, b in enumerate(self.active_buttons):
                if b.contains(pos):
                    self.menu_focus = i
                    self._sync_hover()
                    self._do_action(b.action)
                    break
        elif sid == Screen.INSTRUCTIONS:
            self.start_actual_match()
        elif sid == Screen.THINKING_TIME:
            self.screen_id = Screen.PLAYING
            self.match_started_ms = pygame.time.get_ticks()
        elif sid == Screen.PLAYING:
            if self.wrong_overlay:
                if self.continuar_rect.collidepoint(pos):
                    self.dismiss_wrong_overlay()
                return
            pcx, pcy = self.pause_center
            if math.hypot(pos[0]-pcx, pos[1]-pcy) <= self.pause_r:
                self._open_pause(); return
            if self.rect_paso.collidepoint(pos):
                self.paso_palabra(); return
            if self.rect_responder.collidepoint(pos):
                self.submit_answer(); return

    def _on_key(self, key: int) -> None:
        sid      = self.screen_id
        nav_up   = {pygame.K_UP,   pygame.K_w, pygame.K_LEFT,  pygame.K_a}
        nav_down = {pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d}

        if key == pygame.K_ESCAPE:
            if sid == Screen.PLAYING:
                self._open_pause(); return
            elif sid == Screen.PAUSED:
                self._do_action("resume"); return
            elif sid == Screen.MODE_MENU:
                self.set_menu(self.main_buttons, Screen.MAIN_MENU); return
            elif sid in (Screen.SELECT_TIME, Screen.INSTRUCTIONS, Screen.SETTINGS):
                self.set_menu(self.main_buttons, Screen.MAIN_MENU); return

        if sid in (Screen.MAIN_MENU, Screen.MODE_MENU, Screen.SELECT_TIME,
                   Screen.SETTINGS, Screen.PAUSED):
            if key in nav_up:
                self.navigate_menu(-1); self._sync_hover()
            elif key in nav_down:
                self.navigate_menu(1); self._sync_hover()
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.activate_focused()
            return

        if sid == Screen.INSTRUCTIONS:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.start_actual_match()
            return

        if sid == Screen.THINKING_TIME:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                       pygame.K_SPACE, pygame.K_2, pygame.K_KP2):
                self.screen_id = Screen.PLAYING
                self.match_started_ms = pygame.time.get_ticks()
            return

        if sid == Screen.FINISHED:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.set_menu(self.mode_buttons, Screen.MODE_MENU)
            return

        if sid == Screen.PLAYING:
            if self.wrong_overlay:
                if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self.dismiss_wrong_overlay()
                return
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.submit_answer(); return
            if key in (pygame.K_2, pygame.K_KP2):
                self.paso_palabra(); return
            if key == pygame.K_BACKSPACE:
                self.answer_buffer = self.answer_buffer[:-1]; return

    def _open_pause(self) -> None:
        self.screen_id = Screen.PAUSED
        self.set_menu(self.pause_buttons, Screen.PAUSED)

    # ══════════════════════════════════════════════════════════════════════════
    # RENDERIZADO
    # ══════════════════════════════════════════════════════════════════════════
    def _draw(self, mp: tuple[int, int]) -> None:
        sid = self.screen_id

        if sid in (Screen.MAIN_MENU, Screen.MODE_MENU,
                   Screen.SETTINGS) and self.assets.bg_menu:
            self.surf.blit(self.assets.bg_menu, (0, 0))
        elif sid == Screen.SELECT_TIME and self.assets.bg_seleccion:
            self.surf.blit(self.assets.bg_seleccion, (0, 0))
        elif sid in (Screen.PLAYING, Screen.PAUSED,
                     Screen.FINISHED) and self.assets.bg_juego:
            self.surf.blit(self.assets.bg_juego, (0, 0))
        else:
            color = COLOR_GRAY_BG if sid in (Screen.INSTRUCTIONS,
                                             Screen.THINKING_TIME) else COLOR_BG
            self.surf.fill(color)

        if sid == Screen.MAIN_MENU:
            self._draw_dimmer(); self._draw_main_menu()
        elif sid == Screen.MODE_MENU:
            self._draw_dimmer(); self._draw_mode_menu()
        elif sid == Screen.SELECT_TIME:
            self._draw_dimmer(); self._draw_select_time_menu()
        elif sid == Screen.SETTINGS:
            self._draw_dimmer(); self._draw_settings_menu()
        elif sid == Screen.INSTRUCTIONS:
            self._draw_instructions_screen()
        elif sid == Screen.THINKING_TIME:
            self._draw_thinking_screen()
        elif sid in (Screen.PLAYING, Screen.PAUSED, Screen.FINISHED):
            self._draw_header()
            self._draw_rosco()
            self._draw_panel()
            self._draw_hud()
            if sid == Screen.PAUSED:
                self._draw_pause_overlay()
            elif sid == Screen.FINISHED:
                self._draw_finish_overlay()
            elif self.wrong_overlay:
                self._draw_wrong_overlay()
            elif self.feedback_timer > 0 and self.feedback:
                self._draw_feedback()

    def _draw_dimmer(self) -> None:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 15, 50, 140))
        self.surf.blit(ov, (0, 0))

    def _draw_header(self) -> None:
        H_LOGO = 140
        if self.assets.logo_top:
            logo = self.assets.logo_top
            lw, _ = logo.get_size()
            if lw != WIDTH:
                logo = pygame.transform.smoothscale(logo, (WIDTH, H_LOGO))
            self.surf.blit(logo, (0, 0))
        else:
            pygame.draw.rect(self.surf, (8, 22, 65), (0, 0, WIDTH, H_LOGO))

    def _draw_rosco(self) -> None:
        cx, cy  = self.rosco_center
        R, lr   = self.rosco_radius, self.letter_radius
        n       = len(ROSCO_LETTERS)
        current = self.current_letter()

        for i, letter in enumerate(ROSCO_LETTERS):
            angle = -math.pi/2 + 2*math.pi*i/n
            x = cx + int(math.cos(angle) * R)
            y = cy + int(math.sin(angle) * R)

            state  = self.letter_states.get(letter, "idle")
            active = (letter == current
                      and self.screen_id == Screen.PLAYING
                      and not self.wrong_overlay)

            if active:            fill, tc, rw = COLOR_ROSCO_ACT,  (20, 60, 140), 3
            elif state == "ok":   fill, tc, rw = COLOR_ROSCO_OK,   COLOR_TEXT,    2
            elif state == "fail": fill, tc, rw = COLOR_ROSCO_FAIL, COLOR_TEXT,    2
            elif state == "pass": fill, tc, rw = COLOR_ROSCO_PASS, COLOR_TEXT,    2
            else:                 fill, tc, rw = COLOR_ROSCO_IDLE, COLOR_TEXT,    2

            pygame.draw.circle(self.surf, fill,          (x, y), lr)
            pygame.draw.circle(self.surf, (255,255,255), (x, y), lr, rw)
            lbl = self.fn_rosco.render(letter, True, tc)
            self.surf.blit(lbl, lbl.get_rect(center=(x, y)))

    def _draw_panel(self) -> None:
        letter = self.current_letter()
        if not letter or letter not in self.questions or self.wrong_overlay:
            return

        q    = self.questions[letter]
        pcx  = self.panel_cx
        hw   = self.panel_half_w
        kind = "EMPIEZA POR" if q.hint_type == "empieza" else "CONTIENE LA"

        pill_txt  = self.fn_small_b.render(f"{kind} {letter}", True, (25, 90, 200))
        pill_w    = pill_txt.get_width() + 28
        pill_h    = pill_txt.get_height() + 10
        pill_rect = pygame.Rect(pcx - pill_w//2, self.y_pill - pill_h//2, pill_w, pill_h)
        pygame.draw.rect(self.surf, (255,255,255), pill_rect, border_radius=pill_h//2)
        self.surf.blit(pill_txt, pill_txt.get_rect(center=pill_rect.center))

        lines = self._wrap(q.clue, self.fn_body, hw * 2)
        lh    = int(self.fn_body.get_height() * 1.25)
        y     = self.y_clue_start
        for line in lines[:4]:
            s = self.fn_body.render(line, True, COLOR_TEXT)
            self.surf.blit(s, s.get_rect(centerx=pcx, top=y))
            y += lh

        box_w = hw * 2; box_h = 38
        box   = pygame.Rect(pcx - box_w//2, self.y_input - box_h//2, box_w, box_h)
        pygame.draw.rect(self.surf, (20, 55, 130), box, border_radius=8)
        pygame.draw.rect(self.surf, (255,255,255), box, 2, border_radius=8)
        if self.answer_buffer:
            ans = self.fn_body_b.render(self.answer_buffer, True, COLOR_TEXT)
            self.surf.blit(ans, ans.get_rect(center=box.center))
        else:
            ph = self.fn_caps.render("ESCRIBE TU RESPUESTA...", True, (160,190,230))
            self.surf.blit(ph, ph.get_rect(center=box.center))

        rb    = self.rect_responder
        r_hov = rb.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.surf, (50,130,230) if r_hov else (25,90,190),
                         rb, border_radius=rb.h//2)
        pygame.draw.rect(self.surf, (255,255,255), rb, 2, border_radius=rb.h//2)
        rt = self.fn_small_b.render("[ENTER] RESPONDER", True, COLOR_TEXT)
        self.surf.blit(rt, rt.get_rect(center=rb.center))

        pb    = self.rect_paso
        p_hov = pb.collidepoint(pygame.mouse.get_pos())
        pc    = (255,240,100) if p_hov else (210,230,255)
        pt    = self.fn_caps.render("[2] PASAPALABRA", True, pc)
        self.surf.blit(pt, pt.get_rect(center=pb.center))

    def _draw_select_time_menu(self) -> None:
        cx = WIDTH // 2
        title = self.fn_title.render("Seleccionar Tiempo de Juego", True, COLOR_TEXT)
        self.surf.blit(title, title.get_rect(center=(cx, 160)))
        for b in self.time_buttons:
            b.draw(self.surf, self.fn_menu)

    def _draw_instructions_screen(self) -> None:
        cx = WIDTH // 2
        t  = self.fn_title.render("INSTRUCCIONES DE JUEGO", True, COLOR_TEXT)
        self.surf.blit(t, t.get_rect(center=(cx, 160)))
        instrucciones = [
            "• El objetivo es completar las 25 letras del rosco de Pasapalabra.",
            "• Escribe tu respuesta usando el teclado convencional.",
            "• Presiona [ENTER] para verificar y enviar tu respuesta.",
            "• Presiona [2] si no estás seguro para hacer PASAPALABRA.",
            "• Si haces Pasapalabra, tendrás un espacio aislado para pensar.",
            "• Presiona [ESC] en cualquier momento para pausar la partida.",
        ]
        y = 280
        for line in instrucciones:
            txt = self.fn_body.render(line, True, (240,240,240))
            self.surf.blit(txt, txt.get_rect(left=cx - 440, top=y))
            y += 55
        btn_rect = pygame.Rect(cx - 180, 660, 360, 56)
        hov = btn_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.surf, (60,150,90) if hov else COLOR_GRAY_DARK,
                         btn_rect, border_radius=12)
        pygame.draw.rect(self.surf, COLOR_FOCUS, btn_rect, 2, border_radius=12)
        lbl = self.fn_menu.render("¡EMPEZAR A JUGAR!", True, COLOR_TEXT)
        self.surf.blit(lbl, lbl.get_rect(center=btn_rect.center))

    def _draw_thinking_screen(self) -> None:
        cx = WIDTH // 2
        t  = self.fn_title.render("TIEMPO PARA PENSAR", True, COLOR_ACCENT)
        self.surf.blit(t, t.get_rect(center=(cx, 160)))
        if self.assets.img_pensar:
            img = self.assets.img_pensar
            self.surf.blit(img, img.get_rect(center=(cx, HEIGHT//2 - 20)))
        else:
            ph = pygame.Rect(cx - 200, HEIGHT//2 - 140, 400, 240)
            pygame.draw.rect(self.surf, COLOR_GRAY_DARK, ph, border_radius=10)
            pygame.draw.rect(self.surf, COLOR_FOCUS,     ph, 2, border_radius=10)
            info = self.fn_small.render("[Imagen Personalizada Aquí]", True, COLOR_MUTED)
            self.surf.blit(info, info.get_rect(center=ph.center))
        msg = self.fn_body_b.render("Tómate un tiempo para pensar", True, COLOR_TEXT)
        self.surf.blit(msg, msg.get_rect(center=(cx, HEIGHT - 220)))
        btn_rect = pygame.Rect(cx - 160, HEIGHT - 140, 320, 50)
        hov = btn_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.surf, (50,110,180) if hov else COLOR_GRAY_DARK,
                         btn_rect, border_radius=10)
        pygame.draw.rect(self.surf, COLOR_FOCUS, btn_rect, 2, border_radius=10)
        lbl = self.fn_small_b.render("VOLVER AL ROSCO [ENTER]", True, COLOR_TEXT)
        self.surf.blit(lbl, lbl.get_rect(center=btn_rect.center))

    def _draw_settings_menu(self) -> None:
        cx = WIDTH // 2
        title = self.fn_title.render("Configuración", True, COLOR_TEXT)
        self.surf.blit(title, title.get_rect(center=(cx, 220)))

        sub = self.fn_small_b.render("VOLUMEN DE AUDIO", True, COLOR_ACCENT)
        self.surf.blit(sub, sub.get_rect(center=(cx, 310)))

        # Línea separadora
        pygame.draw.line(self.surf, COLOR_MUTED, (cx - 260, 330), (cx + 260, 330), 1)

        # Sliders
        self.slider_music.draw(self.surf, self.fn_body)
        self.slider_sfx.draw(self.surf, self.fn_body)

        # Nota
        nota = self.fn_caps.render(
            "Arrastrá los sliders para ajustar · Los cambios se aplican al instante",
            True, COLOR_MUTED)
        self.surf.blit(nota, nota.get_rect(center=(cx, 540)))

        for b in self.settings_buttons:
            b.draw(self.surf, self.fn_menu)

    def _draw_hud(self) -> None:
        H_LOGO = 140
        mp     = pygame.mouse.get_pos()

        ov = pygame.Surface((260, H_LOGO), pygame.SRCALPHA)
        ov.fill((0, 10, 40, 170))
        self.surf.blit(ov, (0, 0))
        ov2 = pygame.Surface((320, H_LOGO), pygame.SRCALPHA)
        ov2.fill((0, 10, 40, 170))
        self.surf.blit(ov2, (WIDTH - 320, 0))

        pcx, pcy = self.pause_center
        p_hov = math.hypot(mp[0]-pcx, mp[1]-pcy) <= self.pause_r
        pygame.draw.circle(self.surf, (50,130,230) if p_hov else (30,100,200),
                           (pcx, pcy), self.pause_r)
        pygame.draw.circle(self.surf, (255,255,255), (pcx, pcy), self.pause_r, 2)
        ps = self.fn_caps.render("II", True, COLOR_TEXT)
        self.surf.blit(ps, ps.get_rect(center=(pcx, pcy)))

        tx, ty = self.timer_center; tr = self.timer_r
        alert  = self.mode == GameMode.TIMED and self.time_left_ms <= 15_000
        pygame.draw.circle(self.surf, COLOR_FAIL if alert else (25,100,210), (tx,ty), tr)
        pygame.draw.circle(self.surf, (255,255,255), (tx,ty), tr, 3)
        tt = self.format_time() if self.mode == GameMode.TIMED else "∞"
        ts = self.fn_timer.render(tt, True, COLOR_TEXT)
        self.surf.blit(ts, ts.get_rect(center=(tx,ty)))

        ox, oy = self.ok_center; orr = self.ok_r
        pygame.draw.circle(self.surf, COLOR_OK,     (ox,oy), orr)
        pygame.draw.circle(self.surf, (255,255,255), (ox,oy), orr, 2)
        os2 = self.fn_body_b.render(str(self.count_correct()), True, COLOR_TEXT)
        self.surf.blit(os2, os2.get_rect(center=(ox,oy)))

        sr  = self.hud_r; hcx = self.hud_cx
        fl  = self.fn_hud_lbl.render("PALABRAS FALLADAS", True, COLOR_TEXT)
        self.surf.blit(fl, fl.get_rect(midright=(self.hud_lbl_right, self.hud_fail_y)))
        pygame.draw.circle(self.surf, COLOR_FAIL, (hcx, self.hud_fail_y), sr)
        fn2 = self.fn_body_b.render(str(self.count_failed()), True, COLOR_TEXT)
        self.surf.blit(fn2, fn2.get_rect(center=(hcx, self.hud_fail_y)))

        rl  = self.fn_hud_lbl.render("PALABRAS RESTANTES", True, COLOR_TEXT)
        self.surf.blit(rl, rl.get_rect(midright=(self.hud_lbl_right, self.hud_rest_y)))
        pygame.draw.circle(self.surf, (30,110,200), (hcx, self.hud_rest_y), sr)
        rn2 = self.fn_body_b.render(str(self.count_remaining()), True, COLOR_TEXT)
        self.surf.blit(rn2, rn2.get_rect(center=(hcx, self.hud_rest_y)))

    def _draw_feedback(self) -> None:
        s = self.fn_body_b.render(self.feedback, True, COLOR_ACCENT)
        self.surf.blit(s, s.get_rect(center=(WIDTH//2, HEIGHT - 30)))

    def _draw_wrong_overlay(self) -> None:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((110, 10, 20, 215))
        self.surf.blit(ov, (0, 0))
        letter = self.wrong_overlay["letter"]
        answer = self.wrong_overlay["answer"]
        cx, cy = self.rosco_center
        pygame.draw.circle(self.surf, (175, 22, 38), (cx, cy-110), 46)
        pygame.draw.circle(self.surf, (255,255,255),  (cx, cy-110), 46, 3)
        lt = self.fn_title.render(letter, True, COLOR_TEXT)
        self.surf.blit(lt, lt.get_rect(center=(cx, cy-110)))
        m1 = self.fn_body.render("La respuesta correcta era:", True, COLOR_TEXT)
        self.surf.blit(m1, m1.get_rect(center=(cx, cy-42)))
        m2 = self.fn_big_ans.render(answer.upper(), True, COLOR_TEXT)
        self.surf.blit(m2, m2.get_rect(center=(cx, cy+10)))
        m3 = self.fn_small.render("Presiona ENTER para continuar con el rosco.",
                                   True, (255, 210, 210))
        self.surf.blit(m3, m3.get_rect(center=(cx, cy+75)))
        cr  = self.continuar_rect
        hov = cr.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.surf, (255,255,255) if hov else (235,235,235),
                         cr, border_radius=cr.h//2)
        ct = self.fn_small_b.render("CONTINUAR", True, COLOR_FAIL)
        self.surf.blit(ct, ct.get_rect(center=cr.center))

    def _draw_main_menu(self) -> None:
        cx = WIDTH // 2
        title = self.fn_title.render("Pasapalabra", True, COLOR_TEXT)
        sub   = self.fn_body.render("Edición Literatura y Lengua", True, COLOR_ACCENT)
        hint  = self.fn_caps.render("Flechas · ENTER para elegir · ESC para salir",
                                     True, COLOR_MUTED)
        self.surf.blit(title, title.get_rect(center=(cx, 130)))
        self.surf.blit(sub,   sub.get_rect(center=(cx, 188)))
        self.surf.blit(hint,  hint.get_rect(center=(cx, 250)))
        for b in self.main_buttons:
            b.draw(self.surf, self.fn_menu)

    def _draw_mode_menu(self) -> None:
        title = self.fn_title.render("Elige el Modo de Juego", True, COLOR_TEXT)
        self.surf.blit(title, title.get_rect(center=(WIDTH//2, 180)))
        for b in self.mode_buttons:
            b.draw(self.surf, self.fn_menu)

    def _draw_pause_overlay(self) -> None:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 15, 50, 190))
        self.surf.blit(ov, (0, 0))
        t = self.fn_title.render("Juego en Pausa", True, COLOR_TEXT)
        h = self.fn_caps.render(
            "Presiona ESC para reanudar la partida instantáneamente", True, COLOR_MUTED)
        self.surf.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 130)))
        self.surf.blit(h, h.get_rect(center=(WIDTH//2, HEIGHT//2 + 140)))
        for b in self.pause_buttons:
            b.draw(self.surf, self.fn_menu)

    def _draw_finish_overlay(self) -> None:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.surf.blit(ov, (0, 0))
        msg   = "¡Rosco completado!" if self.won else "¡Tiempo agotado!"
        color = COLOR_OK if self.won else COLOR_FAIL
        t1    = self.fn_title.render(msg, True, color)
        corr  = self.fn_body.render(
            f"Aciertos: {self.count_correct()}   Fallos: {self.count_failed()}",
            True, COLOR_TEXT)
        t2    = self.fn_small.render("Pulsa ENTER para volver a elegir modo", True, COLOR_MUTED)
        self.surf.blit(t1,   t1.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
        self.surf.blit(corr, corr.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
        self.surf.blit(t2,   t2.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))

    def _wrap(self, text: str, font: pygame.font.Font, max_w: int) -> list[str]:
        words, lines, current = text.split(), [], ""
        for word in words:
            trial = f"{current} {word}".strip()
            if font.size(trial)[0] <= max_w:
                current = trial
            else:
                if current: lines.append(current)
                current = word
        if current: lines.append(current)
        return lines or [text]


def main() -> None:
    PasapalabraGame().run()
    sys.exit(0)


if __name__ == "__main__":
    main()