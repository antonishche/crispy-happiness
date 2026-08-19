from utils.timer import Timer
import settings as settings


class ChunkSystem:

    def __init__(self):
        self.loaded_chunks = {}
        self.cached_chunks = {}
        self.chunk_pixel_size = settings.CHUNK_SIZE * settings.TILE_SIZE
        self.current_player_chunk = None

    def world_to_chunk(self, world_x, world_y):
        chunk_x = world_x // self.chunk_pixel_size
        chunk_y = world_y // self.chunk_pixel_size
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
        self._delete_expired_chunks()

        new_chunk = self.world_to_chunk(player_world_x, player_world_y)
        if self.current_player_chunk == new_chunk:
            return
        self.current_player_chunk = (new_chunk[0], new_chunk[1])
        chunks_around = self.get_chunk_coords_around(new_chunk[0], new_chunk[1])

        self._process_chunks_around(chunks_around, chunk_generator)
        self._unload_extra_chunks(chunks_around)

    def _process_chunks_around(self, chunks_around, chunk_generator):
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

    def _unload_extra_chunks(self, chunks_around):
        to_unload = []
        for coord in self.loaded_chunks:
            if coord not in chunks_around:
                to_unload.append(coord)

        for coord in to_unload:
            chunk = self.loaded_chunks.pop(coord)
            timer = chunk["timer"]  # type: Timer
            timer.start()
            self.cached_chunks[coord] = chunk

    def _delete_expired_chunks(self):
        if not self.cached_chunks:
            return

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
