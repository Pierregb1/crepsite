"""
Version légère de parametres_surface.py sans dépendance Basemap/Shapely.
Fournit :
  - classify_point(lon, lat)      -> capacité thermique massique (J/kg/K)
  - masse_volumique_point(lon, lat) -> masse volumique (kg/m³)
  - get_mean_albedo(lat, lon, ...) -> albédo moyen via NASA POWER
"""
import requests

# Valeurs par défaut (terre)
C_TERRE  = 1046   # J/kg/K
RHO_TERRE= 2600   # kg/m³
C_MER    = 4180
RHO_MER  = 1000
C_GLACE  = 2060
RHO_GLACE= 917

def _is_land_simple(lat, lon):
    """Approche simplifiée : latitudes élevées = glace, sinon terre.
    On ne distingue pas précisément continents/océans sans Basemap.
    """
    if abs(lat) > 75:
        return "ice"
    # Simple heuristique: longitudes entre -30 et 60 sur latitudes  -60..60 → océan Atlantique/Indien => mer
    if -30 < lon < 60 and -60 < lat < 60:
        return "sea"
    return "land"

def classify_point(lon, lat):
    cat = _is_land_simple(lat, lon)
    if cat == "ice":
        return C_GLACE
    elif cat == "sea":
        return C_MER
    else:
        return C_TERRE

def masse_volumique_point(lon, lat):
    cat = _is_land_simple(lat, lon)
    if cat == "ice":
        return RHO_GLACE
    elif cat == "sea":
        return RHO_MER
    else:
        return RHO_TERRE

def get_mean_albedo(lat, lon, start="20220101", end="20231231"):
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }
    try:
        data = requests.get(url, params=params, timeout=8).json()
        down = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        up   = data['properties']['parameter']['ALLSKY_SFC_SW_UP']
        vals = [up[d]/down[d] for d in down if down[d]>0 and up[d] is not None]
        return sum(vals)/len(vals) if vals else 0.3
    except Exception:
        return 0.3