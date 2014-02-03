from math import cos, atan, hypot
from Polygon import cPolygon
from json import load
from numpy import array
from cv2 import pointPolygonTest
from connection import *
from nxt.motor import *


ROBOT_LENGTH = 20
ROBOT_WIDTH = 20
ROBOT_HEIGHT = 10


ROBOT_MOTOR_POWER = 128
ROBOT_MOTOR_L = PORT_B
ROBOT_MOTOR_R = PORT_C


BALL_LENGTH = 5
BALL_WIDTH = 5
BALL_HEIGHT = 5
BALL_POSSESSION_THRESHOLD = 12.5


GOAL_LENGTH = 1
GOAL_WIDTH = 60
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


    def get_dimensions(self):
        return self.dimensions


    def get_polygon(self):
        x, y = self.get_position()
        angle = self.get_orientation()
        (width, length, height) = self.get_dimensions()
        diagonal = hypot(length / 2, width / 2)
        arc = atan(length / width)
        front_left_corner = (x + (diagonal * cos(angle - arc)))
        front_right_corner = (x + (diagonal * cos(angle + arc)))
        back_left_corner = (x + (diagonal * cos(((angle + 180) % 360) + arc)))
        back_right_corner = (x + (diagonal * cos(((angle + 180) % 360) - arc)))
        return (front_left_corner, front_right_corner, back_left_corner, back_right_corner)


    def __repr__(self):
        return ('x: %s\ny: %s\norientation: %s\nvelocity: %s\nid: %s\ndimensions: %s\n' %
                (self.x, self.y, self.orientation, self.velocity, self.id, self.dimensions))


class Pitch:
    '''
    Class that describes the pitch
    '''


    def __init__(self, config):
        config_file = open(config, 'r')
        config_json = load(config_file)
        config_file.close()
        # Getting the zones:
        self.zones = []
        self.zones.append(cPolygon.Polygon(config_json['Zone_0'],))
        self.zones.append(cPolygon.Polygon(config_json['Zone_1']))
        self.zones.append(cPolygon.Polygon(config_json['Zone_2']))
        self.zones.append(cPolygon.Polygon(config_json['Zone_3']))


    def is_within_bounds(self, robot, point):
    # Checks whether the position/point planned for the robot is reachable:
        zone = self.zones[robot.zone]
        zone_coordinates = array([[point.x, point.y] for point in zone.points])
        return


    def __repr__(self):
        return str(self.zones)


class Robot(Pitch_Object):


    def __init__(self, robot_id, zone, x, y, angle, velocity, width, length, height):
        super(Robot, self).__init__(robot_id, x, y, angle, velocity, width, length, height)
        self.zone = zone


    def get_zone(self):
        return self.zone


    def get_possession(self, ball):
        delta_x = self.get_position()[0] - ball.get_position()[0]
        delta_y = self.get_position()[1] - ball.get_position()[1]
        delta_h = hypot(delta_x, delta_y)
        delta_angle = abs(self.get_orientation() - ball.get_orientation())
        return (delta_h < BALL_POSSESSION_THRESHOLD) & (delta_angle == 180)


    def get_kick_path(self, target):
    # Return a polygon representing the path of a ball being kicked
        robot_polygon = self.get_polygon()
        target_polygon = target.get_polygon()
        return (robot_polygon[0], robot_polygon[1], target_polygon[0], target_polygon[1])


class AwayRobot(Robot):


    def __init__(self, robot_id, zone, width=ROBOT_WIDTH, length=ROBOT_LENGTH, height=ROBOT_HEIGHT):
        super(AwayRobot, self).__init__(robot_id, zone, 0, 0, 0, 0, width, length, height)


class HomeRobot(Robot):


    def __init__(self, robot_id, zone, width=ROBOT_WIDTH, length=ROBOT_LENGTH, height=ROBOT_HEIGHT):
        super(HomeRobot, self).__init__(robot_id, zone, 0, 0, 0, 0, width, length, height)
        self.connection = Connection(robot_id)
        self.brick = self.connection.brick
        self.motor_l = Motor(self.brick, ROBOT_MOTOR_L)
        self.motor_r = Motor(self.brick, ROBOT_MOTOR_R)
        self.motor_sync = SynchronizedMotors(self.motor_l, self.motor_r, 1)


    def do_turn(self, angle_delta):
        angle_multiplier = angle_delta * 10
        self.motor_l.turn(ROBOT_MOTOR_POWER, angle_multiplier)
        self.motor_r.turn(-ROBOT_MOTOR_POWER, angle_multiplier)


    def do_move(self, displacement):
        displacement_multiplier = displacement * 10
        self.motor_sync.turn(ROBOT_MOTOR_POWER, displacement_multiplier)


    def do_kick(self, force):
        pass


class Ball(Pitch_Object):


    def __init__(self, ball_id, width=BALL_WIDTH, length=BALL_LENGTH, height=BALL_HEIGHT):
        super(Ball, self).__init__(ball_id, 0, 0, 0, 0, width, length, height)


class Goal(Pitch_Object):


    def __init__(self, goal_id, zone, x, y, angle, width=GOAL_WIDTH, length=GOAL_LENGTH, height=GOAL_HEIGHT):
        super(Goal, self).__init__(goal_id, x, y, angle, 0, width, length, height)
        self.zone = zone


    def get_zone(self):
        return self.zone