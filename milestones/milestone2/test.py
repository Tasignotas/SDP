from nxt.motor import *
from planning.connection import *
from time import sleep

FULL_KICK_TURNS = 100
HALF_KICK_TURNS = 50

full_kick = True
connection = Connection('GRP7A')
brick = connection.brick
kicker = Motor(brick, PORT_A)

def do_full_kick():
    count = 0
    while(True):
        kicker.turn(-60, 360, True)
        count += 1
        print count
        sleep(2)

do_full_kick()
