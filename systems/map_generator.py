import pygame
import random
from noise import pnoise2  # type: ignore

import settings
from utils.timer import Timer
from config.biomes_config import (
    BIOME_CONFIG,
    BIOMES_DISTRIBUTION,
    BIOME_OBJECTS_CONFIG,
    OBJECT_PADDINGS
)


class MapGenerator:

    def __init__(self, seed=None):
        self.seed = seed or settings.SEED
        self.tile_size = settings.TILE_SIZE
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_pixel_size = settings.CHUNK_SIZE * settings.TILE_SIZE

    def _get_chunk_tiles(self, chunk_x, chunk_y):
        chunk_tiles = []

        chunk_world_x = chunk_x * self.chunk_size
        chunk_world_y = chunk_y * self.chunk_size

        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):
                world_x = chunk_world_x + x
                world_y = chunk_world_y + y

                noise_value = self._get_noise(world_x, world_y)
                biome = self._get_biome(noise_value)
                tile = self._create_tile(biome)

                row.append(tile)
            chunk_tiles.append(row)
        return chunk_tiles

    def _draw_tile_placeholder(self, surface, color, tile_pixel_x, tile_pixel_y):
        pygame.draw.rect(
            surface,
            color,
            (tile_pixel_x, tile_pixel_y, self.tile_size, self.tile_size)
        )

    def _draw_object_placeholder(self, surface, color, tile_pixel_x, tile_pixel_y):
        pygame.draw.rect(
            surface,
            color,
            (tile_pixel_x + 6, tile_pixel_y + 6, self.tile_size - 12, self.tile_size - 12)
        )

    def _prepare_visuals(self, chunk_x, chunk_y, chunk_tiles):
        chunk_surface = pygame.Surface((self.chunk_pixel_size, self.chunk_pixel_size))
        chunk_objects = []

        chunk_pixel_margin_x = chunk_x * self.chunk_pixel_size
        chunk_pixel_margin_y = chunk_y * self.chunk_pixel_size

        for y, row in enumerate(chunk_tiles):
            for x, tile in enumerate(row):
                tile_pixel_x = x * self.tile_size
                tile_pixel_y = y * self.tile_size

                tile_config = BIOME_CONFIG[tile["biome_name"]]
                if tile_config["sprite_path"] is not None:
                    # ………
                    pass
                else:
                    self._draw_tile_placeholder(chunk_surface, tile_config["color"], tile_pixel_x, tile_pixel_y)

                tile_object = tile["object"]
                if tile_object is not None:
                    object_config = BIOME_OBJECTS_CONFIG[tile_object]

                    if object_config["sprite_path"] is not None:
                        chunk_objects.append({
                            "name": tile_object,
                            "world_x": chunk_pixel_margin_x + tile_pixel_x,
                            "world_y": chunk_pixel_margin_y + tile_pixel_y
                        })
                    else:
                        self._draw_object_placeholder(chunk_surface, object_config["color"], tile_pixel_x, tile_pixel_y)

        return chunk_surface, chunk_objects

    def generate_chunk(self, chunk_x, chunk_y):
        chunk_tiles = self._get_chunk_tiles(chunk_x, chunk_y)
        chunk_surface, chunk_objects = self._prepare_visuals(chunk_x, chunk_y, chunk_tiles)

        return {
            "tiles": chunk_tiles,
            "visual_surface": chunk_surface,
            "objects": chunk_objects,
            "timer": Timer(settings.CACHE_TIMEOUT)
        }

    def _draw_tile(self, tile):
        pass

    def _get_noise(self, x, y):
        return pnoise2(x / 40, y / 40, octaves = 4, base = self.seed)

    def _get_biome(self, noise_value):
        for spread, biome_name in BIOMES_DISTRIBUTION:
            if noise_value <= spread:
                return biome_name
        return BIOMES_DISTRIBUTION[-1][1]

    def _create_tile(self, biome_name):
        config = BIOME_CONFIG[biome_name]
        spawned_object = None

        for obj_name, chance in config["objects_chance"].items():
            if random.random() <= chance:
                spawned_object = obj_name
                break

        return {
            "biome_name": biome_name,
            "object": spawned_object,
        }
