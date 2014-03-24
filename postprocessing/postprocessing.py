from planning.models import Vector
from copy import deepcopy
from math import atan2, pi, hypot


class Postprocessing(object):

    def __init__(self):
        self._vectors = {}
        self._vectors['ball'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._vectors['our_attacker'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._vectors['their_attacker'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._vectors['our_defender'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._vectors['their_defender'] = {'vec': Vector(0, 0, 0, 0), 'time': 0}
        self._time = 0

    def analyze(self, vector_dict):
        '''
        This method analyzes current positions and previous object vector.
        '''
        self._time += 1
        new_vector_dict = {}
        for name, info in vector_dict.iteritems():
            if name == 'ball':
                new_vector_dict[name] = self.analyze_ball(info)
            else:
                new_vector_dict[name] = self.analyze_robot(name, info)
        return new_vector_dict

    def analyze_ball(self, info):
        '''
        This method calculates the angle and the velocity of the ball.
        '''
        if not(info['x'] is None) and not (info['y'] is None):
            delta_x = info['x'] - self._vectors['ball']['vec'].x
            delta_y = info['y'] - self._vectors['ball']['vec'].y
            velocity = hypot(delta_y, delta_x)/(self._time - self._vectors['ball']['time'])
            angle = atan2(delta_y, delta_x) % (2*pi)
            self._vectors['ball']['vec'] = Vector(info['x'], info['y'], angle, velocity)
            self._vectors['ball']['time'] = self._time
            return Vector(int(info['x']), int(info['y']), angle, velocity)
        else:
            return deepcopy(self._vectors['ball']['vec'])

    def analyze_robot(self, key, info):
        '''
        This method calculates the angle and the velocity of the robot.
        '''
        if not(info['x'] is None) and not(info['y'] is None) and not(info['angle'] is None):

            robot_angle = info['angle']

            delta_x = info['x'] - self._vectors[key]['vec'].x
            delta_y = info['y'] - self._vectors[key]['vec'].y

            # Calculate the angle of the delta vector relative to (1, 0)
            delta_angle = atan2(delta_y, delta_x)
            # Offset the angle if negative, we only want positive values
            delta_angle = delta_angle if delta_angle > 0 else 2 * pi + delta_angle

            velocity = hypot(delta_y, delta_x)/(self._time - self._vectors[key]['time'])

            # Make the velocity negative if the angles are not roughly the same
            if not (-pi / 2 < abs(delta_angle - robot_angle) < pi / 2):
                velocity = -velocity

            self._vectors[key]['vec'] = Vector(info['x'], info['y'], info['angle'], velocity)
            self._vectors[key]['time'] = self._time
            return Vector(info['x'], info['y'], info['angle'], velocity)
        else:
            return deepcopy(self._vectors[key]['vec'])
