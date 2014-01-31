
from json import load
from numpy import array
from cv2 import pointPolygonTest


ROBOT_LENGTH = 20
ROBOT_WIDTH = 20
ROBOT_HEIGHT = 10


BALL_LENGTH = 5
BALL_WIDTH = 5
BALL_HEIGHT = 5

GOAL_LENGTH = 60
GOAL_WIDTH = 1
GOAL_HEIGHT = 10


class Coordinate(object):


    def __init__(self, x, y):
        self.x = x
        self.y = y


    def get_position(self):
        return self.x, self.y


    def set_position(self, x, y):
        self.x = x
        self.y = y


    def __repr__(self):
        return 'x: %s, y: %s\n' % (self.x, self.y)


class Polygon:


    def __init__(self, coord_array):
        self.points = []
        for coords in coord_array:
            self.points.append(Coordinate(*coords))


    def __repr__(self):
        return ''.join([point.__repr__() for point in self.points])



class Vector(Coordinate):


    def __init__(self, x, y, angle, velocity):
        super(Vector, self).__init__(x, y)
        self.orientation = angle
        self.velocity = velocity


    def get_orientation(self):
        return self.orientation


    def get_velocity(self):
        return self.velocity


    def set_orientation(self, orientation):
        self.orientation = orientation


    def set_velocity(self, velocity):
        self.velocity = velocity


    def __repr__(self):
        return 'x: %s, y: %s, orientation: %s, velocity: %s\n' % (self.x, self.y, self.orientation, self.velocity)


class Pitch_Object(Vector):
    '''
    A class that describes an abstract pitch object
    '''

    def __init__(self, object_id, x, y, angle, velocity, width, length, height):
        super(Pitch_Object, self).__init__(x, y, angle, velocity)
        self.id = object_id
        self.dimensions = (width, length, height)


    def get_id(self):
        return self.id


    def __repr__(self):
        return ('x: %s\ny: %s\norientation: %s\nvelocity: %s\nid: %s\ndimensions: %s\n' %
                (self.x, self.y, self.orientation, self.velocity, self.id, self.dimensions))


class Pitch:
    '''
    Class that describes the pitch
    '''


    def __init__(self):
        config_file = open('../vision/calibrate.json', 'r')
        config_json = load(config_file)
        config_file.close()
        # Getting the zones:
        self.zones = []
        self.zones.append(Polygon(config_json['Zone_0']))
        self.zones.append(Polygon(config_json['Zone_1']))
        self.zones.append(Polygon(config_json['Zone_2']))
        self.zones.append(Polygon(config_json['Zone_3']))


    def is_within_bounds(self, robot, point):
    # Checks whether the position/point planned for the robot is reachable:
        zone = self.zones[robot.zone]
        zone_coords = array([[point.x, point.y] for point in zone.points])
        return pointPolygonTest(zone_coords, (point.x, point.y), False)


    def __repr__(self):
        return str(self.zones)


class Robot(Pitch_Object):


    def __init__(self, robot_id, zone, x, y, angle, velocity, width=ROBOT_WIDTH, length=ROBOT_LENGTH, height=ROBOT_HEIGHT):
        super(Robot, self).__init__(robot_id, x, y, angle, velocity, width, length, height)
        self.zone = zone
        self.possession = False


    def get_zone(self):
        return self.zone


    def get_possession(self):
        return self.possession


    def set_possession(self, possession):
        self.possession = possession


    def turn(r):
        pass

    def move(self, s):
        pass


class Ball(Pitch_Object):


    def __init__(self, ball_id, x, y, velocity, width=BALL_WIDTH, length=BALL_LENGTH, height=BALL_HEIGHT):
        super(Ball, self).__init__(ball_id, x, y, 0, velocity, width, length, height)


class Goal(Pitch_Object):


    def __init__(self, goal_id, zone, x, y, angle, velocity, width=GOAL_WIDTH, length=GOAL_LENGTH, height=GOAL_HEIGHT):
        super(Goal, self).__init__(goal_id, x, y, angle, 0, width, length, height)
        self.zone = zone


    def get_zone(self):
        return self.zone