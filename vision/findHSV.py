import cv2
import numpy as np
import cPickle
from optparse import OptionParser

CONTROLS = ["LH", "UH", "LS", "US", "LV", "UV", "BR", "CT", "BL"]
MAXBAR = {"LH":360, 
          "UH":360, 
          "LS":255,
          "US":255,
          "LV":255,
          "UV":255,
          "BR":3,
          "CT":100,
          "BL":100
        }

INDEX = {"LH":0, 
         "UH":0, 
         "LS":1,
         "US":1,
         "LV":2,
         "UV":2
        }

def nothing(x):
    pass

# Holds the object as exported in the pickle and used in tracker.py
# and provides access to its values.
class FileConfig(object):
    
    def __init__(self):
        try:
            pickleFile = open("configMask.txt", "rb")
            self.config = cPickle.load(pickleFile)
        except:
            self.config = {'yellow':[
                                {'min': np.array((0.0, 0.0, 0.0)), #LH, LS, LV
                                 'max': np.array((0.0, 0.0, 0.0)), #UH, US, UV
                                 'contrast': 1.0, #CT
                                 'blur': 0.0 #BL
                                }
                            ],
                            'blue':[
                                {'min': np.array((0.0, 0.0, 0.0)),
                                 'max': np.array((0.0, 0.0, 0.0)),
                                 'contrast': 1.0,
                                 'blur': 0.0
                                }
                            ],
                            'red':[
                                {'min': np.array((0.0, 0.0, 0.0)),
                                 'max': np.array((0.0, 0.0, 0.0)),
                                 'contrast': 1.0,
                                 'blur': 0.0
                                }
                            ]
                        }

    def getValue(self, color, setting):
        if (setting in ['LH', 'LS', 'LV']):
            return self.config[color][0]['min'][INDEX[setting]]
        if (setting in ['UH', 'US', 'UV']):
            return self.config[color][0]['max'][INDEX[setting]]
        if (setting == 'CT'):
            return self.config[color][0]['contrast']
        if (setting == 'BL'):
            return self.config[color][0]['blur']
        # Brightness is not actually used.
        if (setting == 'BR'):
            return 1

    def setValue(self, color, setting, value):
        if (setting in ['LH', 'LS', 'LV']):
            self.config[color][0]['min'][INDEX[setting]] = value
        if (setting in ['UH', 'US', 'UV']):
            self.config[color][0]['max'][INDEX[setting]] = value
        if (setting == 'CT'):
            self.config[color][0]['contrast'] = value
        if (setting == 'BL'):
            self.config[color][0]['blur'] = value


def brighten(img, alpha=1.0, beta=10.0):
    mul_img = cv2.multiply(img, np.array([alpha]))
    new_img = cv2.add(mul_img,np.array([beta]))
    return new_img

def blur(img, ksize=0):
    if (ksize>1):
        return cv2.blur(img, (ksize,ksize))
    return img

def setWindow(color, maskWindowName):
    cv2.namedWindow(color)
    cv2.namedWindow(maskWindowName)

    fileConfig = FileConfig()

    for setting in CONTROLS:
        cv2.createTrackbar(setting, maskWindowName, int(fileConfig.getValue(color, setting)), \
            MAXBAR[setting], nothing)

    return fileConfig

def run(color):
    
    maskWindowName = "Mask: " + color
    fileConfig = setWindow(color, maskWindowName)
    i = 0
    cap = cv2.VideoCapture(0)

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

        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            for setting in CONTROLS:
                value = cv2.getTrackbarPos(setting, maskWindowName)
                fileConfig.setValue(color, setting, float(value))

            pickleFile = open("configMask.txt", "wb")
            cPickle.dump(fileConfig.config, pickleFile)
            pickleFile.close()
            break

    cv2.destroyAllWindows()
    print fileConfig.config

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