import cv2
import tools
from tracker import BallTracker, RobotTracker
import math
from multiprocessing import Process, Queue
import sys
from planning.models import Vector
from colors import BGR_COMMON
from collections import namedtuple
import numpy as np
from copy import deepcopy

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

        # Find the zone division
        self.zones = zones = self._get_zones(width, height)

        opponent_color = self._get_opponent_color()

        if our_side == 'left':
            self.us = [
                RobotTracker(
                    color=color, crop=zones[0], offset=zones[0][0], pitch=pitch,
                    name='Our Defender', calibration=calibration),   # defender
                RobotTracker(
                    color=color, crop=zones[2], offset=zones[2][0], pitch=pitch,
                    name='Our Attacker', calibration=calibration)   # attacker
            ]

            self.opponents = [
                RobotTracker(
                    color=opponent_color, crop=zones[3], offset=zones[3][0], pitch=pitch,
                    name='Their Defender', calibration=calibration),
                RobotTracker(
                    color=opponent_color, crop=zones[1], offset=zones[1][0], pitch=pitch,
                    name='Their Attacker', calibration=calibration)

            ]
        else:
            self.us = [
                RobotTracker(
                    color=color, crop=zones[3], offset=zones[3][0], pitch=pitch,
                    name='Our Defender', calibration=calibration),
                RobotTracker(
                    color=color, crop=zones[1], offset=zones[1][0], pitch=pitch,
                    name='Our Attacker', calibration=calibration)
            ]

            self.opponents = [
                RobotTracker(
                    color=opponent_color, crop=zones[0], offset=zones[0][0], pitch=pitch,
                    name='Their Defender', calibration=calibration),   # defender
                RobotTracker(
                    color=opponent_color, crop=zones[2], offset=zones[2][0], pitch=pitch,
                    name='Their Attacker', calibrattion=calibration)
            ]

        # Set up trackers
        self.ball_tracker = BallTracker(
            (0, width, 0, height), 0, pitch, calibration)

    def _get_zones(self, width, height):
        return [(val[0], val[1], 0, height) for val in tools.get_zones(width, height)]

    def _get_opponent_color(self, our_color):
        return (TEAM_COLORS - set([our_color])).pop()

    def locate(self, frame):
        """
        Find objects on the pitch using multiprocessing.

        Returns:
            [5-tuple] Location of the robots and the ball
        """
        # Run trackers as processes
        positions = self._run_trackers(frame)

        # Error check we got a frame
        height, width, channels = frame.shape if frame is not None else (None, None, None)

        result = {
            'our_attacker': self.to_info(positions[1], height),
            'their_attacker': self.to_info(positions[3], height),
            'our_defender': self.to_info(positions[0], height),
            'their_defender': self.to_info(positions[2], height),
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
        processes = [
            Process(target=obj.find, args=((frame, queues[i]))) for (i, obj) in enumerate(objects)]

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
            if 'x' in args and 'y' in args:
                x = args['x']
                y = args['y']
                if y is not None:
                    y = height - y

            if 'angle' in args:
                angle = args['angle']

            if 'velocity' in args:
                velocity = args['velocity']

        return {'x': x, 'y': y, 'angle': angle, 'velocity': velocity}


class Camera(object):
    """
    Camera access wrapper.
    """

    def __init__(self, port=0):
        self.capture = cv2.VideoCapture(port)
        calibration = tools.get_calibration()
        self.crop_values = tools.find_extremes(calibration['outline'])

        # Parameters used to fix radial distortion
        radial_data = tools.get_radial_data()
        self.nc_matrix = radial_data['new_camera_matrix']
        self.c_matrix = radial_data['camera_matrix']
        self.dist = radial_data['dist']

    def get_frame(self):
        """
        Retrieve a frame from the camera.

        Returns the frame if available, otherwise returns None.
        """
        # status, frame = True, cv2.imread('vision/00000003.jpg')
        status, frame = self.capture.read()
        frame = self.fix_radial_distortion(frame)
        if status:
            return frame[
                self.crop_values[2]:self.crop_values[3],
                self.crop_values[0]:self.crop_values[1]
            ]

    def fix_radial_distortion(self, frame):
        return cv2.undistort(
            frame, self.c_matrix, self.dist, None, self.nc_matrix)


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

            elif 'x' in args and 'y' in args:
                x = args['x']
                y = args['y']

            if 'angle' in args:
                angle = args['angle']

            if 'velocity' in args:
                velocity = args['velocity']

        return {'x': x, 'y': y, 'angle': angle, 'velocity': velocity}

    def cast_binary(self, x):
        return x == 1

    def draw(self, frame, positions, actions, extras, our_color, key=None, preprocess=None):
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

        vec_positions = deepcopy(positions)
        #print extras[4]
        positions = {
            'our_attacker': self.to_info(extras[1]),
            'their_attacker': self.to_info(extras[3]),
            'our_defender': self.to_info(extras[0]),
            'their_defender': self.to_info(extras[2]),
            'ball': self.to_info(extras[4])
        }

        their_color = list(TEAM_COLORS - set([our_color]))[0]

        self.draw_ball(frame, positions['ball']['x'], positions['ball']['y'])

        if extras is not None:
            for x in extras[:4]:
                if x['name'].split()[0] == 'Our':
                    color_c = our_color
                else:
                    color_c = their_color

                # Draw direction
                if x['direction'] is not None:
                    cv2.line(frame, x['direction'][0], x['direction'][1], BGR_COMMON['orange'], 2)

                if x['box'] is not None:
                    cv2.polylines(frame, [np.array(x['box'])], True, BGR_COMMON[color_c], 2)
                    #for point in x['box']:
                        #cv2.circle(frame, (point[0], point[1]), 1, BGR_COMMON['white'], -1)

                if x['dot'] is not None:
                    cv2.circle(
                        frame, (int(x['dot'][0]), int(x['dot'][1])), 2, BGR_COMMON['black'], -1)

                if x['front'] is not None:
                    p1 = (x['front'][0][0], x['front'][0][1])
                    p2 = (x['front'][1][0], x['front'][1][1])
                    cv2.circle(frame, p1, 3, BGR_COMMON['white'], -1)
                    cv2.circle(frame, p2, 3, BGR_COMMON['white'], -1)
                    cv2.line(frame, p1, p2, BGR_COMMON['red'], 2)

        self.data_text(
            frame, "ball", positions['ball']['x'], positions['ball']['y'],
            vec_positions['ball'].angle, vec_positions['ball'].velocity)

        self.data_text(
            frame, "our attacker", positions['our_attacker']['x'],
            positions['our_attacker']['y'], positions['our_attacker']['angle'],
            vec_positions['our_attacker'].velocity)

        self.data_text(
            frame, "their attacker", positions['their_attacker']['x'],
            positions['their_attacker']['y'], positions['their_attacker']['angle'],
            vec_positions['their_attacker'].velocity)

        self.data_text(
            frame, "our defender", positions['our_defender']['x'],
            positions['our_defender']['y'], positions['our_defender']['angle'],
            vec_positions['our_defender'].velocity)

        self.data_text(
            frame, "their defender", positions['their_defender']['x'],
            positions['their_defender']['y'], positions['their_defender']['angle'],
            vec_positions['their_defender'].velocity)

        cv2.imshow(self.VISION, frame)

    def draw_robot(self, frame, x, y, color, thickness=1):
        if x is not None and y is not None:
            cv2.circle(frame, (int(x), int(y)), 16, BGR_COMMON[color], thickness)

    def draw_ball(self, frame, x, y):
        if x is not None and y is not None:
            cv2.circle(frame, (int(x), int(y)), 7, BGR_COMMON['red'], 2)

    def draw_dot(self, frame, location):
        if location is not None:
            cv2.circle(frame, location, 2, BGR_COMMON['white'], 1)

    def draw_box(self, frame, location):
        if location is not None:
            x, y, width, height = location
            cv2.rectangle(frame, (int(x), int(y)), (x + width, y + height), BGR_COMMON['bright_green'], 1)

    def draw_line(self, frame, points):
        if points is not None:
            cv2.line(frame, points[0], points[1], BGR_COMMON['red'], 2)

    def data_text(self, frame, text, x, y, angle, velocity):
        if x is not None and y is not None:
            self.draw_text(frame, text, x, y)
            self.draw_text(frame, 'x: %.2f' % x, (x, y + 10))
            self.draw_text(frame, 'y: %.2f' % y, (x, y + 20))

            if angle is not None:
                self.draw_text(frame, 'angle: %.2f' % angle, (x, y + 30))

            if velocity is not None:
                self.draw_text(frame, 'velocity: %.2f' % velocity, (x, y + 40))

    def draw_text(self, frame, text, x, y, color=BGR_COMMON['white']):
        cv2.putText(frame, text, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1.3)
