import pygame
import settings
from core.chunk_system import ChunkSystem
from config.biomes_config import (
    BIOME_CONFIG,
    OBJECT_PADDINGS,
    BIOME_OBJECTS_CONFIG
)


class Player:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = settings.PLAYER_SPEED
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)

    def _move_x(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

    def _move_y(self, keys):
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

    def _move_player(self, keys, chunk_system: ChunkSystem):
        # X
        old_x = self.rect.x
        self._move_x(keys)
        if self._collides_with_world(chunk_system):
            self.rect.x = old_x
        # Y
        old_y = self.rect.y
        self._move_y(keys)
        if self._collides_with_world(chunk_system):
            self.rect.y = old_y

        self.x, self.y = self.rect.center

    def update(self, keys, chunk_system: ChunkSystem):
        self._move_player(keys, chunk_system)
        # Update_sprites

    def _collides_with_tile_object(self, tile_object_name, tile_x, tile_y,):
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

        for tile_x in range(start_tile_x, end_tile_x + 1):
            for tile_y in range(start_tile_y, end_tile_y + 1):
                chunk = self._get_chunk_from_tile_coords(chunk_system, tile_x, tile_y)
                if chunk is None:
                    return True

                tile = self._get_tile_from_chunk(chunk, tile_x, tile_y)  # type: dict
                if BIOME_CONFIG[tile["biome_name"]]["blocked"]:
                    return True

                tile_object = tile.get("object")
                if tile_object is None:
                    continue

                if self._collides_with_tile_object(tile_object, tile_x, tile_y):
                    return True

        return False
    
