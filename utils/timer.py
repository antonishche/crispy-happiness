import time


class Timer:

    def __init__(self, timeout):
        self.start_time = None
        self.timeout = timeout

    def start(self):
        self.start_time = time.time()

    def reset(self):
        self.start_time = None

    def is_expired(self):
        return (
            self.start_time is not None and
            self.time_left() == 0
        )

    def time_left(self):
        if self.start_time:
            time_passed = time.time() - self.start_time
            diff = self.timeout - time_passed
            return max(0.0, diff)
        return 0.0

    def is_running(self):
        return (
            self.start_time is not None and
            self.time_left() > 0
        )