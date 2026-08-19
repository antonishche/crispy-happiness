import pygame
import settings
from core.chunk_system import ChunkSystem
from core.resource_manager import ResourceManager
from config.map.biomes.biomes_config import (
    BIOME_CONFIG
)
from config.map.biome_objects.biome_objects_config import (
    OBJECT_PADDINGS,
    BIOME_OBJECTS_CONFIG
)
from config.player.player_sprites_config import (
    PLAYER_SPRITES
)

class Player:

    def __init__(self, x, y, resource_manager):
        self.x = x
        self.y = y
        # move
        self.speed = settings.PLAYER_SPEED
        self.ACCELERATION = 0.8
        self.FRICTION = 0.8
        self.momentum_x = 0.0
        self.momentum_y = 0.0
        # hit_box
        self.width = 15
        self.height = 15
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        # animation
        self.state = "idle"
        self.direction = "left"
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.15
        self.afk_timer = 0.0
        self.resource_manager = resource_manager  # type: ResourceManager
        self._init_player_animations()

    def _init_player_animations(self):
        target_animations = ["idle_left", "walk_left", "dead_left"]
        target_height = 64

        for anim_key in target_animations:
            if anim_key not in PLAYER_SPRITES:
                continue

            config = PLAYER_SPRITES[anim_key]

            sheet = self.resource_manager.load_image(config["path"])

            w_count = config.get("width_count", config.get("width", 1))
            h_count = config.get("height_count", config.get("height", 1))

            calc_w = sheet.get_width() // w_count
            calc_h = sheet.get_height() // h_count

            raw_frames = self.resource_manager.load_spritesheet(
                config["path"],
                calc_w,
                calc_h,
                colorkey=None
            )

            needed_frames = raw_frames[:config["count"]]
            scaled_frames = []
    
            for frame in needed_frames:
                orig_w = frame.get_width()
                orig_h = frame.get_height()

                new_w = int((orig_w * target_height) / orig_h)
                scaled_surf = pygame.transform.scale(frame, (new_w, target_height))
                scaled_frames.append(scaled_surf)

            global_key_left = f"player_{anim_key}"
            self.resource_manager.animations[global_key_left] = scaled_frames

            anim_type = anim_key.split('_')[0]
            global_key_right = f"player_{anim_type}_right"

            mirror_frames = [pygame.transform.flip(frame, True, False) for frame in scaled_frames]
            self.resource_manager.animations[global_key_right] = mirror_frames

    def _move_x(self, dx):
        self.rect.x += dx

    def _move_y(self, dy):
        self.rect.y += dy

    def _move_player(self, dx, dy, chunk_system: ChunkSystem):
        # X
        old_x = self.rect.x
        self._move_x(dx)
        if self._collides_with_world(chunk_system):
            self.rect.x = old_x
        # Y
        old_y = self.rect.y
        self._move_y(dy)
        if self._collides_with_world(chunk_system):
            self.rect.y = old_y

        self.x = self.rect.centerx
        self.y = self.rect.bottom

    def update(self, keys, chunk_system: ChunkSystem, dt=1.0):
        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        move_up = keys[pygame.K_UP] or keys[pygame.K_w]
        move_down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        
        # X
        dir_x = int(move_right) - int(move_left)
        if dir_x == 0:
            self.momentum_x *= self.FRICTION
        else:
            self.momentum_x += dir_x * self.ACCELERATION
            if abs(self.momentum_x) > self.speed:
                self.momentum_x = dir_x * self.speed
        # Y
        dir_y = int(move_down) - int(move_up)
        if dir_y == 0:
            self.momentum_y *= self.FRICTION
        else:
            self.momentum_y += dir_y * self.ACCELERATION
            if abs(self.momentum_y) > self.speed:
                self.momentum_y = dir_y * self.speed

        dx = int(self.momentum_x)
        dy = int(self.momentum_y)

        if dir_x != 0 and dir_y != 0:
            dx = int(dx * 0.75)
            dy = int(dy * 0.75)

        self._move_player(dx, dy, chunk_system)
        self._update_animation_state(dir_x, dir_y)

        if self.state == "idle" or self.state == "dead":
            if self.state == "idle":
                self.afk_timer += dt

                if self.afk_timer >= 5.0:
                    self.state = "dead"
                    self.frame_index = 0
        else:
            self.afk_timer = 0.0

        self._animate(dt)

    def _update_animation_state(self, dx, dy):
        if self.state == "dead" and dx == 0 and dy == 0:
            return
        
        if dx == 0 and dy == 0:
            self.state = "idle"
            return
        
        self.state = "walk"
        if dx == -1:
            self.direction = "left"
        elif dx == 1:
            self.direction = "right"

    def _animate(self, dt):
        key = f"player_{self.state}_{self.direction}"
        frames = self.resource_manager.get_animation(key)

        if not frames:
            self.frame_index = 0
            return

        config_key = f"{self.state}_{self.direction}"
        if config_key in PLAYER_SPRITES:
            self.frame_duration = PLAYER_SPRITES[config_key]["frame_duration"]
        else:
            fallback_config_key = f"{self.state}_left"
            if fallback_config_key in PLAYER_SPRITES:
                self.frame_duration = PLAYER_SPRITES[fallback_config_key]["frame_duration"]

        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration

            if self.state == "dead":
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1
            else:
                self.frame_index = (self.frame_index + 1) % len(frames)

    def draw(self, surface, camera):
        key = f"player_{self.state}_{self.direction}"
        frames = self.resource_manager.get_animation(key)
        #………
        screen_rect = camera.apply(self.rect)
        pygame.draw.rect(surface, (255, 0, 0), screen_rect)
        #………
        if not frames:
            fallback_key = f"default_{self.state}_{self.direction}"
            frames = self.resource_manager.get_animation(fallback_key)

        if not frames:
            frames = self.resource_manager.get_animation("default_idle_left")

        idx = self.frame_index if self.frame_index < len(frames) else 0
        current_frame = frames[idx]

        screen_pos = camera.apply_point(self.rect.centerx, self.rect.bottom)
        screen_cx, screen_bottom_y = screen_pos

        draw_x = screen_cx - current_frame.get_width() // 2
        draw_y = screen_bottom_y - current_frame.get_height()

        surface.blit(current_frame, (draw_x, draw_y))

    def _collides_with_tile_object(self, tile_object_name, tile_x, tile_y):
        if tile_object_name not in OBJECT_PADDINGS:
            return False
        
        tile_world_x = tile_x * settings.TILE_SIZE
        tile_world_y = tile_y * settings.TILE_SIZE
        
        hb_w, hb_h = BIOME_OBJECTS_CONFIG[tile_object_name]["hit_box"]
        padding_x = OBJECT_PADDINGS[tile_object_name]["padding_x"]
        padding_y = OBJECT_PADDINGS[tile_object_name]["padding_y"]
        
        obj_left = tile_world_x + padding_x
        obj_right = obj_left + hb_w
        obj_top = tile_world_y + padding_y
        obj_bottom = obj_top + hb_h

        if (
            self.rect.left < obj_right and
            self.rect.right > obj_left and
            self.rect.top < obj_bottom and
            self.rect.bottom > obj_top
        ):
            return True
        return False

    def _get_chunk_from_tile_coords(self, chunk_system: ChunkSystem, tile_x, tile_y):
        chunk_coords = chunk_system.world_to_chunk_tile(tile_x, tile_y)
        chunk = chunk_system.loaded_chunks.get(chunk_coords)
        return chunk

    def _get_tile_from_chunk(self, chunk, tile_x, tile_y):
        local_x = int(tile_x % settings.CHUNK_SIZE)
        local_y = int(tile_y % settings.CHUNK_SIZE)
        tile = chunk["tiles"][local_y][local_x]
        return tile

    def _collides_with_world(self, chunk_system: ChunkSystem):
        start_tile_x = int(self.rect.left // settings.TILE_SIZE)
        end_tile_x = int(self.rect.right // settings.TILE_SIZE)
        start_tile_y = int(self.rect.top // settings.TILE_SIZE)
        end_tile_y = int(self.rect.bottom // settings.TILE_SIZE)

        last_chunk_coords = None
        last_chunk = None

        for tile_x in range(start_tile_x, end_tile_x + 1):
            for tile_y in range(start_tile_y, end_tile_y + 1):
                chunk_coords = chunk_system.world_to_chunk_tile(tile_x, tile_y)

                if chunk_coords != last_chunk_coords:
                    last_chunk_coords = chunk_coords
                    last_chunk = chunk_system.loaded_chunks.get(chunk_coords)

                if last_chunk is None:
                    return True

                tile = self._get_tile_from_chunk(last_chunk, tile_x, tile_y)  # type: dict
                if BIOME_CONFIG[tile["biome_name"]]["blocked"]:
                    return True

                tile_object = tile.get("object")
                if tile_object is None:
                    continue

                if self._collides_with_tile_object(tile_object, tile_x, tile_y):
                    return True

        return False
