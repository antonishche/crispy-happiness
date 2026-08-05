import pygame
import settings
from core.camera import Camera
from core.chunk_system import ChunkSystem
from systems.map_generator import MapGenerator
from entities.player import Player
from utils.math_helpers import (
    find_save_spot
)


def draw_world(screen: pygame.Surface, camera: Camera, chunk_system: ChunkSystem):
    chunk_pixel_size = settings.CHUNK_SIZE * settings.TILE_SIZE

    for coord, chunk in chunk_system.loaded_chunks.items():
        chunk_x, chunk_y = coord

        chunk_world_x = chunk_x * chunk_pixel_size
        chunk_world_y = chunk_y * chunk_pixel_size

        screen_pos = camera.apply_point(chunk_world_x, chunk_world_y)
        screen_x, screen_y = screen_pos

        # Виден ли чанк на экране
        if (
            screen_x + chunk_pixel_size < 0 or
            screen_x > screen.get_width() or
            screen_y + chunk_pixel_size < 0 or
            screen_y > screen.get_height()
        ):
            continue

        screen.blit(chunk["visual_surface"], (screen_x, screen_y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((
        settings.SCREEN_WIDTH,
        settings.SCREEN_HEIGHT
    ))
    pygame.display.set_caption("Survival Adventure")
    clock = pygame.time.Clock()

    camera = Camera(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    chunk_system = ChunkSystem()
    generator = MapGenerator(seed=settings.SEED)

    chunk_system.update(0, 0, generator.generate_chunk)
    center_chunk = chunk_system.loaded_chunks.get((0, 0))

    spawn_x, spawn_y = find_save_spot(center_chunk)
    player = Player(spawn_x, spawn_y)

    chunk_system.update(player.rect.x, player.rect.y, generator.generate_chunk)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys, chunk_system)
        camera.update(player)
        chunk_system.update(player.x, player.y, generator.generate_chunk)

        screen.fill((0, 0, 0))
        draw_world(screen, camera, chunk_system)

        player_screen_rect = camera.apply(player.rect)
        pygame.draw.rect(screen, (255, 0, 0), player_screen_rect)

        pygame.display.flip()
        clock.tick(settings.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()