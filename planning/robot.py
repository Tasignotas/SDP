# Robot Object

ROBOT_LENGTH = 20
ROBOT_WIDTH = 20
ROBOT_HEIGHT = 10

class Robot:

    def __init__(self, rid, zone, l=ROBOT_LENGTH, w=ROBOT_WIDTH, h=ROBOT_HEIGHT):
        self.id = rid
        self.zone = zone
        self.dimension = (l, w, h)
        self.position = (0, 0, 0, 0)
        self.possession = False

    def get_id(self):
        return self.id

    def get_zone(self):
        return self.zone

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