from detect_field import *

def get_crop_coordinates(frame, width=520, height=285):
    """
    Get crop coordinated for the actual image based on masked version.

    Threshold: By how much to adjust the values
    """
    # Smoothen and apply white mask
    mask = mask_field(normalize(frame))

    # Get FAST detection of features
    fast = cv2.FastFeatureDetector()

    # get keypoints
    kp = fast.detect(mask, None)

    x_min = min(kp, key=lambda x: x.pt[0]).pt[0]
    y_min = min(kp, key=lambda x: x.pt[1]).pt[1]
    x_max = max(kp, key=lambda x: x.pt[0]).pt[0]
    y_max = max(kp, key=lambda x: x.pt[1]).pt[1]

    x_delta = x_max - x_min
    y_delta = y_max - y_min

    x_remaining = (width - x_delta) / 2
    y_remaining = (height - y_delta) / 2

    return (
        x_min + x_remaining, x_max + x_remaining,
        y_min + y_remaining, y_max + y_remaining)