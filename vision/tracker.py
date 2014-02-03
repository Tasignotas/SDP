import cv2
import numpy as np
import math
import tools


COLORS = {
    'red': [
        {
            'min': np.array((0.0, 114.0, 250.0)),
            'max': np.array((5.0, 255.0, 255.0)),
            'contrast': 100.0,
            'blur': 5
        }
    ],
    'yellow': [
        {
            'min': np.array((0.0, 193.0, 137.0)),
            'max': np.array((50.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        }
    ],
    'blue': [
        {
            'min': np.array((87.0, 147.0, 82.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        },
        {
            'min': np.array((87.0, 105.0, 82.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        },
        {
            'min': np.array((87.0, 100.0, 90.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        }
           
    ]
    # (np.array((91.0, 118.0, 90.0)), np.array((169.0, 255.0, 255.0)), 1.0, 1)
}


class Tracker(object):

    def get_min_enclousing_circle(self, contours):
        """
        Find the smallest enclousing circle for an object given contours
        """
        return cv2.minEnclosingCircle(contours)

    def preprocess(self, frame, crop, min_color, max_color, contrast, blur):
        # Crop frame
        frame = frame[crop[2]:crop[3], crop[0]:crop[1]]

        # Apply simple kernel blur
        # Take a matrix given by second argument and calculate average of those pixels
        if blur > 1:
            frame = cv2.blur(frame, (blur, blur))

        # Set Contrast
        if contrast > 1.0:
            frame = cv2.add(frame, np.array([contrast]))

        # Convert frame to HSV
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask
        frame_mask = cv2.inRange(frame_hsv, min_color, max_color)

        # Apply threshold to the masked image, no idea what the values mean
        return_val, threshold = cv2.threshold(frame_mask, 127, 255, 0)

        # Find contours, they describe the masked image - our T
        contours, hierarchy = cv2.findContours(
            threshold,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        return (contours, hierarchy)


class RobotTracker(Tracker):

    def __init__(self, color, crop, offset):
        """
        Initialize tracker.

        Params:
            [string] color      the name of the color to pass in
            [(left-min, right-max, top-min, bot-max)] 
                                crop  crop coordinates
            [int] offset        how much to offset the coordinates
        """
        self.crop = crop
        self.color = COLORS[color]
        self.offset = offset


    def find(self, frame, queue):
        for color in self.color:
            contours, hierarchy = self.preprocess(
                frame,
                self.crop,
                color['min'], 
                color['max'], 
                color['contrast'], 
                color['blur']
            )

            if len(contours) <= 0 or len(contours[0]) < 5:
                print 'No contours found.'
                # queue.put(None)
            else:
                # Trim contours matrix
                cnt = contours[0]

                # Get center
                (x, y), radius = self.get_min_enclousing_circle(cnt)

                x = int(x)
                y = int(y)

  #          xmin = np.minimum(x+3*radius,x-3*radius)
 #           xmax = np.maximum(x+3*radius,x-3*radius)            

#            ymin = np.minimum(y+3*radius,y-3*radius)
#            ymax = np.maximum(y+3*radius,y-3*radius)            

#            roi = frame[ymin:ymax,xmin:xmax]
# https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_houghcircles/py_houghcircles.html

#            roi = cv2.medianBlur(roi,5)
#            roi = cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
#            circles = cv2.HoughCircles(roi,cv2.cv.CV_HOUGH_GRADIENT,1,20,param1=50,param2=10,minRadius=3,maxRadius=7)
#            return  circles,roi
     

                angle, speed = None, None
                queue.put(((x + self.offset, y), angle, speed))
                return
        queue.put(None)
        return

        
class BallTracker(Tracker):
        
    def __init__(self, crop, offset):
        """
        Initialize tracker.

        Params:
            [string] color      the name of the color to pass in
            [(left-min, right-max, top-min, bot-max)] 
                                crop  crop coordinates
            [int] offset        how much to offset the coordinates
        """
        self.crop = crop
        self.color = COLORS['red']
        self.offset = offset
        #self.oldPos = (0,0)#None
        self.oldPos = [(0,0)]

    def find(self, frame, queue):
        for color in self.color:
            contours, hierarchy = self.preprocess(
                frame,
                self.crop,
                color['min'], 
                color['max'], 
                color['contrast'], 
                color['blur']
            )

            if len(contours) <= 0 or len(contours[0]) < 5:
                print 'No contours found.'
                # queue.put(None)
            else:
                # Trim contours matrix
                cnt = contours[0]

                # Get center
                (x, y), radius = self.get_min_enclousing_circle(cnt)

                x = int(x)
                y = int(y)
     
                newX,newY = (x + self.offset, y)
               
                #if not self.oldPos:#==(-1,-1):
                    #self.oldPos = (0,0)
     #            angle,changeX,changeY = self.getOrientation((newX,newY))
                vector = self.getOrientation((newX,newY))#,prevPos)
                angle = vector[0]
                changeX = vector[1]
                changeY = vector[2]
                speed = np.sqrt(changeX**2 + changeY**2) # in pixels per frame                
                 #((x,y),orientation,speed)
                #self.oldPos = (0,0)
                #return ((x + self.offset, y), angle, speed)
                #angle, speed = None, None
                queue.put(((x + self.offset, y), angle, speed))
                return

        queue.put(None)
        return

    def getOrientation(self,newPos):
#        if self.
        oldX,oldY = self.oldPos[-1]
        changeX = newPos[0]-oldX
        changeY = newPos[1]-oldY
        if np.abs(changeX) <2 or np.abs(changeY) <2:
            changeX = newPos[0] - self.oldPos[0][0]
            changeY = newPos[1] - self.oldPos[0][1]
                 #alpha = 100
                 #cv2.line(frame,(newX,newY),(newX+alpha*changeX,newY+alpha*changeY),(0,255,0),3)
        k = np.arctan2(changeY,changeX)
        #if k<0:
        #k = np.abs(k) + np.pi
        #angle = k * 180/np.pi
        angle = np.degrees(k)

# Work out angle between y axis and change vector
# seems to work a little better, but is always between
# 0 and 180 degrees.
        originVector = np.array([0,1])
        changeVector = np.array([changeX,changeY])
        angle = np.arccos(np.dot(originVector,changeVector)/np.sqrt(np.dot(changeVector,changeVector)))
        angle = np.degrees(angle)
        print ((changeX,changeY),angle) 
        return (angle,changeX,changeY)
