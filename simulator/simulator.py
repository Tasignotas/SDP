import cv2
from scipy import ndimage
import copy

resetBackground = cv2.imread('bg.jpg')

def rotateImage(image, angle):
  rotated = ndimage.rotate(image, angle)
  return rotated


class Simulator(object):
    
    def __init__(self):
        
        # Images for display
        self.background = cv2.imread('bg.jpg')
        self.yellow = cv2.imread('yellow.jpg', -1)
        self.blue = cv2.imread('blue.jpg', -1)

        # Positions of the robots (x-coordonate, y-coordonate, angle)
        self.robots = {'y1': [50, 100, 90],
                       'y2': [300, 200, 40],
                       'b1': [200, 200, 10],
                       'b2': [450, 100, 90]}
        
        cv2.namedWindow('Simulator')

    # This is a pretty rudimentary function, just to test if the drawing works when chaning position.
    # It will have to be changed so that it actually translates commands from the planner into coordinates and angles
    # on the pitch.
    def updatePositions(self, actions):

        # Get height and width of the pitch and add some padding
        height, width, _ = self.background.shape
        height -= 50
        width -= 50
        
        # This will hold the next position of each yellow robot, computer below.
        dest = {'y1':[0,0], 'y2':[0,0]}
        for i in range(2):
            dest['y1'][i] = self.robots['y1'][i] + actions['attacker'][i][0]
            dest['y2'][i] = self.robots['y2'][i] + actions['defender'][i][0]
        
        # Checks if the next position is valid and updates it if so.
        for r in ['y1', 'y2']:
            if (20 < dest[r][0] and width > dest[r][0] and 20 < dest[r][1] and height > dest[r][1]):
                self.robots[r][0] = dest[r][0]
                self.robots[r][1] = dest[r][1]


    # Takes a background image (l_img) and overlays a smaller one (s_img) and draws it on top.
    def overlayImage(self, x_offset, y_offset, l_img, s_img):
        
        # This code takes alpha channel into account
        # for c in range(0,3):
        #     l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1], c] = \
        #     s_img[:,:,c] * (s_img[:,:,2]/255.0) +  l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1], c] * (1.0 - s_img[:,:,2]/255.0)

        # This code ignores alpha channel
        l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img

        return l_img        

    def getFrame(self):

        l_img = copy.copy(resetBackground)
        for robot in ['y1', 'y2', 'b1', 'b2']:
            x_offset = self.robots[robot][0]
            y_offset = self.robots[robot][1]

            # Rotate each robot image accord to the angle in its attributes and draw it
            # on top of the background
            if (robot[0] == 'y'):
                robot_image = rotateImage(self.yellow, self.robots[robot][2])
            elif (robot[0] == 'b'):
                robot_image = rotateImage(self.blue, self.robots[robot][2])
            l_img = self.overlayImage(x_offset, y_offset, l_img, robot_image)

        self.background = l_img
       
    def run(self):
        """
        Run the simulation.
        """
       
        # This is a placeholder. It will have to be updated in the loop by
        # calling a function from the planner.
        sampleActions = {'attacker':[[1],[-1.5]], 'defender':[[2],[2]]}


        while(1):

            self.updatePositions(sampleActions)

            self.getFrame()

            cv2.imshow('Simulator', self.background)
            
            # Press Esc to exit
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