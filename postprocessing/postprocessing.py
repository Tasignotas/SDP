import sys
from planning.models import Vector


LAG = 0
ANGLE_WEIGHTS = [0.258, 0.225, 0.196, 0.17, 0.148]


class Postprocessing(object):


	def __init__(self):
		self._vectors['ball']= []
		self._vectors['our_attacker'] = []
		self._vectors['their_attacker'] = []
		self._vectors['our_defender'] = []
		self._vectors['their_defender'] = []


	def analyze(self, vector_dict):
		"""
		Method that analyzes current and previous object vectors.
		It adjusts the angle, finds the velocity and predicts the
		value of the vector taking lag into account.
		"""
		new_vector_dict = {}
		for name, vec in vector_dict.iteritems():
			self._vectors[key] = [vec] + self._vectors[key]
			self._vectors[key].pop()
			new_vector_dict[name] = self.analyze_ball(key, vec) if name == 'ball' else self.analyze_robot(key, vec)
		return new_vector_dict


	def analyze_ball(self, key, current_vec):
		# This method calculates the angle and the velocity of the ball.
		# TODO: make it able to PREDICT angle, speed and the location by specified lag.


		return current_vec


	def analyze_robot(self, key, current_vec):
		# This method calculates the angle and the velocity of the robot.
		# TODO: make it able to PREDICT angle, speed and the location by specified lag.
		previous_angles = [v.get_angle() if v else None for v in self._vectors[key]]		
		angle_mult = sum([a if m else 0 for (a, m) in zip(ANGLE_WEIGHTS, previous_angles)])
		if angle_mult:
			angle = sum([(1.0 / angle_mult) * m.get_angle() if m else 0 for (a, m) in zip(ANGLE_WEIGHTS, previous_angles)])
		else:
			angle = None
		
		return Vector(current_vec.get_x(), current_vec.get_y(), angle, velocity)