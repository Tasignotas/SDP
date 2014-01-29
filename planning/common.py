import nxt.locator
from nxt.sensor import *
from nxt.motor import *
import mock

def update(ball, robotA, robotB, robotC, robotD):
    ball.position = mock.get_ball()
    robotA.position = mock.get_robotA()
    robotB.position = mock.get_robotB()
    robotC.position = mock.get_robotC()
    robotD.position = mock.get_robotD()
    return (ball, robotA, robotB, robotC, robotD)


class Connection:

    def __init__(self, name='NXT'):
        print 'Connecting to NXT Brick with name %s' % name
        self.brick = nxt.locator.find_one_brick(
            name=name, method=nxt.locator.Method(usb=False))
        if self.brick:
            print 'Connection successful.'

    def close(self):
        """
        TODO
        Close connection to the brick, return success or failure.
        """
        pass

