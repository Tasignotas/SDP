""" An executable that runs the simulation as a drop-in replacement for the real-world pitch and robots """
from math import pi
from optparse import OptionParser

import pymunk
import pygame
from twisted.internet import reactor

from Drawing import green
from WorldObjects import Ball, Robot, Pitch
from Params import Params
from Simulation import Simulation
from VisionServer import VisionServerStarter
from CommsServer import CommsServerFactory

(w, h) = Params.pitchSize

objects = {}
objects['ball'] = Ball((w-120, h/2), (0, 0))

objects['blue'] = Robot((60, h/2), (0,0), 0, "blue")

objects['bluetwo'] = Robot((w-240, h/2), (0,0), 0, "blue")

objects['yellowtwo'] = Robot((240, h/2), (0,0), pi, "yellow")

objects['yellow'] = Robot((w-60, h/2), (0,0), pi, "yellow")

simulation = Simulation(objects, draw=True)
vss = VisionServerStarter(simulation)
vss.start(31410)
csf = CommsServerFactory(simulation)
csf.start()

simulation.start()

while not simulation.done.value:
    pass
