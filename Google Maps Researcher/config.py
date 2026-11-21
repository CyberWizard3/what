from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TILES_DIR = DATA_DIR / "tiles"
RAW_DIR = DATA_DIR / "raw"
ANALYSIS_DIR = DATA_DIR / "analysis"
for d in (TILES_DIR, RAW_DIR, ANALYSIS_DIR):
    d.mkdir(parents=True, exist_ok=True)

GOOGLE_MIRRORS = ("mt0", "mt1", "mt2", "mt3")
GOOGLE_URL = "https://{m}.google.com/vt/lyrs={lyrs}&x={x}&y={y}&z={z}"
GOOGLE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36",
    "Referer": "https://maps.google.com/",
    "Accept": "image/webp,image/png,image/*,*/*;q=0.8",
}
LAYERS = {
    "satellite": "s",
    "terrain":   "p",
    "hybrid":    "y",
    "roads":     "m",
}

TILE_SIZE = 256
DEFAULT_ZOOM = 15
MAX_TILES = 400
WORKERS = 8

TRIANGULATION_POINTS = 80
LINEAR_MIN_LEN = 25