import mock

def update(ball, robotA, robotB, robotC, robotD):
    ball.position = mock.get_ball()
    robotA.position = mock.get_robotA()
    robotB.position = mock.get_robotB()
    robotC.position = mock.get_robotC()
    robotD.position = mock.get_robotD()
    return (ball, robotA, robotB, robotC, robotD)

