import pygame

def load_animations(entity, sprites_config):
    if entity.loaded_sprite_direction is None:
        target_animations = [f"{anim_key}_{dir}" for anim_key in entity.target_animations for dir in ["left", "right"]]
    else:
        target_animations = [f"{anim_key}_{entity.loaded_sprite_direction}" for anim_key in entity.target_animations]
        if entity.loaded_sprite_direction == "left":
            mirror_direction = "right"
        else:
            mirror_direction = "left"

    for anim_key in target_animations:
        if anim_key not in sprites_config:
            continue

        config = sprites_config[anim_key]
        colorkey = config.get("colorkey", None)
        sheet = entity.resource_manager.load_image(config["path"], colorkey=colorkey)

        w_count = config.get("width_count", config.get("width", 1))
        h_count = config.get("height_count", config.get("height", 1))

        calc_w = sheet.get_width() // w_count
        calc_h = sheet.get_height() // h_count

        raw_frames = entity.resource_manager.load_spritesheet(
            config["path"],
            calc_w,
            calc_h,
            colorkey=colorkey
        )

        needed_frames = raw_frames[:config["count"]]
        scaled_frames = []

        for frame in needed_frames:
            frame_copy = frame.convert() 
            if colorkey:
                frame_copy.set_colorkey(colorkey)

            orig_w = frame.get_width()
            orig_h = frame.get_height()

            new_w = int((orig_w * entity.target_sprite_height) / orig_h)
            scaled_surf = pygame.transform.scale(frame_copy, (new_w, entity.target_sprite_height))

            if colorkey:
                scaled_surf.set_colorkey(colorkey)

            scaled_frames.append(scaled_surf)

        global_key = f"{entity.type}_{anim_key}"
        entity.resource_manager.animations[global_key] = scaled_frames

        if 'mirror_direction' in locals() and mirror_direction:
            anim_type = anim_key.split('_')[0]
            mirror_key = f"{entity.type}_{anim_type}_{mirror_direction}"

            mirror_frames = [pygame.transform.flip(frame, True, False) for frame in scaled_frames]
            entity.resource_manager.animations[mirror_key] = mirror_frames
            
            config_mirror_key = f"{anim_type}_{mirror_direction}"
            if config_mirror_key not in sprites_config:
                sprites_config[config_mirror_key] = config.copy()
