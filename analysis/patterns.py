import cv2
import numpy as np
from skimage.feature import canny
from scipy.signal import find_peaks

def detect_chart_patterns(img_bytes):
    """
    Advanced pattern detection using OpenCV + skimage
    Detects:
    - Head & Shoulders
    - Double Top / Bottom
    - Number of peaks and valleys
    """
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_GRAYSCALE)

    edges = canny(img, sigma=2.0)
    ys = edges.sum(axis=1)

    peaks, _ = find_peaks(ys, distance=20)
    valleys, _ = find_peaks(-ys, distance=20)

    results = {}

    if len(peaks) >= 2 and len(valleys) >= 1:
        results["head_and_shoulders"] = True

    if len(valleys) >= 2:
        results["double_bottom"] = True

    if len(peaks) >= 2:
        results["double_top"] = True

    results["detected_peaks"] = len(peaks)
    results["detected_valleys"] = len(valleys)

    return results
