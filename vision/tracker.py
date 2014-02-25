import cv2
import numpy as np
import math
import tools
import cPickle
from colors import PITCH0, PITCH1, KMEANS0
import scipy.optimize as optimization
from collections import namedtuple
import warnings

# Turning on KMEANS fitting:
KMEANS = False

# Turn off warnings for PolynomialFit
warnings.simplefilter('ignore', np.RankWarning)
warnings.simplefilter('ignore', RuntimeWarning)


BoundingBox = namedtuple('BoundingBox', 'x y width height')
Center = namedtuple('Center', 'x y')


class Tracker(object):

    def get_contours(self, frame, adjustments):
        """
        Adjust the given frame based on 'min', 'max', 'contrast' and 'blur'
        keys in adjustments dictionary.
        """
        if adjustments['blur'] > 1:
            frame = cv2.blur(frame, (adjustments['blur'], adjustments['blur']))

        if adjustments['contrast'] > 1.0:
            frame = cv2.add(frame, np.array([adjustments['contrast']]))

        # Convert frame to HSV
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask
        frame_mask = cv2.inRange(frame_hsv, adjustments['min'], adjustments['max'])

        # Apply threshold to the masked image, no idea what the values mean
        return_val, threshold = cv2.threshold(frame_mask, 127, 255, 0)

        # Find contours
        contours, hierarchy = cv2.findContours(
            threshold,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        # print contours
        return contours

    # TODO: Used by Ball tracker - REFACTOR
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

        kernel = np.ones((5, 5), np.uint8)
        erosion = cv2.erode(frame_mask, kernel, iterations=1)

        # Apply threshold to the masked image, no idea what the values mean
        return_val, threshold = cv2.threshold(frame_mask, 127, 255, 0)

        # Find contours, they describe the masked image - our T
        contours, hierarchy = cv2.findContours(
            threshold,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        return (contours, hierarchy, frame_mask)

    def get_contour_extremes(self, cnt):
        """
        Get extremes of a countour.
        """
        leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
        rightmost = tuple(cnt[cnt[:, :, 0].argmax()][0])
        topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
        bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])
        return (leftmost, topmost, rightmost, bottommost)

    def get_corner_points(self, contours):
        """
        Get exact corner points for the plate given contours.
        """
        cnts = []
        for i, cnt in enumerate(contours):
                cnts.append(cnt)
        newcnt = reduce(lambda x, y: np.concatenate((x, y)), cnts)

        rectangle = cv2.minAreaRect(newcnt)
        box = cv2.cv.BoxPoints(rectangle)
        return np.int0(box)

    def get_bounding_box(self, contours):
        if not contours:
            return None

        cnts = []

        for i, cnt in enumerate(contours):
                cnts.append(cnt)

        newcnt = reduce(lambda x, y: np.concatenate((x, y)), cnts)

        # x,y,w,h = cv2.boundingRect(cnt)
        # cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        rect = cv2.minAreaRect(newcnt)
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)
        # cv2.drawContours(frame,[box],0,(0,255,0),2)

        # x, y, w, h = cv2.
        # print box
        # return

        left, top, right, bot = [], [], [], []

        for cnt in contours:
            area = cv2.contourArea(cnt)

            if area > 100:
                # Contours obtained are fragmented, find extreme values
                leftmost, topmost, rightmost, bottommost = self.get_contour_extremes(cnt)

                left.append(leftmost)
                top.append(topmost)
                right.append(rightmost)
                bot.append(bottommost)

        if left and top and right and bot:

            left, top, right, bot = min(left, key=lambda x: x[0])[0], min(top, key=lambda x: x[1])[1], max(right, key=lambda x: x[0])[0], max(bot, key=lambda x: x[1])[1]

            # x, y of top left corner, widht, height
            return (BoundingBox(left, top, right - left, bot - top), box)
        return None


class RobotTracker(Tracker):

    def __init__(self, color, crop, offset, pitch, name, calibration):
        """
        Initialize tracker.

        Params:
            [string] color      the name of the color to pass in
            [(left-min, right-max, top-min, bot-max)]
                                crop  crop coordinates
            [int]       offset          how much to offset the coordinates
            [int]       pitch           the pitch we're tracking - used to find the right colors
            [string]    name            name for debug purposes
            [dict]      calibration     dictionary of calibration values
        """
        self.name = name
        self.crop = crop

        self.color = [calibration[color]]

        self.color_name = color
        self.offset = offset
        self.pitch = pitch
        self.calibration = calibration

    def get_plate(self, frame):
        """
        Given the frame to search, find a bounding rectangle for the green plate

        Returns:
            (x, y, width, height) top left corner x,y
        """
        adjustments = self.calibration['plate']
        contours = self.get_contours(frame.copy(), adjustments)
        return self.get_bounding_box(contours)   # (x, y, width, height)

    def get_dot(self, frame, x_offset, y_offset):
        height, width, channel = frame.shape

        mask_frame = frame.copy()

        cv2.rectangle(mask_frame, (0, 0), (width, height), (0,0,0), -1)
        cv2.circle(mask_frame, (width / 2, height / 2), 9, (255, 255, 255), -1)



        mask_frame = cv2.cvtColor(mask_frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.bitwise_and(frame, frame, mask=mask_frame)

        # cv2.imshow('frame', frame)
        # cv2.waitKey(0)

        adjustments = [self.calibration['dot']]
        for adjustment in adjustments:
            contours = self.get_contours(frame.copy(), adjustment)
            if contours and len(contours) > 0:
                areas = [cv2.contourArea(c) for c in contours]
                max_index = np.argmax(areas)
                cnt=contours[max_index]
                (x,y),radius = cv2.minEnclosingCircle(cnt)
                # Return relative position to the frame given the offset
                return Center(int(x + x_offset), int(y + y_offset))
        #else:
            #print 'No dot found for %s' % self.name

    def get_angle(self, line, dot):
        """
        From dot to line
        """
        diff_x = dot[0] - line[0]
        diff_y = line[1] - dot[1]
        angle = np.arctan2(diff_y, diff_x) % (2 * np.pi)

            # if diff_x < 0 and diff_y > 0:
            #     angle = -abs(angle)

            # if diff_x > 0 and diff_y < 0:
            #     angle = 2 * np.pi - angle
            # if diff_x > 0 and diff_y < 0:
            #    angle = np.pi / 2.0 - angle
            # if diff_x > 0 and diff_y > 0:
            #    angle = np.pi - angle
            # if diff_x < 0 and diff_y > 0:
            #    angle = np.pi + angle
            # if diff_x < 0 and diff_y < 0:
            #    angle = 2 * np.pi - angle
        return angle

    def calcLine(self,(a,b),(d,e)):
        m = (b-e)*1.0/(a-d)
        c1 = b-m*a
        c2 = e-m*d
        c = ((c1+c2)/2)
        return (m,c)

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


        plate_tup = self.get_plate(frame)
        if plate_tup is not None:
            plate = plate_tup[0]

            plate_points = plate_tup[1]

            for p in plate_points:
                p[0] = p[0] + self.offset

            # print plate_points
        else:
            plate = None
            plate_points = None



        if plate and plate.width > 0 and plate.height > 0:

            plate_frame = frame.copy()[plate.y:plate.y + plate.height, plate.x:plate.x + plate.width]

            # Use k-means for detecting the robots if the KMEANS colors are used.
            if KMEANS == True:
                plate_frame = self.kmeans(plate_frame)

            plate_center = Center(plate.x + self.offset + plate.width / 2, plate.y + plate.height / 2)
            dot = self.get_dot(plate_frame.copy(), plate.x + self.offset, plate.y)

            # Euclidean distance
            distance = lambda x, y: np.sqrt((x[0]-y[0])**2 + (x[1]-y[1])**2)

            if self.color_name == 'yellow' or self.color_name == 'blue':

                if dot:
                    points = (dot, plate_center)
                    angle = self.get_angle(dot, plate_center)
                else:
                    points = None
                    angle = None
            else:
                # Only use the center of the detected blue zone if it is within a reasonable distance of the
                # plate center (in order to avoid extremes) and if the distance between the dot and inf_i is greater
                # than the distance between the dot and the plate center.
                if dot:
                    points = (dot, plate_center)
                    angle = self.get_angle(dot, plate_center)
                else:
                    points = None
                    angle = None

            # if self.name == 'Their Attacker' and angle:
                # print "angle", angle
                # print '>>>>>', angle * 360 / (2.0 * np.pi)

            speed = None

            queue.put({
                'name': self.name,
                'location': plate_center,
                'angle': angle,
                'velocity': speed,
                'dot': dot,
                #'i': inf_i,
                'box': BoundingBox(plate.x + self.offset, plate.y, plate.width, plate.height),
                'line': points,
                'plate_points': plate_points
            })
            return

        queue.put({
            'name': self.name,
            'location': None,
            'angle': None,
            'velocity': None,
            'dot': None,
            #'i': None,
            'box': None,
            'line': None
        })
        return

    def kmeans(self, plate):

        prep = plate.reshape((-1,3))
        prep = np.float32(prep)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        k = 4
        ret, label, colour_centers = cv2.kmeans(prep, k, criteria, 20, cv2.KMEANS_RANDOM_CENTERS)
        colour_centers = np.uint8(colour_centers)

        # Get the new image based on the clusters found
        res = colour_centers[label.flatten()]
        res2 = res.reshape((plate.shape))

        # if self.name == 'Their Defender':
        #     colour_centers = np.array([colour_centers])
        #     print "********************", self.name
        #     print colour_centers
        #     print 'HSV######'
        #     print cv2.cvtColor(colour_centers, cv2.COLOR_BGR2HSV)

        return res2


class BallTracker(Tracker):
    """
    Track red ball on the pitch.
    """

    def __init__(self, crop, offset, pitch, calibration, name='ball'):
        """
        Initialize tracker.

        Params:
            [string] color      the name of the color to pass in
            [(left-min, right-max, top-min, bot-max)]
                                crop  crop coordinates
            [int] offset        how much to offset the coordinates
        """
        self.crop = crop
        # if pitch == 0:
        #     self.color = PITCH0['red']
        # else:
        #     self.color = PITCH1['red']
        self.color = [calibration['red']]
        print self.color
        self.offset = offset
        self.name = name
        self.calibration = calibration

    def find(self, frame, queue):
        for color in self.color:
            contours, hierarchy, mask = self.preprocess(
                frame,
                self.crop,
                color['min'],
                color['max'],
                color['contrast'],
                color['blur']
            )

            if len(contours) <= 0:
                # print 'No ball found.'
                pass
                # queue.put(None)
            else:
                # Trim contours matrix
                cnt = contours[0]

                # Get center
                (x, y), radius = cv2.minEnclosingCircle(cnt)

                queue.put({
                    'name': self.name,
                    'location': (int(x) + self.offset, int(y)),
                    'angle': None,
                    'velocity': None
                })
                # queue.put([(x + self.offset, y), angle, speed])
                return

        queue.put(None)
        return
