import pygame
import settings
from core.chunk_system import ChunkSystem
from config.biomes import (
    OBJECT_HITBOXES
)


class Player:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = settings.PLAYER_SPEED
        self.width = 20
        self.height = 20

    def update(self, keys, chunk_system: ChunkSystem):
        old_x = self.x
        old_y = self.y

        # X
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if self._collides_with_world(chunk_system):
            self.x = old_x

        # Y
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        if self._collides_with_world(chunk_system):
            self.y = old_y

    def _collides_with_world(self, chunk_system: ChunkSystem):
        left = self.x - self.width / 2
        right = self.x + self.width / 2
        top = self.y - self.height / 2
        bottom = self.y + self.height / 2

        start_tile_x = int(left // settings.TILE_SIZE)
        end_tile_x = int(right // settings.TILE_SIZE)
        start_tile_y = int(top // settings.TILE_SIZE)
        end_tile_y = int(bottom // settings.TILE_SIZE)

        for tile_x in range(start_tile_x, end_tile_x + 1):
            for tile_y in range(start_tile_y, end_tile_y + 1):
                chunk_coords = chunk_system.world_to_chunk_tile(tile_x, tile_y)
                chunk = chunk_system.loaded_chunks.get(chunk_coords)

                if chunk is None:
                    return True

                local_x = int(tile_x % settings.CHUNK_SIZE)
                local_y = int(tile_y % settings.CHUNK_SIZE)

                tile = chunk["tiles"][local_y][local_x]  # type: dict

                if tile["blocked"]:
                    return True

                for obj_name, hitbox_config in OBJECT_HITBOXES.items():
                    if tile.get(obj_name):
                        tile_world_x = tile_x * settings.TILE_SIZE
                        tile_world_y = tile_y * settings.TILE_SIZE

                        hb_w, hb_h = hitbox_config

                        offset_x = (settings.TILE_SIZE - hb_w) // 2
                        offset_y = (settings.TILE_SIZE - hb_h) // 2

                        obj_left = tile_world_x + offset_x
                        obj_right = obj_left + hb_w
                        obj_top = tile_world_y + offset_y
                        obj_bottom = obj_top + hb_h

                        if (
                            left < obj_right and
                            right > obj_left and
                            top < obj_bottom and
                            bottom > obj_top
                        ):
                            return True

        return False
    

