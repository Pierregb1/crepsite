"""
Modèle 5 : bilan complet (évap, convection, IR atmos.)
(input)  lat, lon
(output) T[K] sur 8760 h
"""
import librairie_puissances as l_p
import parametres_surface as p_s
import parametre_convection as p_c
import fonction_calcul_alpha as f_c

dt = 3600                   # 1 h

def temp(lat=48.85, lon=2.35):
    cm   = p_s.classify_point(lon, lat)
    rho  = p_s.masse_volumique_point(lon, lat)
    A    = p_s.get_mean_albedo(lat, lon)
    h    = p_c.liste_h(lat, lon)
    alpha= f_c.calcul_alpha(5.67e-8*288**4, 2024)  # annee arbitraire
    d,S  = 0.1,1
    c    = cm*rho*S*d
    T    =[283]
    for i in range(24*365):
        P_em  = (l_p.P_em_surf_thermal(lat,lon,i,T[i])
                +l_p.P_em_surf_conv(lat,lon,i,T[i],283,h[i])
                +l_p.P_em_surf_evap(lat,lon,i))
        P_in  = (l_p.P_abs_surf_solar(lat,lon,i,A)
                +l_p.P_em_atm_thermal_down(lat,lon,i,alpha,P_em))
        T.append(T[i] + dt*(P_in-P_em)/c)
    return T[1:]
