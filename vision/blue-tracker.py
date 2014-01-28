import cv2
import numpy as np
import tools
import math


class BlueTracker:

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

    def euclidean_distance(self, m, n):
        m = m[0]
        n = n[0]
        return math.pow(abs(m[0] - n[0]), 2) + math.pow(abs(m[1] - n[1]), 2)

    def furthest_apart(self, points):
        distance = float('-inf')
        x, y, z = points.shape
        index = -1
        for i in range(0, x - 1):
            curr_dist = self.euclidean_distance(points[i], points[i+1])
            if curr_dist > distance:
                distance = curr_dist
                index = i

        return (points[index], points[index+1])

    def measure_segments(self, points):
        dummy = []
        x, y, z = points.shape
        for i in range(0, x):
            m = points[i][0]
            n = points[(i+1) % x][0]
            dummy.append(
                (
                    (m[0], m[1]), 
                    (n[0], n[1]), 
                    self.euclidean_distance(points[i], points[(i+1) % x])
                )
            )


        dummy.sort(key=lambda x: x[2], reverse=True)
        return dummy

    def draw_ellipse(self, contours):
        ellipse = cv2.fitEllipse(contours)
        angle = ellipse[2]
        cv2.ellipse(self.frame, ellipse, (0, 0, 255), 3)
        return angle

    def draw_bounding_box(self, contours):
        x, y, w, h = cv2.boundingRect(contours)
        rect = cv2.minAreaRect(contours)
        box = np.int0(cv2.cv.BoxPoints(rect))
        cv2.drawContours(self.frame, [box], 0, (0, 0, 255), 2)

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

    def approx_poly(self, curve):
        return cv2.approxPolyDP(curve, 2, True)

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
            # self.frame = cv2.add(self.frame, np.array([100.0]))

            # Convert frame to HSV
            frame_hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2XYZ)

            # Create a mask for the yellow T
            frame_mask = cv2.inRange(
                frame_hsv,
                np.array((1.0, 75.0, 145.0)),
                np.array((25.0, 112.0, 255.0))
            )

            # Display the masked image
            if gui:
                cv2.imshow('Masked image', frame_mask)

            # Apply threshold to the masked image, no idea what the values mean
            return_val, threshold = cv2.threshold(frame_mask, 127, 255, 0)

            # Find contours, they describe the masked image - our T
            contours, hierarchy = cv2.findContours(
                threshold,
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE
            )

            if len(contours) <= 0 or len(contours[0]) < 5:
                print 'No contours found.'
            else:
                # Trim contours matrix
                cnt = contours[0]

                # Draw bounding ellipse and get the ellipse angle
                # angle = self.draw_ellipse(cnt)
                # print angle

                poly = self.approx_poly(cnt)
                print poly.shape

                segments = self.measure_segments(poly)

                front =  self.furthest_apart(poly)

                left = front[0][0]
                right = front[1][0]

                x1, y1 = left
                x2, y2 = right

                cv2.line(self.frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                for segment in segments[1:3]:
                    (x1, y1), (x2, y2), length = segment
                    cv2.line(self.frame, (x1, y1), (x2, y2), (255, 0, 0), 1)

                # Draw a rotated bounding box around the T
                # self.draw_bounding_box(cnt)

                # Fit a line into the T
                # self.draw_fitted_line(frame_mask, cnt)

                # Draw contours as filled object
                # self.draw_contours(cnt)

                # Find extreme values - left most, topmost, rightmost and bottom most values of the T
                # self.draw_extremes(cnt)

            # Display feed
            if gui:
                cv2.imshow('Yellow Tracker', self.frame)

            # Wait for 4ms before continuing, terminate by pressing 'q'
            k = cv2.waitKey(2) & 0xFF



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

y = BlueTracker()
y.run()