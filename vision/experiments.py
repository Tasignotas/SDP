import cv2
import numpy as np
import tools
import math
from matplotlib import pyplot as plt


class Experiment(object):

    def __init__(self):
        self.capture = cv2.VideoCapture(0)

        # pitch_outline = tools.get_calibration('calibrate.json')['outline']
        # self.crop = tools.find_crop_coordinates(self.frame, pitch_outline)

    def run(self):

        fgbg = cv2.BackgroundSubtractorMOG2(0,30, False)

        for i in range(5):
            status, img = self.capture.read()

        k = True
        while k != ord('q'):
            status, frame = self.capture.read()

            img = frame

            frame = cv2.blur(frame, (2, 2))

            surf = cv2.SURF(400)

            # Find keypoints and descriptors directly
            >>> kp, des = surf.detectAndCompute(img,None)

            >>> len(kp)


            fgmask = fgbg.apply(frame)
            frame = cv2.bitwise_and(frame,frame, mask=fgmask)

            cv2.imshow('frame', frame)
            # frame = frame[crop[2]:crop[3], crop[0]:crop[1]]

            # fast = cv2.FastFeatureDetector()

            # find and draw the keypoints
            # kp = fast.detect(frame, None)
            # img2 = cv2.drawKeypoints(frame, kp, color=(255,0,0))

            # Print all default params
            # print "Threshold: ", fast.getInt('threshold')
            # print "nonmaxSuppression: ", fast.getBool('nonmaxSuppression')
            # print "neighborhood: ", fast.getInt('type')
            # print "Total Keypoints with nonmaxSuppression: ", len(kp)

            # Disable nonmaxSuppression
            # fast.setBool('nonmaxSuppression',0)
            # kp = fast.detect(frame, None)

            # print "Total Keypoints without nonmaxSuppression: ", len(kp)

            # img = cv2.drawKeypoints(frame, kp, color=(255,0,0))

            # cv2.imshow('frame', frame)

            # gray = cv2.cvtColor(frame ,cv2.COLOR_BGR2GRAY)

            # corners = cv2.goodFeaturesToTrack(gray,25,0.01,10)
            # corners = np.int0(corners)

            # for i in corners:
            #     x,y = i.ravel()
            #     cv2.circle(img,(x,y),3,255,-1)

            # cv2.imshow('corners', img)


            # gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            # gray = np.float32(gray)
            # dst = cv2.cornerHarris(gray,2,3,0.04)

            # #result is dilated for marking the corners, not important
            # dst = cv2.dilate(dst,None)

            # # Threshold for an optimal value, it may vary depending on the image.
            # frame[dst>0.01*dst.max()]=[0,0,255]

            # cv2.imshow('dst',frame)



            cv2.imshow('frame2', frame)
            k = cv2.waitKey(5) & 0xFF


e = Experiment()
e.run()