import queue
from helpers.utils.timer import Timer
import settings.game_settings as game_settings


class ChunkSystem:

    def __init__(self):
        # cash
        self.loaded_chunks = {}
        self.cached_chunks = {}
        self.all_blocked_subtiles = set()
        # queue
        self.generation_queue = queue.Queue()
        self.finished_queue = queue.Queue()
        self.pending_chunks = set()
        # other
        self.chunk_pixel_size = game_settings.CHUNK_SIZE * game_settings.TILE_SIZE
        self.current_player_chunk = None

    def _bg_generation_worker(self, math_generator_func):
        while True:
            chunk_x, chunk_y = self.generation_queue.get()

            if chunk_x is None:
                break

            try:
                raw_chunk_data = math_generator_func(chunk_x, chunk_y)
                self.finished_queue.put(((chunk_x, chunk_y), raw_chunk_data))
            except Exception as e:
                print(f"chunk {chunk_x, chunk_y} - generation fault in background: {e}")
            finally:
                self.generation_queue.task_done()

    def world_to_chunk(self, world_x, world_y):
        chunk_x = world_x // self.chunk_pixel_size
        chunk_y = world_y // self.chunk_pixel_size
        return (chunk_x, chunk_y)

    def world_to_chunk_tile(self, tile_x, tile_y):
        chunk_x = tile_x // game_settings.CHUNK_SIZE
        chunk_y = tile_y // game_settings.CHUNK_SIZE
        return (chunk_x, chunk_y)

    def world_subtile_to_tile(self, sub_x, sub_y):
        tile_x = sub_x // game_settings.SUB_DIVISIONS
        tile_y = sub_y // game_settings.SUB_DIVISIONS
        return (tile_x, tile_y)

    def get_chunk_coords_around(self, center_chunk_x, center_chunk_y):
        coords = set()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                coords.add((center_chunk_x + dx, center_chunk_y + dy))
        return coords

    def update(self, player_world_x, player_world_y, math_generator_func, visual_generator_func):
        self._delete_expired_chunks()
        self._collect_finished_chunks(visual_generator_func)

        new_chunk = self.world_to_chunk(player_world_x, player_world_y)
        if self.current_player_chunk == new_chunk:
            return
        
        self.current_player_chunk = (new_chunk[0], new_chunk[1])
        chunks_around = self.get_chunk_coords_around(new_chunk[0], new_chunk[1])

        self._request_chunks_around(chunks_around)
        self._unload_extra_chunks(chunks_around)

    def _request_chunks_around(self, chunks_around):
        for coord in chunks_around:
            if coord in self.loaded_chunks or coord in self.pending_chunks:
                continue

            if coord in self.cached_chunks:
                chunk = self.cached_chunks.pop(coord)
                timer = chunk["timer"]  # type: Timer
                timer.reset()
                self.loaded_chunks[coord] = chunk
                self.all_blocked_subtiles |= chunk["blocked_subtiles"]
                continue

            self.pending_chunks.add(coord)
            self.generation_queue.put(coord)

    def _collect_finished_chunks(self, visual_generator_func):
        chunks_processed = 0
        
        while chunks_processed < 1:
            try:
                coord, raw_chunk_data = self.finished_queue.get_nowait()
            except queue.Empty:
                break

            new_chunk = self.current_player_chunk
            if new_chunk:
                chunks_around = self.get_chunk_coords_around(new_chunk[0], new_chunk[1])
                if coord not in chunks_around:
                    self.pending_chunks.discard(coord)
                    self.finished_queue.task_done()
                    continue

            self.pending_chunks.discard(coord)

            full_chunk = visual_generator_func(raw_chunk_data)
            self.loaded_chunks[coord] = full_chunk
            self.all_blocked_subtiles |= full_chunk["blocked_subtiles"]
            
            self.finished_queue.task_done()
            chunks_processed += 1

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
            self.all_blocked_subtiles -= chunk["blocked_subtiles"]

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
