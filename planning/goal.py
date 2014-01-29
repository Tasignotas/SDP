# Goal Object

GOAL_LENGTH = 60
GOAL_WIDTH = 1
GOAL_HEIGHT = 10

class Goal:

    def __init__(self, x, y, r):
        self.dimension = (GOAL_LENGTH, GOAL_WIDTH, GOAL_HEIGHT)
        self.position = (x, y, r, 0)

    def get_position(self):
        return self.position

    def get_dimension(self):
        return self.dimension