from nxt.motor import *
from time import sleep
import nxt


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

FULL_KICK_TURNS = 100
HALF_KICK_TURNS = 50

full_kick = True
connection = Connection('GRP7A')
brick = connection.brick
kicker = Motor(brick, PORT_A)

def kick():
	"""
	The dummest method ever. Turn the motor a wee bit.
	"""
	kicker.turn(-100, 100)	#turn about 100 degrees
	kicker.idle()	# release the brake


def do_full_kick():
    count = 0
    while(True):
        kicker.turn(-60, 360, True)
        count += 1
        print count
        sleep(2)

# do_full_kick()
