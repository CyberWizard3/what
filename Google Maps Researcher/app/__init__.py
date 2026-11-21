"""Watershed Analyzer — Google-tiles-only analysis package.

Модули:
    mercator     — Web Mercator ↔ WGS84, grid тайлов
    tiles        — загрузка и сшивка тайлов Google
    indices_rgb  — RGB-индексы (VARI, ExG, NDWI_rgb, built, soil)
    classifier   — 5-классовая маска + гистограмма
    terrain      — уклон/аспект/hillshade/структуры/триангуляция
    analysis     — пайплайн (s→indices→mask→terrain→PNG+JSON)
    main         — FastAPI-приложение
"""
__version__ = "3.1.0"