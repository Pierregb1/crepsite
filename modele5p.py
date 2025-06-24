
def temp_backend(lat, lon, year=2024):
    import math
    T=[288+0.1*math.sin(i/365*2*math.pi) for i in range(8760)]
    return T
