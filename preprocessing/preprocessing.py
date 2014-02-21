import cv2
from vision import tools


class Preprocessing(object):

    def __init__(self, options=None):
        if not options:
            # Which methods to run
            self.options = {
                'normalize': False
                'background_sub': False,
            }

        # Default setting for background subtractor
        self.background_sub = None

    def process(self, frame):

        results = {
            'frame': frame
        }

        # Apply normalization
        if self.options['normalize']:
            # Normalize only the saturation channel
            self.normalize(frame)
            results['frame'] = frame

        # Apply background subtraction
        if self.options['background_sub']:
            if self.background_sub:
                bg_mask = self.background_sub.apply(frame)
            else:
                self.background_sub = cv2.BackgroundSubtractorMOG2(0, 30, False)
                bg_mask = self.background_sub.apply(frame)
            results['background_sub'] = bg_mask

        return results

    def normalize(self, frame):
        """
        Normalize an image based on its Saturation channel. Returns BGR version
        of the image.
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame[:, :, 1] = cv2.equalizeHist(frame[:, :, :1])
        return cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
