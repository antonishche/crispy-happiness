import math
from entities.base.creature import Creature


class Enemy(Creature):

    NON_TARGETABLE_PLAYER_STATES = ("dead", "sleep")

    def __init__(self, x, y, resource_manager, enemy_type, enemies_settings, enemies_sprites):
        my_settings = enemies_settings[enemy_type]
        my_sprites = enemies_sprites[enemy_type]
        super().__init__(x, y, resource_manager, my_settings, my_sprites)

    @staticmethod
    def _is_player_vulnerable(player):
        return player is not None and player.state not in Enemy.NON_TARGETABLE_PLAYER_STATES

    def update(self, chunk_system, player, dt):
        if self.state == "dead":
            self.dir_x = 0
            self.dir_y = 0
            self.momentum_x = 0.0
            self.momentum_y = 0.0
            self._animate(dt)
            return

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        player_vulnerable = self._is_player_vulnerable(player)
        dist = abs(self.x - player.x) + abs(self.y - player.y)

        if self.ai_state == "chase":
            if dist > self.forget_range or not player_vulnerable:
                self.ai_state = "idle"
                self.state = "idle"
        else:
            if dist <= self.reaction_range and player_vulnerable:
                self.ai_state = "chase"

        if self.ai_state == "chase":
            self._execute_chase_logic(chunk_system, player, dist, dt)
        else:
            self.update_creature(chunk_system, dt)

    def _execute_chase_logic(self, chunk_system, player, dist, dt):
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        current_attack_radius = self.advanced_range if self.state == "hit" else self.action_range

        if dist <= current_attack_radius:
            self.dir_x = 0
            self.dir_y = 0
            self.momentum_x *= self.friction
            self.momentum_y *= self.friction

            if self.attack_cooldown_timer <= 0:
                self.state = "hit"
            else:
                self.state = "idle"
            self._move(chunk_system)

        else:
            self.state = "walk"
            self._move_to(player.x, player.y)
            self._move(chunk_system)

        animation_finished = self._animate(dt)
        if self.state == "hit" and animation_finished:
            if self._is_player_vulnerable(player):
                player.hp -= self.damage
                if player.hp <= 0:
                    player.hp = 0
                    player.state = "dead"
                    player.frame_index = 0

            self.attack_cooldown_timer = self.attack_cooldown
            self.state = "idle"
            self.ai_state = "idle"