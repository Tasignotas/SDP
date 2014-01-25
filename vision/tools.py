import numpy as np
import cv2


# HSV Colors
WHITE_LOWER = np.array([1,0,100])
WHITE_HIGHER = np.array([36, 255, 255])

BLUE_LOWER = np.array([95., 50.,50.])
BLUE_HIGHER = np.array([110.,255.,255.])

RED_LOWER = np.array([0, 240, 140])
RED_HIGHER = np.array([9, 255, 255])

YELLOW_LOWER = np.array([9, 50, 50])
YELLOW_HIGHER = np.array([11, 255, 255])

def find_crop_coordinates(frame, width=520, height=285):
    """
    Get crop coordinated for the actual image based on masked version.

    Params:
        [int] width     fixed width of the image to crop to
        [int[ height    fixed height of the image to crop to

    Returns:
        A 4-tuple with crop values
    """
    frame_width, frame_height, channels = frame.shape
    if frame_width < width or frame_height < height:
        print 'get_crop_coordinates:', 'Requested size of the frame is smaller than the original frame'
        return frame

    # Smoothen and apply white mask
    mask = mask_field(normalize(frame))

    # Get FAST detection of features
    fast = cv2.FastFeatureDetector()

    # get keypoints - list of Keypoints with x/y coordinates
    kp = fast.detect(mask, None)

    x_min = min(kp, key=lambda x: x.pt[0]).pt[0]
    y_min = min(kp, key=lambda x: x.pt[1]).pt[1]
    x_max = max(kp, key=lambda x: x.pt[0]).pt[0]
    y_max = max(kp, key=lambda x: x.pt[1]).pt[1]

    x_delta = x_max - x_min
    y_delta = y_max - y_min

    x_remaining = max(0, (width - x_delta) / 2)
    y_remaining = max(0, (height - y_delta) / 2)

    return (
        x_min + x_remaining, x_max + x_remaining,
        y_min + y_remaining, y_max + y_remaining)

def crop(frame, size=None):
    """
    Crop a frame given the size.
    If size not provided, attempt to extract the field and crop.

    Params:
        [OpenCV Frame] frame    frame to crop
        [(x1,x2,y1,y2)] size
    """
    if not size:
        x_min, x_max, y_min, y_max = get_crop_coordinates(frame)
    else:
        x_min, x_max, y_min, y_max = size
    return frame[y_min:y_max, x_min:x_max]

def adjust_light(frame, brightness=2.0, contrast=50.0):
    """
    Increase image brightness and/or contrast.

    Params:
        [float] brightness      brightness increase factor (1.0 - 3.0)
        [float] contrast        contrast increase factor (1.0 - 100.0)

    Returns:
        updated frame
    """
    brightness = max(3.0, float(brightness))
    contrast = max(100.0, float(contrast))
    return cv2.add(cv2.multiply(frame, np.array[brightness]), np.array([contrast]))

def view(frame, label='Frame'):
    """
    Display an image using OpenCV
    """
    cv2.imshow(label, frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def mask(frame, lower, higher):
    """
    Create an image mask.

    Params:
        [OpenCV frame] frame    frame to mask
        [HSV color] lower       lower boundary for color matching
        [HSV color] higher      higher boundary for color matching

    Returns:
        masked frame
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, lower, higher)

def slice(frame, pieces=4):
    """
    TODO

    Given a frame, slice into n pieces given by the argument.
    Either use fancy methods for precise slicing or just split into n equal for now.
    To get size do frame.shape

    Returns:
        [4-tuple  of 2-tuples]  of slized frames, offset is the
                                distance from the left side of the original frame
    """
    offset = 0
    return ((frame, offset), (frame, offset), (frame, offset), (frame, offset))
