import cv2


class Simulator(object):
    
    def __init__(self):
        self.clean = cv2.imread('bg.jpg')
        cv2.namedWindow('Simulator')



    def run(self):
        """
        Run the simulation.
        """
        # self._initialize()
        while(1):
            cv2.imshow('Simulator', self.clean)
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