import cv2
import numpy as np
import cPickle

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

class CalibrationGUI(object):

    def __init__(self, pitch):
        self.color = 'yellow'
        self.pitch = pitch
        self.maskWindowName = "Mask"
        self.key_handler = EventHandler()
       
        self.setWindow()

    def setWindow(self):

        cv2.namedWindow(self.maskWindowName)
        self.config_file = FileConfig()

        for setting in CONTROLS:
            cv2.createTrackbar(setting, self.maskWindowName, int(self.config_file.get_value(self.color, setting)), \
                MAXBAR[setting], nothing)

        def yellow(): self.change_color('yellow')
        def blue(): self.change_color('blue')
        def red(): self.change_color('red')

        self.key_handler.addListener('y', yellow)
        self.key_handler.addListener('b', blue)
        self.key_handler.addListener('r', red)
        self.key_handler.addListener('s', self.save_to_file)

    def change_color(self, color):

        self.color = color
        for setting in CONTROLS:
            cv2.setTrackbarPos(setting, self.maskWindowName, int(self.config_file.get_value(self.color, setting)))

    def save_to_file(self):

        pickle_file = open("vision/configMask.txt", "wb")
        cPickle.dump(self.config_file.config, pickle_file)
        pickle_file.close()
        print "Saved claibration to file."

    def show(self, frame):
        
        LH = cv2.getTrackbarPos("LH", self.maskWindowName)
        UH = cv2.getTrackbarPos("UH", self.maskWindowName)
        LS = cv2.getTrackbarPos("LS", self.maskWindowName)
        US = cv2.getTrackbarPos("US", self.maskWindowName)
        LV = cv2.getTrackbarPos("LV", self.maskWindowName)
        UV = cv2.getTrackbarPos("UV", self.maskWindowName)
        BR = cv2.getTrackbarPos("BR", self.maskWindowName)
        CT = cv2.getTrackbarPos("CT", self.maskWindowName)
        BL = cv2.getTrackbarPos("BL", self.maskWindowName)

        mask = cv2.inRange(frame, np.array([LH, LS, LV]), np.array([UH, US, UV]))

        cv2.imshow(self.maskWindowName, mask)

        for setting in CONTROLS:
            value = cv2.getTrackbarPos(setting, self.maskWindowName)
            self.config_file.set_value(self.color, setting, float(value))

# Holds the object as exported in the pickle and used in tracker.py
# and provides access to its values.
class FileConfig(object):
    
    def __init__(self):
        try:
            pickle_file = open("vision/configMask.txt", "rb")
            self.config = cPickle.load(pickle_file)
            pickle_file.close()
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

    def get_value(self, color, setting):
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

    def set_value(self, color, setting, value):
        if (setting in ['LH', 'LS', 'LV']):
            self.config[color][0]['min'][INDEX[setting]] = value
        if (setting in ['UH', 'US', 'UV']):
            self.config[color][0]['max'][INDEX[setting]] = value
        if (setting == 'CT'):
            self.config[color][0]['contrast'] = value
        if (setting == 'BL'):
            self.config[color][0]['blur'] = value

# Class copied over from Team 6 / 2013
class EventHandler:
        
    def __init__(self):
        self._listeners = {}
        self._clickListener = None
    
    def processKey(self, key):
        if key in self._listeners.keys():
            self._listeners[key]()

    def processClick(self, where):
        if self._clickListener is not None:
            self._clickListener(where)
        
    def addListener(self, key, callback):
        """
        Adds a function callback for a key.
        """
        
        assert callable(callback), '"callback" must be callable'
        
        self._listeners[key] = callback

    def setClickListener(self, callback):
        """
        Sets a function to be called on clicking on the image.
        The function will be passed a tuple with the (x,y) of the click.

        Setting a new callback will override the last one (or pass None to clear)
        """
        assert callback is None or callable(callback), '"callback" must be callable'
        
        self._clickListener = callback
