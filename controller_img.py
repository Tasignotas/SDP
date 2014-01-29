import cv2
from vision.crop_field import *
from vision.tracker import Tracker
#from milestone1.milestone1 import Robot

def normalize(img):
    kernel = np.ones((5, 5), np.float32) / 25
    dst = cv2.filter2D(img, -1, kernel)
    return dst

def brighten(img, alpha=1.0, beta=10.0):
    mul_img = cv2.multiply(img, np.array([alpha]))
    new_img = cv2.add(mul_img,np.array([beta]))
    return new_img  

def getPitch(frame):
    lower_black = np.array([0,0,0])
    upper_black = np.array([180,83,83])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_black = 255 - mask_black
    frame = cv2.bitwise_and(frame,frame, mask= mask_black)

    return frame

def readFrame(c, xmin, xmax, ymin, ymax):
    frame = cv2.imread("img/t_blue/000000%02d.jpg" % c)
    frame = frame[ymin:ymax,xmin:xmax]
    frame = getPitch(frame)
    frame = brighten(frame, 2.0, 50.0)
    return frame

def run(color):

    # Take each frame
    frame = cv2.imread("img/t_blue/00000001.jpg")

    xmin,xmax,ymin,ymax = get_crop_coordinates(frame)
    print xmin,xmax,ymin,ymax

    frame = brighten(frame[ymin:ymax,xmin:xmax], 2.0, 50.0)
    width = (xmax - xmin)#/4
    height = ymax - ymin

    tracker = Tracker(frame, color, 0, 0, int(width), int(height))
    tracker.update(frame)
    i = 0
    j = 1
    while(1):
        if i == 58:
            j = -1
        if i == 1:
            j = 1
        i = (i % 59) + (j *1)
        print i
        print "properties"
        print tracker.pos
        print tracker.angle
        frame = readFrame(i, xmin,xmax,ymin,ymax)
        ret = tracker.update(frame)
        if not ret:
            break
        

        cv2.ellipse(frame, ret, (0, 0, 255), 2)
        cv2.imshow('img',frame)

        k = cv2.waitKey(60) & 0xff
        if k == 27:
            break

    #run()

    cv2.destroyAllWindows()
    
run("t_blue")