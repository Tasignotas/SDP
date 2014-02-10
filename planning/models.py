
from numpy import roots
from json import load
from Polygon.cPolygon import Polygon
from Polygon.Utils import pointList
from math import pow, cos, sin, hypot, pi, acos, atan2

# Width measures the front and back of an object
# Length measures along the sides of an object

ROBOT_WIDTH = 20
ROBOT_LENGTH = 20
ROBOT_HEIGHT = 10

ROBOT_VELOCITY = 127

BALL_WIDTH = 5
BALL_LENGTH = 5
BALL_HEIGHT = 5

BALL_POSS_DIST = 12.5
BALL_POSS_ANGLE = pi / 4

GOAL_WIDTH = 60
GOAL_LENGTH = 1
GOAL_HEIGHT = 10


class Coordinate(object):


    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._dx = 0
        self._dy = 0


    def get_x(self):
        return self._x


    def get_y(self):
        return self._y


    def get_dx(self):
        return self._dx


    def get_dy(self):
        return self._dy


    def set_x(self, x):
        self._dx = x - self._x if not(x is None) else 0
        self._x = x if not(x is None) else self._x


    def set_y(self, y):
        self._dy = y - self._y if not(y is None) else 0
        self._y = y if not(y is None) else self._y


    def __repr__(self):
        return 'x: %s, y: %s\n' % (self._x, self._y)


class Vector(Coordinate):


    def __init__(self, x, y, angle, velocity):
        super(Vector, self).__init__(x, y)
        self._angle = angle
        self._velocity = velocity
        self._dr = 0
        self._dv = 0


    def get_angle(self):
        return self._angle


    def get_velocity(self):
        return self._velocity


    def get_dr(self):
        return self._dr


    def get_dv(self):
        return self._dv


    def set_angle(self, angle):
        self._dr = angle - self.get_angle() if not (angle == None) else 0
        self._angle = angle if not (angle == None) else self._angle


    def set_velocity(self, velocity):
        self._dv = velocity - self.get_velocity() if not (velocity == None) else 0
        self._velocity = velocity if not (velocity == None) else self._velocity


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


    def get_vector(self):
        return self._vector


    def set_vector(self, vector):
        self._vector.set_angle(vector.get_angle())
        self._vector.set_velocity(vector.get_velocity())
        self._vector.set_x(vector.get_x())
        self._vector.set_y(vector.get_y())


    def get_polygon_point(self, d, theta):
        # Get point for drawing polygon around object
        angle = self.get_angle()
        delta_x = self.get_x() + (d * cos(theta + angle))
        delta_y = self.get_y() + (d * sin(theta + angle))
        return delta_x, delta_y


    def get_generic_polygon(self, width, length):
        # Get polygon drawn around a generic object
        dist = hypot(length * 0.5, width * 0.5)
        theta = atan2(length * 0.5, width * 0.5)
        front_left = (self.get_polygon_point(dist, theta))
        front_right = (self.get_polygon_point(dist, -theta))
        back_left = (self.get_polygon_point(dist, -(theta + pi)))
        back_right = (self.get_polygon_point(dist, theta + pi))
        return Polygon((front_left, front_right, back_left, back_right))


    def get_polygon(self):
        # Get polygon drawn around this object
        (width, length, height) = self.get_dimensions()
        self.get_generic_polygon(width, length)


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


    def get_alignment_angle(self, target):
        # Get angle necessary to align the robot with a target
        alignment_angle = target.get_angle() + pi
        delta_angle = alignment_angle - self.get_angle()
        return delta_angle


    def get_possession(self, ball):
        # Get if the robot has possession of the ball
        delta_x = ball.get_x() - self.get_x()
        delta_y = ball.get_y() - self.get_y()
        delta_angle = ball.get_angle() - self.get_angle()
        check_angle = abs(delta_angle) <= BALL_POSS_ANGLE
        check_displacement = hypot(delta_x, delta_y) <= BALL_POSS_DIST
        return check_angle and check_displacement


    def get_path_to_point(self, x, y):
        # Get path to a given point (x, y)
        delta_x = x - self.get_x()
        delta_y = y - self.get_y()
        displacement = hypot(delta_x, delta_y)
        theta = self.get_angle() - atan2(delta_y, delta_x)
        return displacement, theta


    def get_stationary_ball(self, ball):
        # Get path to grab stationary ball
        return self.get_path_to_point(ball.get_x(), ball.get_y())


    def get_moving_ball(self, ball):
        # Get path to intercept moving ball
        delta_x = ball.get_x() - self.get_x()
        delta_y = ball.get_y() - self.get_y()
        ball_v_x = ball.get_velocity() * cos(ball.get_angle())
        ball_v_y = ball.get_velocity() * sin(ball.get_angle())
        a = pow(ball.get_velocity(), 2) - pow(self.get_velocity(), 2)
        b = 2 * ((ball_v_x * delta_x) + (ball_v_y * delta_y))
        c = pow(delta_x, 2) + pow(delta_y, 2)
        t = max(roots([a, b, c]))
        x = ball.get_x() + (ball_v_x * t)
        y = ball.get_y() + (ball_v_y * t)
        return self.get_path_to_point(x, y)


    def get_pass_path(self, target):
        # Get path for passing ball between two robots
        robot_poly = self.get_polygon()
        target_poly = target.get_polygon()
        return Polygon(robot_poly[0], robot_poly[1], target_poly[0], target_poly[1])


    def get_shoot_path(self, goal):
        # Get closest possible shooting path between the robot and the goal
        robot_poly = self.get_generic_polygon(BALL_WIDTH, self.get_dimensions()[1])
        goal_poly = self.get_polygon()
        goal_top = goal_poly[0] if goal_poly[0][0] == 0 else goal_poly[1]
        goal_bottom = goal_poly[1] if goal_poly[0][0] == 0 else goal_poly[0]
        robot_top = robot_poly[1] if (pi / 2) < self.get_angle() < ((3*pi) / 2) else robot_poly[0]
        robot_bottom = robot_poly[0] if (pi / 2) < self.get_angle() < ((3*pi) / 2) else robot_poly[1]
        path_top = (goal_top[0], robot_top[1])
        path_bottom = (goal_bottom[0], robot_bottom[1])
        if robot_top[1] > goal_top[1]:
            path_top = (goal_top[0], goal_top[1])
            path_bottom = (goal_bottom[0], goal_top[1] - BALL_WIDTH)
        if robot_bottom[1] < goal_bottom[1]:
            path_top = (goal_top[0], goal_bottom[1] + BALL_WIDTH)
            path_bottom = (goal_bottom[0], goal_bottom[1])
        path_left = path_top if path_top[0] == 0 else path_bottom
        path_right = path_bottom if path_top[0] == 0 else path_top
        robot_left = robot_bottom if (pi / 2) < self.get_angle() < ((3*pi) / 2) else robot_top
        robot_right = robot_top if (pi / 2) < self.get_angle() < ((3*pi) / 2) else robot_bottom
        return Polygon((robot_left, robot_right, path_left, path_right))


    def get_path_alignment(self, path):
        # Get the angle alignment necessary for a clear kick
        robot_midpoint = ((path[0][0] + path[1][0]) * 0.5, (path[0][1] + path[1][1]) * 0.5)
        target_midpoint = ((path[2][0] + path[3][0]) * 0.5, (path[2][3] + path[1][1]) * 0.5)
        delta_x = target_midpoint[0] - robot_midpoint[0]
        delta_y = target_midpoint[1] - robot_midpoint[1]
        theta = atan2(delta_y, delta_x)
        delta_angle = theta - self.get_angle()
        return delta_angle


    def __repr__(self):
        return ('zone: %s\nx: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self._zone, self.get_x(), self.get_y(),
                 self.get_angle(), self.get_velocity(), self.get_dimensions()))


class Ball(Pitch_Object):


    def __init__(self, x, y, angle, velocity):
        super(Ball, self).__init__(x, y, angle, velocity, BALL_WIDTH, BALL_LENGTH, BALL_HEIGHT)


class Goal(Pitch_Object):


    def __init__(self, zone, x, y, angle):
        super(Goal, self).__init__(x, y, angle, 0, GOAL_WIDTH, GOAL_LENGTH, GOAL_HEIGHT)
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
        config_file = open('../vision/calibrate.json', 'r')
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
        self._goals.append(Goal(0, 0, (self._pitch.get_height() - GOAL_WIDTH) * 0.5, 0))
        self._goals.append(Goal(3, self._pitch.get_width(), (self._pitch.get_height() - GOAL_WIDTH) * 0.5, pi))


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
