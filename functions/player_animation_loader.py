import pygame
from config.player.player_sprites_config import PLAYER_SPRITES


def load_player_animations(resource_manager):
    target_animations = ["idle_left", "walk_left", "dead_left"]
    target_height = 64

    for anim_key in target_animations:
        if anim_key not in PLAYER_SPRITES:
            continue

        config = PLAYER_SPRITES[anim_key]
        sheet = resource_manager.load_image(config["path"])

        w_count = config.get("width_count", config.get("width", 1))
        h_count = config.get("height_count", config.get("height", 1))

        calc_w = sheet.get_width() // w_count
        calc_h = sheet.get_height() // h_count

        raw_frames = resource_manager.load_spritesheet(
            config["path"],
            calc_w,
            calc_h,
            colorkey=None
        )

        needed_frames = raw_frames[:config["count"]]
        scaled_frames = []

        for frame in needed_frames:
            orig_w = frame.get_width()
            orig_h = frame.get_height()

            new_w = int((orig_w * target_height) / orig_h)
            scaled_surf = pygame.transform.scale(frame, (new_w, target_height))
            scaled_frames.append(scaled_surf)

        global_key_left = f"player_{anim_key}"
        resource_manager.animations[global_key_left] = scaled_frames

        anim_type = anim_key.split('_')[0]
        global_key_right = f"player_{anim_type}_right"

        mirror_frames = [pygame.transform.flip(frame, True, False) for frame in scaled_frames]
        resource_manager.animations[global_key_right] = mirror_frames