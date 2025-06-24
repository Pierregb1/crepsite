"""
Modèle 3 : influence convection + albédo NASA POWER
(input)  lat, lon  (° décimaux)
(output) liste T[K] sur 8760 h
"""
import numpy as np
import requests

sigma = 5.67e-8
c = 2.25e5          # J K⁻¹ m⁻² pour 0,1 m de sol humide
dt = 3600           # 1 h
S = 1
T_air = 283
h  = 10             # W m⁻² K⁻¹  (coef conv.)
start, end = "20220101", "20231231"

def mean_albedo(lat, lon, start_=start, end_=end):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    prm = {"parameters":"ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP","community":"AG",
           "longitude": lon,"latitude": lat,"start": start_,"end": end_,"format":"JSON"}
    try:
        d = requests.get(url, params=prm).json()
        down = d["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        up   = d["properties"]["parameter"]["ALLSKY_SFC_SW_UP"]
        vals = [up[k]/down[k] for k in down if down[k]>0 and up[k] is not None]
        return sum(vals)/len(vals) if vals else 0.3
    except Exception:
        return 0.3

def P_hour(lat, lon, j):
    S0 = 1361
    lat, lon = np.radians([lat, lon])
    incl=np.radians(23.5)
    decl=np.arcsin(np.sin(incl)*np.sin(2*np.pi*(j-81)/365))
    sun=np.array([np.cos(decl),0,np.sin(decl)]); sun/=np.linalg.norm(sun)
    out=[]
    for h in range(24):
        ang=np.radians(15*(h-12))
        n=[np.cos(lat)*np.cos(lon+ang),np.cos(lat)*np.sin(lon+ang),np.sin(lat)]
        out.append(max(0,S0*np.dot(n,sun)))
    return out

def puissance_annee(lat, lon):
    return [val for j in range(1,366) for val in P_hour(lat,lon,j)]

def temp(lat=48.85, lon=2.35):
    P = puissance_annee(lat, lon)
    A = mean_albedo(lat, lon)
    T=[283]
    for i in range(len(P)):
        flux_in  = (1-A)*P[i]*S
        flux_out = 0.5*sigma*T[i]**4 + h*(T[i]-T_air)
        dT = dt*(flux_in - flux_out)/c
        T.append(T[i]+dT)
    return T[1:]
