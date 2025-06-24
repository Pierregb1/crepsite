import math
def temp_backend(lat, lon, year=2024, view='year'):
    hrs=24*365
    T=[288+10*math.sin(2*math.pi*i/hrs)+2*math.sin(2*math.pi*i/24) for i in range(hrs)]
    if view=='month':
        return T[:24*31]
    if view=='day':
        return T[:24]
    return T