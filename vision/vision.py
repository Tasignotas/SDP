import cv2
import tools
from tracker import BallTracker, RobotTracker
import math
from multiprocessing import Process, Queue
import sys
from planning.models import Vector


TEAM_COLORS = set(['yellow', 'blue'])
SIDES = ['left', 'right']


class Vision:
    """
    Locate objects on the pitch.
    """

    def __init__(self, side='left', color='yellow', port=0):

        # Check params
        if not self._param_check(side, color):
            return
        
        # Initialize camera
        self._init_camera(port)

        # Retrieve crop values from calibration
        self.calibration = tools.get_calibration('vision/calibrate.json')
        self.crop_values = tools.find_extremes(self.calibration['outline'])

        # print self.crop_values

        self.ball_tracker = BallTracker(
            (0, self.crop_values[1], 0, self.crop_values[3]), 0)

        # Initialize side assignment
        self._init_robot_trackers(side, color)        

    def _param_check(self, side, color):
        """
        Check the params passed in.
        """
        if color not in TEAM_COLORS:
            print 'Incorrect color assignment.', 'Valid colors are:', TEAM_COLORS
            return None
        if side not in SIDES:
            print 'Incorrect side assignment.', 'Valid sides are:', SIDES
            return None
        return True

    def _init_camera(self, port):
        """
        Initialize camera capture.
        """
        # Capture video port
        self.capture = cv2.VideoCapture(port)

        # Read in couple of frames to clear corrupted frames
        for i in range(3):
            status, frame = self.capture.read()

    def _init_robot_trackers(self, side, color):
        """
        Initialize side assignment.
        """
        # Temporary: divide zones into section
        zone_size = int(math.floor(self.crop_values[1] / 4.0))
        
        zones = [(zone_size * i, zone_size * (i + 1), 0, self.crop_values[3]) for i in range(4)]

        # Do set difference to find the other color - if is too long :)
        opponent_color = (TEAM_COLORS - set([color])).pop()

        if side == 'left':
            self.us = [
                RobotTracker(color, zones[0], 0),   # defender
                RobotTracker(color, zones[2], zone_size * 2) # attacker
            ]

            self.opponents = [
                RobotTracker(opponent_color, zones[1], zone_size),
                RobotTracker(opponent_color, zones[3], zone_size * 3)
            ]
        else:
            self.us = [
                RobotTracker(color, zones[1], zone_size),
                RobotTracker(color, zones[3], zone_size * 3)
            ]

            self.opponents = [
                RobotTracker(opponent_color, zones[0], 0),   # defender
                RobotTracker(opponent_color, zones[2], zone_size * 2)
            ]

    def locate(self):
        """
        Find objects on the pitch using multiprocessing.

        Returns:
            [5-tuple] Location of the robots and the ball
        """
        status, frame = self.capture.read()

        # Crop frame
        frame = self._trim_image(frame)

        # Run trackers as processes
        positions = self._run_trackers(frame)

        # Draw positions
        self._draw(frame, positions)

        # NO IDEA WHAT THIS DOES!
        # if positions[4]:
        #     objects[4].oldPos.append(positions[4][0])
        # if len(objects[4].oldPos) > 5:
        #     objects[4].oldPos.pop(0)
        #for i in objects:
        # print objects[4].oldPos
            
        # MULTIPROCESSING DEBUG

        # if hasattr(os, 'getppid'):  # only available on Unix
        #     print 'parent process:', os.getppid()
        # print 'process id:', os.getpid()

        result = {
            'our_attacker': self.to_vector(positions[1]),
            'their_attacker': self.to_vector(positions[3]),
            'our_defender': self.to_vector(positions[0]),
            'their_defender': self.to_vector(positions[2]),
            'ball': self.to_vector(positions[4])
        }
        return result

    def _draw(self, frame, positions):
        # print positions
        for position in positions[:4]:
            cv2.circle(frame, (int(position[0]), int(position[1])), 10, (255, 0, 0), 1)

        print positions[4]

        if positions[4] is not None and positions[4][0] is not None and positions[4][0][0] is not None and positions[4][0][1] is not None:
            cv2.circle(frame, (int(positions[4][0][0]), int(positions[4][0][1])), 8, (0,0,255), 1)

        # Draw results
        # TODO: Convert to a process!
        # for val in positions:
        #     if val is not None:
        #         cv2.circle(frame, (val[0][0], val[0][1]), 10, (0, 255, 0), 1)
        # for i in range(4):
        #     if positions[i] is not None and positions[i][2] is not None:
        #         cv2.circle(frame, (positions[i][2][0],positions[i][2][1]),5,(255,0,0),1)
        #         cv2.line(frame,(positions[i][0][0],positions[i][0][1]),(positions[i][2][0],positions[i][2][1]),(0,0,255),3)

        cv2.imshow('SUCH VISION', frame)
        cv2.waitKey(4)

    def _trim_image(self, frame):
        # Trim the image
        return frame[
            self.crop_values[2]:self.crop_values[3],
            self.crop_values[0]:self.crop_values[1]
        ]

    def _run_trackers(self, frame):
        queues = [Queue() for i in range(5)]
        objects = [self.us[0], self.us[1], self.opponents[0], self.opponents[1], self.ball_tracker]

        # Define processes
        processes = [Process(target=obj.find, args=((frame, queues[i]))) for (i, obj) in enumerate(objects)]

        # Start processes
        for process in processes:
            process.start()

        # Find robots and ball, use queue to 
        # avoid deadlock and share resources
        positions = [q.get() for q in queues]

        # terminate processes
        for process in processes:
            process.join()

        return positions

    def to_vector(self, args):
        """
        Convert a tuple into a vector

        Return a Vector
        """
        return Vector(None, None, None, None)
        if args is not None:
            x, y = args[0] if args[0] is not None else (None, None)
            return Vector(x, y, args[1], args[2])

