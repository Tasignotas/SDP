import cv2
import threading
import time
from tools import *


class Camera(threading.Thread):
	"""
	Threaded wrapper for the camera. Reads in frames from the camera.
	"""

	def __init__(self):
		threading.Thread.__init__(self)
		self.camera = cv2.VideoCapture(0)
		for i in range(10):
			self.frame = self.get_frame()
		self.frame_count = 1
		self.frame_rate = 0
		self.active = True
		self.crop = find_crop_coordinates(self.frame)

	def run(self):
		"""
		Main execution thread. Get frames and store them in the frame variable
		Terminate by calling stop().
		"""
		status, frame = self.get_frame()
		start_time = time.time()
		while self.active:
			status, self.frame = self.get_frame()
			self.frame_count += 1
			self.frame_rate = self.frame_count / (time.time() - start_time)
			print self.frame_rate

	def get_frame(self):
		return self.camera.read()[1]

	def stop():
		self.active = False