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
        # Terminate program by pressing q
        while k != ord('q'):
            # Read frame
            status, self.frame = self.capture.read()

            # Crop frame
            self.frame = self.frame[self.crop[2]:self.crop[3], self.crop[0]:self.crop[1]]

            # Apply simple kernel blur
            # Take a matrix given by second argument and calculate average of those pixels
            # self.frame = cv2.blur(self.frame, (5, 5))

            # Set Contrast
            # self.frame = cv2.add(self.frame, np.array([100.0]))

            # Convert frame to HSV
            frame_hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

            # Create a mask for the t_yellow T
            frame_mask = cv2.inRange(
                frame_hsv,
                np.array((0.0, 181.0, 130.0)),
                np.array((10.0, 255.0, 255.0))
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

                # Draw a rotated bounding box around the T
                # self.draw_bounding_box(cnt)

                # Draw enclousing circle
                # self.draw_enclosing_circle(cnt)

                # Draw crosshair
                self.draw_crosshair(cnt)

                # Fit a line into the T
                # self.draw_fitted_line(frame_mask, cnt)

                # Draw contours as filled object
                # self.draw_contours(cnt)

                # Find extreme values - left most, topmost, rightmost and bottom most values of the T
                # self.draw_extremes(cnt)

		point,radius = self.get_min_enclousing_circle(cnt)
                alpha = 50
                newX,newY = point
#                if oldPos:

            
		if len(predictionpoints) > 1:
			predictionpoints.pop(0)
			predictionpoints.append(point)
			x1, y1 = predictionpoints[0][0], predictionpoints[0][1]
			x2, y2 = predictionpoints[1][0], predictionpoints[1][1]
###############
                        oldX,oldY = x1,y1
                        changeX = newX-oldX
                        changeY = newY-oldY
                        cv2.line(self.frame,(int(newX),int(newY)),(int(newX+alpha*changeX),int(newY+alpha*changeY)),(0,255,0),1)
###############

#			try:
#				gradient = (y2-y1)/(x2-x1)
#			except ZeroDivisionError:
#				gradient = 0
#			constant = y2-gradient*x2
#
#			if abs(x2-x1) >0.25 and abs(y2-y1)>0.25: #only draw line if it moves fast enough.
#				if gradient <0:	#negative gradient
#					if x2 > x1:
#						cv2.line(self.frame, predictionpoints[0], (-constant/gradient,0), (0, 255, 0), 2)
#					else:
#						cv2.line(self.frame, predictionpoints[0], (0,constant), (0, 255, 0), 2)
#				else: #positive gradient
#					if x2 > x1:
#						cv2.line(self.frame, predictionpoints[0], ((285-constant)/gradient,285), (0, 255, 0), 2) #hardcoded the so called edge, value 285 needs to be readjusted
#					else:
#						cv2.line(self.frame, predictionpoints[0], (0,constant), (0, 255, 0), 2)
#			#calculating velocity, sampling over two frames. Origin is at top left corner of video feed.
#			velocity = [(y2-y1)*1000/25,(x2-x1)*1000/25] #units are pixels per millisecond
#			#print "Velocity =", velocity[1],"i +", velocity[0],"j"
#
		else:
			predictionpoints.append(point)

            # Display feed
            if gui:
                cv2.imshow('Red Ball Tracker', self.frame)

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

y = RedTracker()
y.run()
