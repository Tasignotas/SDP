from models import World


class Planner:

    def __init__(self, our_side):
        self.world = World(our_side)

    def update_and_plan(self, position_dict):
        self.world.update_positions(position_dict)
        return self.plan()

    def plan(self):
        '''
        This method comes up with a plan - a list of actions that need
        to be performed. The plan is then carried out by the controller
        '''




        return ((0,0,0), (0,0,0))
