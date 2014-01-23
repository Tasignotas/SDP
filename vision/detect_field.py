import cv2
import numpy as np

WHITE_LOWER = np.array([1,0,100])
WHITE_HIGHER = np.array([36, 255, 255])

BLUE_LOWER = np.array((213, 32,  54))
BLUE_HIGHER = np.array((255, 32,  54))

def mask_field(frame, lower=WHITE_LOWER, higher=WHITE_HIGHER):
    # convert to hsv image
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # create a mask
    mask = cv2.inRange(hsv, lower, higher)
    return mask

def view_image(img, label='Image'):
    cv2.imshow(label, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def normalize(img):
    kernel = np.ones((5, 5), np.float32) / 25
    dst = cv2.filter2D(img, -1, kernel)
    return dst

def brighten(img, alpha, beta):
    mul_img = cv2.multiply(img, np.array([alpha]))
    new_img = cv2.add(mul_img,np.array([beta]))
    return new_img
