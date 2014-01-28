import cv2
from detect_field import * #meh
import numpy as np

# img = cv2.imread('tshape.jpg')
# view_image(img)

def getShapes(contours):
	polys = []
	for cnt in contours:
		p = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True) #cv2.arcLength(cnt, True) * 0.02, True)
		polys.append(p)

	return polys

def centreOfMass(polygon):
	cx = 0
	cy = 0
	area = 0
	polygon = np.append(polygon, [polygon[0]], axis=0)
	for i in range(len(polygon)-1):
		p1 = polygon[i][0]
		p2 = polygon[i+1][0]
		prod = p1[0]*p2[1] - p2[0]*p1[1]
		cx += (p1[0] + p2[0]) * prod
		cy += (p1[1] + p2[1]) * prod
		area += prod

	area *= 3
	cx /= area
	cy /= area
	# print (area, cx,cy)
	return cx, cy

def getPointPairs(polygon, (cx, cy)):
	pass

