import cv2
import numpy as np
import cPickle

CONTROLS = ["LH", "UH", "LS", "US", "LV", "UV", "CT", "BL"]
MAXBAR = {"LH":360, 
          "UH":360, 
          "LS":255,
          "US":255,
          "LV":255,
          "UV":255,
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

    def __init__(self, calibration):
        self.color = 'yellow'
        # self.pre_options = pre_options
        self.calibration = calibration
        self.maskWindowName = "Mask"
        self.key_handler = EventHandler()
       
        self.setWindow()

    def setWindow(self):

        cv2.namedWindow(self.maskWindowName)

        createTrackbar = lambda setting, value: cv2.createTrackbar(setting, self.maskWindowName, int(value), \
                MAXBAR[setting], nothing)

        createTrackbar('LH', self.calibration[self.color]['min'][0])
        createTrackbar('UH', self.calibration[self.color]['max'][0])
        createTrackbar('LS', self.calibration[self.color]['min'][1])
        createTrackbar('US', self.calibration[self.color]['max'][1])
        createTrackbar('LV', self.calibration[self.color]['min'][2])
        createTrackbar('UV', self.calibration[self.color]['max'][2])
        createTrackbar('CT', self.calibration[self.color]['contrast'])
        createTrackbar('BL', self.calibration[self.color]['blur'])

        def blue(): self.change_color('blue')
        def red(): self.change_color('red')

        # self.key_handler.addListener('y', yellow)
        # self.key_handler.addListener('b', blue)
        # self.key_handler.addListener('r', red)

    def change_color(self, color):

        self.color = color

        setTrackbarPos = lambda setting, value: cv2.setTrackbarPos(setting, self.maskWindowName, int(value))

        setTrackbarPos('LH', self.calibration[color]['min'][0])
        setTrackbarPos('UH', self.calibration[color]['max'][0])
        setTrackbarPos('LS', self.calibration[color]['min'][1])
        setTrackbarPos('US', self.calibration[color]['max'][1])
        setTrackbarPos('LV', self.calibration[color]['min'][2])
        setTrackbarPos('UV', self.calibration[color]['max'][2])
        setTrackbarPos('CT', self.calibration[color]['contrast'])
        setTrackbarPos('BL', self.calibration[color]['blur'])

    def show(self, frame, key=None):
        
        if key == ord('y'):
            self.change_color('yellow')
        elif key == ord('b'):
            self.change_color('blue')
        elif key == ord('r'):
            self.change_color('red')        

        getTrackbarPos = lambda setting: cv2.getTrackbarPos(setting, self.maskWindowName)

        values = {}
        for setting in CONTROLS:
            values[setting] = getTrackbarPos(setting)

        self.calibration[self.color]['min'] = np.array([values['LH'], values['LS'], values['LV']])
        self.calibration[self.color]['max'] = np.array([values['UH'], values['US'], values['UV']])
        self.calibration[self.color]['contrast'] = values['CT']
        self.calibration[self.color]['blur'] = values['BL']

        mask = cv2.inRange(frame, self.calibration[self.color]['min'], self.calibration[self.color]['max'])
        cv2.imshow(self.maskWindowName, mask)

        # for setting in CONTROLS:
        #     value = cv2.getTrackbarPos(setting, self.maskWindowName)
        #     self.config_file.set_value(self.color, setting, float(value))

# Holds the object as exported in the pickle and used in tracker.py
# and provides access to its values.
# class FileConfig(object):
    
#     def __init__(self):
#         try:
#             pickle_file = open("vision/configMask.txt", "rb")
#             self.config = cPickle.load(pickle_file)
#             pickle_file.close()
#         except:
#             self.config = {'yellow':[
#                                 {'min': np.array((0.0, 0.0, 0.0)), #LH, LS, LV
#                                  'max': np.array((0.0, 0.0, 0.0)), #UH, US, UV
#                                  'contrast': 1.0, #CT
#                                  'blur': 0.0 #BL
#                                 }
#                             ],
#                             'blue':[
#                                 {'min': np.array((0.0, 0.0, 0.0)),
#                                  'max': np.array((0.0, 0.0, 0.0)),
#                                  'contrast': 1.0,
#                                  'blur': 0.0
#                                 }
#                             ],
#                             'red':[
#                                 {'min': np.array((0.0, 0.0, 0.0)),
#                                  'max': np.array((0.0, 0.0, 0.0)),
#                                  'contrast': 1.0,
#                                  'blur': 0.0
#                                 }
#                             ]
#                         }

#     def get_value(self, color, setting):
#         if (setting in ['LH', 'LS', 'LV']):
#             return self.config[color][0]['min'][INDEX[setting]]
#         if (setting in ['UH', 'US', 'UV']):
#             return self.config[color][0]['max'][INDEX[setting]]
#         if (setting == 'CT'):
#             return self.config[color][0]['contrast']
#         if (setting == 'BL'):
#             return self.config[color][0]['blur']
#         # Brightness is not actually used.
#         if (setting == 'BR'):
#             return 1

#     def set_value(self, color, setting, value):
#         if (setting in ['LH', 'LS', 'LV']):
#             self.config[color][0]['min'][INDEX[setting]] = value
#         if (setting in ['UH', 'US', 'UV']):
#             self.config[color][0]['max'][INDEX[setting]] = value
#         if (setting == 'CT'):
#             self.config[color][0]['contrast'] = value
#         if (setting == 'BL'):
#             self.config[color][0]['blur'] = value

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
