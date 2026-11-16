import os
import helpers.paths.paths as paths
from helpers.utils.settings_parser import parse_settings
from helpers.utils.entity_sprites_loader import load_entity_sprites_config


def load_all_enemies():
    enemies_settings = {}
    enemies_sprites = {}

    for folder_name in os.listdir(paths.ENEMIES_DATA_PATH):
        entity_data_dir = os.path.join(paths.ENEMIES_DATA_PATH, folder_name)

        if not os.path.isdir(entity_data_dir):
            continue

        settings_json_path = os.path.join(entity_data_dir, f"{folder_name}_settings.json")
        sprites_json_path = os.path.join(entity_data_dir, f"{folder_name}_sprites.json")
        
        entity_assets_dir = os.path.join(paths.ENEMIES_SPRITES_PATH, folder_name)

        if not os.path.exists(settings_json_path) or not os.path.exists(sprites_json_path):
            continue

        if os.path.getsize(settings_json_path) == 0 or os.path.getsize(sprites_json_path) == 0:
            print(f"Warning: one file of dir '{folder_name}' is empty. Skip...")
            continue

        if not os.path.exists(settings_json_path) or not os.path.exists(sprites_json_path):
            continue

        settings_dict = parse_settings(settings_json_path)
        
        sprites_dict = load_entity_sprites_config(
            json_path=sprites_json_path,
            main_path=entity_assets_dir,
            target_height=settings_dict["target_sprite_height"]
        )

        entity_type = settings_dict["type"]

        enemies_settings[entity_type] = settings_dict
        enemies_sprites[entity_type] = sprites_dict

    return enemies_settings, enemies_sprites
