from utils.timer import Timer
import settings


class ChunkSystem:

    def __init__(self):
        self.loaded_chunks = {}
        self.cached_chunks = {}

    def world_to_chunk(self, world_x, world_y):
        chunk_pixel_size = settings.CHUNK_SIZE * settings.TILE_SIZE
        chunk_x = world_x // chunk_pixel_size
        chunk_y = world_y // chunk_pixel_size
        return (chunk_x, chunk_y)

    def world_to_chunk_tile(self, tile_x, tile_y):
        chunk_x = tile_x // settings.CHUNK_SIZE
        chunk_y = tile_y // settings.CHUNK_SIZE
        return (chunk_x, chunk_y)

    def get_chunk_coords_around(self, center_chunk_x, center_chunk_y):
        coords = set()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                coords.add((center_chunk_x + dx, center_chunk_y + dy))
        return coords

    def update(self, player_world_x, player_world_y, chunk_generator):
        player_chunk_x, player_chunk_y = self.world_to_chunk(player_world_x, player_world_y)
        chunks_around = self.get_chunk_coords_around(player_chunk_x, player_chunk_y)

        for coord in chunks_around:
            if coord in self.loaded_chunks:
                continue
            if coord in self.cached_chunks:
                chunk = self.cached_chunks.pop(coord)
                timer = chunk["timer"]  # type: Timer
                timer.reset()
                self.loaded_chunks[coord] = chunk
            else:
                self.loaded_chunks[coord] = chunk_generator(coord[0], coord[1])

        to_unload = []
        for coord in self.loaded_chunks:
            if coord not in chunks_around:
                to_unload.append(coord)

        for coord in to_unload:
            chunk = self.loaded_chunks.pop(coord)
            timer = chunk["timer"]  # type: Timer
            timer.start()
            self.cached_chunks[coord] = chunk

        expired = []
        for coord, data in self.cached_chunks.items():
            timer = data["timer"]  # type: Timer
            if timer.is_expired():
                expired.append(coord)

        for coord in expired:
            del self.cached_chunks[coord]

    def get_chunk(self, cx, cy):
        return self.loaded_chunks.get((cx, cy))

    def get_loaded_count(self):
        return len(self.loaded_chunks)

    def get_cached_count(self):
        return len(self.cached_chunks)
