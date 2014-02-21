import numpy as np
import cv2
import tools

cap = cv2.VideoCapture(0)

for i in range(5):
	status, frame = cap.read()

fgbg = cv2.BackgroundSubtractorMOG2(0,30,False)

'''cropping'''
pitch_outline = tools.get_calibration('calibrate.json')['outline']
crop = tools.find_crop_coordinates(frame, pitch_outline)

while(1):
    ret,frame = cap.read()

    frame = frame[crop[2]:crop[3], crop[0]:crop[1]]
    frame = cv2.blur(frame, (2, 2))
    fgmask = fgbg.apply(frame)
    #frame = cv2.bitwise_and(frame,frame,mask=fgmask)

    ret,thresh = cv2.threshold(fgmask,127,255,0)

    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #print len(contours)

    for x in contours:
        area = cv2.contourArea(x)
        if area >180 and area < 300:
            (x,y),radius = cv2.minEnclosingCircle(x)
            center = (int(x),int(y))
            radius = int(radius)
            cv2.circle(frame,center,radius,(0,255,0),2)
            #print "Area:", area
        elif area > 600 and area < 1400:    #bounds for worst (on green field) and best (on white boundary) case.
            x,y,w,h = cv2.boundingRect(x)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
    #try:
    #    area = cv2.contourArea(contours[0])
    #    print area
    #except:
    #    pass

    cv2.imshow('frame',frame)
    cv2.imshow('fgmask',fgmask)
    k = cv2.waitKey(5) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
