"""
This module holds the class that actually performs a simulation.
It can be loaded as a library or ran as a server (via Simulator.py)
"""
from multiprocessing import Process, Value, Array, Queue
from Queue import Empty
from math import pi

import pymunk
import pygame
from pygame.locals import *

from WorldObjects import Pitch
from Drawing import green
from Params import Params
from Commands import Move, Kick, Turn, Stop


def simpleAngle(a):
    while a >= pi:
        a -= 2*pi
    while a <= -pi:
        a += 2*pi
    return a

class Simulation:
    """ The simulation class. Keeps track of useful information to ease manipulation of the simulation """
    # Special functions {
    def __init__(self, objects, draw=True, space=None, screen=None):
        # Make a space if none was given
        if not space:
            space = pymunk.Space()

        if draw and not screen:
            # Make a pygame instance if none was given *and* we want one
            pygame.init()
            screen = pygame.display.set_mode(Params.pitchSize)
        elif screen and not draw:
            # Ensure the screen is None if we shouldn't have one
            screen = None

        # Add the objects to the space, including a pitch
        self.pitch = Pitch(Params.pitchSize)
        self.pitch.add_to_space(space)

        for key in objects:
            objects[key].add_to_space(space)

        startFrame = dict()

        try:
            bot = objects['blue']
            body = bot.body
            (x, y) = tuple(body.position)
            a = body.angle
            self.blueRobot = Array('f', [x, y, a])
            startFrame['blue'] = { 'position' : (x, y)
                                 , 'velocity' : tuple(body.velocity)
                                 , 'wheels' : (bot.lwheelVel, bot.rwheelVel)
                                 , 'angle' : a
                                 }
        except KeyError:
            self.blueRobot = None

        try:
            bot = objects['yellow']
            body = bot.body
            (x, y) = tuple(body.position)
            a = body.angle
            self.yellowRobot = Array('f', [x, y, a])
            startFrame['yellow'] = { 'position' : (x, y)
                                   , 'velocity' : tuple(body.velocity)
                                   , 'wheels' : (bot.lwheelVel, bot.rwheelVel)
                                   , 'angle' : a
                                   }
        except KeyError:
            self.yellowRobot = None

        try:
            body = objects['ball'].body
            (x, y) = tuple(body.position)
            objects['ball'].originals = (x, y)
            self.ball = Array('f', [x, y])
            startFrame['ball'] = { 'position' : (x, y)
                                 , 'velocity' : tuple(body.velocity)
                                 , 'angle' : body.angle
                                 }
        except KeyError:
            self.ball = None

        # Set some attributes
        self.clock = pygame.time.Clock()
        self.space = space
        self.screen = screen
        self.objects = objects
        self.dims = Params.pitchSize
        self.command_queue = Queue()
        self.done = Value('b', False)
        self.moving = None
        self.startFrame = startFrame
    # }

    # Simulation subprocess functions {
    def start(self, FPS=Params.FPS):
        """ Start the simulation subprocess """
        self._running_process = Process(target=self._run, args=(FPS,))
        self._running_process.start()

    def _run(self, FPS=Params.FPS):
        """ Do the simulation loop """
        self.done.value = False
        q = self.command_queue
        while not self.done.value: # Perhaps we could pull some of this code out into functions
            try:
                # Run all the things
                self._do_draw_if_screen()
                self._run_control_queue(q)
                self._try_vision_serve()
                self._tick(FPS)
            except KeyboardInterrupt:
                print "SIMULATION: Finishing"
                self.done.value = True

    def finish(self):
        """ Stop simulating """
        print "SIMULATION: Finishing"
        self.done.value = True
        self._running_process.terminate()

    def _do_draw_if_screen(self):
        """ Draw the objects to the screen if we're supposed to """
        if self.screen:
            self._handle_events()
            self._draw()
            pygame.display.flip()

    def _run_control_queue(self, q):
        """ Control the blue robot using commands from comms """
        blue = self.objects['blue']
        while True:
            # Loop through getting commands from the queue
            try:
                # Run through commands, running them on the blue robot
                command = q.get_nowait()
                if not blue.turning:
                    try:
                        command(blue)
                    except TypeError:
                        self.keyFrame(command)
                else:
                    q.put(command)
            except Empty:
                break
        if blue.blocking:
            blue.do_timeout()
        if blue.turning:
            blue.do_turnout()

    def _try_vision_serve(self):
        """ Serve vision data for the objects that exist """
        try:
            body = self.objects['blue'].body
            (x, y) = tuple(body.position)
            a = simpleAngle(body.angle)
            self.blueRobot[0] = x
            self.blueRobot[1] = y
            self.blueRobot[2] = a
        except KeyError:
            pass

        try:
            body = self.objects['yellow'].body
            (x, y) = tuple(body.position)
            a = simpleAngle(body.angle)
            self.yellowRobot[0] = x
            self.yellowRobot[1] = y
            self.yellowRobot[2] = a
        except KeyError:
            pass

        try:
            body = self.objects['ball'].body
            (x, y) = tuple(body.position)
            self.ball[0] = x
            self.ball[1] = y
        except KeyError:
            pass

    def _tick(self, FPS):
        """ Advance the simulation and limit the drawing framerate """
        if FPS != 'unlimited':
            self.space.step(Params.simulationSpeed/float(FPS))
            self.clock.tick_busy_loop(FPS)
        else:
            self.space.step(1/30.0)

    # }

    # Functions used by vision server {
    def getBlueRobot(self):
        """ Return the position and angle of the blue robot """
        try:
            return tuple(self.blueRobot)
        except AttributeError:
            return None
        except TypeError:
            return None

    def getBlueBot(self):
        return self.getBlueRobot()

    def getYellowRobot(self):
        """ Return the position and angle of the yellow robot """
        try:
            return tuple(self.yellowRobot)
        except AttributeError:
            return None
        except TypeError:
            return None

    def getYellowBot(self):
        return self.getYellowRobot()

    def getBall(self):
        """ Return the position of the ball """
        try:
            return tuple(self.ball)
        except AttributeError:
            return None
        except TypeError:
            return None

    def getDimensions(self):
        """ Return the pixel dimensions of the pitch """
        return self.dims
    def getAbstractDims(self):
        return self.dims
    # }

    # Pygame functions {
    def _draw(self):
        """ Draw the pitch and all objects on the pygame screen """
        self.screen.fill(green)
        self.pitch.draw_on_screen(self.screen)
        for key in self.objects:
            self.objects[key].draw_on_screen(self.screen)

    def _handle_events(self):
        """ Do all of the pygame event handling """
        def do_keys():
            """ Check the keys and respond appropriately """
            blue = self.objects['yellow']
            keys = pygame.key.get_pressed()
            move = blue.move
            if keys[K_k]:
                blue.kick()
            if keys[K_r]:
                self.reset()
            if keys[K_SPACE]:
                move(0,0)
            elif keys[K_w]:
                if keys[K_a]:
                    move(60,128)
                elif keys[K_d]:
                    move(128, 60)
                elif keys[K_s]:
                    move(0,0)
                else:
                    move(127, 127)
            elif keys[K_s]:
                if keys[K_a]:
                    move(-60,-128)
                elif keys[K_d]:
                    move(-128, -60)
                elif keys[K_w]:
                    move(0,0)
                else:
                    move(-110, -110)
            elif keys[K_a]:
                move(-40, 40)
            elif keys[K_d]:
                move(40, -40)
            elif keys[K_o]:
                blue.turn(pi)
	    elif keys[K_q]:
		pygame.quit()
		self.done.value = True

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                for key in self.objects:
                    if self.objects[key].hasPoint(pygame.mouse.get_pos()):
                        self.moving = self.objects[key]
                        self.moving.setVelocity((0,0))

            elif event.type == MOUSEMOTION:
                if self.moving:
                    self.moving.setPosition(pygame.mouse.get_pos())
                    self.moving.setVelocity((0,0))
            elif event.type == KEYDOWN:
                do_keys()
            elif event.type == KEYUP:
                do_keys()
            elif event.type == MOUSEBUTTONUP:
                self.moving = None
    # }

    # Robot control commands {
    def move(self, left, right):
        """ Make the wheels turn """
        self.command_queue.put(Move(left, right))

    def kick(self):
        """ Make the robot kick """
        self.command_queue.put(Kick())

    def turn(self, angle):
        """ Make the robot turn """
        self.command_queue.put(Turn(angle))

    def stop(self):
        """ Make the robot stay put """
        self.command_queue.put(Stop())

    def forwards(self, move_speed=40):
        self.move(move_speed, move_speed)

    def backwards(self, move_speed=20):
        self.move(move_speed, move_speed)

    def exit(self):
        pass
    # }

    # State change at runtime methods {
    def keyFrame(self, keyframe, external=False):
        """ Change the entire state of the pitch during runtime without making the physics simulator become strange """
        if external:
            self.command_queue.put(keyframe)
        else:
            for key in keyframe:
                self.objects[key].setKeyFrame(keyframe[key])

    def reset(self):
        """ Set everything to the way it was at initialisation """
        print "SIMULATION: Resetting"
        self.keyFrame(self.startFrame)
    # }
