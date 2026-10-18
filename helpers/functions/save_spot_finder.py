import settings.game_settings as game_settings
from config.map.biomes_config import (
    BIOME_CONFIG
)


def _emergency_spot(chunk):
    emergency_tile = chunk["tiles"][0][0]
    emergency_tile["biome_name"] = "grass"
    emergency_tile["object"] = None
    
    px = game_settings.TILE_SIZE // 2
    py = game_settings.TILE_SIZE // 2
    return px, py

def _find_existing_save_spot(chunk):
    for y in range(game_settings.CHUNK_SIZE):
        for x in range(game_settings.CHUNK_SIZE):
            tile = chunk["tiles"][y][x]
    
            is_blocked = BIOME_CONFIG[tile["biome_name"]]["blocked"]
            has_object = tile.get("object") is not None
    
            if not is_blocked and not has_object:
                px = x * game_settings.TILE_SIZE + game_settings.TILE_SIZE // 2
                py = y * game_settings.TILE_SIZE + game_settings.TILE_SIZE // 2
                return px, py
    return None

def find_save_spot(center_chunk) -> tuple:
    found_spot = _find_existing_save_spot(center_chunk)
    if found_spot is None:
        return _emergency_spot(center_chunk)
    return found_spot
