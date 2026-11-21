import math

def lonlat_to_pixel(lon, lat, z):
    """Дробные пиксельные координаты в мировом полотне (256·2^z)."""
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n * 256
    lat_r = math.radians(max(min(lat, 85.05112878), -85.05112878))
    y = (1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n * 256
    return x, y

def pixel_to_lonlat(px, py, z):
    n = 2 ** z
    lon = px / (256 * n) * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * py / (256 * n)))))
    return lon, lat

def bbox_to_grid(bbox, z):
    """Возвращает границы тайлов + точные пиксели обрезки."""
    lon_min, lat_min, lon_max, lat_max = bbox
    px0, py0 = lonlat_to_pixel(lon_min, lat_max, z)
    px1, py1 = lonlat_to_pixel(lon_max, lat_min, z)
    tx0, ty0 = int(px0 // 256), int(py0 // 256)
    tx1, ty1 = int(px1 // 256), int(py1 // 256)
    return {
        "tx0": tx0, "ty0": ty0, "tx1": tx1, "ty1": ty1,
        "crop": (
            int(px0 - tx0 * 256), int(py0 - ty0 * 256),
            int(px1 - tx0 * 256), int(py1 - ty0 * 256),
        ),
    }