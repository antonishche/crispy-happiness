import pygame
from helpers.functions.placeholder_generator import generate_placeholder_sprites


class ResourceManager:

    def __init__(self):
        self.sprites = {}
        self.animations = {}
        generate_placeholder_sprites(self)

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
                