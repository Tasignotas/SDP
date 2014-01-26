import cv2
import numpy as np
from vision import Camera


FRAME_NAME = 'ConfigureWindow'


class Configure:

	def __init__(self, width=640, height=480):
		self.width = width
		self.height = height
		self.camera = cv2.VideoCapture(0)

		self.points = []
		

	def run(self):
		frame = cv2.namedWindow(FRAME_NAME)

		# Set callback
		cv2.setMouseCallback(FRAME_NAME, self.draw)

		for i in range(10):
			state, self.image = self.camera.read()
		# if not image:
		# 	self.stop()

		self.running = True

		while self.running:
			cv2.imshow(FRAME_NAME, self.image)
			k = cv2.waitKey(200) & 0xFF
			if k == ord('x'):
				self.stop()
			elif k == ord('q'):
				self.next = True


		cv2.destroyAllWindows()

	def stop(self):
			self.running = False

	def draw(self, event, x, y, flags, param):
		
		if event == cv2.EVENT_LBUTTONDOWN:
			if len(self.points) > 0:
				cv2.line(self.image, (x, y), self.points[len(self.points) -1], (0,0,255), 1)
			self.points.append((x,y))


c = Configure()
c.run()




