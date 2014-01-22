# adapted from
# http://docs.opencv.org/master/doc/py_tutorials/py_video/py_meanshift/py_meanshift.html#meanshift

import numpy as np
import cv2

class Tracker():
    def __init__(self,frame,color,col,row,width,height):
        self.colors = {"blue":(np.array((88., 50.,50.)), np.array((110.,255.,255.))),
                       "red":(np.array((0., 240.,140.)), np.array((9.,255.,255.))),
                       "yellow":(np.array((11., 238.,140.)), np.array((19.,255.,255.)))}
        self.upper,self.lower = self.colors[color]
        self.pos = None
        self.angle = None
        self.frame = frame
        self.initwindow = (col,row,width,height)
        self.window = (col,row,width,height)
        self.term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        self.setup(frame)
        
    def setup(frame):
        c,r,w,h = self.initwindow
        roi = frame[r:r+h,c:c+w]
        hsv_roi = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi,self.lower,self.upper)
        self.roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
        cv2.normalize(self.roi_hist,self.roi_hist,0,255,cv2.NORM_MINMAX)

    def update(frame): 

        i = 0
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)

            ret, self.window = cv2.CamShift(dst, self.window, self.term_crit)

            pos,dim,angle = ret
            self.pos = pos
            self.angle = angle

        except:
            if i < 10:
                self.window = self.initwindow
                self.update(frame)
                i += 1
