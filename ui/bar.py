import pygame


def draw_bar(surface, x, y, w, h, value, max_value, color, font=None):
    ratio = max(0.0, min(1.0, value / max_value)) if max_value > 0 else 0.0
    outer = pygame.Rect(x, y, w, h)

    # Compact wooden frame matching the pause menu.
    pygame.draw.rect(surface, (48, 39, 28), outer, border_radius=3)
    inner = outer.inflate(-4, -4)
    pygame.draw.rect(surface, (82, 67, 47), inner, border_radius=2)

    fill_width = int(inner.width * ratio)
    if fill_width:
        fill_rect = pygame.Rect(inner.x, inner.y, fill_width, inner.height)
        pygame.draw.rect(surface, color, fill_rect, border_radius=2)
        lighter = tuple(min(255, channel + 35) for channel in color)
        pygame.draw.line(
            surface, lighter,
            (fill_rect.left + 2, fill_rect.top + 1),
            (max(fill_rect.left + 2, fill_rect.right - 2), fill_rect.top + 1), 1
        )

    pygame.draw.rect(surface, (190, 151, 91), outer, 1, border_radius=3)

    if font is not None:
        value_text = font.render(str(int(value)), True, (255, 239, 202))
        surface.blit(value_text, (x + w + 7, y + (h - value_text.get_height()) // 2))


def draw_player_bar(surface, player, username, font):
    surface.blit(font.render(username, True, (255, 239, 202)), (16, 10))
    draw_bar(surface, 16, 31, 200, 17, player.hp, player.max_hp, (57, 190, 76))
    draw_bar(
        surface, 16, 54, 200, 13,
        getattr(player, "stamina", 100),
        getattr(player, "max_stamina", 100),
        (225, 184, 54)
    )


def draw_target_bar(surface, target, color, font, w=200):
    x = surface.get_width() // 2 - w // 2
    draw_bar(surface, x, 32, w, 16, target.hp, target.max_hp, color)
