import cv2
import numpy as np
import tools
import cPickle

FRAME_NAME = 'ConfigureWindow'

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

with open('calibrations/undistort.txt','rb') as fp:
	distort_data = cPickle.load(fp)
distort_data = distort_data[0]

NCMATRIX = distort_data['new_camera_matrix']
CMATRIX = distort_data['camera_matrix']
DIST = distort_data['dist']


class Configure:

	def __init__(self, width=640, height=480):
		self.width = width
		self.height = height
		self.camera = cv2.VideoCapture(0)
		self.new_polygon = True
		self.polygon = self.polygons = []
		self.points = []

		keys = ['outline', 'Zone_0', 'Zone_1', 'Zone_2', 'Zone_3']
		self.data = self.drawing = {}

		# Create keys
		for key in keys:
			self.data[key] = []
			self.drawing[key] = []

		self.color = RED


	def run(self, camera=False):
		frame = cv2.namedWindow(FRAME_NAME)

		# Set callback
		cv2.setMouseCallback(FRAME_NAME, self.draw)

		if camera:
			cap = cv2.VideoCapture(0)
			for i in range(10):
				status, image = cap.read()
		else:
			image = cv2.imread('00000001.jpg')

		self.image = cv2.undistort(image, CMATRIX, DIST, None, NCMATRIX)

		# Get various data about the image from the user
		self.get_pitch_outline()

		self.get_zone('Zone_0', 'draw LEFT Defender')
		self.get_zone('Zone_1', 'draw LEFT Attacker')
		self.get_zone('Zone_2', 'draw RIGHT Attacker')
		self.get_zone('Zone_3', 'draw RIGHT Defender')

		print 'Press any key to finish.'
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		# Write out the data
		self.dump('calibrate.json', self.data)

	def reshape(self):
		return np.array(self.data[self.drawing], np.int32).reshape((-1,1,2))

	def draw_poly(self, points):
		cv2.polylines(self.image, [points], True, self.color)
		cv2.imshow(FRAME_NAME, self.image)

	def get_zone(self, key, message):
		print '%s. %s' % (message, "Continue by pressing q")
		self.drawing, k = key, True

		while k != ord('q'):
			cv2.imshow(FRAME_NAME, self.image)
			k = cv2.waitKey(100) & 0xFF

		self.draw_poly(self.reshape())

	def get_pitch_outline(self):
		"""
		Let user select points that corespond to the pitch outline.
		End selection by pressing 'q'.
		Result is masked and cropped.
		"""
		self.get_zone('outline', 'Draw the outline of the pitch. Contine by pressing \'q\'')

		# Setup black mask to remove overflows
		self.image = tools.mask_pitch(self.image, self.data[self.drawing])

		# Get crop size based on points
		size = tools.find_crop_coordinates(self.image, self.data[self.drawing])
		# Crop
		self.image = self.image[size[2]:size[3], size[0]:size[1]]

		cv2.imshow(FRAME_NAME, self.image)

	def draw(self, event, x, y, flags, param):
		"""
		Callback for events
		"""
		if event == cv2.EVENT_LBUTTONDOWN:
			color = self.color
			cv2.circle(self.image, (x-1, y-1), 2, color, -1)
			self.data[self.drawing].append((x,y))

	def dump(self, filename='calibrate.json', data={}):
		tools.write_json(filename, data)


c = Configure()
c.run(camera=True)
