import cv2
import numpy as np
from scipy import ndimage

def rotateImage(image, angle):
  rotated = ndimage.rotate(image, angle)
  return rotated


class Simulator(object):
    
    def __init__(self):
        
        # Images for display
        self.background = cv2.imread('bg.jpg')
        self.yellow = cv2.imread('yellow.jpg', -1)
        self.blue = cv2.imread('blue.jpg', -1)

        # Positions of the robots
        self.robots = {'y1': [100, 200, 0],
                       'y2': [200, 200, 20],
                       'b1': [300, 200, 180],
                       'b2': [400, 200, 90]}
        cv2.namedWindow('Simulator')

    def overlayImage(self, x_offset, y_offset, s_img):
        l_img = self.background
        for c in range(0,3):
            l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1], c] = \
            s_img[:,:,c] * (s_img[:,:,2]/255.0) +  l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1], c] * (1.0 - s_img[:,:,2]/255.0)
        self.background = l_img        

    def getFrame(self):

        for robot in ['y1', 'y2', 'b1', 'b2']:
            x_offset = self.robots[robot][0]
            y_offset = self.robots[robot][1]
            if robot[0] == 'y':
                robot_image = rotateImage(self.yellow, self.robots[robot][2])
            elif robot[0] == 'b':
                robot_image = rotateImage(self.blue, self.robots[robot][2])
            self.overlayImage(x_offset, y_offset, robot_image)

       
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


# sim = Simulator()
# sim.run()