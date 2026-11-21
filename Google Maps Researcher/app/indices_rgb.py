import numpy as np
import cv2

_EPS = 1e-6

def _channels(bgr):
    b = bgr[:, :, 0].astype(np.float32)
    g = bgr[:, :, 1].astype(np.float32)
    r = bgr[:, :, 2].astype(np.float32)
    return b, g, r

def brightness(bgr):
    b, g, r = _channels(bgr)
    return (b + g + r) / 3.0

def exg(bgr):
    """Excess Green — растительность (не нормировано, ×255)."""
    b, g, r = _channels(bgr)
    return 2.0 * g - r - b

def vari(bgr):
    """Visible Atmospherically Resistant Index."""
    b, g, r = _channels(bgr)
    den = g + r - b
    den[np.abs(den) < _EPS] = _EPS
    return (g - r) / den

def ngrdi(bgr):
    b, g, r = _channels(bgr)
    den = g + r
    den[den < _EPS] = _EPS
    return (g - r) / den

def ndwi_rgb(bgr):
    """Вода по синеве относительно зелёного (для RGB-снимков)."""
    b, g, _ = _channels(bgr)
    den = b + g
    den[den < _EPS] = _EPS
    return (b - g) / den

def bare_soil_proxy(bgr):
    """R доминирует над B — тёплый пиксель."""
    b, g, r = _channels(bgr)
    return (r - b) / 255.0

def builtup_proxy(bgr):
    """Низкая насыщенность + высокая яркость."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1].astype(np.float32) / 255.0
    v = hsv[:, :, 2].astype(np.float32) / 255.0
    return (1.0 - s) * v

def all_indices(bgr):
    return {
        "exg":    exg(bgr),
        "vari":   vari(bgr),
        "ngrdi":  ngrdi(bgr),
        "ndwi":   ndwi_rgb(bgr),
        "soil":   bare_soil_proxy(bgr),
        "built":  builtup_proxy(bgr),
        "bright": brightness(bgr),
    }