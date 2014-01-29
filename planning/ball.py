# Ball Object

BALL_LENGTH = 5
BALL_WIDTH = 5
BALL_HEIGHT = 5

class Ball:

    def __init__(self):
        self.dimension = (BALL_LENGTH, BALL_WIDTH, BALL_HEIGHT)
        self.position = (0, 0, 0, 0)

    def set_position(self, x, y, r, v):
        self.position = (x, y, r, v)

    def get_position(self):
        return self.position

    def get_dimension(self):
        return self.dimension