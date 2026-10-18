import random
import math
from core.entity import Entity

class Creature(Entity):

    def __init__(self, x, y, resource_manager, entity_settings, sprites_config):
        super().__init__(x, y, resource_manager, entity_settings, sprites_config)

        self.ai_timer = 0.0
        self.ai_target_time = random.uniform(2.0, 4.0)

        self.last_x = x
        self.last_y = y

    def update_creature(self, chunk_system, dt):
        if self.state == "dead":
            return

        self._update_ai(dt)

        # X
        if self.dir_x == 0:
            self.momentum_x *= self.friction
        else:
            self.momentum_x += self.dir_x * self.acceleration
            if abs(self.momentum_x) > self.speed:
                self.momentum_x = self.dir_x * self.speed
        # Y
        if self.dir_y == 0:
            self.momentum_y *= self.friction
        else:
            self.momentum_y += self.dir_y * self.acceleration
            if abs(self.momentum_y) > self.speed:
                self.momentum_y = self.dir_y * self.speed

        if self.dir_x != 0 and self.dir_y != 0:
            self.momentum_x *= 0.75
            self.momentum_y *= 0.75

        self._move(chunk_system)

        if (self.dir_x != 0 or self.dir_y != 0) and (self.x == self.last_x and self.y == self.last_y):
            self.ai_timer = 99.0

        self.last_x = self.x
        self.last_y = self.y

        self._animate(dt)

    def _update_ai(self, dt):
        self.ai_timer += dt
        
        if self.ai_timer >= self.ai_target_time:
            self.ai_timer = 0.0
            self.ai_target_time = random.uniform(2.0, 4.0)
            
            self.ai_state = random.choices(["wander", "idle"], weights=[70, 30])[0]
            
            if self.ai_state == "wander":
                self.dir_x, self.dir_y = random.choices(
                    [
                        (-1, 0), (1, 0),
                        (0, -1), (0, 1),
                        (-1, -1), (-1, 1), (1, -1), (1, 1)
                    ]
                )[0]
            else:
                self.dir_x = 0
                self.dir_y = 0
                
                if random.random() < 0.5:
                    self.direction = "right" if self.direction == "left" else "left"

    def _move_to(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        hypotenuse = math.sqrt(dx * dx + dy * dy)

        if hypotenuse > 0:
            self.dir_x = dx / hypotenuse
            self.dir_y = dy / hypotenuse
            
            self.momentum_x += self.dir_x * self.acceleration
            if abs(self.momentum_x) > self.speed: 
                self.momentum_x = self.dir_x * self.speed
                
            self.momentum_y += self.dir_y * self.acceleration
            if abs(self.momentum_y) > self.speed: 
                self.momentum_y = self.dir_y * self.speed

