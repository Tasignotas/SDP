# adapted from
# http://docs.opencv.org/master/doc/py_tutorials/py_video/py_meanshift/py_meanshift.html#meanshift

import numpy as np
import cv2

BLUE_LOWER = np.array((89, 132,  91))
BLUE_HIGHER = np.array((129, 132,  91))

class Tracker():
    def __init__(self,frame,color,col,row,width,height):
        self.colors = {"blue":(np.array((100., 110.,60.)), np.array((110.,150.,100.))),
                       "red":(np.array((0., 240.,175.)), np.array((10.,250.,195.))),
                       "yellow":(np.array((10., 235.,  190.)), np.array((30., 255., 230.))),
                       "white":(BLUE_LOWER, BLUE_HIGHER)}
        self.lower,self.upper = self.colors[color]
        print self.upper
        print self.lower
        self.pos = None
        self.angle = None
        self.frame = frame
        self.initwindow = (col,row,width,height)
        self.window = (col,row,width,height)
        self.term_crit = ( 
            cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 
            100, 5 )
        c,r,w,h = col,row,width,height
        roi = frame[r:r+h,c:c+w]
        hsv_roi = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
        print roi == None, len(roi)
        cv2.imshow("",frame)
        cv2.waitKey(0)
        mask = cv2.inRange(hsv_roi,self.lower,self.upper)
        self.roi_hist = cv2.calcHist([hsv_roi],[0],mask,[255],[0,180])
        cv2.normalize(self.roi_hist,self.roi_hist,0,255,cv2.NORM_MINMAX)
        
    def update(self,frame): 

        i = 0

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv],[0],self.roi_hist,[0,180],5)
        print "window"
        print self.window
        try:
            ret, self.window = cv2.CamShift(dst, self.window, self.term_crit)
            pos,dim,angle = ret
            self.pos = pos
            self.angle = angle
        except:
            print "ERROR"
            return None

        return ret
