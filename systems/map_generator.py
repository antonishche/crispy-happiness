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
    OBJECT_SPRITES_GEOMETRY
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
        self.placeholder_padding = (settings.TILE_SIZE - settings.PLACEHOLDER_RECT_SIZE) // 2
        self.half_tile_size = settings.TILE_SIZE // 2

    def generate_chunk_math(self, chunk_x, chunk_y):
        chunk_world_x = chunk_x * self.chunk_pixel_size
        chunk_world_y = chunk_y * self.chunk_pixel_size

        chunk_tile_start_x = chunk_x * self.chunk_size
        chunk_tile_start_y = chunk_y * self.chunk_size

        chunk_tiles = self._get_chunk_tiles(chunk_tile_start_x, chunk_tile_start_y)
        
        blocked_subtiles = set()
        for y, row in enumerate(chunk_tiles):
            for x, tile in enumerate(row):
                world_tile_x = chunk_tile_start_x + x
                world_tile_y = chunk_tile_start_y + y

                sub_base_x = world_tile_x * settings.SUB_DIVISIONS
                sub_base_y = world_tile_y * settings.SUB_DIVISIONS

                tile_config = BIOME_CONFIG[tile["biome_name"]]
                if tile_config["blocked"]:
                    for sy in range(settings.SUB_DIVISIONS):
                        for sx in range(settings.SUB_DIVISIONS):
                            blocked_subtiles.add((sub_base_x + sx, sub_base_y + sy))

                tile_object = tile["object"]
                if tile_object is not None:
                    object_config = BIOME_OBJECTS_CONFIG[tile_object]
                    if object_config["subtiles"]:
                        world_object_subtiles = {
                            (sub_base_x + sx, sub_base_y + sy) 
                            for sx, sy in object_config["subtiles"]
                        }
                        blocked_subtiles |= world_object_subtiles

        return {
            "tiles": chunk_tiles,
            "blocked_subtiles": blocked_subtiles,
            "chunk_world_x": chunk_world_x,
            "chunk_world_y": chunk_world_y,
            "chunk_tile_start_x": chunk_tile_start_x,
            "chunk_tile_start_y": chunk_tile_start_y
        }

    def generate_chunk_visual(self, raw_chunk_data):
        chunk_world_x = raw_chunk_data["chunk_world_x"]
        chunk_world_y = raw_chunk_data["chunk_world_y"]
        
        chunk_tiles = raw_chunk_data["tiles"]
        blocked_subtiles = raw_chunk_data["blocked_subtiles"]

        chunk_surface = pygame.Surface((self.chunk_pixel_size, self.chunk_pixel_size))
        chunk_objects = []
        dummy_set = set()

        for y, row in enumerate(chunk_tiles):
            for x, tile in enumerate(row):
                tile_pixel_x = x * self.tile_size
                tile_pixel_y = y * self.tile_size

                self._process_tile_biome(
                    chunk_surface=chunk_surface,
                    blocked_subtiles=dummy_set,
                    tile=tile,
                    tile_pixel_x=tile_pixel_x,
                    tile_pixel_y=tile_pixel_y,
                    sub_base_x=0,
                    sub_base_y=0
                )

                if tile["object"] is not None:
                    self._process_tile_object(
                        chunk_surface=chunk_surface,
                        chunk_objects=chunk_objects,
                        blocked_subtiles=dummy_set,
                        tile=tile,
                        tile_pixel_x=tile_pixel_x,
                        tile_pixel_y=tile_pixel_y,
                        chunk_world_x=chunk_world_x,
                        chunk_world_y=chunk_world_y,
                        sub_base_x=0,
                        sub_base_y=0
                    )

        return {
            "tiles": chunk_tiles,
            "visual_surface": chunk_surface,
            "objects": chunk_objects,
            "blocked_subtiles": blocked_subtiles,
            "world_x": chunk_world_x,
            "world_y": chunk_world_y,
            "timer": Timer(settings.CACHE_TIMEOUT)
        }

    def _get_chunk_tiles(self, chunk_tile_start_x, chunk_tile_start_y):
        chunk_tiles = []

        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):
                world_tile_x = chunk_tile_start_x + x
                world_tile_y = chunk_tile_start_y + y

                noise_value = self._get_noise(world_tile_x, world_tile_y)
                biome_name = self._get_biome(noise_value)
                tile = self._create_tile(biome_name, world_tile_x, world_tile_y)

                row.append(tile)
            chunk_tiles.append(row)
        return chunk_tiles

    def _process_tile_biome(
        self, chunk_surface, blocked_subtiles,
        tile, tile_pixel_x, tile_pixel_y,
        sub_base_x, sub_base_y
    ):
        tile_config = BIOME_CONFIG[tile["biome_name"]]

        if tile_config["blocked"]:
            for sy in range(settings.SUB_DIVISIONS):
                for sx in range(settings.SUB_DIVISIONS):
                    blocked_subtiles.add((sub_base_x + sx, sub_base_y + sy))

        if tile_config["sprite_path"] is not None:
            tile_sprite = self.resource_manager.load_image(tile_config["sprite_path"])
            chunk_surface.blit(tile_sprite, (tile_pixel_x, tile_pixel_y))
        else:
            pygame.draw.rect(
                chunk_surface,
                tile_config["color"],
                (tile_pixel_x, tile_pixel_y, self.tile_size, self.tile_size)
            )

    def _process_tile_object(
        self, chunk_surface, chunk_objects, blocked_subtiles,
        tile, tile_pixel_x, tile_pixel_y,
        chunk_world_x, chunk_world_y,
        sub_base_x, sub_base_y 
    ):
        tile_object = tile["object"]
        object_config = BIOME_OBJECTS_CONFIG[tile_object]
        sprite_index = tile["sprite_index"]
        sprites_geometry = OBJECT_SPRITES_GEOMETRY[tile_object]

        if object_config["subtiles"]:
            for sx, sy in object_config["subtiles"]:
                blocked_subtiles.add((sub_base_x + sx, sub_base_y + sy))

        if sprites_geometry:
            geom = sprites_geometry[sprite_index]

            tile_world_pixel_x = chunk_world_x + tile_pixel_x
            tile_world_pixel_y = chunk_world_y + tile_pixel_y

            if object_config["hit_box"]:
                world_sort_y = tile_world_pixel_y + OBJECT_PADDINGS[tile_object]["bottom_margin"]
            else:
                world_sort_y = tile_world_pixel_y + self.half_tile_size

            chunk_objects.append({
                "name": tile_object,
                "sprite_path": geom["path"],
                "world_draw_x": tile_world_pixel_x + geom["sprite_x"],
                "world_draw_y": tile_world_pixel_y + geom["sprite_y"],
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
                        settings.PLACEHOLDER_RECT_SIZE,
                        settings.PLACEHOLDER_RECT_SIZE
                    )
                )

    def _get_noise(self, x, y):
        return pnoise2(
            x / settings.NOISE_SCALE_x,
            y / settings.NOISE_SCALE_y,
            octaves = settings.NOISE_OCTAVES,
            base = self.seed
        )

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
                "sprite_index": 0
            }
        
        config = BIOME_CONFIG[biome_name]
        spawned_object = None
        sprite_index = 0

        base_hash = (
            (world_x * settings.HASH_MULTIPLIER_X) ^
            (world_y * settings.HASH_MULTIPLIER_Y) ^
            (self.seed * settings.HASH_MULTIPLIER_SEED)
        )

        for i, (obj_name, chance) in enumerate(config["objects_chance"].items()):
            obj_hash = base_hash ^ (i << 16)
            pseudo_rand = (obj_hash % 100000) / 100000.0

            if pseudo_rand <= chance:
                spawned_object = obj_name

                obj_config = BIOME_OBJECTS_CONFIG[obj_name]
                if obj_config["sprite_paths"]:
                    variations_count = len(obj_config["sprite_paths"])
                    sprite_hash = base_hash ^ settings.SPRITE_VARIATION_SALT
                    sprite_index = sprite_hash % variations_count
                break

        return {
            "biome_name": biome_name,
            "object": spawned_object,
            "sprite_index": sprite_index
        }
