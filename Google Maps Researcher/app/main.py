from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from config import BASE_DIR, TILES_DIR, DEFAULT_ZOOM
from app.analysis import run_analysis

app = FastAPI(title="Watershed Analyzer (Google-only)", version="3.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/tiles",  StaticFiles(directory=TILES_DIR), name="tiles")

@app.get("/")
def root():
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/api/health")
def health():
    return {"ok": True, "source": "Google tiles (mt0-3)", "version": "3.1.0"}

@app.get("/api/analyze")
async def analyze(
    lon_min: float = Query(..., ge=-180, le=180),
    lat_min: float = Query(..., ge=-85,  le=85),
    lon_max: float = Query(..., ge=-180, le=180),
    lat_max: float = Query(..., ge=-85,  le=85),
    zoom: int = DEFAULT_ZOOM,
    include_roads: bool = False,
):
    if lon_max <= lon_min or lat_max <= lat_min:
        raise HTTPException(400, "invalid bbox")
    if not (13 <= zoom <= 18):
        raise HTTPException(400, "zoom must be 13..18")
    bbox = [lon_min, lat_min, lon_max, lat_max]
    try:
        result = await run_in_threadpool(run_analysis, bbox, zoom, include_roads)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"analysis failed: {e}")
    return JSONResponse(result)