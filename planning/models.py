

from json import load
from Polygon.cPolygon import Polygon
from Polygon.Utils import pointList
from math import atan, cos, sin, hypot, pi


ROBOT_LENGTH = 20
ROBOT_WIDTH = 20
ROBOT_HEIGHT = 10


BALL_LENGTH = 5
BALL_WIDTH = 5
BALL_HEIGHT = 5
BALL_POSSESSION_THRESHOLD = 12.5

GOAL_LENGTH = 60
GOAL_WIDTH = 1
GOAL_HEIGHT = 10


class Coordinate(object):


    def __init__(self, x, y):
        self._x = x
        self._y = y


    def get_x(self):
        return self._x


    def get_y(self):
        return self._y


    def set_x(self, x):
        self._x = x if x else self._x


    def set_y(self, y):
        self._y = y if y else self._y


    def __repr__(self):
        return 'x: %s, y: %s\n' % (self._x, self._y)


class Vector(Coordinate):


    def __init__(self, x, y, angle, velocity):
        super(Vector, self).__init__(x, y)
        self._angle = angle
        self._velocity = velocity


    def get_angle(self):
        return self._angle


    def get_velocity(self):
        return self._velocity


    def set_angle(self, angle):
        self._angle = angle if angle else self._angle


    def set_velocity(self, velocity):
        self._velocity = velocity if velocity else self._velocity


    def __repr__(self):
        return ('x: %s, y: %s, angle: %s, velocity: %s\n' %
                (self.get_x(), self.get_y(),
                 self._angle, self._velocity))


class Pitch_Object(object):
    '''
    A class that describes an abstract pitch object
    '''

    def __init__(self, x, y, angle, velocity, width, length, height):
        self._vector = Vector(x, y, angle, velocity)
        self._dimensions = (width, length, height)


    def get_dimensions(self):
        return self._dimensions


    def get_angle(self):
        return self._vector.get_angle()


    def get_velocity(self):
        return self._vector.get_velocity()


    def get_x(self):
        return self._vector.get_x()


    def get_y(self):
        return self._vector.get_y()


    def get_position_shift(self, d, theta):
        angle = self._vector.get_angle()
        x_shift = self._vector.get_x() + (d * cos(theta + angle))
        y_shift = self._vector.get_x() + (d * sin(theta + angle))
        return (x_shift, y_shift)


    def get_vector(self):
        return self._vector


    def set_vector(self, vector):
        self._vector.set_angle(vector.get_angle())
        self._vector.set_velocity(vector.get_velocity())
        self._vector.set_x(vector.get_x())
        self._vector.set_y(vector.get_y())


    def get_polygon(self):
        # This returns the Polygon (boundary box) around the object:
        (width, length, height) = self.get_dimensions()
        d = hypot(width / 2, length / 2)
        theta = atan((width * 0.5)/(height * 0.5))
        back_right = self.get_position_shift(d, theta-(pi/2))
        back_left = self.get_position_shift(d, -theta-(pi/2))
        front_right = self.get_position_shift(d, -theta+(pi/2))
        front_left = self.get_position_shift(d, theta+(pi/2))
        return Polygon((front_left, front_right, back_left, back_right))


    def __repr__(self):
        return ('x: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self.get_x(), self.get_y(),
                 self.get_angle(), self.get_velocity(), self.get_dimensions()))


class Robot(Pitch_Object):


    def __init__(self, zone, x, y, angle, velocity, width=ROBOT_WIDTH, length=ROBOT_LENGTH, height=ROBOT_HEIGHT):
        super(Robot, self).__init__(x, y, angle, velocity, width, length, height)
        self._zone = zone
        self._possession = False


    def get_zone(self):
        return self._zone


    def get_possession(self, ball):
        # Checks if the robot has possession:
        check_angle = abs(self.get_angle() - ball.get_angle()) <= pi / 4
        displacement = hypot(self.get_x() - ball.get_x(), self.get_x() - ball.get_x())
        check_displacement = displacement <= BALL_POSSESSION_THRESHOLD
        return (check_angle and check_displacement)


    def get_pass_path(self, robot):
        robot_poly = self.get_polygon()
        target_poly = self.get_polygon()
        return Polygon(robot_poly[0], robot_poly[1], target_poly[0], target_poly[1])


    def get_shoot_paths(self, goal, path_width=BALL_WIDTH):
        robot_poly = self.get_polygon()
        goal_poly = self.get_polygon()
        path_min = goal_poly[0] if goal_poly[0][1] <= goal_poly[1][1] else goal_poly[1]
        path_max = goal_poly[0] if goal_poly[0][1] > goal_poly[1][1] else goal_poly[1]
        shoot_paths = []
        while path_min[1] <= path_max[1] - path_width:
            y_max = path_min
            y_max[1] = y_max[1] + path_width
            shoot_paths.append(Polygon(robot_poly[0], robot_poly[1], path_min, y_max))
            path_min = y_max
        return shoot_paths


    def get_kick_angle(self, kick_path):
        # Check for angle change necessary for a clear kick
        pass


    def __repr__(self):
        return ('zone: %s\nx: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self._zone, self.get_x(), self.get_y(),
                 self.get_angle(), self.get_velocity(), self.get_dimensions()))


class Ball(Pitch_Object):


    def __init__(self, x, y, velocity, width=BALL_WIDTH, length=BALL_LENGTH, height=BALL_HEIGHT):
        super(Ball, self).__init__(x, y, 0, velocity, width, length, height)


class Goal(Pitch_Object):


    def __init__(self, zone, x, y, angle, velocity, width=GOAL_WIDTH, length=GOAL_LENGTH, height=GOAL_HEIGHT):
        super(Goal, self).__init__(x, y, angle, 0, width, length, height)
        self._zone = zone


    def get_zone(self):
        return self._zone


    def __repr__(self):
        return ('zone: %s\nx: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self._zone, self.get_dimensions()[0], self.get_dimensions()[1],
                 self.get_angle(), self.get_velocity(), self.get_dimensions()))

class Pitch:
    '''
    Class that describes the pitch
    '''


    def __init__(self):
        config_file = open('vision/calibrate.json', 'r')
        config_json = load(config_file)
        config_file.close()
        # Getting the zones:
        self._zones = []
        self._zones.append(Polygon(config_json['Zone_0']))
        self._zones.append(Polygon(config_json['Zone_1']))
        self._zones.append(Polygon(config_json['Zone_2']))
        self._zones.append(Polygon(config_json['Zone_3']))
        self._width = max([max([point[0] for point in pointList(zone)]) for zone in self._zones])
        self._height = max([max([point[1] for point in pointList(zone)]) for zone in self._zones])


    def is_within_bounds(self, robot, point):
    # Checks whether the position/point planned for the robot is reachable:
        zone = self._zones[robot.get_zone()]
        return zone.isInside(point.get_x(), point.get_y())


    def get_width(self):
        return self._width


    def get_height(self):
        return self._height


    def __repr__(self):
        return str(self._zones)


class World:
    '''
    This class describes the environment
    '''


    def __init__(self, our_side):
        assert our_side in ['left', 'right']
        self._pitch = Pitch()
        self.our_side = our_side
        self.their_side = 'left' if our_side == 'right' else 'right'
        self._ball = Ball(0, 0, 0, 0)
        self._robots = []
        self._robots.append(Robot(0, 0, 0, 0, 0))
        self._robots.append(Robot(1, 0, 0, 0, 0))
        self._robots.append(Robot(2, 0, 0, 0, 0))
        self._robots.append(Robot(3, 0, 0, 0, 0))
        self._goals = []
        self._goals.append(Goal(0, 0, self._pitch.get_height() / 2.0, 0, 0))
        self._goals.append(Goal(3, self._pitch.get_width(), self._pitch.get_height() / 2.0, 0, 0))


    def get_our_attacker(self):
        return self._robots[2] if self.our_side == 'left' else self._robots[1]


    def get_their_attacker(self):
        return self._robots[1] if self.our_side == 'left' else self._robots[2]


    def get_our_defender(self):
        return self._robots[0] if self.our_side == 'left' else self._robots[3]


    def get_their_defender(self):
        return self._robots[3] if self.our_side == 'left' else self._robots[0]


    def get_ball(self):
        return self._ball


    def get_our_goal(self):
        return self._goals[0] if self.our_side == 'left' else self._goals[1]


    def get_their_goal(self):
        return self._goals[1] if self.our_side == 'left' else self._goals[2]


    def get_pitch(self):
        return self._pitch


    def update_positions(self, position_dict):
        ''' This method will update the positions of the pitch objects
            that it gets passed by the vision system '''
        if position_dict['our_attacker']:
            self.get_our_attacker().set_vector(position_dict['our_attacker'])
        if position_dict['their_attacker']:
            self.get_their_attacker().set_vector(position_dict['their_attacker'])
        if position_dict['our_defender']:
            self.get_our_defender().set_vector(position_dict['our_defender'])
        if position_dict['their_defender']:
            self.get_their_defender().set_vector(position_dict['their_defender'])
        if position_dict['ball']:
            self.get_ball().set_vector(position_dict['ball'])
