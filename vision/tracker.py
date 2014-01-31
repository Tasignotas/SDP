import cv2
import numpy as np
import math
import tools


COLORS = {
    'red': (np.array((0.0, 114.0, 250.0)), np.array((5.0, 255.0, 255.0))),
    'yellow': (np.array((0.0, 193.0, 137.0)), np.array((50.0, 255.0, 255.0))),
    'blue': (np.array((87.0, 147.0, 82.0)), np.array((104.0, 255.0, 255.0)))
}


class Tracker:

    def __init__(self, color, crop, offset, contrast=1.0, blur=1):
        self.crop = crop
        self.contrast = contrast
        self.blur = blur
        self.color = COLORS[color]
        self.offset = offset
        self.oldPos = None

    def get_min_enclousing_circle(self, contours):
        return cv2.minEnclosingCircle(contours)

    def find(self, frame, queue, i=0):
        """
        Find object definied in init.
        Put result into the queue to retrieve by main process.
        """
        # Crop frame
        frame = frame[self.crop[2]:self.crop[3], self.crop[0]:self.crop[1]]

        # Apply simple kernel blur
        # Take a matrix given by second argument and calculate average of those pixels
        if self.blur > 1:
            frame = cv2.blur(frame, (self.blur, self.blur))

        # Set Contrast
        if self.contrast > 1.0:
            frame = cv2.add(frame, np.array([self.contrast]))

        # Convert frame to HSV
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask
        frame_mask = cv2.inRange(frame_hsv, self.color[0], self.color[1])

        # Apply threshold to the masked image, no idea what the values mean
        return_val, threshold = cv2.threshold(frame_mask, 127, 255, 0)

        # Find contours, they describe the masked image - our T
        contours, hierarchy = cv2.findContours(
            threshold,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        cv2.imshow('mask' + str(i), frame_mask)
        cv2.waitKey(4)


        if len(contours) <= 0 or len(contours[0]) < 5:
            print 'No contours found.'
            queue.put(None)
        else:
            # Trim contours matrix
            cnt = contours[0]

            # Get center
            (x, y), radius = self.get_min_enclousing_circle(cnt)

            x = int(x)
            y = int(y)
 
            newX,newY = (x + self.offset, y)
           
            if self.oldPos:
                angle,changeX,changeY = self.getOrientation((newX,newY))
                speed = np.sqrt(changeX**2 + changeY**2) # in pixels per frame
                
            #((x,y),orientation,speed)
                queue.put(((x + self.offset, y), angle, speed))
            else:
                queue.put(((x+self.offset,y),0,0))
            self.oldPos = (newX,newY)

    def getOrientation(self):
        pass

class RobotTracker(Tracker):
    def __init__(self, color, crop, offset, contrast=1.0, blur=1):
        Tracker.__init__(self, color, crop, offset, contrast=1.0, blur=1)
        self.oldPos = True

    def getOrientation(self,newPos):
        return (0,0,0)
        
class BallTracker(Tracker):
    def getOrientation(self,newPos):
        oldX,oldY = self.oldPos
        changeX = newX-oldX
        changeY = newY-oldY 
                #alpha = 100
                #cv2.line(frame,(newX,newY),(newX+alpha*changeX,newY+alpha*changeY),(0,255,0),3)
        k = np.arctan2(changeX,changeY)
        if k<0:
            k = np.abs(k) + np.pi
        angle = k * 180/np.pi

        return (angle,changeX,changeY)
