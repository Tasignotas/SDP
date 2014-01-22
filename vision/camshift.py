# This algorithm looks for and tracks objects of a 
# certain colour. By setting the initial search zones
# to be the four zones, we would be able to find the 
# robot in each zone, and output the coords and angle of
# the containing rectangle/ellipse.


import numpy as np
import cv2
from crop_field import *

cap = cv2.VideoCapture(0)

# take first frame of the video
for i in range(10):
    ret,frame = cap.read()

#cv2.normalize(frame,frame,0,255,cv2.NORM_MINMAX)

xmin,xmax,ymin,ymax = get_crop_coordinates(frame,5)
print xmin,xmax,ymin,ymax
#xmin,xmax=x
frame = frame[ymin:ymax,xmin:xmax]
width = (xmax - xmin)/4
height = ymax - ymin
cv2.rectangle(frame,(0,int(width*3)),(int(width),int(height)),(0,255,0))
cv2.imshow("",frame)
cv2.waitKey(0)



# setup initial location of window
r,h,c,w = 0,height,width*3,width  # simply hardcoded the values # these values initialise to zone4 (nearest the door)
#r,h,c,w = 110,250,85,480 #whole pitch
track_window = (c,r,w,h)


#bg = cv2.BackgroundSubtractorMOG(24*60,1,0.9,0.01)
#fgMask = bg.apply(frame)
#frame = cv2.bitwise_and(frame,frame,mask=fgMask)
#cv2.imshow("",fgMask)
#cv2.waitKey(0)

# set up the ROI for tracking
roi = frame[r:r+h, c:c+w]
hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
#mask = cv2.inRange(hsv_roi, np.array((11., 238.,140.)), np.array((19.,255.,255.))) # Yellow objects
#mask = cv2.inRange(hsv_roi, np.array((0., 240.,140.)), np.array((9.,255.,255.))) # Red objects 
#mask = cv2.inRange(hsv_roi, np.array((100., 50.,50.)), np.array((150.,255.,255.))) # blue objects
mask = cv2.inRange(hsv_roi, np.array((88., 50.,50.)), np.array((110.,255.,255.))) # blue objects
roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)

# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )



while(1):
    ret ,frame = cap.read()
    #bg = cv2.BackgroundSubtractorMOG()
    #bg.apply(frame)
    #frame = cv2.bitwise_and(frame,frame,mask=fgMask)
    #frame2= frame[:,:,2]
    frame = frame[ymin:ymax,xmin:xmax]

    if ret == True:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)

        # apply meanshift to get the new location
        ret, track_window = cv2.CamShift(dst, track_window, term_crit)

        # Draw it on image
        #pts = ret.points
        #pts = np.int0(pts)
        pos,dim, angle = ret
        print pos
        print angle
        x,y = pos
        w2,h2 = dim
        points = np.array([[x,y],[x+w2,y],[x,y+h2],[x+w2,y+h2]])

        #cv2.imshow('roi',roi)
        cv2.ellipse(frame, ret, (0, 0, 255), 2)
        #img2 = cv2.polylines(frame,points,True, 255,2)
        #cv2.rectangle(frame,(x,y),(x+w2,y+h2),(0,255,0))
        cv2.imshow('img',frame)
        #cv2.imshow('mask', mask)
        cv2.imshow('dst',dst)
        #cv2.imshow('img2',frame2)
        
        k = cv2.waitKey(60) & 0xff
        if k == 27:
            break
    else:
        break

cv2.destroyAllWindows()
cap.release()

# adapted from
# http://docs.opencv.org/master/doc/py_tutorials/py_video/py_meanshift/py_meanshift.html#meanshift
