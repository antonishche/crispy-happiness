import pygame


def generate_placeholder_sprites(resource_manager):
    size = 64
    states = ["idle", "walk"]
    directions = ["left", "right"]

    for state in states:
        frame_count = 1 if state == "idle" else 2
        for direction in directions:
            frames = []
            for i in range(frame_count):
                surf = pygame.Surface((size, size))
                surf.fill((255, 0, 255))

                body_rect = pygame.Rect(8, 8, 48, 48)
                if i == 1:
                    body_rect.y += 2

                pygame.draw.rect(surf, (200, 50, 50), body_rect)
                eye_color = (255, 220, 50)

                if direction == "left":
                    pygame.draw.rect(surf, eye_color, (0, 20, 8, 24))
                elif direction == "right":
                    pygame.draw.rect(surf, eye_color, (56, 20, 8, 24))

                surf.set_colorkey((255, 0, 255))
                surf = surf.convert()

                frames.append(surf)

            key = f"default_{state}_{direction}"
            resource_manager.animations[key] = frames