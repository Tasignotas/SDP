import cv2
import numpy as np
from tools import *
import math

def distance(x,y):
	return math.pow(abs(x[0] - y[0]), 3) + math.pow(abs(x[1] - y[1]), 3)

def average(x,y):
	return (
		int(math.ceil((x[0] + y[0]) / 2.0)), 
		int(math.ceil((x[1] + y[1]) / 2.0))
	)

def closest(points):
	_min = 9999999
	closest = None
	for i in range(len(points)):
		current = points[i]
		for j in range(i+1, len(points)):
			next = points[j]
			dist = distance(current, next)
			if dist < _min:
				_min = dist
				closest = (i, j)
	return closest

cap = cv2.VideoCapture(0)

for i in range(10):
	ret, frame = cap.read()

coords = get_calibration()

crop = find_crop_coordinates(frame, coords['outline'])

k = True
while k != ord('q'):

	ret, frame = cap.read()
	frame = frame[crop[2]:crop[3], crop[0]:crop[1]]
	frame = cv2.blur(frame,(5,5))

	# frame = cv2.multiply(frame, np.array[1])
	frame = cv2.add(frame, np.array([100.0]))

	hsv_roi = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(
		hsv_roi, np.array((15.0, 115.0,255.0)), 
		np.array((360.0,255.0,255.0))
	)

	cv2.imshow('mask', mask)

	# cv2.circle(frame, (50,50), 10, (0, 255, 0), -1)



	ret,thresh = cv2.threshold(mask,127,255,0)
	contours, hierarchy = cv2.findContours(
		thresh,
		cv2.RETR_LIST,
		cv2.CHAIN_APPROX_SIMPLE
	)

	if len(contours) > 0 and len(contours[0]) > 5:

		cnt = contours[0]

		(x,y),(MA,ma),angle = cv2.fitEllipse(cnt)
		ellipse = ((x,y), (MA, ma), angle)
		cv2.ellipse(frame, ellipse,(0,0,255),3)
		print angle

		area = cv2.contourArea(cnt)
		hull = cv2.convexHull(cnt)
		hull_area = cv2.contourArea(hull)
		solidity = float(area)/hull_area

		# print area, hull_area, solidity
		# print cnt

		x,y,w,h = cv2.boundingRect(cnt)
		rect = cv2.minAreaRect(cnt)
		box = cv2.cv.BoxPoints(rect)
		box = np.int0(box)
		# cv2.drawContours(frame,[box],0,(0,0,255),1)

		# cv2.drawContours(frame, [cnt], -1, (0,255,0), -1)

		# print cnt.shape


		# cv2.drawContours(mask,cnt,-1,(0,255,0), 3)

		# cv2.imshow('im', im)
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()

		rows,cols = mask.shape[:2]
		[vx,vy,x,y] = cv2.fitLine(cnt, 1,0,0.01,0.01)
		lefty = int((-x*vy/vx) + y)
		righty = int(((cols-x)*vy/vx)+y)
		# cv2.line(frame,(cols-1,righty),(0,lefty),(0,0,255),2)

		leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
		rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
		topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
		bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])

		points = [leftmost, rightmost, topmost, bottommost]

		# Average out the two closest points
		
		_closest = closest(points)

		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(mask, mask = mask)
		# print min_val, max_val, min_loc, max_loc

		# print closest, _min

		new_point = average(points[_closest[0]], points[_closest[1]])
		# print points[closest[0]], points[closest[1]], new_point

		points.pop(_closest[0])
		# points.pop(_closest[1]-1)
		# points.append(new_point)

		t_top = closest(points)
		# print t_top

		# cv2.line(frame, points[0], points[1], (255, 0, 0), 4)
		# print t_top	

		# for point in points:
		# 	cv2.circle(frame, point, 2, (0,0,255), -1)




		# print leftmost, rightmost, topmost
		# cv2.circle(frame, leftmost, 2, (0,0,255), -1)
		# cv2.circle(frame, rightmost, 2, (0,255,0), -1)
		# cv2.circle(frame, topmost, 2, (255,0,0), -1)
		# cv2.circle(frame, bottommost, 2, (0,0,0), -1)

	else:
		print 'No vals'
	# cv2.circle(mask, (50,50), 10, (0, 255, 0), -1)

	cv2.imshow('image', frame)
	k = cv2.waitKey(4) & 0xFF



# im = cv2.imread('mask.jpg')





# ret,thresh = cv2.threshold(imgray,127,255,0)
# contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

# cnt = contours[0]
# print len(cnt)

# # cv2.drawContours(im,contours,-1,(0,255,0),1)

# # cv2.imshow('im', im)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()

# rows,cols = im.shape[:2]
# [vx,vy,x,y] = cv2.fitLine(cnt, 1,0,0.01,0.01)
# lefty = int((-x*vy/vx) + y)
# righty = int(((cols-x)*vy/vx)+y)
# # cv2.line(im,(cols-1,righty),(0,lefty),(0,255,0),2)

# leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
# rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
# topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
# bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])

# print leftmost, rightmost, topmost, bottommost
# cv2.circle(im, leftmost, 2, (0,0,255), -1)
# cv2.circle(im, rightmost, 2, (0,0,255), -1)
# cv2.circle(im, topmost, 2, (0,0,255), -1)
# cv2.circle(im, bottommost, 2, (0,0,255), -1)

# cv2.imshow('image', im)
# cv2.waitKey(0)