import cv2
import numpy as np
import tools
import math


class RedTracker:

    def __init__(self):
        self.frame = self.capture = self.crop = None

    def setup_camera(self, port=0):
        self.capture = cv2.VideoCapture(port)

        # Loop over few frames to clear up initial mess
        for i in range(5):
            status, self.frame = self.capture.read()

        if not status:
            return

        # Get crop coordinates from calibrate.json
        pitch_outline = tools.get_calibration('calibrate.json')['outline']
        self.crop = tools.find_crop_coordinates(self.frame, pitch_outline)
        return True

    def draw_ellipse(self, contours):
        ellipse = cv2.fitEllipse(contours)
        angle = ellipse[2]
        cv2.ellipse(self.frame, ellipse, (0, 0, 255), 3)
        return angle

    def draw_bounding_box(self, contours):
        x, y, w, h = cv2.boundingRect(contours)
        rect = cv2.minAreaRect(contours)
        box = np.int0(cv2.cv.BoxPoints(rect))
        cv2.drawContours(self.frame, [box], 0, (255, 0, 0), 2)

    def get_min_enclousing_circle(self, contours):
        return cv2.minEnclosingCircle(contours)

    def draw_enclosing_circle(self, contours):
        (x,y),radius = self.get_min_enclousing_circle(contours)
        center = (int(x),int(y))
        radius = int(radius)
        cv2.circle(self.frame, center, 10, (0, 255, 0), 2)
        return center

    def draw_crosshair(self, contours):
        (x, y), radius = self.get_min_enclousing_circle(contours)
        x = int(math.floor(x))
        y = int(math.floor(y))
        height, width, channels = self.frame.shape
        cv2.line(self.frame, (0, y), (width, y), (0, 0, 255), 1)
        cv2.line(self.frame, (x, 0), (x, height), (0, 0, 255), 1)

    def draw_fitted_line(self, mask, cnt):
        rows, cols = mask.shape[:2]
        [vx, vy, x, y] = cv2.fitLine(cnt, 1, 3, 0.01, 0, 0.01)
        lefty = int((-x * vy / vx) + y)
        righty = int(((cols - x) * vy / vx) + y)
        cv2.line(self.frame, (cols - 1, righty), (0, lefty), (0, 0, 255), 2)

    def draw_contours(self, contours):
        cv2.drawContours(self.frame, [contours], -1, (0,255,0), -1)

    def get_extreme_points(self, contours):
        leftmost = tuple(contours[contours[:,:,0].argmin()][0])
        rightmost = tuple(contours[contours[:,:,0].argmax()][0])
        topmost = tuple(contours[contours[:,:,1].argmin()][0])
        bottommost = tuple(contours[contours[:,:,1].argmax()][0])

        return (leftmost, rightmost, topmost, bottommost)

    def draw_extremes(self, contours):
        leftmost, rightmost, topmost, bottommost = self.get_extreme_points(contours)
        cv2.circle(self.frame, leftmost, 2, (0,0,255), -1)
        cv2.circle(self.frame, rightmost, 2, (0,255,0), -1)
        cv2.circle(self.frame, topmost, 2, (255,0,0), -1)
        cv2.circle(self.frame, bottommost, 2, (0,0,0), -1)

    def run(self, gui=True, port=0):
	predictionpoints = []
        status = self.setup_camera(port)

        if not status:
            print 'Camera not available'
            return

        k = True

        fast = cv2.FastFeatureDetector()
        sift = cv2.SIFT()

        # Terminate program by pressing q
        while k != ord('q'):
            # Read frame
            status, self.frame = self.capture.read()

            # Crop frame
            self.frame = self.frame[self.crop[2]:self.crop[3], self.crop[0]:self.crop[1]]

            self.original = self.frame.copy()

            # Set Contrast
            self.frame = cv2.add(self.frame, np.array([100.0]))
            # self.frame = cv2.multiply(self.frame, np.array([2.0]))

            # Convert frame to HSV
            frame_hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

            # Create a mask for the t_yellow T
            frame_mask = cv2.inRange(
                frame_hsv,
                np.array((57.0, 62.0, 38.0)),
                np.array((85.0, 136.0, 255.0))
            )

            self.frame = cv2.bitwise_and(self.frame, self.frame,mask=frame_mask)

            grey = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)

            kp = fast.detect(grey, None)
            cv2.drawKeypoints(frame_mask, kp, color=(255,0,0))

            # kp = sift.detect(frame_mask, None)

            # cv2.drawKeypoints(self.frame, kp)

            cv2.imshow('mask mask', frame_mask)
            cv2.imshow('frame', self.frame)

            k = cv2.waitKey(2) & 0xFF


y = RedTracker()
y.run()
