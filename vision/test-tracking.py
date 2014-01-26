import numpy as np
import cv2
from tools import *

cap = cv2.VideoCapture(0)

# take first frame of the video
for i in range(10):
	ret,frame = cap.read()

coords = get_calibration()

crop = find_crop_coordinates(frame, coords['outline'])
frame = frame[crop[2]:crop[3], crop[0]:crop[1]]

# frame = cv2.multiply(frame, np.array[1])
frame = cv2.add(frame, np.array([90.0]))

# setup initial location of window
r,h,c,w = 0,480,0, 320  # simply hardcoded the values
track_window = (c,r,w,h)

# set up the ROI for tracking
roi = frame[r:r+h, c:c+w]
hsv_roi =  cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv_roi, np.array((13.0, 160.0,255.0)), np.array((360.0,255.0,255.0)))

cv2.imshow('mask', mask)
cv2.imwrite('mask.jpg', mask)
cv2.waitKey(0)

roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
print roi_hist
cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)

# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

while(1):
    ret ,frame = cap.read()
    frame = mask_pitch(frame, coords['outline'])
    frame = frame[crop[2]:crop[3], crop[0]:crop[1]]
    frame = cv2.add(frame, np.array([90.0]))
   
    if ret == True:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)

        # apply meanshift to get the new location
        t1, t2, t3, t4 = track_window
        if t1 <= 0 or t2 <= 0 or t3 <= 0 or t4 <= 0:
        	track_window = (0,480,320, 480) 
        print track_window
        ret, track_window = cv2.CamShift(dst, track_window, term_crit)

        # print track_window

        x,y,w,h = track_window
        cv2.rectangle(frame, (x,y), (x+w,y+h), 255,2)
        # # Draw it on image
        # pts = cv2.boxPoints(ret)`
        # pts = np.int0(pts)
        # img2 = cv2.polylines(frame,[pts],True, 255,2)
        cv2.imshow('img2',frame)

        k = cv2.waitKey(60) & 0xff
        if k == 27:
            break
       

    else:
        break

cv2.destroyAllWindows()
cap.release()