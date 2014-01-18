import nxt.locator
from nxt.sensor import *
from nxt.motor import *

class Connection:

    def __init__(self, name='NXT'):
        print 'Connecting to NXT Brick with name %s' % name
        self.brick = nxt.locator.find_one_brick(
            name=name, method=nxt.locator.Method(usb=False))
        if self.brick:
            print 'Connection succesfull.'

    def close(self):
        """
        TODO
        Close connection to the brick, return success or failure.
        """
        pass

