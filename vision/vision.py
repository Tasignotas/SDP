import cv2
import tools
from tracker import BallTracker, RobotTracker
import math
from multiprocessing import Process, Queue
import os


TEAM_COLORS = set(['yellow', 'blue'])


class Vision:
    """
    Locate objects on the pitch.
    """

    def __init__(self, side='left', color='yellow', port=0):
        # Capture video port
        self.capture = cv2.VideoCapture(port)

        # Read in couple of frames to clear corrupted frames
        for i in range(5):
            status, frame = self.capture.read()

        # Retrieve crop values from calibration
        self.crop_values = tools.find_extremes(
            tools.get_calibration('vision/calibrate.json')['outline'])

        # Temporary: divide zones into section
        zone_size = int(math.floor(self.crop_values[1] / 4.0))


        self.ball_tracker = BallTracker(
            (0, self.crop_values[1], 0, self.crop_values[3]), 0)

        zone1 = (0, zone_size)
        zone2 = (zone_size, 2 * zone_size)
        zone3 = (zone_size * 2, zone_size * 3)
        zone4 = (zone_size * 3, zone_size * 4)

        # Do set difference to find the other color - if is too long :)
        opponent_color = (TEAM_COLORS - set([color])).pop()

        if side == 'left':
            self.us = [
                RobotTracker(color, (zone1[0], zone1[1], 0, self.crop_values[3]), 0),   # defender
                RobotTracker(color, (zone3[0], zone3[1], 0, self.crop_values[3]), zone_size * 2) # attacker
            ]

            self.opponents = [
                RobotTracker(opponent_color, (zone2[0], zone2[1], 0, self.crop_values[3]), zone_size),
                RobotTracker(opponent_color, (zone4[0], zone4[1], 0, self.crop_values[3]), zone_size * 3)
            ]
        else:
            self.us = [
                RobotTracker(color, (zone2[0], zone2[1], 0, self.crop_values[3]), zone_size),
                RobotTracker(color, (zone4[0], zone4[1], 0, self.crop_values[3]), zone_size * 3)
            ]

            self.opponents = [
                RobotTracker(opponent_color, (zone1[0], zone1[1], 0, self.crop_values[3]), 0),   # defender
                RobotTracker(opponent_color, (zone3[0], zone3[1], 0, self.crop_values[3]), zone_size * 2)
            ]

    def locate(self):
        """
        Find objects on the pitch using multiprocessing.

        Returns:
            [5-tuple] Location of the robots and the ball
        """
        status, frame = self.capture.read()
        if not status:
            print 'No Frame'
            return None

        # Trim the image
        frame = frame[
            self.crop_values[2]:self.crop_values[3],
            self.crop_values[0]:self.crop_values[1]
        ]

        queues = [Queue() for i in range(5)]
        objects = [self.us[0], self.us[1], self.opponents[0], self.opponents[1], self.ball_tracker]

        processes = [Process(target=obj.find)]

        # Define processes
        processes = [
            Process(target=self.us[0].find, args=((frame, queues[0]))),
            Process(target=self.us[1].find, args=((frame, queues[1]))),
            Process(target=self.opponents[0].find, args=((frame, queues[2]))),
            Process(target=self.opponents[1].find, args=((frame, queues[3]))),
            Process(target=self.ball_tracker.find, args=((frame, queues[4])))
        ]

        # Start processes
        for process in processes:
            process.start()

        # Find robots and ball, use queue to avoid deadlock and share resources
        positions = [q.get() for q in queues]

        # terminate processes
        for process in processes:
            process.join()

        # Draw results
        # TODO: Convert to a process!
        for val in positions:
            if val is not None:
                cv2.circle(frame, (val[0][0], val[0][1]), 10, (0, 255, 0), 1)

        cv2.imshow('Frame', frame)
        cv2.waitKey(4)

        # MULTIPROCESSING DEBUG

        # if hasattr(os, 'getppid'):  # only available on Unix
        #     print 'parent process:', os.getppid()
        # print 'process id:', os.getpid()

        return tuple(positions)
