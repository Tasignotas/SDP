"""
Exports various objects that deal with setting up a number of shapes in the physical simulation

WorldObject: Generic, shapeless, collisionless object

Ball: Small, circular object with high elasticity

Robot: Rectangular object with wheels and a kicker. Low elasticity and high friction.

Pitch: Stationary rectangular box of segments to contain the other objects within a certain area
"""
from math import degrees, pi, cos, sin
import time

import pymunk

from VelocityFunctions import BallVelocity, RobotVelocity, WheelVelocity
from Params import Params
from Drawing import drawRobot, drawBall, drawPitch, red, blue, yellow
from Funcs import get_robot_vertices, rotateAbout, simpleAngle, vecDist

class WorldObject(object):
    """ Represents an object in the world, in this class as a solid point """
    # Special functions {
    def __init__(self, (x, y), (vx, vy), a, mass, radius):
        # Physics details
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, inertia)

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 1

        # Initial values
        self.body.position = x, y
        self.body.angle = a
        self.body.apply_impulse((vx, vy))

        # Drawing details
        self.centre = (x, y)
        self.radius = radius

        try:
            self.body.velocity_func = self.velocity_function
        except AttributeError:
            # No velocity function
            pass
    # }

    def update(self):
        """ Update the in-object position information from the body. """
        self.centre = map(lambda n: int(round(n)), self.body.position)

    def add_to_space(self, space):
        """ Make the simulation take the body into account """
        space.add(self.shape, self.body)

    def draw_on_screen(self, screen):
        """ Make this object appear on the pygame screen """
        self.update()
        #drawBall(screen, self.centre, self.radius)
        drawBall(screen, self.centre, self.radius)

class Ball(WorldObject):
    """ Extends the WorldObject to a circle rather than a point """
    def __init__(self, (x, y), (vx, vy)):
        self.velocity_func = BallVelocity()
        super(Ball, self).__init__((x, y), (vx, vy), 0, Params.ballMass, Params.ballRadius)

    def hasPoint(self, point):
        """ Is the given point on this object? """
        return vecDist(point, tuple(self.body.position)) < self.radius

    def setPosition(self, (x, y)):
        """ Move the ball """
        self.body.position = (x, y)

    def setVelocity(self, (vx, vy)):
        """ Make the ball move itself """
        self.body.velocity = (vx, vy)

    def setAngle(self, angle):
        """ Mostly useless I think. """
        self.body.angle = angle

    def setKeyFrame(self, keyframe):
        """ Given a snapshot make the ball be in that state """
        self.setPosition(keyframe['position'])
        self.setVelocity(keyframe['velocity'])
        self.setAngle(keyframe['angle'])

class Robot(WorldObject):
    """ Extends the WorldObject to a robot """
    # Special functions {
    def __init__(self, (x, y), (vx, vy), a, colour):
        dims = Params.robotDims

        # Robot Body {
        ## Body ##
        inertia = pymunk.moment_for_box(Params.robotMass, dims[0], dims[1])
        body = pymunk.Body(Params.robotMass, inertia)

        ## Shape ##
        shape = pymunk.Poly(body, get_robot_vertices((0,0), (dims[0], dims[1])))
        shape.elasticity = Params.robotElasticity
        shape.group = 1 if colour == 'blue' else 2

        ## Initial values ##
        body.position = x, y
        body.angle = a
        # }

        # Wheels {
        ## Bodies ##
        wheelInertia = pymunk.moment_for_circle(Params.wheelMass, 0, Params.wheelRadius)
        lwheel = pymunk.Body(Params.wheelMass, wheelInertia)
        rwheel = pymunk.Body(Params.wheelMass, wheelInertia)

        ## Velocity functions ##
        lwheel.velocity_func = WheelVelocity(body, self.get_lwheel_velocity)
        rwheel.velocity_func = WheelVelocity(body, self.get_rwheel_velocity)

        ## Initial Values ##
        axle = Params.axleLength/2
        lwheel.position = rotateAbout((x, y-axle), (x, y), a)
        rwheel.position = rotateAbout((x, y+axle), (x, y), a)
        # }

        # Kicker {
        ## Body ##
        kw, kl = Params.kickerDims
        kickerInertia = pymunk.moment_for_box(Params.kickerMass, kw, kl)
        kicker = pymunk.Body(Params.kickerMass, kickerInertia)

        ## Shape ##
        kickerShape = pymunk.Poly(kicker, get_robot_vertices((0,0), (kw, kl)))
        kickerShape.group = shape.group
        kickerShape.elasticity = Params.kickerElasticity

        ## Initial Values ##
        kicker.position = rotateAbout((x+Params.kickerOffset, y), (x, y), a)
        kicker.angle = a
        #}

        # Joints {
        lwheelJoint = pymunk.PivotJoint(body, lwheel, (0, -axle), (0,0))
        rwheelJoint = pymunk.PivotJoint(body, rwheel, (0, +axle), (0,0))
        kgdist = Params.kickerDims[0]/2
        kickerSpringJoint1 = pymunk.DampedSpring( body
                                                , kicker
                                                , (Params.kickerOffset, kgdist)
                                                , (0,kgdist)
                                                , 0
                                                , Params.kickerSpringStiffness
                                                , Params.kickerSpringDamping
                                                )
        kickerSpringJoint2 = pymunk.DampedSpring( body
                                                , kicker
                                                , (Params.kickerOffset, -kgdist)
                                                , (0,-kgdist)
                                                , 0
                                                , Params.kickerSpringStiffness
                                                , Params.kickerSpringDamping
                                                )
        kickerGrooveJoint = pymunk.GrooveJoint( body
                                              , kicker
                                              , (Params.kickerOffset, 0)
                                              , (Params.kickerOffset+Params.kickerExtend, 0)
                                              , (0,0)
                                              )
        # }


        # Drawing details
        self.centre = (x, y)
        self._colour = blue if colour == "blue" else yellow
        self._dims = dims

        # Velocity function with partial application
        self.velocity_function = RobotVelocity(self)
        body.velocity_func = self.velocity_function

        self.rwheelVel = 0
        self.lwheelVel = 0

        # Attach variables to the object
        ## Bodies ##
        self.body = body
        self.lwheel = lwheel
        self.rwheel = rwheel
        self.kicker = kicker

        ## Shapes ##
        self.shape = shape
        self.kickerShape = kickerShape

        ## Joints ##
        self.lwheelJoint = lwheelJoint
        self.rwheelJoint = rwheelJoint
        self.kickerSpringJoint1 = kickerSpringJoint1
        self.kickerSpringJoint2 = kickerSpringJoint2
        self.kickerGrooveJoint = kickerGrooveJoint

        ## Other ##
        self.blocking = False
        self.turning = False

    # }

    # Simulation functions {
    def add_to_space(s, space):
        """ Make chipmunk deal with the objects and shapes this robot contains """
        space.add( s.body
                 , s.lwheel
                 , s.rwheel
                 , s.kicker
                 , s.shape
                 , s.kickerShape
                 , s.lwheelJoint
                 , s.rwheelJoint
                 , s.kickerSpringJoint1
                 , s.kickerSpringJoint2
                 , s.kickerGrooveJoint
                 )

    def get_lwheel_velocity(self):
        """ Get the velocity of the left wheel """
        return self.lwheelVel*Params.moveCoefficient

    def get_rwheel_velocity(self):
        """ Get the velocity of the right wheel """
        return self.rwheelVel*Params.moveCoefficient
    # }

    # Runtime update functions {
    def setPosition(self, (x, y)):
        """ Move the robot to (x, y) instantly without making the physics throw a wobbly. """
        self.body.position = x,y
        axle = Params.axleLength/2
        a = self.body.angle
        self.lwheel.position = rotateAbout((x, y-axle), (x, y), a)
        self.rwheel.position = rotateAbout((x, y+axle), (x, y), a)
        self.kicker.position = rotateAbout((x+Params.kickerOffset, y), (x, y), a)

    def setVelocity(self, (vx, vy)):
        """ Change the robot's motion """
        self.body.velocity = vx,vy
        self.lwheel.velocity = vx, vy
        self.rwheel.velocity = vx, vy
        self.kicker.velocity = vx, vy

    def setAngle(self, a):
        """ Rotate the robot to the given angle """
        self.body.angle = a
        self.lwheel.angle = a
        self.rwheel.angle = a
        self.kicker.angle = a
        x, y = tuple(self.body.position)
        axle = Params.axleLength/2
        self.lwheel.position = rotateAbout((x, y-axle), (x, y), a)
        self.rwheel.position = rotateAbout((x, y+axle), (x, y), a)
        self.kicker.position = rotateAbout((x+Params.kickerOffset, y), (x, y), a)

    def setKeyFrame(self, keyframe):
        """
        Put the robot in a position, facing a direction, with a given motion and wheels rotating at given speeds.
        All of this information is stored in a dictionary.
        """
        # Get values
        (x, y) = keyframe['position']
        (vx, vy) = keyframe['velocity']
        a = keyframe['angle']
        try:
            (self.lwheelVel, self.rwheelVel) = keyframe['wheels']
        except KeyError:
            (self.lwheelVel, self.rwheelVel) = (0,0)
        axle = Params.axleLength/2

        # Set values
        ## Positions ##
        self.body.position = x, y
        self.lwheel.position = rotateAbout((x, y-axle), (x, y), a)
        self.rwheel.position = rotateAbout((x, y+axle), (x, y), a)
        self.kicker.position = rotateAbout((x+Params.kickerOffset, y), (x, y), a)

        ## Velocities ##
        self.body.velocity = vx,vy
        self.lwheel.velocity = vx, vy
        self.rwheel.velocity = vx, vy
        self.kicker.velocity = vx, vy

        ## Angles ##
        self.body.angle = a
        self.lwheel.angle = a
        self.rwheel.angle = a
        self.kicker.angle = a

    # }

    # Control functions {
    def move(self, lwheelVel, rwheelVel):
        """ Set the wheel speeds """
        self.lwheelVel = lwheelVel
        self.rwheelVel = rwheelVel

    def kick(self):
        """ Move the kicker """
        a = self.body.angle
        i, j = cos(a), sin(a)
        t = Params.kickerImpulse
        self.kicker.apply_impulse((t*i, t*j))

    def turn(self, angle):
        """ Rotate by angle radians """
        turnspeed = Params.turnSpeed
        if degrees(abs(angle)) < 2:
            # If the angle is too small we'll just stay still
            return
        if angle < 0:
            self.move(-turnspeed, turnspeed)
        elif angle > 0:
            self.move(turnspeed, -turnspeed)
        self.set_stop_angle(angle)

    def set_stop_time(self, timeout):
        """ Set a time in the future at which to stop """
        self.blocking = True
        self.timeout = timeout

    def set_stop_angle(self, angle):
        """ Set an angle at which to stop """
        currAngle = self.body.angle
        self.going_up = angle > 0
        self.target_angle = currAngle+angle
        self.turning = True

    def do_turnout(self):
        """ Stop when we're facing the angle """
        if self.going_up:
            if self.body.angle-self.target_angle > 0:
                self.move(0,0)
                self.turning = False
        else:
            if self.body.angle-self.target_angle < 0:
                self.move(0,0)
                self.turning = False

    def do_timeout(self):
        """ Stop when a timeout has occurred """
        self.timeout -= Params.simulationSpeed/Params.FPS
        if self.timeout <= 0:
            self.move(0,0)
            self.blocking = False
    # }

    # Pygame functions {

    def draw_on_screen(self, screen):
        """ Draw this robot on a screen """
        self.update()
        drawRobot(screen, self._colour, self.centre, self._dims, self.body.angle, self.kicker.position, self.kicker.angle)

    def hasPoint(self, point):
        """ Returns whether or not the position is in this robot """
        (ux, uy) = tuple(self.body.position)
        (w, h) = self._dims
        (hw,hh) = (w/2, h/2)
        angle = simpleAngle(self.body.angle)
        (x, y) = rotateAbout(point, (ux, uy), -angle)
        in_w = (ux-hw) < x and x < (ux+hw)
        in_h = (uy-hh) < y and y < (uy+hh)
        return in_w and in_h
    #}

class Pitch(WorldObject):
    def __init__(self, (w, h)):
        self.dims = (w,h)
        self.body = pymunk.Body()
        self.body.position = 0,0
        r = 2
        top = pymunk.Segment(self.body, (0, 0), (w, 0), r)
        bottom = pymunk.Segment(self.body, (0, h), (w, h), r)
        left = pymunk.Segment(self.body, (0, 0), (0, h), r)
        right = pymunk.Segment(self.body, (w, 0), (w, h), r)

        self._sides = (top, bottom, left, right)
        map(lambda side: side._set_elasticity(Params.wallElasticity), self._sides)

    def add_to_space(self, space):
        space.add(*self._sides)

    def draw_on_screen(self, screen):
        drawPitch(screen, *self.dims)
