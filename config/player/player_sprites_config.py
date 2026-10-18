import helpers.paths.paths as paths
from helpers.utils.entity_sprites_loader import load_entity_sprites_config
from settings.player_settings import PLAYER_SETTINGS

PLAYER_SPRITES = load_entity_sprites_config(
    json_path=paths.PLAYER_SPRITES_JSON,
    main_path=paths.PLAYER_SPRITES_PATH,
    target_height=PLAYER_SETTINGS["target_sprite_height"]
)
