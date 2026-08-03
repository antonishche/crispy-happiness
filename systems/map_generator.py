import pygame
import random
from noise import pnoise2  # type: ignore

import settings
from utils.timer import Timer
from config.biomes import (
    BIOME_CONFIGS,
    BIOMES_DISTRIBUTION,
    DEFAULT_TILE_STATE,
    BIOME_COLORS,
    OBJECT_COLORS
)


class MapGenerator:

    def __init__(self, seed=None):
        self.seed = seed or settings.SEED

    def generate_chunk(self, chunk_x, chunk_y):
        chunk_data = []

        chunk_pixel_size = settings.CHUNK_SIZE * settings.TILE_SIZE
        chunk_surface = pygame.Surface((chunk_pixel_size, chunk_pixel_size))

        for y in range(settings.CHUNK_SIZE):
            row = []
            for x in range(settings.CHUNK_SIZE):
                world_x = chunk_x * settings.CHUNK_SIZE + x
                world_y = chunk_y * settings.CHUNK_SIZE + y
                
                noise_value = self._get_noise(world_x, world_y)
                biome = self._get_biome(noise_value)
                tile = self._create_tile(biome)
                row.append(tile)

                tile_pixel_x = x * settings.TILE_SIZE
                tile_pixel_y = y * settings.TILE_SIZE

                color = BIOME_COLORS.get(biome, (0, 0, 0))
                tile_coords = (
                    tile_pixel_x,
                    tile_pixel_y,
                    settings.TILE_SIZE,
                    settings.TILE_SIZE
                )

                # Рисунок плитки
                pygame.draw.rect(
                    chunk_surface,
                    color,
                    tile_coords
                )

                obj_coords = (
                    tile_pixel_x + 6,
                    tile_pixel_y + 6,
                    settings.TILE_SIZE - 12,
                    settings.TILE_SIZE - 12
                )

                # Рисунок объекта на плитке
                for obj_name, obj_color in OBJECT_COLORS.items():
                    if tile.get(obj_name):
                        pygame.draw.rect(
                            chunk_surface,
                            obj_color,
                            obj_coords
                        )
                        break

            chunk_data.append(row)

        return {
            "tiles": chunk_data,
            "visual_surface": chunk_surface,
            "timer": Timer(settings.CACHE_TIMEOUT)
        }

    def _get_noise(self, x, y):
        return pnoise2(x / 20, y / 20, octaves = 4, base = self.seed)

    def _get_biome(self, noise_value):
        for threshold, biome_name in BIOMES_DISTRIBUTION:
            if noise_value <= threshold:
                return biome_name
        return BIOMES_DISTRIBUTION[-1][1]

    def _create_tile(self, biome_name):
        config = BIOME_CONFIGS[biome_name]

        tile = {
            "biome": biome_name,
            **DEFAULT_TILE_STATE,
            "blocked": config["blocked"]
        }

        for obj_name, chance in config["objects_chance"]:
            if random.random() < chance:
                tile[obj_name] = True
                break

        return tile
