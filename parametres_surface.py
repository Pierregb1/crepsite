"""parametres_surface.py – version sans dépendances compilées
Essaie d'utiliser Basemap/Shapely si dispo, sinon fournit un fallback simple.
"""

def _fallback_classify(lat, lon):
    """Retourne capacité thermique massique approximative:
    1046 J/kg·K terre, 4180 mer, 2060 glace (>75° de latitude)
    """
    if abs(lat) > 75:
        return 2060
    # heuristique basique : latitudes |lon|<25 → mer sinon terre
    return 1046 if abs(lon) < 25 else 4180

def _fallback_rho(lat, lon):
    if abs(lat) > 75:
        return 917
    return 2600 if abs(lon) < 25 else 1000

def _fallback_albedo(lat, lon):
    return 0.3

# Essaye d'importer shapely/basemap
try:
    from shapely.geometry import Point, Polygon
    from mpl_toolkits.basemap import Basemap
    from matplotlib.figure import Figure

    fig = Figure()
    ax = fig.add_subplot(111)
    m = Basemap(projection='cyl', resolution='l', ax=ax)
    m.drawcoastlines()
    land_polygons = [Polygon(p.get_coords()) for p in m.landpolygons]

    def classify_point(lon, lat):
        if abs(lat) > 75:
            return 2060
        p = Point(lon, lat)
        return 1046 if any(poly.contains(p) for poly in land_polygons) else 4180

    def masse_volumique_point(lon, lat):
        if abs(lat) > 75:
            return 917
        p = Point(lon, lat)
        return 2600 if any(poly.contains(p) for poly in land_polygons) else 1000

except Exception as e:
    # Basemap/Shapely indisponibles
    print("Basemap/Shapely indisponibles, utilisation d'une approximation simple:", e)
    classify_point = lambda lon, lat: _fallback_classify(lat, lon)
    masse_volumique_point = lambda lon, lat: _fallback_rho(lat, lon)

import requests, functools, time

@functools.lru_cache(maxsize=32)
def _cached_nasa(url, params):
    for _ in range(3):
        try:
            r = requests.get(url, params=params, timeout=10)
            if r.ok:
                return r.json()
        except Exception:
            time.sleep(1)
    return None

def get_mean_albedo(lat, lon, start="20220101", end="20231231"):
    d = _cached_nasa(
        "https://power.larc.nasa.gov/api/temporal/daily/point",
        {"parameters":"ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP","community":"AG","longitude":lon,"latitude":lat,"start":start,"end":end,"format":"JSON"}
    )
    if not d: return _fallback_albedo(lat, lon)
    try:
        down = d['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        up   = d['properties']['parameter']['ALLSKY_SFC_SW_UP']
        vals = [up[k]/down[k] for k in down if down[k]>0 and up[k] is not None]
        return sum(vals)/len(vals) if vals else _fallback_albedo(lat, lon)
    except Exception:
        return _fallback_albedo(lat, lon)