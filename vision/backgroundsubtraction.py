import numpy as np
import cv2

cap = cv2.VideoCapture(0)

fgbg = cv2.BackgroundSubtractorMOG2(0,30,True)

while(1):
    ret,frame = cap.read()
    fgmask = fgbg.apply(frame)
    frame = cv2.bitwise_and(frame,frame,mask=fgmask)
    cv2.imshow('frame',fgmask)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()