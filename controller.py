import cv2
from vision.crop_field import *
from vision.tracker import Tracker
#from src.milestone1 import Robot



def readFrame(c,   xmin,xmax,ymin,ymax):
    ret,frame = c.read()
    frame = frame[ymin:ymax,xmin:xmax]
    return frame

def run():
    cap = cv2.VideoCapture(0)
    for i in range(10):
        ret,frame = cap.read()
    print frame.shape
    xmin,xmax,ymin,ymax = get_crop_coordinates(frame)
    print xmin,xmax,ymin,ymax
    frame = frame[ymin:ymax,xmin:xmax]
    width = (xmax - xmin)#/4
    height = ymax - ymin

    tracker = Tracker(frame,"blue",int(0),0,int(width),int(height))
    tracker.update(frame)
    
    while(1):
        print "properties"
        print tracker.pos
        print tracker.angle
        frame = readFrame(cap, xmin,xmax,ymin,ymax)
        ret = tracker.update(frame)
      

        cv2.ellipse(frame, ret, (0, 0, 255), 2)

        cv2.imshow('img',frame)

        k = cv2.waitKey(60) & 0xff
        if k == 27:
            break

    cv2.destroyAllWindows()
    cap.release()
    
