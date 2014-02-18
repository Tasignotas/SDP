import sys
from planning.models import Vector
from math import atan2, pi, hypot


class Postprocessing(object):

	def __init__(self):
		self._vectors = {}
		self._vectors['ball']= Vector(0, 0, 0, 0)
		self._vectors['our_attacker'] = Vector(0, 0, 0, 0)
		self._vectors['their_attacker'] = Vector(0, 0, 0, 0)
		self._vectors['our_defender'] = Vector(0, 0, 0, 0)
		self._vectors['their_defender'] = Vector(0, 0, 0, 0)

	def analyze(self, vector_dict):
		'''
		This method analyzes current positions and previous object vector.
		'''
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
		if info['x'] and info['y']:
			delta_x = info['x'] - self._vectors['ball'].x
			delta_y = info['y'] - self._vectors['ball'].y
			velocity = hypot(delta_y, delta_x)
			angle = atan2(delta_y, delta_x) % 2*pi
			self_vectors['ball'] = Vector(info['x'], info['y'], angle, velocity)
			return Vector(info['x'], info['y'], angle, velocity)
		else:
			return Vector(self._vectors['ball'].x, self._vectors['ball'].y, self._vectors['ball'].angle, self._vectors['ball'].velocity)

	def analyze_robot(self, key, current_vec):
		'''
		This method calculates the angle and the velocity of the robot.
		'''
		if info['x'] and info['y'] and info['angle']:
			delta_x = info['x'] - self._vectors[key].x
			delta_y = info['y'] - self._vectors[key].y
			velocity = hypot(delta_y, delta_x)
			self_vectors[key] = Vector(info['x'], info['y'], info['angle'], velocity)
			return Vector(info['x'], info['y'], info['angle'], velocity)
		else:
			return Vector(self._vectors[key].x, self._vectors[key].y, self._vectors[key].angle, self._vectors[key].velocity)		
