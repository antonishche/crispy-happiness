class Camera:
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0.0
        self.y = 0.0
        self.half_width = width // 2
        self.half_height = height // 2
        self.smooth_speed = 6

    def update(self, target, dt):
        target_x = target.x - self.half_width
        target_y = target.y - self.half_height

        self.x += (target_x - self.x) * self.smooth_speed * dt
        self.y += (target_y - self.y) * self.smooth_speed * dt

    def apply(self, rect):
        return rect.move(-int(self.x), -int(self.y))

    def apply_point(self, world_x, world_y):
        return (int(world_x - self.x), int(world_y - self.y))

    def reverse_point(self, screen_x, screen_y):
        return (int(screen_x + self.x), int(screen_y + self.y))