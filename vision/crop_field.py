from detect_field import *

def get_crop_coordinates(frame, tolerance=0):
    """
    Get crop coordinated for the actual image based on masked version.

    Threshold: By how much to adjust the values
    """
    # Smoothen and apply white mask
    mask = mask_field(normalize(frame))

    # Get FAST detection of features
    fast = cv2.FastFeatureDetector()

    # get keypoints
    kp = fast.detect(frame, None)

    x_min = min(kp, key=lambda x: x.pt[0]).pt[0]
    y_min = min(kp, key=lambda x: x.pt[1]).pt[1]
    x_max = max(kp, key=lambda x: x.pt[0]).pt[0]
    y_max = max(kp, key=lambda x: x.pt[1]).pt[1]

    return (
        x_min - tolerance, x_max + tolerance,
        y_min - tolerance, y_max + tolerance)