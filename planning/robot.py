ROBOT_LENGTH = 20
ROBOT_WIDTH = 20
ROBOT_HEIGHT = 10

class Robot:

    def __init__(self, l=ROBOT_LENGTH, w=ROBOT_WIDTH, h=ROBOT_HEIGHT):
        self.dimension = (l, w, h)
        self.position = (0, 0, 0, 0)
        self.possession = False

    def set_position(self, x, y, r, v):
        self.position = (x, y, r, v)

    def get_position(self):
        return self.position

    def get_dimension(self):
        return self.dimension

    def get_possession(self):
        return self.possession

    def set_possession(self, possession):
        self.possession = possession