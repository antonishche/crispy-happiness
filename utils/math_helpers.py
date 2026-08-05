import settings
from config.biomes_config import (
    BIOME_CONFIG
)


def _emergency_spot(chunk):
    emergency_tile = chunk["tiles"][0][0]
    emergency_tile["biome_name"] = "grass"
    emergency_tile["object"] = None
    
    px = settings.TILE_SIZE // 2
    py = settings.TILE_SIZE // 2
    return px, py

def _find_existing_save_spot(chunk):
    for y in range(settings.CHUNK_SIZE):
        for x in range(settings.CHUNK_SIZE):
            tile = chunk["tiles"][y][x]
    
            is_blocked = BIOME_CONFIG[tile["biome_name"]]["blocked"]
            has_object = tile.get("object") is not None
    
            if not is_blocked and not has_object:
                px = x * settings.TILE_SIZE + settings.TILE_SIZE // 2
                py = y * settings.TILE_SIZE + settings.TILE_SIZE // 2
                return px, py
    return None

def find_save_spot(center_chunk) -> tuple:
    found_spot = _find_existing_save_spot(center_chunk)
    if found_spot is None:
        return _emergency_spot(center_chunk)
    return found_spot