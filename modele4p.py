"""
Modèle 4 : bilan + convection variable (vent NASA POWER)
(input)  lat, lon
(output) T[K] sur 8760 h
"""
import numpy as np, requests

sigma = 5.67e-8
c = 2.25e5
dt = 3600
S = 1
alpha = 0.77          # fraction IR réémise vers le bas

def coeff_conv(v):
    rho, mu, L, Pr, lam = 1.2, 1.8e-5, 1.0, 0.71, 0.026
    Re = rho*v*L/mu
    C,m,n = (0.664,0.5,1/3) if Re<5e5 else (0.037,0.8,1/3)
    Nu = C*Re**m*Pr**n
    return Nu*lam/L

def wind_365(lat, lon, year="2024"):
    url="https://power.larc.nasa.gov/api/temporal/daily/point"
    prm={"parameters":"WS2M","community":"AG","longitude":lon,"latitude":lat,
         "start":f"{year}0101","end":f"{year}1231","format":"JSON"}
    try:
        r=requests.get(url,params=prm).json()
        data=r["properties"]["parameter"]["WS2M"]
        return [data[d] for d in sorted(data)]
    except Exception:
        return [2.5]*365

def mean_albedo(lat, lon):
    url="https://power.larc.nasa.gov/api/temporal/daily/point"
    prm={"parameters":"ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP","community":"AG",
         "longitude":lon,"latitude":lat,"start":"20220101","end":"20231231",
         "format":"JSON"}
    try:
        d=requests.get(url,params=prm).json()
        down=d["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        up  =d["properties"]["parameter"]["ALLSKY_SFC_SW_UP"]
        vals=[up[k]/down[k] for k in down if down[k]>0 and up[k] is not None]
        return sum(vals)/len(vals) if vals else 0.3
    except Exception:
        return 0.3

def P_hour(lat, lon, j):
    S0=1361; lat,lon=np.radians([lat,lon])
    incl=np.radians(23.5)
    decl=np.arcsin(np.sin(incl)*np.sin(2*np.pi*(j-81)/365))
    sun=np.array([np.cos(decl),0,np.sin(decl)]); sun/=np.linalg.norm(sun)
    out=[]
    for h in range(24):
        ang=np.radians(15*(h-12))
        n=[np.cos(lat)*np.cos(lon+ang),np.cos(lat)*np.sin(lon+ang),np.sin(lat)]
        out.append(max(0,S0*np.dot(n,sun)))
    return out

def P_annee(lat, lon):
    return [val for j in range(1,366) for val in P_hour(lat,lon,j)]

def temp(lat=48.85, lon=2.35):
    P = P_annee(lat, lon)
    A = mean_albedo(lat, lon)
    vj= wind_365(lat, lon)
    T=[283]
    for i in range(len(P)):
        v = vj[i//24]
        h = coeff_conv(v)
        flux_in  = (1-A)*0.8*P[i]*S
        flux_out = (1-alpha/2)*sigma*T[i]**4 + h*(T[i]-283)
        dT = dt*(flux_in-flux_out)/c
        T.append(T[i]+dT)
    return T[1:]
