import pygame

pygame.init()

from src.map.base.map_size import BaseMapSize
from src.map.generators.standard.generator import StandardMapGenerator
from src.map.generators.standard.params import StandardMapParameters

class RetroCiv:
    TILE_SIZE_PX: int = 64
    MAP_SIZE_X: int = 100
    MAP_SIZE_Y: int = 80
    SCROLL_SPEED: int = 5
    MOUSE_SCROLL_SPEED: int = 30
    ZOOM_STEP: float = 0.1
    ZOOM_MIN: float = 0.25
    ZOOM_MAX: float = 3.0
    SLIDER_W: int = 200
    SLIDER_H: int = 20
    SLIDER_PADDING: int = 20
    SLIDER_KNOB_R: int = 10

    def __init__(self):
        print("Creating map...")

        map_size = BaseMapSize(size_x=self.MAP_SIZE_X, size_y=self.MAP_SIZE_Y)
        self.wrap_x = map_size.wrap_x
        self.wrap_y = map_size.wrap_y

        map_params = StandardMapParameters(
            map_size=map_size,
            island_seeds=4,
            island_radius_mean=5,
        )
        game_map = StandardMapGenerator(map_params).generate()
        self.map_surface = game_map.render(tile_size=self.TILE_SIZE_PX)
        self.map_pixel_w = self.MAP_SIZE_X * self.TILE_SIZE_PX
        self.map_pixel_h = self.MAP_SIZE_Y * self.TILE_SIZE_PX

        pygame.display.set_caption("Retro Civ")
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_w, self.screen_h = self.screen.get_size()
        self.clock = pygame.time.Clock()

        self._build_tiled_surface()

        self.scroll_x = 0
        self.scroll_y = 0
        self.zoom = 1.0
        self.running = True
        self.dragging_slider = False

        slider_x = self.screen_w - self.SLIDER_W - self.SLIDER_PADDING
        slider_y = self.screen_h - self.SLIDER_H - self.SLIDER_PADDING
        self.slider_rect = pygame.Rect(slider_x, slider_y, self.SLIDER_W, self.SLIDER_H)

    def _build_tiled_surface(self):
        self.copies_x = 2 if self.wrap_x else 1
        self.copies_y = 2 if self.wrap_y else 1
        self.tiled_surface = pygame.Surface(
            (self.map_pixel_w * self.copies_x, self.map_pixel_h * self.copies_y)
        )
        for tx in range(self.copies_x):
            for ty in range(self.copies_y):
                self.tiled_surface.blit(
                    self.map_surface,
                    (tx * self.map_pixel_w, ty * self.map_pixel_h),
                )

    def _tile_dims(self):
        return (
            self.map_pixel_w * self.copies_x,
            self.map_pixel_h * self.copies_y,
        )

    def _zoom_to(self, value: float):
        self.zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, value))
        self._clamp_scroll()

    def _zoom_to_slider(self, mouse_x: int):
        fraction = (mouse_x - self.slider_rect.left) / self.SLIDER_W
        fraction = max(0.0, min(1.0, fraction))
        self._zoom_to(self.ZOOM_MIN + fraction * (self.ZOOM_MAX - self.ZOOM_MIN))

    def _handle_slider_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            knob_x = self._slider_knob_x()
            knob_rect = pygame.Rect(knob_x - self.SLIDER_KNOB_R, self.slider_rect.centery - self.SLIDER_KNOB_R, self.SLIDER_KNOB_R * 2, self.SLIDER_KNOB_R * 2)
            if knob_rect.collidepoint(event.pos) or self.slider_rect.collidepoint(event.pos):
                self.dragging_slider = True
                self._zoom_to_slider(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_slider = False
        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            self._zoom_to_slider(event.pos[0])

    def _slider_knob_x(self) -> float:
        fraction = (self.zoom - self.ZOOM_MIN) / (self.ZOOM_MAX - self.ZOOM_MIN)
        return self.slider_rect.left + fraction * self.SLIDER_W

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEWHEEL:
                self._handle_mouse_scroll(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self._zoom_in()
                elif event.key == pygame.K_MINUS:
                    self._zoom_out()
            self._handle_slider_event(event)

    def _handle_mouse_scroll(self, event):
        mods = pygame.key.get_mods()
        if mods & pygame.KMOD_CTRL:
            if event.y > 0:
                self._zoom_in()
            elif event.y < 0:
                self._zoom_out()
        else:
            self.scroll_y -= event.y * self.MOUSE_SCROLL_SPEED
            self.scroll_x -= event.x * self.MOUSE_SCROLL_SPEED

    def _zoom_in(self):
        self.zoom = min(self.ZOOM_MAX, self.zoom + self.ZOOM_STEP)
        self._clamp_scroll()

    def _zoom_out(self):
        self.zoom = max(self.ZOOM_MIN, self.zoom - self.ZOOM_STEP)
        self._clamp_scroll()

    def scroll(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.scroll_x -= self.SCROLL_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.scroll_x += self.SCROLL_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.scroll_y -= self.SCROLL_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.scroll_y += self.SCROLL_SPEED
        self._clamp_scroll()

    def _clamp_scroll(self):
        if self.wrap_x:
            self.scroll_x %= self.map_pixel_w
        else:
            scaled_w = self.map_pixel_w * self.zoom
            max_x = max(0, scaled_w - self.screen_w)
            self.scroll_x = max(0, min(self.scroll_x, max_x))

        if self.wrap_y:
            self.scroll_y %= self.map_pixel_h
        else:
            scaled_h = self.map_pixel_h * self.zoom
            max_y = max(0, scaled_h - self.screen_h)
            self.scroll_y = max(0, min(self.scroll_y, max_y))

    def _render_view(self):
        view_w = self.screen_w / self.zoom
        view_h = self.screen_h / self.zoom

        tile_w, tile_h = self._tile_dims()
        src_rect = pygame.Rect(self.scroll_x, self.scroll_y, view_w, view_h)
        src_rect.clamp_ip(pygame.Rect(0, 0, tile_w, tile_h))

        scaled = pygame.transform.smoothscale(
            self.tiled_surface.subsurface(src_rect),
            (self.screen_w, self.screen_h),
        )
        self.screen.blit(scaled, (0, 0))
        self._render_slider()

    def _render_slider(self):
        bg = pygame.Surface((self.SLIDER_W, self.SLIDER_H), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        self.screen.blit(bg, self.slider_rect.topleft)

        knob_x = self._slider_knob_x()
        knob_center = (int(knob_x), self.slider_rect.centery)
        pygame.draw.circle(self.screen, (220, 220, 220), knob_center, self.SLIDER_KNOB_R)

        font = pygame.font.SysFont(None, 18)
        label = font.render(f"{self.zoom:.1f}x", True, (255, 255, 255))
        self.screen.blit(label, (self.slider_rect.left - 38, self.slider_rect.centery - 9))

    def run(self):
        while self.running:
            self.handle_events()
            self.scroll()
            self._render_view()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
