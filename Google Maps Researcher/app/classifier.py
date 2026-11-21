import numpy as np

CLASS_LABELS = {
    0: "other", 1: "water", 2: "vegetation",
    3: "built", 4: "bare_soil",
}

def classify(idx,
             water_thr=0.05,
             veg_thr=0.10,
             built_thr=0.55,
             soil_thr=0.15,
             bright_water_max=140.0):
    h, w = idx["vari"].shape
    mask = np.zeros((h, w), dtype=np.uint8)

    water = (idx["ndwi"] > water_thr) & (idx["bright"] < bright_water_max)
    mask[water] = 1

    veg = (mask == 0) & ((idx["vari"] > veg_thr) | (idx["exg"] > 10))
    mask[veg] = 2

    built = (mask == 0) & (idx["built"] > built_thr)
    mask[built] = 3

    soil = (mask == 0) & (idx["soil"] > soil_thr) & (idx["bright"] > 90)
    mask[soil] = 4

    return mask

def histogram(mask):
    counts = np.bincount(mask.ravel(), minlength=5)
    total = counts.sum() or 1
    return {CLASS_LABELS[i]: {"count": int(counts[i]),
                              "pct": round(100.0 * counts[i] / total, 2)}
            for i in range(5)}