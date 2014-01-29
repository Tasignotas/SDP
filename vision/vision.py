import cv2
import time
import thread
import tools


class Camera():

    def __init__(self, port=0):
        self.camera = cv2.VideoCapture(port)

    def _get_frame(self, *args):
        """
        Read in and check a frame.
        """
        success, frame = self.camera.read()
        if success:
            return frame
        print 'Could not retrieve frame'
        return None

    def get_frame(self):
        """
        Read in a single frame as a thread
        """
        # return thread.start_new_thread(self._get_frame, ())
        return self._get_frame()


class Vision:
    """
    Locate objects on the pitch.
    """

    def __init__(self, port=0):
        self.camera = Camera(port)
        self.time = time.time()
        self.frame_count = 0
        self.active = True

    def locate(self):
        """
        Find objects on the pitch.

        Returns:
            [5-tuple] Location of the robots and the ball
        """
        frame = self.camera.get_frame()
        if not frame:
            return None

        # TESTING ONLY, REMOVE WHEN METHODS BELOW IMPLEMENTED
        crop_coords = 0, 640, 0, 480
        # END OF TEST SECTION


        # Trim the image
        # crop_coords = tools.find_crop_coordinates(frame)
        # Slice image into 4 sections
        frame_1, frame_2, frame_3, frame_4 = tools.slice(frame)

        # Find robots
        robot_1 = thread.start_new_thread(self.find_robot, (frame_1[0], 't_yellow', frame_1[1]))
        robot_2 = thread.start_new_thread(self.find_robot, (frame_2[0], 't_blue', frame_2[1]))
        robot_3 = thread.start_new_thread(self.find_robot, (frame_3[0], 't_blue', frame_3[1]))
        robot_4 = thread.start_new_thread(self.find_robot, (frame_4[0], 't_blue', frame_4[1]))

        # Find ball
        ball = thread.start_new_thread(self.find_ball, (frame, ))
        return (robot_1, robot_2, robot_3, robot_4, ball)

    def find_robot(self, frame, color, left_offset):
        """
        Given the sliced frame, find the location of the robot.

        Params:
            [np Matrix] frame   Sliced up frame
            [string] color      Color of the object to find.
            [int] frame_offset  How many pixels to add to our x-values to get actual position on the field

        Returns:
            [3-tuple (x, y, radius)]    Radius can be either the size of a square with x,y as mid point
                                        Or simply the radius of a circle
        """
        if color == 't_yellow':
            self.find_yellow_robot()
        return (0, 0, 5)

    def find_yellow_robot(self, frame):
        pass

    def find_ball(self, frame):
        """
        Find a ball on the whole pitch. Couple of ideas could be used:

        1. Split into 4/8 sections and search for ball in each
        2. Use q = queue.Queue() and q.get() which is blocking untill an element is found.
        3. Once q.get() returns an element return.

        Params:
            [np Matrix] frame

        Returns:
            [5-tuple (x, y, radius, direction, speed)]    Radius should be for the circular shape
        """
        return (0,0,5,0,0)

    def stop(self):
        self.active = False

    def get_fps(self):
        return None if self.time <= 0 else float(self.frame_count) / float(time.time() - self.time)

