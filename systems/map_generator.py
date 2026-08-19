import pygame
from noise import pnoise2  # type: ignore
from core.resource_manager import ResourceManager
import settings as settings
from utils.timer import Timer
from config.map.biomes.biomes_config import (
    BIOME_CONFIG,
    BIOMES_DISTRIBUTION
)
from config.map.biome_objects.biome_objects_config import (
    OBJECT_PADDINGS,
    BIOME_OBJECTS_CONFIG,
    OBJECT_SPRITES_POSITIONS
)


class MapGenerator:

    def __init__(self, resource_manager: ResourceManager, seed=None):
        self.seed = seed or settings.SEED
        self.resource_manager = resource_manager
        self.destroyed_objects = set()
        # constant
        self.tile_size = settings.TILE_SIZE
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_pixel_size = settings.CHUNK_SIZE * settings.TILE_SIZE
        self.placeholder_padding = (settings.TILE_SIZE - 20) // 2

    def generate_chunk(self, chunk_x, chunk_y):
        chunk_tiles = self._get_chunk_tiles(chunk_x, chunk_y)
        chunk_surface, chunk_objects = self._prepare_visuals(chunk_x, chunk_y, chunk_tiles)
    
        return {
            "tiles": chunk_tiles,
            "visual_surface": chunk_surface,
            "objects": chunk_objects,
            "world_x": chunk_x * self.chunk_pixel_size,
            "world_y": chunk_y * self.chunk_pixel_size,
            "timer": Timer(settings.CACHE_TIMEOUT)
        }

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
                biome_name = self._get_biome(noise_value)
                tile = self._create_tile(biome_name, world_x, world_y)

                row.append(tile)
            chunk_tiles.append(row)
        return chunk_tiles

    def _draw_tile_placeholder(self, surface, color, tile_pixel_x, tile_pixel_y):
        pygame.draw.rect(
            surface,
            color,
            (tile_pixel_x, tile_pixel_y, self.tile_size, self.tile_size)
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
                # surface
                tile_config = BIOME_CONFIG[tile["biome_name"]]
                if tile_config["sprite_path"] is not None:
                    tile_sprite = self.resource_manager.load_image(tile_config["sprite_path"])
                    chunk_surface.blit(tile_sprite, (tile_pixel_x, tile_pixel_y))
                else:
                    self._draw_tile_placeholder(chunk_surface, tile_config["color"], tile_pixel_x, tile_pixel_y)
                # objects
                tile_object = tile["object"]
                if tile_object is not None:
                    object_config = BIOME_OBJECTS_CONFIG[tile_object]

                    if object_config["sprite_path"] is not None:
                        tile_world_x = chunk_pixel_margin_x + tile_pixel_x
                        tile_world_y = chunk_pixel_margin_y + tile_pixel_y

                        if BIOME_OBJECTS_CONFIG[tile_object]["hit_box"]:
                            world_sort_y = tile_world_y + OBJECT_PADDINGS[tile_object]["bottom_margin"]
                        else:
                            world_sort_y = tile_world_y + settings.TILE_SIZE

                        chunk_objects.append({
                            "name": tile_object,
                            "world_draw_x": tile_world_x + OBJECT_SPRITES_POSITIONS[tile_object]["x"],
                            "world_draw_y": tile_world_y + OBJECT_SPRITES_POSITIONS[tile_object]["y"],
                            "world_sort_y": world_sort_y
                        })
                    else:
                        if object_config["hit_box"] is not None:
                            pygame.draw.rect(
                                chunk_surface,
                                object_config["color"],
                                (
                                    tile_pixel_x + OBJECT_PADDINGS[tile_object]["padding_x"],
                                    tile_pixel_y + OBJECT_PADDINGS[tile_object]["padding_y"],
                                    object_config["hit_box"][0],
                                    object_config["hit_box"][1]
                                )
                            )
                        else:
                            pygame.draw.rect(
                                chunk_surface,
                                (255, 255, 255),
                                (
                                    tile_pixel_x + self.placeholder_padding,
                                    tile_pixel_y + self.placeholder_padding,
                                    20,
                                    20
                                )
                            )

        return chunk_surface, chunk_objects

    def _get_noise(self, x, y):
        return pnoise2(x / 20, y / 20, octaves = 4, base = self.seed)

    def _get_biome(self, noise_value):
        for spread, biome_name in BIOMES_DISTRIBUTION:
            if noise_value <= spread:
                return biome_name
        return BIOMES_DISTRIBUTION[-1][1]

    def _create_tile(self, biome_name, world_x, world_y):
        if (world_x, world_y) in self.destroyed_objects:
            return {
                "biome_name": biome_name,
                "object": None,
            }
        
        config = BIOME_CONFIG[biome_name]
        spawned_object = None

        base_hash = (world_x * 73856093) ^ (world_y * 19349663) ^ (self.seed * 83492791)

        for i, (obj_name, chance) in enumerate(config["objects_chance"].items()):
            obj_hash = base_hash ^ (i << 16)
            pseudo_rand = (obj_hash % 100000) / 100000.0

            if pseudo_rand <= chance:
                spawned_object = obj_name
                break

        return {
            "biome_name": biome_name,
            "object": spawned_object,
        }
