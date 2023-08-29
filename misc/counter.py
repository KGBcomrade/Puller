import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import cumtrapz

radius, thetas = np.genfromtxt('misc/theta.csv')

def getLx(r0=62.5, Ltorch=0.49, lw=30, rw=20, dr=1):
    '''Вычисляет зависимость эфективной ширины пламяни L, радиуса перетяжки R
    от удлиннения волокна x. Также возвращает итоговое удлиннение волокна x_max
    Расчёт основан на предельных углах из статьи:
    Intermodal Energy Transfer in a Tapered Optical Fiber: Optimizing Transmission
    (fig 3)

    Args:
        r0 (float, optional): радиус не растянутого волокна. Defaults to 62.5.
        Ltorch (float, optional): физическая ширина пламени. Defaults to 0.49.
        lw (float, optional): длина перетяжки мм. Defaults to 30.
        rw (float, optional): радиус перетяжки. Defaults to 20.
        dr (float, optional): точность расчёта (должно быть меньше rw). Defaults to 1.
    '''
    def integr(y, x):
        inte = np.hstack((0, cumtrapz(y, x)))
        return inte

    def Map(fun, x):
        return np.array(list(map(fun, x)))

    lw = lw - Ltorch
    Theta = interp1d(radius, thetas, kind='cubic')
    r = np.arange(rw, r0, dr)
    dz = Map(lambda x: 1 / float(Theta(x)), r)
    z = integr(dz, r)
    z = z[-1] - z
    inte = integr((r**2), z)
    L = 1 / (r**2) * (rw**2 * (lw) + 2 * (-inte))
    x = 2 * z + L - L[-1]

    x = np.append(x, -0.1)
    r = np.append(r, r[-1])
    L = np.append(L, L[-1])
    R_x = interp1d(x, r, kind='cubic')
    L_x = interp1d(x, L, kind='cubic')
    xMax = x[0]
    rMin = radius.min()
    
    dz = np.array(list(map(lambda x: 1 / float(Theta(x) if r >= rMin else Theta(rMin)), r)))
    z = np.hstack((0, cumtrapz(dz, r)))
    return L_x, R_x, xMax, z, r