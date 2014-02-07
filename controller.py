from vision.vision import Vision
from planning.planner import Planner
from vision.tracker import Tracker
from postprocessing.postprocessing import Postprocessing
import vision.tools as tools
from nxt import *


class Controller:
    """
    Primary source of robot control. Ties vision and planning together.
    """

    def __init__(self, port=0, connect=True, debug=False):
        self.debug = debug
        self.vision = Vision(side='left')
        self.postprocessing = Postprocessing()
        self.planner = Planner(our_side='left')
        #self.attacker = Attacker_Controller(connectionName='GRP7A', leftMotorPort=PORT_A, rightMotorPort=PORT_C, kickerMotorPort=PORT_B)
        #self.defender = Defender_Controller('GRP7A', leftMotorPort=PORT_C, rightMotorPort=PORT_B, kickerMotorPort=PORT_A)

    def wow(self):
        """
        Ready your sword, here be dragons.

        Main flow of the program. Run the controller with vision and planning combined.
        """
        # positions = (None,None,None,None,((0,0),0,0))
        try:
            while True:
                # Find object positions
                positions = self.vision.locate()
                positions = self.postprocessing.analyze(positions)
                if self.debug:
                    print positions

                # Find appropriate action
                actions = self.planner.plan(positions)
                print 'Actions:', actions['defender']

                # Execute action
                # self.attacker.execute(actions[0])
                # self.defender.execute(actions['defender'])
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

    def execute(self, action):
        """
        Execute robot action.
        """
        print 'Actions:'
        print action['left_motor']
        print action['right_motor']
        self.MOTOR_L.run(action['left_motor'], True)
        self.MOTOR_R.run(action['right_motor'], True)


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


class Defender_Controller(Robot_Controller):
    """
    Defender implementation.
    """

    def __init__ (self, connectionName, leftMotorPort, rightMotorPort, kickerMotorPort):
        """
        Do the same setup as the Robot class, as well as anything specific to the Defender.
        """
        super(Defender_Controller, self).__init__(connectionName, leftMotorPort, rightMotorPort, kickerMotorPort)


if __name__ == '__main__':
    c = Controller(debug=True).wow()  # Such controller
