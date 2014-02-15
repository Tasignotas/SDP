from vision.vision import Vision, Camera, GUI
from planning.planner import Planner
from vision.tracker import Tracker
from postprocessing.postprocessing import Postprocessing
import vision.tools as tools
from nxt import *
from time import sleep
from cv2 import waitKey

import sys


class Controller:
    """
    Primary source of robot control. Ties vision and planning together.
    """

    def __init__(self, pitch, color, our_side, port=0, connect=True, debug=False):
        """
        Entry point for the SDP system.

        Params:
            [int] port      port number for the camera
            [bool] connect  connect to the nxt?
            [int] pitch     0 - main pitch, 1 - secondary pitch
            [bool] debug    print debug messages?
        """
        if pitch not in [0, 1]:
            raise Exception('Incorrect pitch number.')

        if color not in ['yellow', 'blue']:
            raise Exception('Incorrect color.')

        if our_side not in ['left', 'right']:
            raise Exception('Icorrect side. Valid options are "left" and "right"')

        # Set up camera for frames
        self.camera = Camera(port=port)
        frame = self.camera.get_frame()

        # Set up vision
        self.vision = Vision(
            pitch=pitch, color=color, our_side=our_side, frame_shape=frame.shape)

        # Set up postprocessing for vision
        self.postprocessing = Postprocessing()

        # Set up main planner
        self.planner = Planner(our_side=our_side)

        # Set up GUI
        self.GUI = GUI()

        # Debug flag for print statements
        self.debug = debug
        self.color = color

        #self.attacker = Attacker_Controller(connectionName='GRP7A', leftMotorPort=PORT_C, rightMotorPort=PORT_B, kickerMotorPort=PORT_A)
        # self.defender = Defender_Controller('GRP7D', PORT_C, PORT_A, PORT_B)

    def wow(self):
        #
        """
        Ready your sword, here be dragons.

        Main flow of the program. Run the controller with vision and planning combined.
        """
        # positions = (None,None,None,None,((0,0),0,0))
        try:
            while True:
                frame = self.camera.get_frame()
                # Find object positions
                positions, extras = self.vision.locate(frame)
                positions = self.postprocessing.analyze(positions)
                # print 'Positions: ', positions
                # Find appropriate action
                #actions = self.planner.plan(positions, part='attacker')
                # print 'Actions:', actions
                actions = []
                # Execute action
                #self.attacker.execute(actions)
                # self.defender.execute(actions)

                # Draw vision content and actions
                self.GUI.draw(frame, positions, actions, extras, our_color=self.color)

                # Key listener for chaning color in calibration GUI and saving calibration to file
                # For some reason, it noly responds when you hold the key down.
                # Use 'y', 'b', 'r' to change color and 's' to save.
                c = waitKey(1) & 0xFF
                self.GUI.calibration_gui.key_handler.processKey(chr(c % 0x100))

        except:
            if hasattr(self, 'defender'):
                  self.defender.shutdown()
            raise

class Connection:

    def __init__(self, name='NXT'):
        print 'Connecting to NXT Brick with name %s' % name
        self.brick = locator.find_one_brick(
            name=name, method=locator.Method(usb=False))
        if self.brick:
            print 'Connection successful.'

    def close(self):
        """
        TODO
        Close connection to the brick, return success or failure.
        """
        pass


class Robot_Controller(object):
    """
    Robot_Controller superclass for robot control.
    """

    def __init__(self, connectionName, leftMotorPort, rightMotorPort, kickerMotorPort):
        """
        Connect to Brick and setup Motors/Sensors.
        """
        connection = Connection(name=connectionName)
        self.BRICK = connection.brick
        self.MOTOR_L = Motor(self.BRICK,leftMotorPort)
        self.MOTOR_R = Motor(self.BRICK,rightMotorPort)
        self.MOTOR_K = Motor(self.BRICK,kickerMotorPort)

    def shutdown(self):
        self.MOTOR_L.idle()
        self.MOTOR_R.idle()



class Attacker_Controller(Robot_Controller):
    """
    Attacker implementation.
    """

    def __init__ (self, connectionName, leftMotorPort, rightMotorPort, kickerMotorPort):
        """
        Do the same setup as the Robot class, as well as anything specific to the Attacker.
        """
        super(Attacker_Controller, self).__init__(connectionName, leftMotorPort, rightMotorPort, kickerMotorPort)

    def execute(self, action):
        """
        Execute robot action.
        """
        self.MOTOR_L.run(action['attacker']['left_motor'], True)
        self.MOTOR_R.run(action['attacker']['right_motor'], True)
        if action['attacker']['kicker'] != 0:
            try:
                self.MOTOR_K.turn(action['attacker']['kicker'], 70, False, False)
            except Exception, e:
                pass
        else:
            self.MOTOR_K.idle()


class Defender_Controller(Robot_Controller):
    """
    Defender implementation.
    """

    def __init__ (self, connectionName, leftMotorPort, rightMotorPort, kickerMotorPort):
        """
        Do the same setup as the Robot class, as well as anything specific to the Defender.
        """
        super(Defender_Controller, self).__init__(connectionName, leftMotorPort, rightMotorPort, kickerMotorPort)

    def execute(self, action):
        """
        Execute robot action.
        """
        self.MOTOR_L.run(action['defender']['left_motor'], True)
        self.MOTOR_R.run(action['defender']['right_motor'], True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Main pitch, [1] Secondary pitch")
    parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    args = parser.parse_args()
    # print args
    c = Controller(debug=True, pitch=int(args.pitch), color=args.color, our_side=args.side).wow()  # Such controller
