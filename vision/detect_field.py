import cv2
import numpy as np

WHITE_LOWER = np.array([1,0,100])
WHITE_HIGHER = np.array([36, 255, 255])

def mask_field(frame):
    # convert to hsv image
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # create a mask
    mask = cv2.inRange(hsv, WHITE_LOWER, WHITE_HIGHER)
    return mask

def view_image(img, label='Image'):
    cv2.imshow(label, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def normalize(img):
    kernel = np.ones((5, 5), np.float32) / 25
    dst = cv2.filter2D(img, -1, kernel)
    return dst
