""" Simulates the strategy -> robot communications """
import struct
import socket
from multiprocessing import Process
import pygame

# Constants
CMD_MOVE = 1
CMD_KICK = 2
CMD_TURN = 3
CMD_STOP = 4
CMD_EXIT = 99

class CommsServer:
    """ Takes commands and runs them in the simulation """
    def __init__(self, tryPort=6789, host=''):
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(tryPort)

        gotSocket = False
        # Keep trying to get sockets until we find one that is unused
        while not gotSocket:
            try:
                self._serverSocket.bind((host, port))
                gotSocket = True
            except socket.error:
                port += 1
        self._port = port
        self.__clock = pygame.time.Clock()

    def handle_request(self, (cmd, args)):
        """ Given a command and some arguments to that command, perform it """
        (c,) = struct.unpack("b", cmd)
        if c == CMD_MOVE:
            (l, r) = struct.unpack('bb', args[:2])
            self.simulation.move(l, r)
        elif c == CMD_KICK:
            self.simulation.kick()
        elif c == CMD_TURN:
            (angle1,angle2) = struct.unpack('BB', args[:2])
            angle = angle2+(angle1<<8)
            self.simulation.turn(angle)
        elif c == CMD_STOP:
            self.simulation.stop()
        elif c == CMD_EXIT:
            self.simulation.done.value = True
        self.__clock.tick(30)

    def waitForClient(self):
        """ Listen until a client connects """
        print "COMMS: Listening for client on %d" % self._port
        self._serverSocket.listen(2)
        (self._clientSocket, (self._clientAddr, _)) = self._serverSocket.accept()
        print "COMMS: Got client from %s"%self._clientAddr

    def run(self, simulation):
        """ Take commands from a client until that client disconnects """
        self.simulation = simulation
        while not simulation.done.value:
            data = self.getData()
            self.handle_request(data)
        print "COMMS.run: Simulation done"

    def getData(self):
        """ Get a command out of the socket """
        try:
            cmd = self._clientSocket.recv(1)
            args = self._clientSocket.recv(4)
            assert len(cmd)>0 and len(args)>0, "Data from socket was empty"
            return (cmd, args)
        except socket.timeout as (str, _):
            print "COMMS: Socket timed out:\n%s"%str
        except socket.error as (str, _):
            print "COMMS: Client disconnected:\n%s"%str
        except AssertionError, e:
            print "COMMS: Assertion failed, client probably disconnected:\n%s"%e
            return None

class CommsServerFactory:
    """ Create a comms server subprocess """
    def __init__(self, simulation):
        self.simulation = simulation

    def start(self):
        """ Spawn the subprocess that will take commands """
        self._subp = Process(target=self._start_server, args=(self.simulation,))
        self._subp.start()

    def _start_server(self, simulation):
        """ The subprocess that will run """
        print "COMMS: Subprocess started"
        server = CommsServer()
        while not simulation.done.value:
            try:
                server.waitForClient()
                server.run(simulation)
            except KeyboardInterrupt:
                print "COMMS: User closed"
            except:
                print "COMMS: Client disconnected"

    def stop_server(self):
        """ Cease serving """
        print "COMMS: Terminating"
        self._subp.terminate()
