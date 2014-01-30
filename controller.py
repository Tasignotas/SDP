from vision.vision import Vision
from planning.planner import Planner
from vision.tracker import Tracker
import vision.tools as tools


class Controller:
    """
    Primary source of robot control. Ties vision and planning together.
    """

    def __init__(self, port=0):
        self.vision = Vision()
        # self.planner = Planner()
        # self.attacker = Attacker()
        # self.defender = Defender()

    def wow(self):
        """
        Main flow of the program. Run the controller with vision and planning combined.
        """
        while True:
            # Get frame
            positions = self.vision.locate()
            print positions
            # actions = self.planner.plan(*positions)

            # Execute action
            # self.attacker.execute(actions[0])
            # self.defender.execute(actions[1])


class Robot:
    """
    Robot superclass for control.
    Should encapsulate robot communication as well.
    """

    def __init__ (self, connectionName,leftMotorPort,rightMotorPort,kickerMotorPort,lightSensorPort):
        """
        Connect to Brick and setup Motors/Sensors.
        """
        connection = src.common.Connection(name=connectionName)
        self.BRICK = connection.brick
        self.MOTOR_L = Motor(self.BRICK,leftMotorPort)
        self.MOTOR_R = Motor(self.BRICK,rightMotorPort)
        self.MOTOR_K = Motor(self.BRICK,kickerMotorPort)
        self.LIGHT_L = Light(self.BRICK,lightSensorPort)
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

    def __init__ (self, connectionName,leftMotorPort,rightMotorPort,kickerMotorPort,lightSensorPort):
        """
        Do the same setup as the Robot class, as well as anything specific to the Attacker.
        """
        Robot.__init__(self, connectionName,leftMotorPort,rightMotorPort,kickerMotorPort,lightSensorPort)
       # No need for the parameters once the robots have been finalised.
       #Robot.__init__(self, connectionName, PORT_B, PORT_C, PORT_A, PORT_2)

    pass


class Defender(Robot):
    """
    Defender implementation.
    """

    def __init__ (self, connectionName,leftMotorPort,rightMotorPort,kickerMotorPort,lightSensorPort):
        """
        Do the same setup as the Robot class, as well as anything specific to the Defender.
        """
        Robot.__init__(self, connectionName,leftMotorPort,rightMotorPort,kickerMotorPort,lightSensorPort)
       # No need for the parameters once the robots have been finalised.
       #Robot.__init__(self, connectionName, PORT_B, PORT_C, PORT_A, PORT_2)

    pass


if __name__ == '__main__':
    c = Controller().wow()
