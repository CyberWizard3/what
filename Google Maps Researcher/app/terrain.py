import numpy as np
import cv2
from scipy.spatial import Delaunay
from config import TRIANGULATION_POINTS, LINEAR_MIN_LEN

def luminance(bgr):
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

def pseudo_slope(lum_uint8, res_m):
    gx = cv2.Sobel(lum_uint8, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(lum_uint8, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.hypot(gx, gy) / (8.0 * res_m)
    aspect = (np.degrees(np.arctan2(-gx, gy)) + 360.0) % 360.0
    return mag.astype(np.float32), aspect.astype(np.float32)

def pseudo_hillshade(lum):
    return np.clip(lum, 0.0, 1.0)

def elevation_relief_stats(lum):
    return {
        "relief_min": float(lum.min()),
        "relief_max": float(lum.max()),
        "relief_mean": float(lum.mean()),
        "relief_std": float(lum.std()),
        "note": "relative (hillshade), not absolute meters",
    }

def triangulate(shape, n=TRIANGULATION_POINTS, seed=0):
    """Delaunay по уникальным точкам. Устойчиво к коллизиям и коллинеарности."""
    rng = np.random.default_rng(seed)
    h, w = shape
    if h < 2 or w < 2:
        return {"vertices": [], "simplices": []}

    raw = np.column_stack([
        rng.integers(0, w, n * 3),
        rng.integers(0, h, n * 3),
    ])
    pts = np.unique(raw, axis=0).astype(np.float64)[:n]

    if len(pts) < 3:
        return {"vertices": [], "simplices": []}

    try:
        tri = Delaunay(pts)
    except Exception:
        return {"vertices": [], "simplices": []}

    return {
        "vertices": pts.astype(int).tolist(),
        "simplices": tri.simplices.tolist(),
    }

def linear_structures(hs_uint8, min_len=LINEAR_MIN_LEN):
    if hs_uint8.dtype != np.uint8:
        hs_uint8 = hs_uint8.astype(np.uint8)
    edges = cv2.Canny(hs_uint8, 40, 120)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 40,
                            minLineLength=min_len, maxLineGap=4)
    if lines is None:
        return []
    return lines.reshape(-1, 4).astype(int).tolist()