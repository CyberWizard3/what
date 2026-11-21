import json, time, math
import numpy as np
import cv2
from config import ANALYSIS_DIR, TILES_DIR, DEFAULT_ZOOM
from app.tiles import fetch_mosaic
from app.indices_rgb import all_indices
from app.classifier import classify, histogram
from app.terrain import (
    luminance, pseudo_slope, pseudo_hillshade,
    elevation_relief_stats, triangulate, linear_structures,
)

def _png(arr, name, cmap=cv2.COLORMAP_VIRIDIS):
    a = arr.astype(np.float32)
    lo, hi = np.nanpercentile(a, 2), np.nanpercentile(a, 98)
    if hi <= lo:
        hi = lo + 1.0
    a = np.clip((a - lo) / (hi - lo), 0, 1)
    img = cv2.applyColorMap((a * 255).astype(np.uint8), cmap)
    cv2.imwrite(str(TILES_DIR / name), img)
    return f"/tiles/{name}"

def _gray(arr, name):
    a = arr.astype(np.float32)
    lo, hi = np.nanpercentile(a, 2), np.nanpercentile(a, 98)
    if hi <= lo:
        hi = lo + 1.0
    img = np.clip((a - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8)
    cv2.imwrite(str(TILES_DIR / name), img)
    return f"/tiles/{name}"

def _save_bgr(bgr, name):
    cv2.imwrite(str(TILES_DIR / name), bgr)
    return f"/tiles/{name}"

def _resolution_m(bbox, zoom):
    lat_mid = (bbox[1] + bbox[3]) / 2.0
    return 156543.03392 * math.cos(math.radians(lat_mid)) / (2 ** zoom)

def run_analysis(bbox, zoom=DEFAULT_ZOOM, include_roads=False):
    t0 = time.time()
    res_m = _resolution_m(bbox, zoom)

    # 1. Снимок → индексы → классификация
    sat = fetch_mosaic(bbox, zoom, "satellite")
    idx = all_indices(sat)
    mask = classify(idx)
    hist = histogram(mask)

    # 2. Terrain → рельеф / структуры / триангуляция
    terr = fetch_mosaic(bbox, zoom, "terrain")
    lum = luminance(terr)
    lum_u8 = (lum * 255).astype(np.uint8)
    slope, aspect = pseudo_slope(lum_u8, res_m)
    hs = pseudo_hillshade(lum)
    relief = elevation_relief_stats(lum)
    lines = linear_structures(lum_u8)
    tri = triangulate(lum.shape)

    # 3. Roads (опционально)
    roads_mask = None
    if include_roads:
        try:
            roads = fetch_mosaic(bbox, zoom, "roads")
            roads_mask = (cv2.cvtColor(roads, cv2.COLOR_BGR2GRAY) < 100) \
                         .astype(np.uint8) * 255
        except Exception:
            roads_mask = None

    # 4. Плитки для UI
    tiles = {
        "satellite":  _save_bgr(sat, "satellite.png"),
        "vari":       _png(idx["vari"], "vari.png"),
        "exg":        _png(idx["exg"], "exg.png"),
        "ndwi":       _png(idx["ndwi"], "ndwi.png", cv2.COLORMAP_OCEAN),
        "built":      _png(idx["built"], "built.png", cv2.COLORMAP_HOT),
        "soil":       _png(idx["soil"], "soil.png", cv2.COLORMAP_PINK),
        "bright":     _png(idx["bright"], "bright.png", cv2.COLORMAP_BONE),
        "hillshade":  _gray(hs, "hillshade.png"),
        "slope":      _png(slope, "slope.png", cv2.COLORMAP_TURBO),
        "aspect":     _png(aspect, "aspect.png", cv2.COLORMAP_HSV),
        "class_mask": _png(mask.astype(np.float32), "class_mask.png", cv2.COLORMAP_JET),
    }
    if roads_mask is not None:
        tiles["roads"] = _gray(roads_mask, "roads.png")

    result = {
        "bbox": bbox,
        "zoom": zoom,
        "resolution_m": round(res_m, 2),
        "elapsed_s": round(time.time() - t0, 2),
        "image_shape": list(sat.shape[:2]),
        "class_histogram": hist,
        "relief": relief,
        "slope_stats": {
            "mean": float(np.mean(slope)),
            "max": float(np.max(slope)),
            "aspect_mean_deg": float(np.mean(aspect)),
            "note": "relative gradient from hillshade, not degrees",
        },
        "structures": {
            "linear_count": len(lines),
            "linear_sample": lines[:40],
            "triangulation": {
                "vertex_count": len(tri["vertices"]),
                "triangle_count": len(tri["simplices"]),
                "simplices_sample": tri["simplices"][:30],
            },
        },
        "unsupported": [
            "LST (нет теплового канала)",
            "absolute elevation (нет DEM)",
            "minerals / oil / gas (нет геологической семантики)",
            "groundwater (нет гидрогеологии)",
        ],
        "tiles": tiles,
    }

    out = ANALYSIS_DIR / f"result_{int(t0)}.json"
    out.write_text(json.dumps(result, default=str, ensure_ascii=False))
    return result