
def temp():
    T0,T_lim,dt,N,h,S,c=100,20,0.01,1000,0.1,10,1
    T=[T0]
    for _ in range(1,N):
        T.append(T[-1]-dt*(T[-1]-T_lim)*h*S/c)
    return T
