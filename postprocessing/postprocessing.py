import sys
from planning.models import Vector
from math import atan, pi, sqrt, radians



class Postprocessing(object):


	def __init__(self):
		self._vectors = {}
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
			self._vectors[name] = [vec] + self._vectors[name]
			if len(self._vectors[name]) > 5:
				self._vectors[name].pop()
			new_vector_dict[name] = self.analyze_ball(name, vec) if name == 'ball' else self.analyze_robot(name, vec)
		return new_vector_dict


	def analyze_ball(self, key, current_vec):
		# This method calculates the angle and the velocity of the ball.
		# TODO: make it able to PREDICT angle, speed and the location by specified lag.
		# Getting the last two successful ball captures:
		velocity = None
		angle = None
		prev_pos = [(idx, val.get_x(), val.get_y()) for (idx, val) in enumerate(self._vectors[key]) if val]
		if len(prev_pos) > 1:
			delta_x = None if (prev_pos[0][1] == None) or (prev_pos[1][1] == None) else prev_pos[0][1] - prev_pos[1][1]
			delta_y = None if (prev_pos[0][2] == None) or (prev_pos[1][2] == None) else prev_pos[0][2] - prev_pos[1][2]
			ratio = delta_y/delta_x if delta_x and delta_y else (float('inf') if delta_y > 0 else float('-inf'))
			angle = atan(ratio) if not(ratio == None) else None
			velocity = None if (delta_x == None) or (delta_y == None) else sqrt(delta_x**2 + delta_y**2)/(prev_pos[1][0] - prev_pos[0][0])
		return Vector(current_vec.get_x(), current_vec.get_y(), angle, velocity)


	def analyze_robot(self, key, current_vec):
		# This method calculates the angle and the velocity of the robot.
		# TODO: make it able to PREDICT angle, speed and the location by specified lag.
		velocity = None
		angle = current_vec.get_angle() if not(current_vec.get_angle() == None) else None
		prev_pos = [(idx, val.get_x(), val.get_y()) for (idx, val) in enumerate(self._vectors[key]) if val]
		if len(prev_pos) > 1:
			delta_x = None if (prev_pos[0][1] == None) or (prev_pos[1][1] == None) else prev_pos[0][1] - prev_pos[1][1]
			delta_y = None if (prev_pos[0][2] == None) or (prev_pos[1][2] == None) else prev_pos[0][2] - prev_pos[1][2]
			velocity = None if (delta_x == None) or (delta_y == None) else sqrt(delta_x**2 + delta_y**2)/(prev_pos[1][0] - prev_pos[0][0])
		return Vector(current_vec.get_x(), current_vec.get_y(), angle, velocity)
