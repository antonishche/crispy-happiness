import pygame
import settings.game_settings as game_settings
from core.chunk_system import ChunkSystem
# helpers
from helpers.functions.init_entity_fields import init_entity_fields
from helpers.functions.animation_loader import load_animations


class Entity:
    x: float; y: float
    # speed
    speed: float; acceleration: float; friction: float
    momentum_x: float; momentum_y: float
    dir_x: float; dir_y: float
    # hit_box
    width: int; height: int; rect: pygame.Rect
    type: str; state: str; direction: str
    # animation
    target_sprite_height: int; loaded_sprite_direction: str; target_animations: list
    frame_duration: float; frame_index: int; frame_timer: float
    afk_timer: float; ai_timer: float
    ai_state: str; current_frame: pygame.Surface | None
    last_full_key: str
    cached_frames: list | None
    # draw
    current_half_w: int; current_height: int
    # hp
    damage: int
    hp: int; max_hp: int
    attack_cooldown: float
    attack_cooldown_timer: float
    # ai
    reaction_range: int
    action_range: int
    forget_range: int
    advanced_range: int
    ai_state: str

    def __init__(self, x, y, resource_manager, entity_settings, sprites_config):
        self.resource_manager = resource_manager
        self.sprites_config = sprites_config

        init_entity_fields(self, entity_settings)

        self.x = x
        self.y = y
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

        load_animations(self, sprites_config)

    def _move(self, chunk_system: ChunkSystem):
        dx = int(self.momentum_x)
        dy = int(self.momentum_y)

        self._update_animation_state(dx, dy)

        if dx == 0 and dy == 0:
            return

        # X
        if dx != 0:
            old_x = self.rect.x
            self.rect.x += dx
            if self._collides_with_world(chunk_system):
                self.rect.x = old_x
                
        # Y
        if dy != 0:
            old_y = self.rect.y
            self.rect.y += dy
            if self._collides_with_world(chunk_system):
                self.rect.y = old_y

        self.x = self.rect.centerx
        self.y = self.rect.bottom

    def _animate(self, dt, state_override=None):
        # Allows an overlay animation (e.g. player attack) without changing
        # the logical movement state.
        animation_state = state_override or self.state
        current_key = f"{self.type}_{animation_state}_{self.direction}"
        
        if self.last_full_key != current_key:
            self.last_full_key = current_key
            frames = self.resource_manager.get_animation(current_key)

            if not frames:
                fallback_key = f"default_{animation_state}_{self.direction}"
                frames = self.resource_manager.get_animation(fallback_key) or \
                    self.resource_manager.get_animation(f"default_idle_{self.loaded_sprite_direction or 'left'}")
                
                if not frames:
                    self.frame_index = 0
                    self.current_frame = None
                    self.cached_frames = None
                    return

            self.cached_frames = frames

            config_key = f"{animation_state}_{self.direction}"
            sprite_config = self.sprites_config.get(config_key, {})
            
            self.frame_duration = sprite_config.get("frame_duration", 0.15)
            self.current_half_w = sprite_config.get("half_width", self.target_sprite_height // 2)
            self.current_height = sprite_config.get("target_height", self.target_sprite_height)

        frames = self.cached_frames
        if not frames:
            return

        self.frame_timer += dt
        animation_trigger = False

        if self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration

            if animation_state in {"dead", "sleep", "attack", "hit"}:
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1
                else:
                    animation_trigger = True
            else:
                self.frame_index += 1
                if self.frame_index >= len(frames):
                    self.frame_index = 0
                    animation_trigger = True

        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.current_frame = frames[self.frame_index]
        return animation_trigger

    def draw(self, surface, camera):
        screen_rect = camera.apply(self.rect)
        screen_pos = camera.apply_point(self.rect.centerx, self.rect.bottom)
        screen_cx, screen_bottom_y = screen_pos

        if not self.current_frame:
            pygame.draw.rect(surface, (255, 0, 0), screen_rect)
            return

        draw_x = screen_cx - self.current_half_w
        draw_y = screen_bottom_y - self.current_height

        surface.blit(self.current_frame, (draw_x, draw_y))

    def draw_shadow(self, surface, camera):
        cfg = self.sprites_config.get(f"{self.state}_{self.direction}")
        if not cfg or cfg["shadow_width"] <= 0:
            return

        cx, bottom = camera.apply_point(self.rect.centerx, self.rect.bottom)
        x = cx - cfg["shadow_width"] // 2 + cfg["shadow_x_margin"]
        y = bottom - cfg["shadow_height"] // 2 + cfg["shadow_y_margin"]
        surface.blit(cfg["shadow_surf"], (x, y))

    def _collides_with_world(self, chunk_system: ChunkSystem):
        start_sub_x = int(self.rect.left // game_settings.SUB_TILE_SIZE)
        end_sub_x = int(self.rect.right // game_settings.SUB_TILE_SIZE)
        start_sub_y = int(self.rect.top // game_settings.SUB_TILE_SIZE)
        end_sub_y = int(self.rect.bottom // game_settings.SUB_TILE_SIZE)

        for sub_y in range(start_sub_y, end_sub_y + 1):
            for sub_x in range(start_sub_x, end_sub_x + 1):
                if (sub_x, sub_y) in chunk_system.all_blocked_subtiles:
                    return True

        return False

    def _update_animation_state(self, dx, dy):
        if self.state in {"hit", "attack", "sleep", "dead"}:
            return

        if dx == 0 and dy == 0:
            self.state = "idle"
            return

        self.state = "walk"
        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"
    