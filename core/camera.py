class Camera:
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def update(self, target):
        self.x = target.x - self.width / 2
        self.y = target.y - self.height / 2

    def apply(self, rect):
        return rect.move(-self.x, -self.y)

    def apply_point(self, world_x, world_y):
        return (world_x - self.x, world_y - self.y)

    def reverse_point(self, screen_x, screen_y):
        return (screen_x + self.x, screen_y + self.y)