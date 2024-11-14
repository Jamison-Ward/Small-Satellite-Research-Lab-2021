import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.optimize import curve_fit

extracted = [
    6.095129470183376, 1.214470284237726,
    6.645468400721371, 1.2258397932816536,
    8.281113502433072, 1.262532299741602,
    11.701980920119627, 1.2733850129198965,
    14.697230145077945, 1.2620155038759688,
    17.064041995447834, 1.2516795865633075,
    23.00248435689463, 1.2180878552971575,
    31.747277244678738, 1.17312661498708,
    33.54264220263906, 1.165891472868217,
    41.79847235770523, 1.1932816537467699,
    45.932072426405185, 1.1984496124031008,
    47.77282101173263, 1.1922480620155038,
    60.474176882964365, 1.1850129198966408,
    78.99705870191063, 1.1317829457364341,
    89.58152058733208, 1.1328165374677002,
    187.51565993000793, 1.0578811369509045,
    362.8498621769143, 1.0315245478036177,
    516.7858099904173, 1.013953488372093,
    669.7898570955084, 0.9994832041343669,
    828.1113502433069, 0.99328165374677,
    1098.8935680071074, 0.9798449612403102,
    1265.86991519953, 0.9731266149870801,
]

energies = [e for e in extracted[::2]]
loge = np.log(energies)
prop = np.array([p for p in extracted[1::2]])
logp = np.log(prop)


def poly(x, *coefs):
    ret = 0
    for i, c in enumerate(coefs):
        ret += c * x**i
    return ret

def paper_func(e):
    reg_1 = [1.0668, -0.4788, 0.6504, -0.2341, 0.0255]
    reg_2 = [-8.4955, 6.5063, -0.2603, -0.5431, 0.0891]
    reg_3 = [-2.2456, 1.8069, -0.2370]
    reg_4 = [2.25090, -0.4982, 0.0423]
    outs = []
    outs.append(poly(e[np.logical_and(e >= 6, e <= 22)], *reg_1))
    outs.append(poly(e[np.logical_and(e > 22, e < 40)], *reg_2))
    outs.append(poly(e[np.logical_and(e >= 40, e < 70)], *reg_3))
    outs.append(poly(e[np.logical_and(e >= 70, e <= 200)], *reg_4))
    ret = np.array([])
    for part in outs:
        ret = np.concatenate((ret, part))
    return ret

def interp_extracted_test():
    fig, ax = plt.subplots()
    ax.scatter(energies, prop)
    smooth_energies = np.arange(np.min(energies), np.max(energies))

    ax.set_xscale('log')
    ax.plot(smooth_energies, interpolated_ratio(smooth_energies))
    plt.show()

def interpolated_ratio(energy):
    interp_func = interpolate.interp1d(loge, logp, fill_value="extrapolate")
    return np.exp(interp_func(np.log(energy)))

if __name__ == '__main__': interp_extracted_test()
