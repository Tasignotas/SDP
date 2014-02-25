import cv2
import tools
from tracker import BallTracker, RobotTracker
import math
from multiprocessing import Process, Queue
import sys
from planning.models import Vector
from colors import BGR_COMMON
from collections import namedtuple

from findHSV import CalibrationGUI


TEAM_COLORS = set(['yellow', 'blue'])
SIDES = ['left', 'right']
PITCHES = [0, 1]

PROCESSING_DEBUG = False


class Vision:
    """
    Locate objects on the pitch.
    """

    def __init__(self, pitch, color, our_side, frame_shape, calibration):
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

        # Do set difference to find the other color - if is too long :)
        opponent_color = (TEAM_COLORS - set([color])).pop()

        if our_side == 'left':
            self.us = [
                RobotTracker(color=color, crop=zones[0], offset=zones[0][0], pitch=pitch, name='Our Defender', calibration=calibration),   # defender
                RobotTracker(color=color, crop=zones[2], offset=zones[2][0], pitch=pitch, name='Our Attacker', calibration=calibration) # attacker
            ]

            self.opponents = [
                RobotTracker(opponent_color, zones[3], zones[3][0], pitch, 'Their Defender', calibration),
                RobotTracker(opponent_color, zones[1], zones[1][0], pitch, 'Their Attacker', calibration)

            ]
        else:
            self.us = [
                RobotTracker(color, zones[3], zones[3][0], pitch, 'Our Defender', calibration),
                RobotTracker(color, zones[1], zones[1][0], pitch, 'Our Attacker', calibration)
            ]

            self.opponents = [
                RobotTracker(opponent_color, zones[0], zones[0][0], pitch, 'Their Defender', calibration),   # defender
                RobotTracker(opponent_color, zones[2], zones[2][0], pitch, 'Their Attacker', calibration)
            ]

        # Set up trackers
        self.ball_tracker = BallTracker(
            (0, width, 0, height), 0, pitch, calibration)

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
            'our_attacker': self.to_info(positions[1], height),
            'their_attacker': self.to_info(positions[2], height),
            'our_defender': self.to_info(positions[0], height),
            'their_defender': self.to_info(positions[3], height),
            'ball': self.to_info(positions[4], height)
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

    def to_info(self, args, height):
        """
        Returns a dictionary with object position information
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

        return {'x' : x, 'y' : y, 'angle' : angle, 'velocity' : velocity}


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
        status, frame = True, cv2.imread('vision/00000003.jpg')
        # status, frame = self.capture.read()
        if status:
            return frame[
                self.crop_values[2]:self.crop_values[3],
                self.crop_values[0]:self.crop_values[1]
            ]


class GUI(object):

    VISION = 'SUCH VISION'
    BG_SUB = 'BG Subtract'
    NORMALIZE = 'Normalize  '

    def nothing(self, x):
        pass

    def __init__(self, calibration):
        self.zones = None
        self.calibration_gui = CalibrationGUI(calibration)

        cv2.namedWindow(self.VISION)

        cv2.createTrackbar(self.BG_SUB, self.VISION, 0, 1, self.nothing)
        cv2.createTrackbar(self.NORMALIZE, self.VISION, 0, 1, self.nothing)

    def to_info(self, args):
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

        return {'x' : x, 'y' : y, 'angle' : angle, 'velocity' : velocity}

    def cast_binary(self, x):
        return x == 1

    def draw(
        self, frame, positions, actions, extras, our_color, key=None, preprocess=None):

        if preprocess is not None:
            preprocess['normalize'] = self.cast_binary(
                cv2.getTrackbarPos(self.NORMALIZE, self.VISION))
            preprocess['background_sub'] = self.cast_binary(
                cv2.getTrackbarPos(self.BG_SUB, self.VISION))

        # Set values for trackbars

        self.calibration_gui.show(frame, key)

        height, width, channels = frame.shape
        if self.zones is None:
            self.zones = tools.get_zones(width, height)

        for zone in self.zones:
            cv2.line(frame, (zone[1], 0), (zone[1], height), BGR_COMMON['red'], 1)


        positions = {
            'our_attacker': self.to_info(extras[1]),
            'their_attacker': self.to_info(extras[3]),
            'our_defender': self.to_info(extras[0]),
            'their_defender': self.to_info(extras[2]),
            'ball': self.to_info(extras[4])
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
        self.draw_ball(frame, positions['ball']['x'], positions['ball']['y'])
        for key in ['our_defender', 'our_attacker']:
            self.draw_robot(frame, positions[key]['x'], positions[key]['y'], our_color)
        for key in ['their_defender', 'their_attacker']:
            self.draw_robot(frame, positions[key]['x'], positions[key]['y'], their_color)

        if extras is not None:
            for x in extras[:4]:

                # Draw direction
                if x['direction'] is not None:
                    cv2.line(frame, x['direction'][0], x['direction'][1], BGR_COMMON['yellow'], 2)

                if x['box'] is not None:
                    for point in x['box']:
                        cv2.circle(frame, (point[0], point[1]), 1, BGR_COMMON['white'], -1)

                if x['x'] is not None and x['y'] is not None:
                    cv2.circle(frame, (x['x'], x['y']), 5, BGR_COMMON['green'], -1)

        #         if x is not None:
        #             # if x['i'] and 'i' in x.keys():
        #             #     self.draw_dot(frame, x['i'])

        #             if  x['dot'] and 'dot' in x.keys():
        #                 self.draw_dot(frame, x['dot'])

        #             # if  x['box'] and 'box' in x.keys():
        #                 # self.draw_box(frame, x['box'])

        #             if x['location'] and 'location' in x.keys():
        #                 self.draw_dot(frame, x['location'])

        #         if x['line'] and 'line' in x.keys():
        #             self.draw_line(frame, x['line'])

        #         if 'plate_points' in x:
        #             cv2.polylines(frame, [x['plate_points']], True, BGR_COMMON['bright_green'], 1)

        #         if 'sides' in x:
        #             if x['sides'] is not None:
        #                 cv2.line(frame, x['sides'][0][0], x['sides'][0][1], BGR_COMMON['red'], 2)
        #                 cv2.line(frame, x['sides'][1][0], x['sides'][1][1], BGR_COMMON['red'], 2)

        #         if 'direction' in x:
        #             if x['direction'] is not None:
        #                 cv2.line(frame, x['direction'][0], x['direction'][1], BGR_COMMON['yellow'], 2)

        cv2.imshow(self.VISION, frame)

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

