import cv2
import numpy as np

i = 0
while(1):

    # Looping
    i = (i % 59) + 1

    print i
    # Take each frame
    frame = cv2.imread("../img/t_all/000000%02d.jpg" % i)
    frame = cv2.GaussianBlur(frame,(5,5),0)
    print frame.size

    # crop to size of table
    pitch = frame[80:390,50:600]

    #split into zones
    zone1 = pitch[:,0:130]
    zone2 = pitch[:,131:270]
    zone3 = pitch[:,271:420]
    zone4 = pitch[:,421:]

    # Convert BGR to HSV for threshold
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pitch_hsv = cv2.cvtColor(pitch, cv2.COLOR_BGR2HSV)
    zone1_hsv = cv2.cvtColor(zone1, cv2.COLOR_BGR2HSV)
    zone2_hsv = cv2.cvtColor(zone2, cv2.COLOR_BGR2HSV)
    zone3_hsv = cv2.cvtColor(zone3, cv2.COLOR_BGR2HSV)
    zone4_hsv = cv2.cvtColor(zone4, cv2.COLOR_BGR2HSV)

    # define range of t_blue color in HSV define thresholds - need to check these values
    lower_blue = np.array([100,110,60])
    upper_blue = np.array([110,150,100])
    lower_red = np.array([0,240,175])
    upper_red = np.array([10,250,195])
    lower_yellow = np.array([10,235,190])
    upper_yellow = np.array([30,255,230])


# red = (255,0,0) - (100,20,20) RGB
# t_yellow = (232,93,0) - (180,100,10) RGB

    # Threshold the HSV zones to get only t_blue colors
    maskz1 = cv2.inRange(zone1_hsv, lower_yellow, upper_yellow)
    maskz2 = cv2.inRange(zone2_hsv, lower_yellow, upper_yellow)
    maskz3 = cv2.inRange(zone3_hsv, lower_yellow, upper_yellow)
    maskz4 = cv2.inRange(zone4_hsv, lower_yellow, upper_yellow)
    # maskz1 = cv2.inRange(zone1_hsv, lower_red, upper_red)
    # maskz2 = cv2.inRange(zone2_hsv, lower_red, upper_red)
    # maskz3 = cv2.inRange(zone3_hsv, lower_red, upper_red)
    # maskz4 = cv2.inRange(zone4_hsv, lower_red, upper_red)
    # maskz1 = cv2.inRange(zone1_hsv, lower_blue, upper_blue)
    # maskz2 = cv2.inRange(zone2_hsv, lower_blue, upper_blue)
    # maskz3 = cv2.inRange(zone3_hsv, lower_blue, upper_blue)
    # maskz4 = cv2.inRange(zone4_hsv, lower_blue, upper_blue)

    # Bitwise-AND mask and original image
#    res = cv2.bitwise_and(pitch,pitch, mask= mask)

    # get contours from threshold masks
    contours1, h  = cv2.findContours(maskz1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours2, h  = cv2.findContours(maskz2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours3, h  = cv2.findContours(maskz3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours4, h  = cv2.findContours(maskz4,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    
    # draw contours
    cv2.drawContours(pitch, contours1, -1, (0,255,0), 3,offset=(0,0))
    cv2.drawContours(pitch, contours2, -1, (0,255,0), 3,offset=(130,0))
    cv2.drawContours(pitch, contours3, -1, (0,255,0), 3,offset=(270,0))
    cv2.drawContours(pitch, contours4, -1, (0,255,0), 3,offset=(420,0))
	
    pitch_edges = cv2.Canny(frame,100,200)	# Edge detection

    #(x,y),(MA,ma),angle = 
    #print contours4[0][0][0]

    #print cv2.fitEllipse(contours4)
    #print (x,y)
    #print angle
    cv2.imshow("edges",pitch_edges)
    cv2.imshow("z1",zone1)
    cv2.imshow("z2",zone2)
    cv2.imshow("z3",zone3)
    cv2.imshow("z4",zone4)
    cv2.imshow("img",pitch)

    k = cv2.waitKey(5) & 0xFF # press ESC to end
    if k == 27:
        break

cv2.destroyAllWindows()

#adapted from 
# http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html#converting-colorspaces
