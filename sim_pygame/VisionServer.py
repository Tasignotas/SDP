""" Simulates the vision -> strategy communications """
import struct
import time
from math import pi
from multiprocessing import Process

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

from Simulation import Simulation

import pygame

# Constants
RQ_BLUE = 1
RQ_YELLOW = 2
RQ_RED = 3
RQ_DIMENSIONS = 4
RQ_FPS = 5

def _buildPacket(type, one, two, three):
    """ Creates a packet like a string """
    timestamp = time.time()
    try:
        c = struct.pack('cHHddf', type, one, two, timestamp, timestamp, three)
    except struct.error:
        # there's a bug to be fixed here
        c = struct.pack('cHHddf', type, 0, 0, 0, 0, 0)

    assert len(c)==28
    return c

def _buildDimensionPacket(cx, cy, dx, dy):
    """ Creates a packet in which to send the dimensions of the pitch """
    try:
        c = struct.pack('cHHHH', 'd', cx, cy, dx, dy)
    except struct.error:
        # Something went wrong
        c = struct.pack('cHHHH', 'd', 0, 0, 0, 0)
    return c

def _build_fps_packet(fps):
    """ Creates a packet in which to send the dimensions of the pitch """
    try:
        c = struct.pack('cf', 'f', fps)
    except struct.error:
        # Something went wrong
        c = struct.pack('cf', 'f', 0.0)
    return c

class VisionServer(LineReceiver):
    """ Serves vision data """
    def __init__(self, simulation):
        self.simulation = simulation
        self.state = "GETCLIENT"
        self.clock = pygame.time.Clock()

    def connectionMade(self):
        """ Runs when a client connects """
        print "Got client"
        self.state = "GETREQUEST"

    def connectionLost(self, reason):
        """ Runs when a client disconnects """
        print "Lost client: %s" % reason
        self.state = "GETCLIENT"

    def lineReceived(self, line):
        """ Runs when the client sends a request """
        if self.state == "GETREQUEST":
            self.handle_request(line)

    def handle_request(self, data):
        """ Take a client's request and send the requested information back """
        (r,) = struct.unpack("b", data)
        if r == RQ_BLUE:
            self.sendBlue()
        elif r == RQ_YELLOW:
            self.sendYellow()
        elif r == RQ_RED:
            self.sendBall()
        elif r == RQ_DIMENSIONS:
            self.sendDimensions()
        elif r == RQ_FPS:
            self.sendFPS()
        self.clock.tick(100)

    def sendBlue(self):
        """ Send the position and angle of the blue robot """
        try:
            (x, y, a) = self.simulation.getBlueRobot()
        except TypeError:
            (x, y, a) = (-100, -100, 0)
        p = _buildPacket('b', x, y, a+pi)
        self.sendLine(p)

    def sendYellow(self):
        """ Send the position and angle of the yellow robot """
        try:
            (x, y, a) = self.simulation.getYellowRobot()
        except TypeError:
            (x, y, a) = (-100, -100, 0)
        p = _buildPacket('y', x, y, a+pi)
        self.sendLine(p)

    def sendBall(self):
        """ Send the position of the ball """
        try:
            (x, y) = self.simulation.getBall()
        except TypeError:
            (x, y) = (-100, -100)
        p = _buildPacket('r', x, y, 0)
        self.sendLine(p)

    def sendDimensions(self):
        """ Send the dimensions of the pitch """
        (w, h) = self.simulation.getDimensions()
        p = _buildDimensionPacket(w/2, h/2, w/2, h/2)
        self.sendLine(p)
    
    def sendFPS(self):
        p = _build_fps_packet(15.0)
        self.sendLine(p)
        
class VisionServerFactory(Factory):
    """ Listens for clients and creates vision servers for them when they connect """
    def __init__(self, simulation):
        self.s = simulation
    def buildProtocol(self, addr):
        return VisionServer(self.s)

class VisionServerStarter:
    """ Runs vision as a subprocess """
    def __init__(self, simulation):
        self.s = simulation
        self.vsf = VisionServerFactory(simulation)

    def start(self, port):
        """ Start the subprocess """
        self._subp = Process(target=self._run, args=(port,))
        self._subp.start()

    def _run(self, port):
        """ Run the vision server """
        reactor.listenTCP(port, self.vsf)
        try:
            reactor.run()
        except KeyboardInterrupt:
            print "VISION: User exited"
            self.s.finish()
