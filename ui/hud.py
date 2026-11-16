import pygame
from ui.bar import draw_player_bar, draw_target_bar


class HUD:
    def __init__(self, username="Player"):
        self.username = username
        self.font = pygame.font.SysFont(None, 22)

    def draw(self, surface, player, enemies):
        draw_player_bar(surface, player, self.username, self.font)
        target = self._find_target(player, enemies)
        if target:
            color = (230, 200, 40) if getattr(target, "friendly", False) else (200, 40, 40)
            draw_target_bar(surface, target, color, self.font)

    def _find_target(self, player, enemies):
        best, best_distance = None, float("inf")
        for enemy in enemies:
            if enemy.state == "dead":
                continue
            distance = abs(player.x - enemy.x) + abs(player.y - enemy.y)
            if distance <= player.reaction_range and distance < best_distance:
                best, best_distance = enemy, distance
        return best
