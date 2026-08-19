import pygame


class ResourceManager:

    def __init__(self):
        self.sprites = {}
        self.animations = {}
        self.generate_placeholder_sprites()

    def load_image(self, path, colorkey=None):
        if path in self.sprites:
            return self.sprites[path]

        image = pygame.image.load(path).convert()

        if colorkey:
            image.set_colorkey(colorkey)
        else:
            image.set_colorkey((0, 0, 0))

        self.sprites[path] = image
        return image

    def load_spritesheet(self, path, frame_width, frame_height, colorkey=None):
        if path in self.animations:
            return self.animations[path]

        sheet = self.load_image(path, colorkey)
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()

        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                if x + frame_width > sheet_width or y + frame_height > sheet_height:
                    continue

                rect = pygame.Rect(x, y, frame_width, frame_height)
                frame = sheet.subsurface(rect)
                frames.append(frame)

        self.animations[path] = frames
        return frames

    def get_animation(self, name):
        return self.animations.get(name, [])

    def generate_placeholder_sprites(self):
        size = 64
        states = ["idle", "walk"]
        directions = [
            "left", "right"
        ]

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
                self.animations[key] = frames
                