import cv2
import numpy as np
from vision import Camera
import tools


FRAME_NAME = 'ConfigureWindow'

WHITE = (255,255,255)
BLACK = (0,0,0)


class Configure:

	def __init__(self, width=640, height=480):
		self.width = width
		self.height = height
		self.camera = cv2.VideoCapture(0)
		self.new_polygon = True
		self.polygon = self.polygons = []
		self.points = []

		self.data = {
			'outline': []
		}

		self.drawing = {
			'outline': [],
			'left': [],
			'left-middle': [],
			'right-middle': [],
			'right': []
		}

		self.colors = {
			'outline': BLACK
		}


	def run(self):
		frame = cv2.namedWindow(FRAME_NAME)

		# Set callback
		cv2.setMouseCallback(FRAME_NAME, self.draw)

		# for i in range(10):
			# state, self.image = self.camera.read()
		# if not image:
		# 	self.stop()
		self.image = cv2.imread('00000001.jpg')
		self.running = True

		self.get_pitch_outline()

		# while self.running:
		# 	cv2.imshow(FRAME_NAME, self.image)
		# 	k = cv2.waitKey(200) & 0xFF
		# 	if k == ord('x'):
		# 		self.stop()
		# 	elif k == ord('q'):
		# 		# Next polygon
		# 		self.new_polygon = True
		# 		self.polygons.append(self.polygon)
		# 		self.polygon = []
		# 		self.draw_polygon()

		# 	elif k == ord('q'):
		# 		self.next = True
		#
		cv2.waitKey(0)
		cv2.waitKey(0)

		cv2.destroyAllWindows()

	def get_pitch_outline(self):
		print "DRAW OUTLINE and continue by pressin 'q'"
		k = True
		self.drawing = 'outline'

		while k != ord('q'):
			cv2.imshow(FRAME_NAME, self.image)
			k = cv2.waitKey(100) & 0xFF

		points = np.array(self.data[self.drawing], np.int32).reshape((-1,1,2))
		cv2.polylines(self.image, [points], True, BLACK)
		cv2.imshow(FRAME_NAME, self.image)
		cv2.waitKey(0)

		mask = self.image.copy()
		size = tools.find_crop_coordinates(self.image, self.data[self.drawing])

		points = np.array(self.data[self.drawing], np.int32)
		mask = self.image.copy()
		cv2.fillConvexPoly(mask, points, BLACK)

		hsv = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(hsv, (0, 0, 0), (0, 0, 0))

		self.image = cv2.bitwise_and(self.image, self.image, mask= mask)

		self.image = self.image[size[2]:size[3], size[0]:size[1]]

		cv2.imshow(FRAME_NAME, self.image)

	def stop(self):
			self.running = False
			print 'Exiting..'

	def draw(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			color = self.colors[self.drawing]
			cv2.circle(self.image, (x, y), 2, color, -1)
			self.data[self.drawing].append((x,y))


c = Configure()
c.run()




