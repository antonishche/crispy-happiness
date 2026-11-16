import random
from entities.base.enemy import Enemy

class Mashroom(Enemy):

    def __init__(self, x, y, resource_manager, enemies_settings, enemies_sprites):
        super().__init__(x, y, resource_manager, "mashroom", enemies_settings, enemies_sprites)
