import imagesize
from helpers.utils.file_loader import load_json
from helpers.utils.path_constructor import create_path, path_exists
from helpers.utils.shadow_maker import make_shadow_surface


def load_entity_sprites_config(json_path, main_path, target_height):
    loaded_json = load_json(json_path)
    result = {}
    
    for state_direction, data in loaded_json.items():
        path = create_path(main_path, data["path"]) if data.get("path") else None
        half_width = 0
        
        if not path or not path_exists(path):
            continue

        # frames
        orig_sheet_w, orig_sheet_h = imagesize.get(path)
        w_count = data.get("width_count", 1)
        h_count = data.get("height_count", 1)

        orig_frame_w = orig_sheet_w // w_count
        orig_frame_h = orig_sheet_h // h_count

        if orig_frame_h > 0:
            final_frame_w = int((orig_frame_w * target_height) / orig_frame_h)
            half_width = final_frame_w // 2

        # shadow
        shadow_w, shadow_h = tuple(data.get("shadow_size", [0, 0]))
        shadow_x_margin = data.get("shadow_x_margin", 0)
        shadow_y_margin = data.get("shadow_y_margin", 2)
        alpha = data.get("alpha", 80)
        shadow_surf = make_shadow_surface(shadow_w, shadow_h, alpha)

        result[state_direction] = {
            "count": data.get("count", 1),
            "width_count": data.get("width_count", 1),
            "height_count": data.get("height_count", 1),
            "frame_duration": data.get("frame_duration", 0.15),
            "path": path,
            # "colorkey": tuple(data["colorkey"]) if data.get("colorkey") else None,
            "half_width": half_width,
            "target_height": target_height,
            # shadow
            "shadow_width": shadow_w,
            "shadow_height": shadow_h,
            "shadow_x_margin": shadow_x_margin,
            "shadow_y_margin": shadow_y_margin,
            "shadow_surf": shadow_surf,
        }
        
    return result
