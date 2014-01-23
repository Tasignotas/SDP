from detect_field import *

def get_crop_coordinates(frame, width=520, height=285):
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
    if not size:
        x_min, x_max, y_min, y_max = get_crop_coordinates(frame)
    else:
        x_min, x_max, y_min, y_max = size
    return frame[y_min:y_max, x_min:x_max]

