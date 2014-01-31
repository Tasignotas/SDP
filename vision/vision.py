import cv2
import tools
from tracker import BallTracker,RobotTracker
import math
from multiprocessing import Process, Queue


class Vision:
    """
    Locate objects on the pitch.
    """

    def __init__(self, left='yellow', port=0):
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
            'red', (0, self.crop_values[1], 0, self.crop_values[3]), 0, 100.0, 5)

        zone1 = (0, zone_size)
        zone2 = (zone_size, 2 * zone_size)
        zone3 = (zone_size * 2, zone_size * 3)
        zone4 = (zone_size * 3, zone_size * 4)

        # Assign trackers
        self. yellow_left = RobotTracker(
            'yellow', (zone1[0], zone1[1], 0, self.crop_values[3]), 0)

        self. yellow_middle = RobotTracker(
            'yellow', (zone3[0], zone3[1], 0, self.crop_values[3]), zone_size * 2)

        self.blue_middle = RobotTracker(
            'blue', (zone2[0], zone2[1], 0, self.crop_values[3]), zone_size)

        self.blue_right = RobotTracker(
            'blue', (zone4[0], zone4[1], 0, self.crop_values[3]), zone_size * 3)

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
            self.crop_values[0]:self.crop_values[1]]

        robot_1_queue = Queue()
        robot_2_queue = Queue()
        robot_3_queue = Queue()
        robot_4_queue = Queue()

        ball_queue = Queue()

        # Define processes
        processes = [
            Process(target=self.yellow_left.find, args=((frame, robot_1_queue))),
            Process(target=self.blue_middle.find, args=((frame, robot_2_queue))),
            Process(target=self.yellow_middle.find, args=((frame, robot_3_queue))),
            Process(target=self.blue_right.find, args=((frame, robot_4_queue))),
            Process(target=self.ball_tracker.find, args=((frame, ball_queue)))
        ]

        # Start processes
        for process in processes:
            process.start()

        # Find robots, use queue to avoid deadlock and share resources
        robot_1 = robot_1_queue.get()
        robot_2 = robot_2_queue.get()
        robot_3 = robot_3_queue.get()
        robot_4 = robot_4_queue.get()

        # Find ball
        ball = ball_queue.get()

        # terminate processes
        for process in processes:
            process.join()

        result = (robot_1, robot_2, robot_3, robot_4, ball)

        # Draw results
        # TODO: Convert to a process!
        for val in result:
            if val is not None:
                cv2.circle(frame, (val[0][0], val[0][1]), 10, (0, 255, 0), 1)

        cv2.imshow('Frame', frame)
        cv2.waitKey(4)

        return result
