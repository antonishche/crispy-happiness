import pygame

class HUD:
    def __init__(self, username="Player"):
        self.username = username
        self.font = pygame.font.SysFont(None, 22)

    def draw(self, surface, player, enemies):
        self._draw_player_bar(surface, player)
        target = self._find_target(player, enemies)
        if target:
            color = (230, 200, 40) if getattr(target, "friendly", False) else (200, 40, 40)
            self._draw_target_bar(surface, target, color)

    def _find_target(self, player, enemies):
        best, best_d = None, float("inf")
        for e in enemies:
            if e.state == "dead":
                continue
            d = abs(player.x - e.x) + abs(player.y - e.y)
            if d <= player.reaction_range and d < best_d:
                best, best_d = e, d
        return best

    def _bar(self, surface, x, y, w, h, hp, max_hp, color):
        ratio = max(0, min(1, hp / max_hp)) if max_hp > 0 else 0
        pygame.draw.rect(surface, (30, 30, 30), (x, y, w, h))
        pygame.draw.rect(surface, color, (x, y, int(w * ratio), h))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)

    def _draw_player_bar(self, surface, player):
        surface.blit(self.font.render(self.username, True, (255, 255, 255)), (16, 12))
        self._bar(surface, 16, 32, 200, 16, player.hp, player.max_hp, (60, 200, 80))

    def _draw_target_bar(self, surface, target, color):
        w = 240
        x = surface.get_width() // 2 - w // 2
        self._bar(surface, x, 16, w, 16, target.hp, target.max_hp, color)