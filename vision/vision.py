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

        opponent_color = self._get_opponent_color(color)

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
                    name='Their Attacker', calibration=calibration)
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

        # Wrap list of positions into a dictionary
        keys = ['our_defender', 'our_attacker', 'their_defender', 'their_attacker', 'ball']
        positions_dict = dict()
        for i, key in enumerate(keys):
            positions_dict[key] = positions[i]

        # Error check we got a frame
        height, width, channels = frame.shape if frame is not None else (None, None, None)

        result = {
            'our_attacker': self.to_info(positions[1], height),
            'their_attacker': self.to_info(positions[3], height),
            'our_defender': self.to_info(positions[0], height),
            'their_defender': self.to_info(positions[2], height),
            'ball': self.to_info(positions[4], height)
        }
        return result, positions_dict

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
        # status, frame = True, cv2.imread('img/i_all/00000003.jpg')
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

    def draw(self, frame, model_positions, actions, regular_positions, fps, aState, dState, grabbers, our_color, key=None, preprocess=None):
        """
        Draw information onto the GUI given positions from the vision and post processing.

        NOTE: model_positions contains coordinates with y coordinate reversed!
        """
        # Get general information about the frame
        frame_height, frame_width, channels = frame.shape

        # Draw the calibration gui
        self.calibration_gui.show(frame, key)
        # Draw dividors for the zones
        self.draw_zones(frame, frame_width, frame_height)

        their_color = list(TEAM_COLORS - set([our_color]))[0]

        key_color_pairs = zip(['our_defender', 'their_defender', 'our_attacker', 'their_attacker'], [our_color, their_color]*2)

        self.draw_ball(frame, regular_positions['ball'])

        for key, color in key_color_pairs:
            self.draw_robot(frame, regular_positions[key], color)

        # Draw fps on the canvas
        if fps is not None:
            self.draw_text(frame, 'FPS: %.1f' % fps, 0, 10, BGR_COMMON['green'], 1)

        if model_positions and regular_positions:
            for key in ['ball', 'our_defender', 'our_attacker', 'their_defender', 'their_attacker']:
                if model_positions[key] and regular_positions[key]:
                    self.data_text(
                        frame, key, regular_positions[key]['y'],
                        model_positions[key].x, model_positions[key].y,
                        model_positions[key].angle, model_positions[key].velocity)
                    self.draw_velocity(
                        frame,
                        model_positions[key].x, model_positions[key].y,
                        model_positions[key].angle, model_positions[key].velocity)

        if preprocess is not None:
            preprocess['normalize'] = self.cast_binary(
                cv2.getTrackbarPos(self.NORMALIZE, self.VISION))
            preprocess['background_sub'] = self.cast_binary(
                cv2.getTrackbarPos(self.BG_SUB, self.VISION))

        if grabbers:
            self.draw_grabbers(frame, grabbers, frame_height)

        # Extend image downwards and draw states.
        blank = np.zeros_like(frame)[:100,:,:]
        frame_with_blank = np.vstack((frame,blank))
        self.draw_states(frame_with_blank,aState,dState,(frame_width,frame_height))

        cv2.imshow(self.VISION, frame_with_blank)

    def draw_zones(self, frame, width, height):
        # Re-initialize zones in case they have not been initalized
        if self.zones is None:
            self.zones = tools.get_zones(width, height)

        for zone in self.zones:
            cv2.line(frame, (zone[1], 0), (zone[1], height), BGR_COMMON['red'], 1)

    def draw_ball(self, frame, position_dict):
        if position_dict and position_dict['x'] and position_dict['y']:
            cv2.circle(frame, (int(position_dict['x']), int(position_dict['y'])), 7, BGR_COMMON['red'], 2)

    def draw_dot(self, frame, location):
        if location is not None:
            cv2.circle(frame, location, 2, BGR_COMMON['white'], 1)

    def draw_robot(self, frame, position_dict, color):
        if position_dict['box']:
            cv2.polylines(frame, [np.array(position_dict['box'])], True, BGR_COMMON[color], 2)

        if position_dict['front']:
            p1 = (position_dict['front'][0][0], position_dict['front'][0][1])
            p2 = (position_dict['front'][1][0], position_dict['front'][1][1])
            cv2.circle(frame, p1, 3, BGR_COMMON['white'], -1)
            cv2.circle(frame, p2, 3, BGR_COMMON['white'], -1)
            cv2.line(frame, p1, p2, BGR_COMMON['red'], 2)

        if position_dict['dot']:
            cv2.circle(
                frame, (int(position_dict['dot'][0]), int(position_dict['dot'][1])), 4, BGR_COMMON['black'], -1)

        if position_dict['direction']:
            cv2.line(frame, position_dict['direction'][0], position_dict['direction'][1], BGR_COMMON['orange'], 2)

    def draw_line(self, frame, points):
        if points is not None:
            cv2.line(frame, points[0], points[1], BGR_COMMON['red'], 2)

    def data_text(self, frame, text, text_y, x, y, angle, velocity):
        if x is not None and y is not None and text_y is not None:
            self.draw_text(frame, text, x, text_y)
            self.draw_text(frame, 'x: %.2f' % x, x, text_y + 10)
            self.draw_text(frame, 'y: %.2f' % y, x, text_y + 20)

            if angle is not None:
                self.draw_text(frame, 'angle: %.2f' % angle, x, text_y + 30)

            if velocity is not None:
                self.draw_text(frame, 'velocity: %.2f' % velocity, x, text_y + 40)

    def draw_text(self, frame, text, x, y, color=BGR_COMMON['green'], thickness=1.3, size=0.3,):
        if x is not None and y is not None:
            cv2.putText(frame, text, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, size , color, thickness)

    def draw_grabbers(self, frame, grabbers, height):
        def_grabber = grabbers['our_defender'][0]
        att_grabber = grabbers['our_attacker'][0]

        def_grabber = [(x, height - y) for x, y in def_grabber]
        att_grabber = [(x, height - y) for x, y in att_grabber]

        def_grabber = [(int(x) if x > -1 else 0, int(y) if y > -1 else 0) for x, y in def_grabber]
        att_grabber = [(int(x) if x > -1 else 0, int(y) if y > -1 else 0) for x, y in att_grabber]

        def_grabber[2], def_grabber[3] = def_grabber[3], def_grabber[2]
        att_grabber[2], att_grabber[3] = att_grabber[3], att_grabber[2]

        cv2.polylines(frame, [np.array(def_grabber)], True, BGR_COMMON['red'], 1)
        cv2.polylines(frame, [np.array(att_grabber)], True, BGR_COMMON['red'], 1)

    def draw_velocity(self,frame,x,y,angle,vel,scale=10):
        if not(None in [frame,x,y,angle,vel]) and vel is not 0:
            frame_height,_,_ = frame.shape
            r = vel*scale
            y = frame_height-y
            start_point = (x,y)
            end_point = (x+r*np.cos(angle),y-r*np.sin(angle))
            print (start_point,end_point)
            self.draw_line(frame,(start_point,end_point))

    def draw_states(self,frame,aState,dState,frame_offset):
        frame_width,frame_height = frame_offset

        self.draw_text(frame,"Attacker State:",(frame_width/4)-20,frame_height+20,size=0.6)
        self.draw_text(frame, aState[0],(frame_width/4)-20,frame_height+35,size=0.6)
        self.draw_text(frame, aState[1],(frame_width/4)-20,frame_height+50,size=0.6)

        self.draw_text(frame,"Defender State:",(frame_width/4)*2+20,frame_height+20,size=0.6)
        self.draw_text(frame, dState[0],(frame_width/4)*2+20,frame_height+35,size=0.6)
        self.draw_text(frame, dState[1],(frame_width/4)*2+20,frame_height+50,size=0.6)
