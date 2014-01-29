import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):

    # Take each frame
    _, frame = cap.read()
    frame = cv2.GaussianBlur(frame,(5,5),0)
    #print frame.size

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

    # define range of t_blue color in HSV define thresholds - need to check these values
    #lower_blue = np.array([100,50,50])
    #upper_blue = np.array([150,255,255])
    lower_blue = np.array([1,0,100])
    upper_blue = np.array([36,255,255])
    lower_red = np.array([200,100,100])
    upper_red = np.array([250,255,255])
    lower_black = np.array([0,0,0])
    upper_black = np.array([180,75,75])

# red = (255,0,0) - (100,20,20) RGB
# t_yellow = (232,93,0) - (180,100,10) RGB

    # Threshold the HSV zones to get only t_blue colors
    maskz1 = cv2.inRange(zone1_hsv, lower_blue, upper_blue)
    maskz2 = cv2.inRange(zone2_hsv, lower_blue, upper_blue)
    maskz3 = cv2.inRange(zone3_hsv, lower_blue, upper_blue)
    maskz4 = cv2.inRange(zone4_hsv, lower_blue, upper_blue)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_black = 255 - cv2.inRange(hsv, lower_black, upper_black)
    #print mask_black[0,0]
    #mask_black = 255 - mask_black

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask_black)

    # get contours from thresholded masks
    contoursz1, h  = cv2.findContours(maskz1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contoursz2, h  = cv2.findContours(maskz2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contoursz3, h  = cv2.findContours(maskz3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contoursz4, h  = cv2.findContours(maskz4,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    
    # draw contours
    cv2.drawContours(pitch, contoursz1, -1, (0,255,0), 3,offset=(0,0))
    cv2.drawContours(pitch, contoursz2, -1, (0,255,0), 3,offset=(130,0))
    cv2.drawContours(pitch, contoursz3, -1, (0,255,0), 3,offset=(270,0))    
    cv2.drawContours(pitch, contoursz4, -1, (0,255,0), 3,offset=(420,0))
	
    pitch_edges = cv2.Canny(frame,100,200)	# Edge detection

    #(x,y),(MA,ma),angle = 
    #print contoursz4[0][0][0]

    #print cv2.fitEllipse(contoursz4)
    #print (x,y)
    #print angle
    #cv2.imshow("edges",pitch_edges)
    #cv2.imshow("z1",zone1)
    #cv2.imshow("z2",zone2)
    #cv2.imshow("z3",zone3)
    #cv2.imshow("z4",zone4)
    #cv2.imshow("img",pitch)
    cv2.imshow("res",res)
    cv2.imshow("mask",mask_black)

    k = cv2.waitKey(5) & 0xFF # press ESC to end
    if k == 27:
        break

cv2.destroyAllWindows()

#adapted from 
# http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html#converting-colorspaces
