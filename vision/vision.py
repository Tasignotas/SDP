import cv2
import tools
from tracker import BallTracker, RobotTracker
import math
from multiprocessing import Process, Queue
import sys
from planning.models import Vector
from colors import BGR_COMMON
from collections import namedtuple


TEAM_COLORS = set(['yellow', 'blue'])
SIDES = ['left', 'right']
PITCHES = [0, 1]

PROCESSING_DEBUG = False


class Vision:
    """
    Locate objects on the pitch.
    """

    def __init__(self, pitch, color, our_side, frame_shape):
        """
        Initialize the vision system.

        Params:
            [int] pitch         pitch number (0 or 1)
            [string] color      color of our robot
            [string] our_side   our side
        """
        self.pitch = pitch
        self.color = color
        self.our_side = our_side

        height, width, channels = frame_shape

        zone_size = int(math.floor(width / 4.0))

        zones = [(val[0], val[1], 0, height) for val in tools.get_zones(width, height)]
        self.zones = zones

        # zones = [(zone_size * i, zone_size * (i + 1), 0, height) for i in range(4)]
        # print zones

        # Do set difference to find the other color - if is too long :)
        opponent_color = (TEAM_COLORS - set([color])).pop()

        if our_side == 'left':
            self.us = [
                RobotTracker(color=color, crop=zones[0], offset=zones[0][0], pitch=pitch, name='Our Defender'),   # defender
                RobotTracker(color=color, crop=zones[2], offset=zones[2][0], pitch=pitch, name='Our Attacker') # attacker
            ]

            self.opponents = [
                RobotTracker(opponent_color, zones[1], zones[1][0], pitch, 'Their Defender'),
                RobotTracker(opponent_color, zones[3], zones[3][0], pitch, 'Their Attacker')
            ]
        else:
            self.us = [
                RobotTracker(color, zones[1], zones[1][0], pitch, 'Our Defender'),
                RobotTracker(color, zones[3], zones[3][0], pitch, 'Our Attacker')
            ]

            self.opponents = [
                RobotTracker(opponent_color, zones[0], zones[0][0], pitch, 'Their Defender'),   # defender
                RobotTracker(opponent_color, zones[2], zones[2][0], pitch, 'Their Attacker')
            ]

        # Set up trackers
        self.ball_tracker = BallTracker(
            (0, width, 0, height), 0, pitch)

    def locate(self, frame):
        """
        Find objects on the pitch using multiprocessing.

        Returns:
            [5-tuple] Location of the robots and the ball
        """
        # Run trackers as processes
        positions = self._run_trackers(frame)

        # MULTIPROCESSING DEBUG
        if PROCESSING_DEBUG:
            if hasattr(os, 'getppid'):  # only available on Unix
                print 'Parent process:', os.getppid()
            print 'Process id:', os.getpid()

        height, width, channels = frame.shape if frame is not None else (None, None, None)

        result = {
            'our_attacker': self.to_vector(positions[1], height),
            'their_attacker': self.to_vector(positions[2], height),
            'our_defender': self.to_vector(positions[0], height),
            'their_defender': self.to_vector(positions[3], height),
            'ball': self.to_vector(positions[4], height)
        }

        return result, positions

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

    def to_vector(self, args, height):
        """
        Convert a tuple into a vector

        Return a Vector
        """
        x, y, angle, velocity = None, None, None, None
        if args is not None:
            if 'location' in args:
                x = args['location'][0] if args['location'] is not None else None
                y = args['location'][1] if args['location'] is not None else None

                if y is not None:
                    y = height - y

            if 'angle' in args:
                angle = args['angle']

            if 'velocity' in args:
                velocity = args['velocity']

        return Vector(x, y, angle, velocity)

class Camera(object):
    """
    Camera access wrapper.
    """

    def __init__(self, port=0):
        self.capture = cv2.VideoCapture(port)
        calibration = tools.get_calibration('vision/calibrate.json')
        self.crop_values = tools.find_extremes(calibration['outline'])

    def get_frame(self):
        """
        Retrieve a frame from the camera.

        Returns the frame if available, otherwise returns None.
        """
        status, frame = self.capture.read()
        if status:
            return frame[
                self.crop_values[2]:self.crop_values[3],
                self.crop_values[0]:self.crop_values[1]
            ]


class GUI(object):

    def __init__(self):
        self.zones = None

    def to_vector(self, args):
        """
        Convert a tuple into a vector

        Return a Vector
        """
        x, y, angle, velocity = None, None, None, None
        if args is not None:
            if 'location' in args:
                x = args['location'][0] if args['location'] is not None else None
                y = args['location'][1] if args['location'] is not None else None

            if 'angle' in args:
                angle = args['angle']

            if 'velocity' in args:
                velocity = args['velocity']

        return Vector(x, y, angle, velocity)

    def draw(self, frame, positions, actions, extras, our_color):

        height, width, channels = frame.shape
        if not self.zones:
            self.zones = tools.get_zones(width, height)

        for zone in self.zones:
            cv2.line(frame, (zone[1], 0), (zone[1], height), BGR_COMMON['red'], 1)


        positions = {
            'our_attacker': self.to_vector(extras[1]),
            'their_attacker': self.to_vector(extras[3]),
            'our_defender': self.to_vector(extras[0]),
            'their_defender': self.to_vector(extras[2]),
            'ball': self.to_vector(extras[4])
        }

        # if extras not None:
        #     extras = {
        #         'our_attacker': extras[1],
        #         'their_attacker': extras[3],
        #         'our_defender': extras[0],
        #         'their_defender': extras[2],
        #         'ball': extras[4]
        #     }
        their_color = list(TEAM_COLORS - set([our_color]))[0]

        if positions['ball'] is not None:
            self.draw_ball(frame, positions['ball'].get_x(), positions['ball'].get_y())

        for key in ['our_defender', 'our_attacker']:
            if positions[key] is not None:
                self.draw_robot(
                    frame, positions[key].get_x(), positions[key].get_y(), our_color)

        for key in ['their_defender', 'their_attacker']:
            if positions[key] is not None:
                self.draw_robot(
                    frame, positions[key].get_x(), positions[key].get_y(), their_color)

        # print extras

        if extras is not None:
            for x in extras[:4]:
                if x is not None:
                    if x['i'] and 'i' in x.keys():
                        self.draw_dot(frame, x['i'])

                    if  x['dot'] and 'dot' in x.keys():
                        self.draw_dot(frame, x['dot'])

                    if  x['box'] and 'box' in x.keys():
                        self.draw_box(frame, x['box'])

                    if x['location'] and 'location' in x.keys():
                        self.draw_dot(frame, x['location'])

                if x['line'] and 'line' in x.keys():
                    self.draw_line(frame, x['line'])


        cv2.imshow('SUCH VISION', frame)
        cv2.waitKey(3)

    def draw_robot(self, frame, x, y, color, thickness=1):
        if x is not None and y is not None:
            cv2.circle(frame, (x, y), 16, BGR_COMMON[color], thickness)

    def draw_ball(self, frame, x, y):
        if x is not None and y is not None:
            cv2.circle(frame, (x, y), 7, BGR_COMMON['red'], 2)

    def draw_dot(self, frame, location):
        if location is not None:
            cv2.circle(frame, location, 2, BGR_COMMON['white'], 1)

    def draw_box(self, frame, location):
        if location is not None:
            x, y, width, height = location
            cv2.rectangle(frame, (x, y), (x + width, y + height), BGR_COMMON['bright_green'], 1)

    def draw_line(self, frame, points):
        if points is not None:
            cv2.line(frame, points[0], points[1], BGR_COMMON['red'], 2)

