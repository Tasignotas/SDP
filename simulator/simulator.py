import cv2


class Simulator(object):
	
	def __init__(self):
		self.clean = self._get_image('blabla')


	def run(self):
		"""
		Run the simulation.
		"""
		self._initialize()

	def _initialize(self):
		"""
		Display an image and make the user select points for the
		starting locations of the robots.

		Should draw circles/squares in the locations selected to
		provide visual feedback

		Params:
			?? May decide to load this optionally from a file ??

		returns None
		"""
		pass

	def _get_image(self, path):
		"""
		Get the basic pitch image for the simulator

		Params:
			[String] path		path to the image, relative to run_simulator.py

		Returns:
			cv2 frame
		"""
		pass

