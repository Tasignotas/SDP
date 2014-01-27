import cv2
import cv2.cv as cv
import numpy as np
from tools import *
import math

cap = cv2.VideoCapture(0)

for i in range(10):
	ret, frame = cap.read()

coords = get_calibration()

crop = find_crop_coordinates(frame, coords['outline'])

k = True

def brighten(img, alpha=1.0, beta=10.0):
    mul_img = cv2.multiply(img, np.array([alpha]))
    new_img = cv2.add(mul_img,np.array([beta]))
    return new_img

while k != ord('q'):

	ret, frame = cap.read()
	frame = brighten(frame, 1.0, 100.0)
	frame = frame[crop[2]:crop[3], crop[0]:crop[1]]
	frame = cv2.blur(frame,(5,5))

	hsv_roi = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(
		hsv_roi, np.array((0.0,0.0,146.0)), 
		np.array((360.0,101.0,255.0))
	)
	cv2.imshow('mask', mask)
	circles = cv2.HoughCircles(mask,cv2.cv.CV_HOUGH_GRADIENT,1,5,param1=50,param2=13,minRadius=0,maxRadius=12)
	if circles is not None:
            for c in circles[0]:
                    cv2.circle(frame, (c[0],c[1]), c[2], (255,0,0),2)


	#cv2.imshow('mask', mask)
	cv2.imshow('detected circles', frame)
	k = cv2.waitKey(4) & 0xFF

