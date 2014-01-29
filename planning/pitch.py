import goal

D_PITCH = (255, 110)
D_ZONE_G = (50, 100)
D_ZONE_A = (50, 100)

W_BOUND = 15
W_STRIP = 5
W_BLOCK = 10
H_BLOCK = 20
H_GOAL = 20

S_PITCH = (0, 0)
S_ZONE_A = (W_STRIP, W_STRIP)
S_ZONE_B = (W_STRIP + D_ZONE_G[0] + W_BOUND, W_STRIP)
S_ZONE_C = (S_ZONE_B[0] + D_ZONE_A[0] + W_BOUND, W_STRIP)
S_ZONE_D = (S_ZONE_C[0] + D_ZONE_A[0] + W_BOUND, W_STRIP)

LL_BLOCK = (0, 0, W_BLOCK, H_BLOCK)
LR_BLOCK = (D_PITCH[0], 0, -W_BLOCK, H_BLOCK)
UL_BLOCK = (0, D_PITCH[1], W_BLOCK, -H_BLOCK)
UR_BLOCK = (D_PITCH[0], D_PITCH[1], -W_BLOCK, -H_BLOCK)

class Pitch:

    def __init__(self, robotA, robotB, robotC, robotD, ball):
        self.ball = ball
        self.goalA = goal.Goal(0, H_GOAL, 90, W_GOAL)
        self.goalD = goal.Goal(D_PITCH[0], H_GOAL, -90, W_GOAL)
        self.robotA = robotA
        self.robotB = robotB
        self.robotC = robotC
        self.robotD = robotD