import cv2
from vision.vision import Vision
from planner.planner import Planner
from vision.crop_field import *
from vision.tracker import Tracker
#from src.milestone1 import Robot


def normalize(img):
    kernel = np.ones((5, 5), np.float32) / 25
    dst = cv2.filter2D(img, -1, kernel)
    return dst

def brighten(img, alpha=1.0, beta=10.0):
    mul_img = cv2.multiply(img, np.array([alpha]))
    new_img = cv2.add(mul_img,np.array([beta]))
    return new_img

def getPitch(frame):
    lower_black = np.array([0,0,0])
    upper_black = np.array([180,83,83])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_black = 255 - mask_black
    frame = cv2.bitwise_and(frame,frame, mask= mask_black)

    return frame

def readFrame(c, xmin, xmax, ymin, ymax):
    ret,frame = c.read()
    frame = frame[ymin:ymax,xmin:xmax]
    frame = getPitch(frame)
    frame = brighten(frame, 2.0, 50.0)
    return frame

def run(color):
    cap = cv2.VideoCapture(0)
    for i in range(10):
        ret,frame = cap.read()
    # print frame.shape

    xmin,xmax,ymin,ymax = get_crop_coordinates(frame)
    print xmin,xmax,ymin,ymax

    frame = brighten(frame[ymin:ymax,xmin:xmax], 2.0, 50.0)
    width = (xmax - xmin)#/4
    height = ymax - ymin

    tracker = Tracker(frame, color, int(width * 3 / 4), 0, int(width * 4 / 4), int(height))
    tracker.update(frame)

    while(1):
        print "properties"
        print tracker.pos
        print tracker.angle
        frame = readFrame(cap, xmin,xmax,ymin,ymax)
        ret = tracker.update(frame)
        if not ret:
            break


        cv2.ellipse(frame, ret, (0, 0, 255), 2)
        cv2.imshow('img',frame)

        k = cv2.waitKey(60) & 0xff
        if k == 27:
            break

    #run()

    cv2.destroyAllWindows()
    cap.release()


class Controller:
    """
    Primary source of robot control. Ties vision and planning together.
    """

    def __init__(self):
        self.vision = Vision()
        self.planner = Planner()
        self.attacker = Attacker()
        self.defender = Defender()

    def run(self):
        """
        Main flow of the program. Run the controller with vision and planning combined.
        """
        while True:
            positions = self.vision.locate()
            actions = self.planner.plan(*positions)

            # Execute action
            self.attacker.execute(actions[0])
            self.defender.execute(actions[1])

            # TODO: Display vision GUI/feed

            print 'Executed'



class Robot:
    """
    Robot superclass for control.
    Should encapsulate robot communication as well.
    """

    def __init__ (self, connectionName,leftMotorPort,rightMotorPort,sensorPort):
        """
        Connect to Brick and setup Motors/Sensors.
        """
        connection = src.common.Connection(name=connectionName)
        self.Brick = connection.brick
        self.MOTOR_L = Motor(self.Brick,leftMotorPort)
        self.MOTOR_R = Motor(self.brick,rightMotorPort)
        self.LIGHT_L = Light(self.Brick,sensorPort)
        self.LIGHT_L.set_illuminated(True)

    def execute(self, action):
        """
        Execute robot action.
        """
        pass


class Attacker(Robot):
    """
    Attacker implementation.
    """
    pass


class Defender(Robot):
    """
    Defender implementation.
    """
    pass
