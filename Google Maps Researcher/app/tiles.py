import random
import numpy as np
import cv2
import requests
from concurrent.futures import ThreadPoolExecutor
from config import (
    GOOGLE_MIRRORS, GOOGLE_URL, GOOGLE_HEADERS, LAYERS,
    TILE_SIZE, MAX_TILES, WORKERS,
)
from app.mercator import bbox_to_grid

_session = requests.Session()
_session.headers.update(GOOGLE_HEADERS)

_PLACEHOLDER = np.full((TILE_SIZE, TILE_SIZE, 3), 128, dtype=np.uint8)

def _get_tile(tx, ty, z, lyrs):
    """Один тайл с 3 попытками и ротацией зеркал."""
    for attempt in range(3):
        mirror = GOOGLE_MIRRORS[(tx + ty + attempt) % len(GOOGLE_MIRRORS)]
        url = GOOGLE_URL.format(m=mirror, lyrs=lyrs, x=tx, y=ty, z=z)
        try:
            r = _session.get(url, timeout=12)
            if r.status_code != 200 or not r.content:
                continue
            img = cv2.imdecode(np.frombuffer(r.content, np.uint8),
                               cv2.IMREAD_COLOR)
            if img is not None and img.shape[:2] == (TILE_SIZE, TILE_SIZE):
                return img
        except Exception:
            continue
    return _PLACEHOLDER.copy()

def fetch_mosaic(bbox, zoom, layer="satellite"):
    """Параллельно тянет тайлы, склеивает, кропает по bbox."""
    lyrs = LAYERS[layer]
    g = bbox_to_grid(bbox, zoom)
    nx = g["tx1"] - g["tx0"] + 1
    ny = g["ty1"] - g["ty0"] + 1
    if nx * ny > MAX_TILES:
        raise ValueError(
            f"bbox too big: {nx*ny} tiles > MAX_TILES({MAX_TILES}). "
            f"Уменьшите bbox или zoom."
        )

    W, H = nx * TILE_SIZE, ny * TILE_SIZE
    mosaic = np.zeros((H, W, 3), dtype=np.uint8)

    coords = [
        (i, j, tx, ty)
        for i, tx in enumerate(range(g["tx0"], g["tx1"] + 1))
        for j, ty in enumerate(range(g["ty0"], g["ty1"] + 1))
    ]

    def _job(args):
        i, j, tx, ty = args
        return i, j, _get_tile(tx, ty, zoom, lyrs)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for i, j, tile in ex.map(_job, coords):
            y0, x0 = j * TILE_SIZE, i * TILE_SIZE
            mosaic[y0:y0 + TILE_SIZE, x0:x0 + TILE_SIZE] = tile

    cx0, cy0, cx1, cy1 = g["crop"]
    return mosaic[cy0:cy1, cx0:cx1]