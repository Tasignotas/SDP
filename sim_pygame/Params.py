
"""
This is a parameters file which can rewrite itself. To use the parameters import like so: 'from Params import Params' then get the parameters with Params.paramName. If you wish to change the parameters modify them in the Params object then run Params.writeFile()

It is important to note that if you wish your changes to be stored as code you should write them as strings.
"""
from math import pi
import sys
from inspect import getsourcelines, getfile
import re

class ParameterStore:
    def writeFile(self):
        module = sys.modules[__name__]
        lines = getsourcelines(sys.modules[__name__])[0]
        # Parameter definition line regex
        IDENT = "[a-zA-Z_][a-zA-Z0-9_]*"
        pdlr = re.compile("^Params\.(%s) = (.*)$"%IDENT)
        str = ""
        for line in lines:
            m = pdlr.match(line)
            if m:
                varName = m.group(1)
                newVal = self.__dict__[varName]
                line = "Params.%s = %s\n"%(varName, newVal)
            str += line
        f = open(getfile(module), 'w')
        f.write(str)

Params = ParameterStore()

# Simulation options
Params.FPS = 100.0
# This was originally at 100
Params.simulationSpeed = 1

## Mapping to real-world values
# Amount to multiply movement by
Params.moveCoefficient = 1.5
# Amount to multiply an angle by to get the time it takes to turn by that angle
Params.angle_to_time_coefficient = 1/17.0
Params.turnSpeed = 100

# MASS conversion at the moment: 1 unit means 54.5g at the moment

# Physical properties
## Ball
Params.ballCollisionElasticity = 0.4
Params.ballMass = 0.830088497
Params.ballRadius = 5
Params.ballFriction = 0.8

## Robots
# The robot has really high friction, it stops quickly without force applied
Params.robotMass = 20
Params.robotFriction = 0.95
Params.robotDims = (37, 55)
Params.robotElasticity = 0.3

### Kicker
Params.kickerDims = 20, 2
Params.kickerExtend = 20
Params.kickerMass = 2
Params.kickerElasticity = 0.7
Params.kickerOffset = 20
Params.kickerSpringStiffness = 6400
Params.kickerSpringDamping = 2
Params.kickerImpulse = 5000

### Wheels
Params.wheelMass = 10
Params.wheelRadius = 50
Params.wheelFriction = 0.95
Params.axleLength = Params.robotDims[0]/1.5

## Pitch
Params.pitchSize = (618, 311)
Params.goalY = 60
Params.wallElasticity = 0.2
