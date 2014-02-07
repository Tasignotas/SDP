# Source for Kalman filter configuration in kalman():
# http://www.hdm-stuttgart.de/~maucher/Python/ComputerVision/html/Tracking.html
#
# More info on how it works:
# http://www.mathworks.co.uk/help/vision/ref/vision.kalmanfilterclass.html
#
# Requires pykalman
# Clone https://github.com/pykalman/pykalman
# python setup.py install --user

import cv2
import numpy as np
import cPickle
from pykalman import KalmanFilter
from matplotlib import pyplot as plt

from time import sleep

# Pick up values for the red mask
pickleFile = open("configMask.txt", "rb")
config = cPickle.load(pickleFile)
config = config['red'][0]
pickleFile.close()

def blur(img, ksize=0):
    if (ksize>1):
        ksize = int(ksize)
        return cv2.blur(img, (ksize,ksize))
    return img

def brighten(img, alpha=1.0, beta=10.0):
    mul_img = cv2.multiply(img, np.array([alpha]))
    new_img = cv2.add(mul_img,np.array([beta]))
    return new_img

def run():
    capture = cv2.VideoCapture(0)
    cv2.namedWindow('Mask')
    cv2.namedWindow('Track')

    count = 0
    numframes = 15
    measuredTrack=np.zeros((numframes,2))-1

    stat = None

    while(1):
        count += 1
        ret, frame = capture.read()
        frame = brighten(frame, 1.0, float(config['contrast']))
        frame = blur(frame, config['blur'])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, config['min'], config['max'])
        ret,thresh = cv2.threshold(mask,127,255,0)
        cv2.imshow('Track', frame)
        cv2.imshow('Mask', mask)

        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        if (len(contours) > 0):
            m= np.mean(contours[0],axis=0)
            if (stat == None):
                stat = m
            elif (np.linalg.norm(m - stat) < 2):
                # Filter will be reset when ball is stationary.
                pass
            else:
                stat = m

        else:
            m = np.zeros((1,2))-1

        if (count < numframes):
            measuredTrack[count,:] = m[0]
        else:
            for i in range(numframes-1):
                measuredTrack[i] = measuredTrack[i+1]
            measuredTrack[numframes-1] = m[0]

        cv2.circle(frame, tuple(m[0]), 10, (0, 255, 0), 2)

        if count >= 5:
            try:
                if count < numframes:
                    prediction = kalman(measuredTrack[:count])
                else:
                    prediction = kalman(measuredTrack)

                prediction = tuple([prediction[0], prediction[1]])
            except:
                pass

            try:
                cv2.circle(frame, prediction, 10, (0, 0, 0), 2)
            except:
                print tuple(m[0]), prediction

        cv2.imshow('Track', frame)
        cv2.imshow('Mask', mask)

        k = cv2.waitKey(50) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()

def kalman(Measured):

    # Remove frames from beginning if ball was not visible.
    while (Measured[0,0] == -1.):
        Measured=np.delete(Measured,0,0)

    # numMeas=Measured.shape[0]
    MarkedMeasure=np.ma.masked_less(Measured,0)

    Transition_Matrix=[[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]]
    Observation_Matrix=[[1,0,0,0],[0,1,0,0]]

    xinit=MarkedMeasure[0,0]
    yinit=MarkedMeasure[0,1]
    vxinit=MarkedMeasure[1,0]-MarkedMeasure[0,0]
    vyinit=MarkedMeasure[1,1]-MarkedMeasure[0,1]
    initstate=[xinit,yinit,vxinit,vyinit]
    initcovariance=1.0e-3*np.eye(4)
    transistionCov=1.0e-4*np.eye(4)
    observationCov=1.0e-1*np.eye(2)

    kf=KalmanFilter(transition_matrices=Transition_Matrix,
                observation_matrices =Observation_Matrix,
                initial_state_mean=initstate,
                initial_state_covariance=initcovariance,
                transition_covariance=transistionCov,
                observation_covariance=observationCov)

    (filtered_state_means, filtered_state_covariances) = kf.filter(MarkedMeasure)
    # plt.plot(MarkedMeasure[:,0],MarkedMeasure[:,1],'xr',label='measured')
    # plt.axis([0,600,360,0])
    # plt.hold(True)
    # plt.plot(filtered_state_means[:,0],filtered_state_means[:,1],'xg',label='kalman output')
    # plt.legend(loc=2)
    # plt.title("Constant Velocity Kalman Filter")
    # plt.show()
    return filtered_state_means[-1]
# sleep(3)
run()