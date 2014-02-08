import cv2
import numpy as np
import math
import tools
import cPickle
from colors import PITCH0, PITCH1



# In the code, change COLORS to GUICOLORS if you want to use the values you
# picked with the findHSV GUI.
# GUICOLORS = COLORS

# def get_gui_colors():
#     global GUICOLORS
#     try:
#         pickleFile = open("configMask.txt", "rb")
#         GUICOLORS = cPickle.load(pickleFile)
#         pickleFile.close()
#     except:
#         pass

# get_gui_colors()

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
        return (contours, hierarchy, frame_mask)


class RobotTracker(Tracker):

    def __init__(self, color, crop, offset, pitch):
        """
        Initialize tracker.

        Params:
            [string] color      the name of the color to pass in
            [(left-min, right-max, top-min, bot-max)]
                                crop  crop coordinates
            [int] offset        how much to offset the coordinates
        """
        self.crop = crop
        if pitch == 0:
            self.color = PITCH0[color]
        else:
            self.color = PITCH1[color]
        self.color_name = color
        self.offset = offset
        self.pitch = pitch

    def _find_plate(self, frame, pitch=0):
        """
        Given the frame to search, find a bounding rectangle for the green plate

        Returns:
            (x, y, width, height) top left corner x,y
        """
        # Adjust contrast
        frame = cv2.add(frame, np.array([100.0]))
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if pitch == 0:
            frame_mask = cv2.inRange(
                frame_hsv,
                np.array((57.0, 62.0, 38.0)),
                np.array((85.0, 136.0, 255.0))
            )
        else:
            frame_mask = cv2.inRange(
                frame_hsv,
                np.array((41.0, 63.0, 183.0)),
                np.array((60.0, 255.0, 255.0))
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
        left, right, top, bot = (None, None, None, None)

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

                # Extremely non pythonic. I am sorry.
                if left is None or left > leftmost[0]:
                    left = leftmost[0]
                    points[0] = leftmost

                if top is None or top > topmost[1]:
                    top = topmost[1]
                    points[1] = topmost

                if right is None or right < rightmost[0]:
                    right = rightmost[0]
                    points[2] = rightmost

                if bot is None or bot < bottommost[1]:
                    bot = bottommost[1]
                    points[3] = bottommost

        for i in [left, top, right, bot]:
            if i is None:
                return (None, None, None, None)
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
        for color in self.color:
            lowerBoundary = color['min']
            upperBoundary = color['max']
            contrast = color['contrast']
            blur = color['blur']

            if blur > 1:
                frame = cv2.blur(frame,(blur,blur))
            if contrast > 1:
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
                return (int(x + x_offset), int(y + y_offset))
        return None

    def _find_dot(self, frame, x_offset, y_offset, center=None):
        """
        Given a frame, find a colored dot by masking the image.
        """
        frame = cv2.blur(frame,(5,5))
        frame = cv2.add(frame, np.array([5.0]))

        # Create a mask and remove anything that outside of some fixed radius
        # if center is not None:
        #     mask = frame.copy()
        #     width, height, color_space = mask.shape
        #     cv2.rectangle(mask, (0,0), (width, height), (0.0, 0.0, 0.0), -1)
        #     cv2.circle(mask, center, 16, (255.0, 255.0, 255.0), -1)

        #     mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        #     frame = cv2.bitwise_and(frame,frame, mask=mask)


        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if self.pitch == 0:
            frame_mask = cv2.inRange(
                frame_hsv,
                # Needed to change this for the computer I was on.
                np.array((16.0, 39.0, 47.0)),#(0.0, 0.0, 38.0)),     # grey lower
                np.array((68.0, 132.0, 74.0))#(45.0, 100.0, 71.0))   # grey higher
            )
        else:
            frame_mask = cv2.inRange(
                frame_hsv,
                # Needed to change this for the computer I was on.
                np.array((11.106,0.0,0.0)),#(0.0, 0.0, 38.0)),     # grey lower
                np.array((30.0,140.0,124.0))#(45.0, 100.0, 71.0))   # grey higher
            )

        # Create a mask for the


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
            return (int(x + x_offset), int(y + y_offset))
        return None

    #def get_angle(self, m, n):
    #    """
    #    Find the angle between m and n
    #    """
    #    diff_x = m[0] - n[0]
    #    diff_y = m[1] - n[1]

    #    angle = np.arctan((np.abs(diff_y) * 1.0 / np.abs(diff_x)))
    #    angle = np.degrees(angle)
    #    if diff_x > 0 and diff_y < 0:
    #        angle = 90 - angle
    #    if diff_x > 0 and diff_y > 0:
    #        angle = 180 - angle
    #    if diff_x < 0 and diff_y > 0:
    #        angle = 180+angle
    #    if diff_x < 0 and diff_y < 0:
    #        angle = 360 - angle

    #    return angle
    def calcLine(self,(a,b),(d,e)):
        m = (b-e)*1.0/(a-d)
        c1 = b-m*a
        c2 = e-m*d
        c = ((c1+c2)/2)
        return (m,c)

    def get_angle(self,centerOfPlate,centerOfMass,centerOfDisc):
        """
        Find the angle using the lines between the center points of the features.
        """

        # Work out if the center of the disc is close to being on the line
        # that goes through the center of the plate and the center of the
        # i.
        # If it is, use the center of the disc and the center of the i to
        # calculate the angle.
        # Otherwise, use the center of the plate and the center of the i.

        #print "getting angle"

        m,c = self.calcLine(centerOfMass,centerOfPlate)
        tolerance = 5

        #print np.abs(centerOfDisc[1]- (m*centerOfDisc[0]+c))
        #print np.abs(centerOfDisc[0]- ((centerOfDisc[1]-c)*1.0/m))

        if (m*centerOfDisc[0]+c-tolerance) < centerOfDisc[1] < (m*centerOfDisc[0]+c+tolerance) and ((centerOfDisc[1]-c)*1.0/m-tolerance) < centerOfDisc[0] < ((centerOfDisc[1]-c)*1.0/m+tolerance):
        #    m,c = calcLine(centerOfMass,centerofPlate)
            #print "On line"
            diff_x = centerOfDisc[0] - centerOfMass[0]
            diff_y = centerOfDisc[1] - centerOfMass[1]
        else:
            # Not quite sure about calculating the angle in this case.
            return None

        angle = np.arctan((np.abs(diff_y) * 1.0 / np.abs(diff_x)))
        angle = np.degrees(angle)
        if diff_x > 0 and diff_y < 0:
            angle = 360 - angle
        if diff_x > 0 and diff_y > 0:
            angle = 180 + angle
        if diff_x < 0 and diff_y > 0:
            angle = 90+angle

        return angle

    def _find_gradient(self, m, n):
        """
        Calculate the gradient of
        """
        pass

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
        angle, speed, dot = None, None, None
        i = None

        # 1. Retrieve location of the green plate
        x, y, width, height = self._find_plate(frame.copy(), self.pitch)   # x,y are robot positions

        if width > 0 and height > 0:

            # Find square center
            center_x, center_y = x + width / 2, y + height / 2

            # print x,y
            # 2. Crop image
            plate = frame.copy()[y:y + height, x:x + width]

            # 3. Find colored object - x and y of the 'i'
            plate_location = self._find_i(plate, 'yellow', x, y)

            if plate_location is not None:
                x_i, y_i = plate_location[0], plate_location[1]
            else:
                x_i, y_i = None, None

            # 4. Find black colored plate
            black = self._find_dot(plate, x, y, (center_x, center_y))

            if black is not None:
                black_x = black[0]
                black_y = black[0]
            else:
                black_x, black_y = None, None

            if black_x is not None and black_y is not None:
                dot = (black_x + self.offset, black_y + height*2)

            if x_i is not None and y_i is not None:
                i = (x_i + self.offset, y_i)



            # Try working out the angle based on the center points
            #print [center_x,center_y,x_i,y_i,black_x,black_y]
            if not(None in [center_x,center_y,x_i,y_i,black_x,black_y]):
                angle = self.get_angle((center_x,center_y),(x_i,y_i),(black_x,black_y))
            #print angle




            # # 4. Join the two points
            # if x_i and y_i:
            #     angle = self.get_angle((x, y), (x_i, y_i))

        # 5. Return result
        # if
        if x is None and y is None:
            location = None
            box = None
        else:
            location = (x + self.offset + width / 2, y + height / 2)
            box = (x + self.offset, y, width, height)

        queue.put({
            'location': location,
            'angle': angle,
            'velocity': speed,
            'dot': dot,
            'i': i,
            'box': box
        })
        return


class BallTracker(Tracker):
    """
    Track red ball on the pitch.
    """

    def __init__(self, crop, offset, pitch, name='ball'):
        """
        Initialize tracker.

        Params:
            [string] color      the name of the color to pass in
            [(left-min, right-max, top-min, bot-max)]
                                crop  crop coordinates
            [int] offset        how much to offset the coordinates
        """
        self.crop = crop
        if pitch == 0:
            self.color = PITCH0['red']
        else:
            self.color = PITCH1['red']
        self.offset = offset
        self.name = name

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
                print 'No ball found.'
                # queue.put(None)
            else:
                # Trim contours matrix
                cnt = contours[0]

                # Get center
                (x, y), radius = self.get_min_enclousing_circle(cnt)

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
