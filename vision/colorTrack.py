import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):

    # Take each frame
    _, frame = cap.read()
    # crop to size of table
    pitch = frame[80:390,50:600]
    #split into zones
    zone1 = pitch[:,0:130]
    zone2 = pitch[:,131:270]
    zone3 = pitch[:,271:420]
    zone4 = pitch[:,421:]

    # Convert BGR to HSV for thresholding
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    pitch_hsv = cv2.cvtColor(pitch, cv2.COLOR_BGR2HSV)
    zone1_hsv = cv2.cvtColor(zone1, cv2.COLOR_BGR2HSV)
    zone2_hsv = cv2.cvtColor(zone2, cv2.COLOR_BGR2HSV)
    zone3_hsv = cv2.cvtColor(zone3, cv2.COLOR_BGR2HSV)
    zone4_hsv = cv2.cvtColor(zone4, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV define thresholds
    lower_blue = np.array([100,50,50])
    upper_blue = np.array([150,255,255])
    lower_red = np.array([200,100,100])
    upper_red = np.array([250,255,255])

# red = (255,0,0) - (100,20,20) RGB
# yellow = (232,93,0) - (180,100,10) RGB

    # Threshold the HSV zones to get only blue colors
    maskz1 = cv2.inRange(zone1_hsv, lower_blue, upper_blue)
    maskz2 = cv2.inRange(zone2_hsv, lower_blue, upper_blue)
    maskz3 = cv2.inRange(zone3_hsv, lower_blue, upper_blue)
    maskz4 = cv2.inRange(zone4_hsv, lower_blue, upper_blue)

    # Bitwise-AND mask and original image
#    res = cv2.bitwise_and(pitch,pitch, mask= mask)

    # get contours from thresholded masks
    contoursz1, h  = cv2.findContours(maskz1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contoursz2, h  = cv2.findContours(maskz2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contoursz3, h  = cv2.findContours(maskz3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contoursz4, h  = cv2.findContours(maskz4,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    #print contours
    #print h
    
    # draw contours
    cv2.drawContours(pitch, contoursz1, -1, (0,255,0), 3,offset=(0,0))
    cv2.drawContours(pitch, contoursz2, -1, (0,255,0), 3,offset=(130,0))
    cv2.drawContours(pitch, contoursz3, -1, (0,255,0), 3,offset=(270,0))    
    cv2.drawContours(pitch, contoursz4, -1, (0,255,0), 3,offset=(420,0))

    cv2.imshow("img",pitch)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()

#adapted from 
# http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html#converting-colorspaces
