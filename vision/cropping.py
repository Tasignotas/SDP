import numpy as np
import cv2
from crop_field import *
from detect_field import *

cap = cv2.VideoCapture(0)

ret,frame = cap.read()

mask = mask_field(frame)

print get_crop_coordinates(frame)

view_image(mask)
