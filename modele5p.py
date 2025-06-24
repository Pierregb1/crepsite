try:
    import librairie_puissances as l_p
    import fonction_calcul_alpha as f_c
    LIB_OK = True
except ImportError:
    from modele4p import temp as temp4
    LIB_OK = False

import parametres_surface as p_s
import parametre_convection as p_c
dt = 3600

def temp(lat=48.85, lon=2.35, year=2024):
    if not LIB_OK:
        return temp4(lat, lon)
    # ici tu peux insérer la vraie méthode du modèle 5 avec year
    import numpy as np
    return 273.15 + 10 * np.sin(np.linspace(0, 2*np.pi, 8760))  # exemple