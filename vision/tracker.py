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
        },
        {
            'min': np.array((0.0, 181.0, 130.0)),
            'max': np.array((10.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 10
        }
    ],
    'yellow': [
        {
            'min': np.array((0.0, 193.0, 137.0)), #LH,LS,LV
            'max': np.array((50.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
        {
            'min': np.array((6.0, 154.0, 229.0)), #LH,LS,LV
            'max': np.array((130.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
        {
            'min': np.array((10.0, 210.0, 162.0)), #LH,LS,LV
            'max': np.array((20.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        }
    ],
    'blue': [
        { 
            'min': np.array((88.0, 147.0, 82.0)),    #LH,LS,LV
            'max': np.array((104.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 0.0,
            'blur': 0
        },
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
        },
        {	#not too good at edges.
            'min': np.array((80.0, 59.0, 90.0)),	#LH,LS,LV
            'max': np.array((135.0, 142.0, 190.0)),	#UH,US,UV
            'contrast': 1.0,
            'blur': 1
        },
        {   #not too good at edges.
            'min': np.array((80.0, 120.0, 80.0)),    #LH,LS,LV
            'max': np.array((163.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
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
        self.color_name = color
        self.offset = offset

    def _find_plate(self, frame):
        """
        Given the frame to search, find a bounding rectangle for the green plate

        Returns:
            (x, y, width, height) top left corner x,y
        """
        # Adjust contrast
        frame = cv2.add(frame, np.array([100.0]))
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        frame_mask = cv2.inRange(
            frame_hsv,
            np.array((57.0, 62.0, 38.0)),
            np.array((85.0, 136.0, 255.0))
        )

        # Apply threshold to the masked image, no idea what the values mean
        return_val, threshold = cv2.threshold(frame_mask, 127, 255, 0)

        # Find contours for our green plate
        contours, hierarchy = cv2.findContours(
            threshold,
            cv2.RETR_CCOMP,
            cv2.CHAIN_APPROX_TC89_KCOS
        )

        # Hacky!
        # Refactor!
        points = [None for i in range(4)]
        left, right, top, bot = (9999, 0, 9999, 0)

        if not contours:
            contours = []

        for cnt in contours:
            # Contour area
            area = cv2.contourArea(cnt)

            # Reject artifacts from distortion
            if area > 100:
                # Contours obtained are fragmented, find extreme values
                leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
                rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
                topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
                bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])

                # Extremely non pythonic. I am sorry, 3 am has it's toll
                if left > leftmost[0]:
                    left = leftmost[0]
                    points[0] = leftmost

                if top > topmost[1]:
                    top = topmost[1]
                    points[1] = topmost

                if right < rightmost[0]:
                    right = rightmost[0]
                    points[2] = rightmost

                if bot < bottommost[1]:
                    bot = bottommost[1]
                    points[3] = bottommost

        print left, top

        return (left, top, right-left, bot - top)   # (x, y, width, height)

    def _find_i(self, frame, color, x_offset=0, y_offset=0):
        """
        Given a frame, find location of a colored i by masking the image
        and searching for contours.

        Params:
            [np.array] frame    - frame to mask
            [string] color      - name of the color to apply
            [int] x_offset      - correct cropped windows
            [int] y_offset      - correct cropped windows

        Returns:
            [2-tuple] (x_center, y_center) of the object if available
                      (None, None) otherwise
        """
        print frame.shape

        # For now, just use the first set of values in the color list.
        lowerBoundary = COLORS[color][0]['min']
        upperBoundary = COLORS[color][0]['max']
        contrast = COLORS[color][0]['contrast']
        blur = COLORS[color][0]['blur']

        frame = cv2.blur(frame,(blur,blur))
        frame = cv2.add(frame,np.array([contrast]))
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask for the t_yellow T
        frame_mask = cv2.inRange(
            frame_hsv,
            lowerBoundary, #np.array([0, 193, 137], dtype=np.uint8),
            upperBoundary #np.array([50, 255, 255], dtype=np.uint8)
        )

        # Apply threshold to the masked image, no idea what the values mean
        return_val, threshold = cv2.threshold(frame_mask, 127, 255, 0)

        # Find contours, they describe the masked image - our T
        contours, hierarchy = cv2.findContours(
            threshold,
            cv2.RETR_CCOMP,
            cv2.CHAIN_APPROX_TC89_KCOS
        )

        if len(contours) > 0:
            cnt = contours[0]   # Take the largest contour

            (x,y),radius = cv2.minEnclosingCircle(cnt)
            # return (int(x + x_offset), int(y + y_offset))
        return (None, None)

    def _find_dot(self, frame, color, x_offset, y_offset):
        """
        Given a frame, find a colored dot by masking the image.

        TODO!
        """
        pass





    def _find_circle(self, frame, location, offset, search_size=18):
        (x, y) = location


        # Define bounding box for search
        xmin, xmax = x + offset - search_size / 2, x + offset + search_size / 2
        ymin, ymax = y - search_size / 2, y + search_size / 2

        # Trim and convert to grayscale
        box = cv2.cvtColor(frame[ymin:ymax, xmin:xmax], cv2.COLOR_BGR2GRAY)

        # Find circles in the box using Hough Contours
        circles = cv2.HoughCircles(
            box,
            cv2.cv.CV_HOUGH_GRADIENT,
            1, 20, param1=50, param2=10,
            minRadius=3, maxRadius=7
        )

        # calculate angle if circles available
        if circles is not None:
            center = (circles[0][0][0] + xmin, circles[0][0][1] + ymin)
            diff_x = center[0] - x + offset
            diff_y = center[1] - y

            # DEBUG
            # print (diff_x, diff_y)

            angle = np.arctan((np.abs(diff_y) * 1.0 / np.abs(diff_x)))
            angle = np.degrees(angle)
            if diff_x > 0 and diff_y < 0:
                angle = 90 - angle
            if diff_x > 0 and diff_y > 0:
                angle = 180 - angle
            if diff_x < 0 and diff_y > 0:
                angle = 180+angle
            if diff_x < 0 and diff_y < 0:
                angle = 360 - angle

            # What do we need this for???
            speed = (center[0], center[1])
            return (angle, speed)
        else:
            return (None, None)

    def get_angle(self, m, n):
        """
        Find the angle between m and n
        """
        diff_x = m[0] - n[0]
        diff_y = m[1] - n[1]

        angle = np.arctan((np.abs(diff_y) * 1.0 / np.abs(diff_x)))
        angle = np.degrees(angle)
        if diff_x > 0 and diff_y < 0:
            angle = 90 - angle
        if diff_x > 0 and diff_y > 0:
            angle = 180 - angle
        if diff_x < 0 and diff_y > 0:
            angle = 180+angle
        if diff_x < 0 and diff_y < 0:
            angle = 360 - angle

        return angle


    def find(self, frame, queue):
        """
        Retrieve coordinates for the robot, it's orientation and speed - if 
        available.

        Process:
            1. Find green plate by masking
            2. Use result of (1) to crop the image and reduce search space
            3. Find colored object in the result of (2)
            4. Using (1) find center of the box and join with result of (3) to
               produce the orientation
                                            OR
            4. Find black colored circle in the result of (2) and join with (3)
            5. Calculate angle given (4)

            6. Enter result into the queue and return

        Params:
            [np.array] frame                - the frame to scan
            [multiprocessing.Queue] queue   - shared resource for process

        Returns:
            None. Result is put into the queue.
        """
        # Trim and adjust the image
        frame = frame[self.crop[2]:self.crop[3], self.crop[0]:self.crop[1]]

        # Setup vars
        angle = None
        speed = None

        # 1. Retrieve location of the green plate
        x, y, width, height = self._find_plate(frame.copy())   # x,y are robot positions

        if width > 0 and height > 0:
            # print x,y
            # 2. Crop image
            plate = frame[y:y + height, x:x + width]

            # 3. Find colored object - x and y of the 'i'
            x_i, y_i = self._find_i(plate, 'yellow', y, x)

            # # 4. Join the two points
            # if x_i and y_i:
            #     angle = self.get_angle((x, y), (x_i, y_i))

        # 5. Return result
        queue.put((x + self.offset + width / 2, y + height / 2, angle, speed))
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

            if len(contours) <= 0:
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

        originVector = np.array([0,1])
        changeVector = np.array([changeX,changeY])

        denominator = np.sqrt(np.dot(changeVector,changeVector))

        if denominator == 0:
            angle = None
        else:
            angle = np.arccos(
                np.dot(originVector,changeVector) / (np.sqrt(np.dot(changeVector,changeVector)))
            )
            angle = np.degrees(angle)
            if changeX <0:
                angle = 360 - angle
        #print(np.sqrt(np.dot(changeVector,changeVector)))
        
        #print ((changeX,changeY),angle) 
        return (angle,changeX,changeY)
