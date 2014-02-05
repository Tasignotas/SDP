import sys
from planning.models import Vector


LAG = 0


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
			new_vector_dict[name] = self.analyze_ball(vec) if name == 'ball' else self.analyze_robot(vec)
		return new_vector_dict


	def analyze_ball(self, current_vec):
		pass


	def analyze_robot(self, current_vec):
		pass