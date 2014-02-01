
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


    def get_coordinates(self):
        return self.points


    def __repr__(self):
        return ''.join([point.__repr__() for point in self.points])



class Vector(Coordinate):


    def __init__(self, x, y, angle, velocity):
        super(Vector, self).__init__(x, y)
        self.angle = angle
        self.velocity = velocity


    def get_angle(self):
        return self.angle


    def get_velocity(self):
        return self.velocity


    def set_angle(self, angle):
        self.angle = angle


    def set_velocity(self, velocity):
        self.velocity = velocity


    def __repr__(self):
        return 'x: %s, y: %s, angle: %s, velocity: %s\n' % (self.x, self.y, self.angle, self.velocity)


class Pitch_Object(Vector):
    '''
    A class that describes an abstract pitch object
    '''

    def __init__(self, x, y, angle, velocity, width, length, height):
        super(Pitch_Object, self).__init__(x, y, angle, velocity)
        self.dimensions = (width, length, height)


    def __repr__(self):
        return ('x: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self.x, self.y, self.angle, self.velocity, self.dimensions))




class Robot(Pitch_Object):


    def __init__(self, zone, x, y, angle, velocity, width=ROBOT_WIDTH, length=ROBOT_LENGTH, height=ROBOT_HEIGHT):
        super(Robot, self).__init__(x, y, angle, velocity, width, length, height)
        self.zone = zone
        self.possession = False


    def get_zone(self):
        return self.zone


    def get_possession(self):
        return self.possession


    def set_possession(self, possession):
        self.possession = possession


    def __repr__(self):
        return ('zone: %s\nx: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self.zone, self.x, self.y, self.angle, self.velocity, self.dimensions))


class Ball(Pitch_Object):


    def __init__(self, x, y, velocity, width=BALL_WIDTH, length=BALL_LENGTH, height=BALL_HEIGHT):
        super(Ball, self).__init__(x, y, 0, velocity, width, length, height)


class Goal(Pitch_Object):


    def __init__(self, zone, x, y, angle, velocity, width=GOAL_WIDTH, length=GOAL_LENGTH, height=GOAL_HEIGHT):
        super(Goal, self).__init__(x, y, angle, 0, width, length, height)
        self.zone = zone


    def get_zone(self):
        return self.zone


    def __repr__(self):
        return ('zone: %s\nx: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self.zone, self.x, self.y, self.angle, self.velocity, self.dimensions))

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
        self.width = max([max([point.get_position()[0] for point in zone.get_coordinates()]) for zone in self.zones])
        self.height = max([max([point.get_position()[1] for point in zone.get_coordinates()]) for zone in self.zones])


    def is_within_bounds(self, robot, point):
    # Checks whether the position/point planned for the robot is reachable:
        zone = self.zones[robot.zone]
        zone_coords = array([[point.x, point.y] for point in zone.points])
        return pointPolygonTest(zone_coords, (point.x, point.y), False)


    def get_width(self):
        return self.width


    def get_height(self):
        return self.height


    def __repr__(self):
        return str(self.zones)


class World:
    '''
    This class describes the environment
    '''


    def __init__(self, our_color, our_side):
        self.pitch = Pitch()
        self.our_color = our_color
        self.our_side = our_side
        self.their_color = 'yellow' if our_color == 'blue' else 'blue'
        self.their_side = 'left' if our_side == 'right' else 'right'
        self.ball = Ball(0, 0, 0, 0)
        self.robots = []
        self.robots.append(Robot(0, 0, 0, 0, 0))
        self.robots.append(Robot(1, 0, 0, 0, 0))
        self.robots.append(Robot(2, 0, 0, 0, 0))
        self.robots.append(Robot(3, 0, 0, 0, 0))
        self.goals = []
        self.goals.append(Goal(0, 0, self.pitch.get_height()/2.0, 0, 0))
        self.goals.append(Goal(3, self.pitch.get_width(), self.pitch.get_height()/2.0, 0, 0))


    def get_our_attacker(self):
        return self.robots[2] if self.our_side == 'left' else self.robots[1]


    def get_their_attacker(self):
        return self.robots[1] if self.our_side == 'left' else self.robots[2]


    def get_our_goalkeeper(self):
        return self.robots[0] if self.our_side == 'left' else self.robots[3]


    def get_their_goalkeeper(self):
        return self.robots[3] if self.our_side == 'left' else self.robots[0]


    def get_ball(self):
        return self.ball


    def get_our_goal(self):
        return self.goals[0] if self.our_side == 'left' else self.goals[1]


    def get_their_goal(self):
        return self.goals[1] if self.our_side == 'left' else self.goals[2]


    def update_positions(position_dict):
        ''' This method will update the positions of the pitch objects
            that it gets passed by the vision system '''
        pass
