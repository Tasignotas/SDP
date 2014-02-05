import cv2
import numpy as np
import cPickle
from optparse import OptionParser

CONTROLS = ["LH", "UH", "LS", "US", "LV", "UV", "BR", "CT", "BL"]
MAXBAR={"LH":360, 
          "UH":360, 
          "LS":255,
          "US":255,
          "LV":255,
          "UV":255,
          "BR":3,
          "CT":100,
          "BL":100}

def nothing(x):
    pass

def brighten(img, alpha=1.0, beta=10.0):
    mul_img = cv2.multiply(img, np.array([alpha]))
    new_img = cv2.add(mul_img,np.array([beta]))
    return new_img

def blur(img, ksize=0):
    if (ksize>1):
        return cv2.blur(img, (ksize,ksize))
    return img

def setWindow(color):
    cv2.namedWindow(color)
    cv2.namedWindow("Mask: " + color)

    try:
        configFile = open("configMask.txt", "rb")
        config = cPickle.load(configFile)
    except:
        initialConfig = {}
        for control in CONTROLS:
            initialConfig[control] = 0
        config = {'yellow':initialConfig,
                  'blue':initialConfig,
                  'red':initialConfig}

    for setting in CONTROLS:
        cv2.createTrackbar(setting, "Mask: " + color, config[color][setting], \
            MAXBAR[setting], nothing)

    return config

def run(color):
    
    selectColor = setWindow(color)
    i = 0
    cap = cv2.VideoCapture(0)

    maskWindowName = "Mask: " + color
    while(1):
        i = (i % 59) + 1
        LH = cv2.getTrackbarPos("LH", maskWindowName)
        UH = cv2.getTrackbarPos("UH", maskWindowName)
        LS = cv2.getTrackbarPos("LS", maskWindowName)
        US = cv2.getTrackbarPos("US", maskWindowName)
        LV = cv2.getTrackbarPos("LV", maskWindowName)
        UV = cv2.getTrackbarPos("UV", maskWindowName)
        BR = cv2.getTrackbarPos("BR", maskWindowName)
        CT = cv2.getTrackbarPos("CT", maskWindowName)
        BL = cv2.getTrackbarPos("BL", maskWindowName)

        ret, frame = cap.read()
        frame = brighten(frame, float(BR), float(CT))
        frame = blur(frame, BL)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([LH, LS, LV]), np.array([UH, US, UV]))

        cv2.imshow(color, frame)
        cv2.imshow(maskWindowName, mask)

        config = {}
        k = cv2.waitKey(5) & 0xFF

        if k == 27:
            for setting in CONTROLS:
                config[setting] = cv2.getTrackbarPos(setting, maskWindowName)
                
                selectColor[color] = config
                
            configFile = open("configMask.txt", "wb")
            cPickle.dump(selectColor, configFile)
            print selectColor
            configFile.close()
            break

    cv2.destroyAllWindows()

def main():
    parser = OptionParser()
    color = 'all'
    parser.add_option("-c", "--color", dest="color",
                      help="all / yellow / red / blue")
    (opts, args) = parser.parse_args()
    if opts == 'None':
        opts = 'all'
    selectColor = {}
    if (color in ['all', 'yellow']):
        run('yellow')
    if (color in ['all', 'blue']):
        run('blue')
    if (color in ['all', 'red']):
        run('red')

main()