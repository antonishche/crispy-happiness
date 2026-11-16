import pygame
from noise import pnoise2  # type: ignore
from core.resource_manager import ResourceManager
import settings.game_settings as settings
from helpers.utils.timer import Timer
from config.map.biomes_config import (
    BIOME_CONFIG,
)
from config.map.biome_objects_config import (
    BIOME_OBJECTS_CONFIG,
    OBJECT_SPRITES_GEOMETRY,
)


_SUBS_PER_TILE = settings.SUB_DIVISIONS ** 2

# ---------------------------------------------------------------- biomes ----
# Таблица (elevation, moisture) -> biome. Порядок важен: первое совпадение.
# elevation: -1..1, moisture: -1..1
BIOME_CLIMATE = [
    (-1.00, -0.15, -1.00,  1.00, "water"),
    (-0.15,  0.05, -1.00, -0.10, "desert"),
    (-0.15,  0.05, -0.10,  1.00, "grass"),
    ( 0.05,  0.30, -1.00, -0.05, "desert"),
    ( 0.05,  0.30, -0.05,  0.20, "grass"),
    ( 0.05,  0.30,  0.20,  1.00, "forest"),
    ( 0.30,  0.60, -1.00,  0.00, "grass"),
    ( 0.30,  0.60,  0.00,  1.00, "forest"),
    ( 0.60,  1.00, -1.00,  1.00, "forest"),
]

_BIOME_JITTER = 0.04
_WARP_STRENGTH = 25.0
_WARP_SCALE = 40.0

_SMALL_OBJECT_NOISE_SCALE = 18.0
_SMALL_OBJECT_NOISE_THRESHOLD = 0.35


# ---------------------------------------------------------- thresholds -----
BIOME_THRESHOLDS = {}
for biome, cfg in BIOME_CONFIG.items():
    chances = cfg["objects_chance"]
    if not chances:
        BIOME_THRESHOLDS[biome] = ([], 0.0)
        continue
    raw_sum = sum(chances.values())
    total = raw_sum / _SUBS_PER_TILE
    acc = []
    running = 0.0
    for name, ch in chances.items():
        running += ch
        acc.append((name, running / raw_sum))
    BIOME_THRESHOLDS[biome] = (acc, total)


class MapGenerator:

    def __init__(self, resource_manager: ResourceManager, seed=None):
        self.seed = seed or settings.SEED
        self.resource_manager = resource_manager
        self.destroyed_objects = set()
        self.tile_size = settings.TILE_SIZE
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_pixel_size = settings.CHUNK_SIZE * settings.TILE_SIZE

    # ------------------------------------------------------------------ math

    def generate_chunk_math(self, chunk_x, chunk_y):
        chunk_world_x = chunk_x * self.chunk_pixel_size
        chunk_world_y = chunk_y * self.chunk_pixel_size

        chunk_tile_start_x = chunk_x * self.chunk_size
        chunk_tile_start_y = chunk_y * self.chunk_size

        chunk_tiles = self._get_chunk_tiles(chunk_tile_start_x, chunk_tile_start_y)

        blocked_subtiles = set()
        for y, row in enumerate(chunk_tiles):
            for x, tile in enumerate(row):
                if not BIOME_CONFIG[tile["biome_name"]]["blocked"]:
                    continue

                sub_base_x = (chunk_tile_start_x + x) * settings.SUB_DIVISIONS
                sub_base_y = (chunk_tile_start_y + y) * settings.SUB_DIVISIONS
                for sy in range(settings.SUB_DIVISIONS):
                    for sx in range(settings.SUB_DIVISIONS):
                        blocked_subtiles.add((sub_base_x + sx, sub_base_y + sy))

        objects = self._spawn_objects(chunk_tiles, chunk_tile_start_x, chunk_tile_start_y)
        for obj in objects:
            cfg = BIOME_OBJECTS_CONFIG[obj["name"]]
            if not cfg["hit_box"]:
                continue  # декоративный объект — не блокирует
            fw, fh = cfg["footprint"]
            for fx in range(fw):
                for fy in range(fh):
                    blocked_subtiles.add((obj["sub_x"] + fx, obj["sub_y"] + fy))

        return {
            "tiles": chunk_tiles,
            "objects": objects,
            "blocked_subtiles": blocked_subtiles,
            "chunk_world_x": chunk_world_x,
            "chunk_world_y": chunk_world_y,
            "chunk_tile_start_x": chunk_tile_start_x,
            "chunk_tile_start_y": chunk_tile_start_y
        }

    def _get_chunk_tiles(self, chunk_tile_start_x, chunk_tile_start_y):
        chunk_tiles = []

        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):
                tx = chunk_tile_start_x + x
                ty = chunk_tile_start_y + y
                elevation, moisture = self._get_climate(tx, ty)
                jitter = self._get_noise(tx * 2.3, ty * 2.3, seed_offset=31) * _BIOME_JITTER
                biome_name = self._get_biome(elevation + jitter, moisture)
                row.append({"biome_name": biome_name})
            chunk_tiles.append(row)
        return chunk_tiles

    # -------------------------------------------------------------- spawn ----

    def _spawn_objects(self, chunk_tiles, tile_start_x, tile_start_y):
        sub = settings.SUB_DIVISIONS
        base_sx = tile_start_x * sub
        base_sy = tile_start_y * sub
        n = self.chunk_size * sub

        candidates = []
        for ly in range(n):
            for lx in range(n):
                sx = base_sx + lx
                sy = base_sy + ly

                biome = chunk_tiles[ly // sub][lx // sub]["biome_name"]
                cfg_biome = BIOME_CONFIG[biome]
                if cfg_biome["blocked"]:
                    continue

                name, sprite_index = self._pick_object(biome, sx, sy)
                if name is None:
                    continue

                if (sx, sy) in self.destroyed_objects:
                    continue

                candidates.append({
                    "name": name,
                    "sub_x": sx,
                    "sub_y": sy,
                    "sprite_index": sprite_index,
                })

        def _footprint_area(c):
            fw, fh = BIOME_OBJECTS_CONFIG[c["name"]]["footprint"]
            return max(fw, 1) * max(fh, 1)

        candidates.sort(key=_footprint_area, reverse=True)

        occupied = set()
        objects = []
        for c in candidates:
            cfg = BIOME_OBJECTS_CONFIG[c["name"]]
            fw, fh = cfg["footprint"]
            fw = max(fw, 1)
            fh = max(fh, 1)
            mx, my = cfg["margin_sub"]

            area = {
                (x, y)
                for x in range(c["sub_x"] - mx, c["sub_x"] + fw + mx)
                for y in range(c["sub_y"] - my, c["sub_y"] + fh + my)
            }
            if cfg["hit_box"]:
                if area & occupied:
                    continue
                occupied |= area
            # декоративные объекты не проверяют и не занимают occupied
            objects.append(c)

        return objects

    def _pick_object(self, biome_name, sx, sy):
        thresholds, total = BIOME_THRESHOLDS[biome_name]
        if not thresholds or total <= 0.0:
            return None, 0

        base_hash = (
            (sx * settings.HASH_MULTIPLIER_X) ^
            (sy * settings.HASH_MULTIPLIER_Y) ^
            (self.seed * settings.HASH_MULTIPLIER_SEED)
        )

        r = (base_hash % 1000000) / 1000000.0
        if r > total:
            return None, 0

        pick = ((base_hash // 1000000) % 1000000) / 1000000.0
        chosen = None
        for obj_name, cum in thresholds:
            if pick <= cum:
                chosen = obj_name
                break
        if chosen is None:
            return None, 0

        cfg = BIOME_OBJECTS_CONFIG[chosen]
        paths = cfg["sprite_paths"]
        sprite_index = (
            (base_hash ^ settings.SPRITE_VARIATION_SALT) % len(paths)
            if paths else 0
        )
        return chosen, sprite_index

    # ---------------------------------------------------------------- visual

    def generate_chunk_visual(self, raw_chunk_data):
        chunk_world_x = raw_chunk_data["chunk_world_x"]
        chunk_world_y = raw_chunk_data["chunk_world_y"]

        chunk_tiles = raw_chunk_data["tiles"]
        blocked_subtiles = raw_chunk_data["blocked_subtiles"]

        chunk_surface = pygame.Surface((self.chunk_pixel_size, self.chunk_pixel_size))
        chunk_objects = []

        for y, row in enumerate(chunk_tiles):
            for x, tile in enumerate(row):
                self._draw_tile_biome(
                    chunk_surface, tile,
                    x * self.tile_size, y * self.tile_size
                )

        for obj in raw_chunk_data["objects"]:
            self._process_object(
                chunk_surface, chunk_objects, obj,
                chunk_world_x, chunk_world_y
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

    def _draw_tile_biome(self, chunk_surface, tile, tile_pixel_x, tile_pixel_y):
        tile_config = BIOME_CONFIG[tile["biome_name"]]

        if tile_config["sprite_path"] is not None:
            tile_sprite = self.resource_manager.load_image(tile_config["sprite_path"])
            chunk_surface.blit(tile_sprite, (tile_pixel_x, tile_pixel_y))
        else:
            pygame.draw.rect(
                chunk_surface,
                tile_config["color"],
                (tile_pixel_x, tile_pixel_y, self.tile_size, self.tile_size)
            )

    def _process_object(self, chunk_surface, chunk_objects, obj, chunk_world_x, chunk_world_y):
        name = obj["name"]
        cfg = BIOME_OBJECTS_CONFIG[name]
        geoms = OBJECT_SPRITES_GEOMETRY[name]

        world_px = obj["sub_x"] * settings.SUB_TILE_SIZE
        world_py = obj["sub_y"] * settings.SUB_TILE_SIZE

        if geoms:
            g = geoms[obj["sprite_index"]]
            chunk_objects.append({
                "name": name,
                "sprite_path": g["path"],
                "world_draw_x": world_px + g["sprite_x"],
                "world_draw_y": world_py + g["sprite_y"],
                "world_sort_y": world_py + cfg["sort_offset"]
            })
        else:
            # декоративный объект без спрайтов — не рисуем ничего
            if not cfg["hit_box"]:
                return
            # обычная заглушка для объектов с хитбоксом, но без спрайтов
            fw, fh = cfg["footprint"]
            w = fw * settings.SUB_TILE_SIZE
            h = fh * settings.SUB_TILE_SIZE
            pygame.draw.rect(
                chunk_surface, cfg["color"],
                (world_px - chunk_world_x, world_py - chunk_world_y, w, h)
            )

    # ----------------------------------------------------------------- noise

    def _get_noise(self, x, y, seed_offset=0):
        return pnoise2(
            x / settings.NOISE_SCALE_x,
            y / settings.NOISE_SCALE_y,
            octaves=settings.NOISE_OCTAVES,
            base=self.seed + seed_offset,
        )

    def _get_climate(self, x, y):
        wx = pnoise2(x / _WARP_SCALE, y / _WARP_SCALE, octaves=2,
                     base=self.seed + 101) * _WARP_STRENGTH
        wy = pnoise2(x / _WARP_SCALE + 50, y / _WARP_SCALE + 50, octaves=2,
                     base=self.seed + 102) * _WARP_STRENGTH

        elevation = pnoise2(
            (x + wx) / settings.NOISE_SCALE_x,
            (y + wy) / settings.NOISE_SCALE_y,
            octaves=settings.NOISE_OCTAVES,
            persistence=0.5,
            lacunarity=2.0,
            base=self.seed,
        )
        moisture = pnoise2(
            (x + wx) / (settings.NOISE_SCALE_x * 1.7),
            (y + wy) / (settings.NOISE_SCALE_y * 1.7),
            octaves=3,
            persistence=0.55,
            lacunarity=2.0,
            base=self.seed + 7,
        )
        return elevation, moisture

    def _get_biome(self, elevation, moisture):
        for emin, emax, mmin, mmax, biome_name in BIOME_CLIMATE:
            if emin <= elevation <= emax and mmin <= moisture <= mmax:
                return biome_name
        return "grass"