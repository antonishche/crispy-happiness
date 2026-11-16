import pygame


def make_shadow_surface(width, height, alpha=0):
    if width <= 0 or height <= 0:
        return None
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(
        surf,
        (0, 0, 0, alpha),
        pygame.Rect(0, 0, width, height)
    )

    return surf