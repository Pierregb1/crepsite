def temp():
    T0=100; T_lim=20; dt=0.01; N=1000; h=0.1; S=10; c=1
    T=[T0]
    for _ in range(1,N):
        T.append(T[-1] - dt*(T[-1]-T_lim)*h*S/c)
    return T