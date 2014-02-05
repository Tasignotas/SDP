import cv2
import tools
from tracker import BallTracker, RobotTracker
import math
from multiprocessing import Process, Queue
import sys
from planning.models import Vector


TEAM_COLORS = set(['yellow', 'blue'])
SIDES = ['left', 'right']

PROCESSING_DEBUG = False


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

        Params:
            [string] side   - our side
            [string] color  - our color

        Returns:
            None.
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
            
        # MULTIPROCESSING DEBUG
        if PROCESSING_DEBUG:
            if hasattr(os, 'getppid'):  # only available on Unix
                print 'Parent process:', os.getppid()
            print 'Process id:', os.getpid()

        result = {
            'our_attacker': self.to_vector(positions[1]),
            'their_attacker': self.to_vector(positions[3]),
            'our_defender': self.to_vector(positions[0]),
            'their_defender': self.to_vector(positions[2]),
            'ball': self.to_vector(positions[4])
        }

        return result

    def _draw(self, frame, positions):
        """
        Draw positions from the trackers on the screen.

        Params:
            [np.array] frame    - the frame to draw on
            [5-tuple] positions - positions of the robots and the ball

        Returns:
            None. Image is displayed
        """

        
        
        # Hacky! Refactor!
        for position in positions[:4]:
            cv2.circle(frame, (int(position[0]), int(position[1])), 10, (255, 0, 0), 1)

        self._draw_ball(frame, positions[4])

        # print positions[4]

        # if positions[4] is not None and positions[4][0] is not None and positions[4][0][0] is not None and positions[4][0][1] is not None:
        #     cv2.circle(frame, (int(positions[4][0][0]), int(positions[4][0][1])), 7, (0,0,255), 1)

        cv2.imshow('SUCH VISION', frame)
        cv2.waitKey(4)

    def _draw_ball(self, frame, position):
        """
        Draw the ball as a circle. In place.

        Params:
            [dict] positions    - information about the location of the ball
        """
        if position is not None:
            center = position['location']
            cv2.circle(frame, center, 7, (0, 0, 255), 2)

    def _trim_image(self, frame):
        """
        Given a frame, crop it to the size given in self.crop_values

        Returns:
            Cropped image
        """
        return frame[
            self.crop_values[2]:self.crop_values[3],
            self.crop_values[0]:self.crop_values[1]
        ]

    def _run_trackers(self, frame):
        """
        Run trackers as separate processes

        Params:
            [np.frame] frame        - frame to run trackers on

        Returns:
            [5-tuple] positions     - locations of the robots and the ball
        """
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
