import cv2
import numpy as np
import tools
import math


class YellowTracker:

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

    def draw_ellipse(self, contours):
        ellipse = cv2.fitEllipse(contours)
        angle = ellipse[2]
        cv2.ellipse(self.frame, ellipse, (0, 0, 255), 3)
        return angle

    def draw_bounding_box(self, contours):
        x, y, w, h = cv2.boundingRect(cnt)
        rect = cv2.minAreaRect(cnt)
        box = np.int0(cv2.cv.BoxPoints(rect))
        cv2.drawContours(self.frame, [box], 0, (0, 0, 255), 1)

    def draw_fitted_line(self, mask):
        rows, cols = mask.shape[:2]
        [vx, vy, x, y] = cv2.fitLine(cnt, 1, 0, 0.01, 0.01)
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

    def draw_extreme_points(self, contours):
        leftmost, rightmost, topmost, bottommost = self.get_extreme_points(contours)
        cv2.circle(self.frame, leftmost, 2, (0,0,255), -1)
        cv2.circle(self.frame, rightmost, 2, (0,255,0), -1)
        cv2.circle(self.frame, topmost, 2, (255,0,0), -1)
        cv2.circle(self.frame, bottommost, 2, (0,0,0), -1)

    def run(self, gui=True, port=0):
        status = self.setup_camera(port)

        if not status:
            print 'Camera not available'
            return

        k = True
        # Terminate program by pressing q
        while k != ord('q'):
            # Read frame
            status, self.frame = self.capture.read()

            # Crop frame
            self.frame = self.frame[self.crop[2]:self.crop[3], self.crop[0]:self.crop[1]]

            # Apply simple kernel blur
            # Take a matrix given by second argument and calculate average of those pixels
            self.frame = cv2.blur(self.frame, (5, 5))

            # Set Contrast
            self.frame = cv2.add(self.frame, np.array([100.0]))

            # Convert frame to HSV
            frame_hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

            # Create a mask for the yellow T
            frame_mask = cv2.inRange(
                frame_hsv,
                np.array((15.0, 115.0, 255.0)),
                np.array((360.0, 255.0, 255.0))
            )

            # Display the masked image
            if gui:
                cv2.imshow('Masked image', frame_mask)

            # Apply threshold to the masked image, no idea what the values mean
            return_val, threshold = cv2.threshold(mask, 127, 255, 0)

            # Find contours, they describe the masked image - our T
            contours, hierarchy = cv2.findContours(
                threshold,
                cv2.RETR_LIST,
                cv2.CHAIN_APPROX_SIMPLE
            )

            if len(contours) <= 0 or len(contours[0]) < 5:
                print 'No contours found.'
            else:
                # Trim contours matrix
                cnt = contours[0]

                # Draw bounding ellipse and get the ellipse angle
                angle = self.draw_ellipse(cnt)

                # Draw a rotated bounding box around the T
                self.draw_bounding_box(cnt)

                # Fit a line into the T
                self.draw_fitted_line(frame_mask)

                # Draw contours as filled object
                self.draw_contours(cnt)

                # Find extreme values - left most, topmost, rightmost and bottom most values of the T
                self.draw_extremes(cnt)

            # Display feed
            if gui:
                cv2.imshow('Yellow Tracker', self.frame)

            # Wait for 4ms before continuing, terminate by pressing 'q'
            k = cv2.waitKey(4) & 0xFF



# MAC's code, not refactored just yet

# ## removing outliars, so modifying the marker will not be necessary
# if len(stack) > 5:
#   stack.pop(0)
#   stack.append(multiplier * angle)
# else:
#   stack.append(multiplier * angle)

# mean = sum(stack)/len(stack)

# if abs(mean - stack[-1]) > 50: # if latest value jumps by more than 50 degrees, simple outlier checking...
#   print "jump!!"
#   stack.pop() # discard that value
# print sum(stack)/len(stack)

y = YellowTracker()
y.run()