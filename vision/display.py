import pygame
import time
import cv
from SimpleCV import Display, DrawingLayer, Image, Blob

class Gui:

    """
    Default layer groups available to display
    First element is the 'base' layer, and must be an image,
    the rest must be features and will be drawn on top
    """
    layersets = {
            'default': ['raw', 'yellow', 'blue', 'ball'],
            'yellow': ['threshY', 'yellow'],
            'blue': ['threshB', 'blue'],
            'ball': ['threshR', 'ball']
            }

    def __init__(self, size=(720, 540)):
        self._layers = {
                # Base layers
                'raw': None,
                'threshY': None,
                'threshB': None,
                'threshR': None,

                # Overlay layers
                'yellow': None,
                'blue': None,
                'ball' : None,
                }

        # These layers are drawn regardless of the current layerset
        self._persistentLayers = {
                'mouse': None
        }

        self._currentLayerset = self.layersets['default']
        self._display = Display(size)
        self._eventHandler = Gui.EventHandler()
        self._lastMouseState = 0
        self._showMouse = True
        self._lastFrame = None
        self._lastFrameTime = time.time()

    def __draw(self):

        iterator = iter(self._currentLayerset)
        
        # First element is the base layer
        baseLayer = self._layers[iterator.next()]

        if baseLayer is None:
            return

        size = baseLayer.size()

        # Draw all entities to one layer (for speed)
        entityLayer = baseLayer.dl()
        for key in iterator:
            toDraw = self._layers[key]
            if toDraw is None:
                continue
            
            elif isinstance(toDraw, DrawingLayer):
                baseLayer.addDrawingLayer(toDraw)

            else:
                toDraw.draw(entityLayer)

        for layer in self._persistentLayers.itervalues():
            if layer is not None:
                baseLayer.addDrawingLayer(layer)

        finalImage = baseLayer.applyLayers()
        self._display.writeFrame(finalImage, fit=False)

    def __updateFps(self):
        smoothConst = 0.1
        thisFrameTime = time.time()

        thisFrame = thisFrameTime - self._lastFrameTime
        if self._lastFrame is not None:
            # Smooth values
            thisFrame = thisFrame * (1 - smoothConst) + smoothConst * self._lastFrame
        
        fps = 1.0 / thisFrame

        self._lastFrame = thisFrame
        self._lastFrameTime = thisFrameTime

        layer = self._layers['raw'].dl()
        layer.ezViewText('{0:.1f} fps'.format(fps), (10, 10))

    def drawCrosshair(self, pos, layerName = None):
        size = self._layers['raw'].size()
        if layerName is not None:
            layer = self.getDrawingLayer()
        else:
            layer = self._layers['raw'].dl()

        layer.line((0, pos[1]), (size[0], pos[1]), color=(0, 0, 255))
        layer.line((pos[0], 0), (pos[0], size[1]), color=(0, 0, 255))

        if layerName is not None:
            self.updateLayer(layerName, layer)

 
    def loop(self):
        """
        Draw the image to the display, and process any events
        """

        for event in pygame.event.get(pygame.KEYDOWN):
            self._eventHandler.processKey(chr(event.key % 0x100))

        self._display.checkEvents()
        mouseX = self._display.mouseX
        mouseY = self._display.mouseY

        if self._showMouse:
            self.drawCrosshair((mouseX, mouseY), 'mouse')

        mouseLeft = self._display.mouseLeft
        # Only fire click event once for each click
        if mouseLeft == 1 and self._lastMouseState == 0:
            self._eventHandler.processClick((mouseX, mouseY))
        
        self._lastMouseState = mouseLeft
        
        # Processing OpenCV events requires calling cv.WaitKey() with a reasonable timeout,
        # which hits our framerate hard (NOTE: Need to confirm this on DICE), so only do
        # this if the focus isn't on the pygame (image) window`
        if not pygame.key.get_focused():
            c = cv.WaitKey(2)
            self._eventHandler.processKey(chr(c % 0x100))

        self.__updateFps()
        self.__draw()

    def getEventHandler(self):
        return self._eventHandler   

    def getDrawingLayer(self):
        return DrawingLayer(self._layers['raw'].size())

    def updateLayer(self, name, layer):
        """
        Update the layer specified by 'name'
        If the layer name is not in the known list of layers, 
        then it will be drawn regardless of the current view setting
        """
        
        if name in self._layers.keys():
            self._layers[name] = layer
        else:
            self._persistentLayers[name] = layer

    def switchLayerset(self, name):
        assert name in self.layersets.keys(), 'Unknown layerset ' + name + '!'

        self._currentLayerset = self.layersets[name]

    def setShowMouse(self, showMouse):
        if not showMouse:
            self.updateLayer('mouse', None)

        self._showMouse = showMouse
        
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


class ThresholdGui:

    def __init__(self, thresholdinstance, gui, window=None):

        if window is None:
            self.window = 'thresh_adjust'
            cv.NamedWindow(self.window, 0)
        else:
            self.window = window

        self._gui = gui
        self.threshold = thresholdinstance

        self._showOnGui = False

        self.__createTrackbars()
        self.__setupKeyEvents()

        self.changeEntity('yellow')
        
    def __setupKeyEvents(self):
        """
        Adds key listeners to the main gui for switching between entities
        """
        
        def yellow(): self.changeEntity('yellow')
        def blue(): self.changeEntity('blue')
        def ball(): self.changeEntity('ball')
        
        keyHandler = self._gui.getEventHandler()
        keyHandler.addListener('y', yellow)
        keyHandler.addListener('b', blue)
        keyHandler.addListener('r', ball)

        keyHandler.addListener('t', self.toggleShowOnGui)
        
        keyHandler.addListener('n', self.normalizeImg)

    def __createTrackbars(self):

        cv.CreateTrackbar('H min', self.window, 0, 179, self.__onTrackbarChanged)
        cv.CreateTrackbar('S min', self.window, 0, 255, self.__onTrackbarChanged)
        cv.CreateTrackbar('V min', self.window, 0, 255, self.__onTrackbarChanged)

        cv.CreateTrackbar('H max', self.window, 0, 179, self.__onTrackbarChanged)
        cv.CreateTrackbar('S max', self.window, 0, 255, self.__onTrackbarChanged)
        cv.CreateTrackbar('V max', self.window, 0, 255, self.__onTrackbarChanged)

        cv.CreateTrackbar('Blur', self.window, 0, 20, self.__onTrackbarChanged)

    def __onTrackbarChanged(self, x):

        allvalues = []
        for which in ['min', 'max']:
            values = []
            for channel in ['H', 'S', 'V']:
                pos = cv.GetTrackbarPos('{0} {1}'.format(channel, which), \
                        self.window)
                
                values.append(pos)
                
            allvalues.append(values)

        self.threshold.updateValues(self.currentEntity, allvalues)
        self.threshold.updateBlur(cv.GetTrackbarPos('Blur', self.window))

    def toggleShowOnGui(self):
        self._showOnGui = not self._showOnGui
        
        if self._showOnGui:
            self._gui.switchLayerset(self.currentEntity)
        else:
            self._gui.switchLayerset('default')
    
    def normalizeImg(self):
        self.threshold.normalizeImg()
        self.changeEntity(self.currentEntity)

    def changeEntity(self, name):
        """
        Change which entity to adjust thresholding
        Can be 'blue', 'yellow' or 'ball'
        """
        
        self.currentEntity = name
        self.setTrackbarValues(self.threshold._values[name], self.threshold._blur)

        # Make sure trackbars update immediately
        cv.WaitKey(2)

        if self._showOnGui:
            self._gui.switchLayerset(name)

    def setTrackbarValues(self, values, blur):
        for i, which in enumerate(['min', 'max']):
            for j, channel in enumerate(['H', 'S', 'V']):
                cv.SetTrackbarPos('{0} {1}'.format(channel, which), \
                        self.window, values[i][j])
        cv.SetTrackbarPos('Blur', self.window, blur)


