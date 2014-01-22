import cv2
from vision.crop_field import *
from vision.tracker import Tracker
from src.milestone1 import Robot



def readFrame(c):
    ret,frame = cap.read()
    xmin,xmax,ymin,ymax = get_crop_coordinates(frame)
    frame = frame[ymin:ymax,xmin:xmax]
    return frame

def run():
    cap = cv2.VideoCapture(0)

    for i in range(10):
        ret,frame = cap.read()

    xmin,xmax,ymin,ymax = get_crop_coordinates(frame)
    frame = frame[ymin:ymax,xmin:xmax]
    width = (xmax - xmin)/4
    height = ymax - ymin

    tracker = Tracker(frame,"blue",width*3,0,width,height)
    tracker.update(frame)
    
    while(1):
        print tracker.pos
        print tracker.angle
        frame = readFrame(cap)
        tracker.update(frame)
      
        k = cv2.waitKey(60) & 0xff
        if k == 27:
            break
        else:
            break

    cv2.destroyAllWindows()
    cap.release()
    
