import cv2
import numpy as np

def nothing(x):
    pass

def brighten(img, alpha=1.0, beta=10.0):
    mul_img = cv2.multiply(img, np.array([alpha]))
    new_img = cv2.add(mul_img,np.array([beta]))
    return new_img

def setWindow():
    cv2.namedWindow("Image")
    cv2.namedWindow("Mask")
    cv2.createTrackbar("LH", "Mask", 0, 360, nothing)
    cv2.createTrackbar("UH", "Mask", 0, 360, nothing)
    cv2.createTrackbar("LS", "Mask", 0, 255, nothing)
    cv2.createTrackbar("US", "Mask", 0, 255, nothing)
    cv2.createTrackbar("LV", "Mask", 0, 255, nothing)
    cv2.createTrackbar("UV", "Mask", 0, 255, nothing)
    cv2.createTrackbar("BR", "Mask", 1, 3, nothing)
    cv2.createTrackbar("CT", "Mask", 1, 100, nothing)

def run():
    setWindow()
    i = 0
    cap = cv2.VideoCapture(0)

    while(1):
        i = (i % 59) + 1
        LH = cv2.getTrackbarPos("LH", "Mask")
        UH = cv2.getTrackbarPos("UH", "Mask")
        LS = cv2.getTrackbarPos("LS", "Mask")
        US = cv2.getTrackbarPos("US", "Mask")
        LV = cv2.getTrackbarPos("LV", "Mask")
        UV = cv2.getTrackbarPos("UV", "Mask")
        BR = cv2.getTrackbarPos("BR", "Mask")
        CT = cv2.getTrackbarPos("CT", 'Mask')

        ret, frame = cap.read()
        frame = brighten(frame, float(BR), float(CT))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([LH, LS, LV]), np.array([UH, US, UV]))

        cv2.imshow("Image", frame)
        cv2.imshow("Mask", mask)

        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()

run()