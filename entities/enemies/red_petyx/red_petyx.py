import random
from entities.base.enemy import Enemy

class RedPetyx(Enemy):

    def __init__(self, x, y, resource_manager, enemies_settings, enemies_sprites):
        super().__init__(x, y, resource_manager, "red_petyx", enemies_settings, enemies_sprites)
