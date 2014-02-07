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

    def __init__(self, side='right', color='yellow', port=0, pitch=0):

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
        self._init_robot_trackers(side, color, pitch)

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

    def _init_robot_trackers(self, side, color, pitch=0):
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
                RobotTracker(color, zones[0], 0, pitch),   # defender
                RobotTracker(color, zones[2], zone_size * 2, pitch) # attacker
            ]

            self.opponents = [
                RobotTracker(opponent_color, zones[1], zone_size, pitch),
                RobotTracker(opponent_color, zones[3], zone_size * 3, pitch)
            ]
        else:
            self.us = [
                RobotTracker(color, zones[1], zone_size, pitch),
                RobotTracker(color, zones[3], zone_size * 3, pitch)
            ]

            self.opponents = [
                RobotTracker(opponent_color, zones[0], 0, pitch),   # defender
                RobotTracker(opponent_color, zones[2], zone_size * 2, pitch)
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

    def _draw(self, frame, positions, our_color='yellow'):
        """
        Draw positions from the trackers on the screen.

        Params:
            [np.array] frame    - the frame to draw on
            [5-tuple] positions - positions of the robots and the ball

        Returns:
            None. Image is displayed
        """
        # Draw our robots
        for position in positions[:2]:
            self._draw_robot(frame, position, our_color)

        for position in positions[2:4]:
            self._draw_robot(frame, position, list(TEAM_COLORS - set(our_color))[0])

        self._draw_ball(frame, positions[4])

        cv2.imshow('SUCH VISION', frame)
        cv2.waitKey(4)

    def _draw_robot(self, frame, position, color):
        """
        Draw the location of the robots given the color
        """
        colors = {
            'yellow': (0, 255, 255),
            'blue': (255, 0, 0)
        }
        if position:
            center = position['location']
            cv2.circle(frame, center, 16, colors[color], 1)

        if 'dot' in position.keys():
            self._draw_dot(frame, position['dot'])

        if 'i' in position.keys():
            self._draw_i(frame, position['i'])

        if 'i' in position.keys() and 'dot' in position.keys():
            self._draw_angle(frame, position['dot'], center)

    def _draw_i(self, frame, position):
        if position:
            cv2.circle(frame, (position[0], position[1]), 1, (255, 255, 255), -1)

    def _draw_dot(self, frame, position):
        if position:
            cv2.circle(frame, (position[0], position[1]), 1, (255, 255, 255), -1)

    def _draw_angle(self, frame, dot, i):
        if dot and i:
            x_diff, y_diff = (dot[0] - i[0]) * 3, (dot[1] - i[1]) * 3
            endpoint = (i[0] + x_diff, i[1] + y_diff)
            cv2.line(frame, i, endpoint, (255,255,255), 1)

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
        keys = args.keys() if args is not None else []
        x, y, angle, velocity = None, None, None, None
        if 'location' in keys:
            x, y = args['location']
        if 'angle' in keys:
            angle = args['angle']
        if 'velocity' in keys:
            velocity = args['velocity']

        return Vector(x, y, angle, velocity)


class Camera(object):
    """
    Camera access wrapper.
    """

    def __init__(self, port=0):
        self.capture = cv2.VideoCapture(port)

    def get_frame(self):
        """
        Retrieve a frame from the camera.

        Returns the frame if available, otherwise returns None.
        """
        status, frame = self.capture.read()
        if status:
            return frame
