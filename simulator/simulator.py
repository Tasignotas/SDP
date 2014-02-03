import cv2


class Simulator(object):
    
    def __init__(self):
        
        # Images for display
        self.background = cv2.imread('bg.jpg')
        self.yellow = cv2.imread('yellow.jpg')
        self.blue = cv2.imread('blue.jpg')

        # Positions of the robots
        self.robots = {'y1': (100, 100, 0),
                       'y2': (200, 100, 0),
                       'b1': (300, 100, 0),
                       'b2': (400, 100, 0)}
        cv2.namedWindow('Simulator')

    def getFrame(self):

        for robot in ['y1', 'y2']:
            x_offset = self.robots[robot][0]
            y_offset = self.robots[robot][1]
            self.background[y_offset:y_offset+self.yellow.shape[0], x_offset:x_offset+self.yellow.shape[1]] = self.yellow

        for robot in ['b1', 'b2']:
            x_offset = self.robots[robot][0]
            y_offset = self.robots[robot][1]
            self.background[y_offset:y_offset+self.blue.shape[0], x_offset:x_offset+self.blue.shape[1]] = self.blue


    def run(self):
        """
        Run the simulation.
        """

        while(1):
            self.getFrame()
            cv2.imshow('Simulator', self.background)
            k = cv2.waitKey(5) & 0xFF

            if k == 27:
                break

    def _initialize(self):
        """
        Display an image and make the user select points for the
        starting locations of the robots.

        Should draw circles/squares in the locations selected to
        provide visual feedback

        Params:
            ?? May decide to load this optionally from a file ??

        returns None
        """
        pass

    def _get_image(self, path):
        """
        Get the basic pitch image for the simulator

        Params:
            [String] path       path to the image, relative to run_simulator.py

        Returns:
            cv2 frame
        """
        pass


sim = Simulator()
sim.run()