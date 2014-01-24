import cv2
from detect_field import *

LAB_LOWER = np.array([30, 115, 115])
LAB_HIGHER = np.array([50, 130, 130])

BGR_LOWER = np.array([65, 116, 110])
BGR_HIGHER = np.array([65, 130, 123])
# RGB_LOWER = np.array([100, 100 ,100])
# RGB_HIGHER = np.array([255, 255, 255])

def convertToLab(src='00000001.jpg'):
	img =  cv2.imread(src) 
	conv = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
	cv2.imwrite('lab.jpg', conv )

def mask():
	img = cv2.imread('lab.jpg')
	# print img
	# x = mask_field(img, BGR_LOWER, BGR_HIGHER)
	x = mask_field(img, LAB_LOWER, LAB_HIGHER)
	view_image(x)

mask()