# This program performs a linear regression of and plots the linear source data

import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def get_input():
    file_name = 'source_data_new.txt'
    x_values, x_errors, y_values, y_errors = np.loadtxt(file_name, delimiter = ',', unpack=True)
    return x_values, x_errors, y_values, y_errors

def calc_sums(x_values, y_values, y_errors):
    S_x = 0
    S_y = 0
    S_xx = 0
    S_xy = 0
    S = 0
    for i in range(len(x_values)):
        S_x += x_values[i] / (y_errors[i] ** 2)
        S_y += y_values[i] / (y_errors[i] ** 2)
        S_xx += (x_values[i] ** 2) / (y_errors[i] ** 2)
        S_xy += (x_values[i] * y_values[i]) / (y_errors[i] ** 2)
        S += 1 / (y_errors[i] ** 2)
    return S_x, S_y, S_xx, S_xy, S

def calc_delta(S_xx, S, S_x):
    return (S_xx * S) - (S_x ** 2)

def calc_y_int(delta, S_xx, S_y, S_x, S_xy):
    return ((S_xx * S_y) - (S_x * S_xy)) / delta

def calc_slope(delta, S, S_xy, S_x, S_y):
    return ((S * S_xy) - (S_x * S_y)) / delta

def calc_y_int_error(delta, S_xx):
    return S_xx / delta

def calc_slope_error(delta, S):
    return S / delta

def plot_data(energies, energy_error, bins, bin_error, slope, slope_error, y_int, y_int_error):
    '''Plots the raw data and the linear fit on a graph'''
    plt.plot(np.linspace(0, 100), (np.linspace(0, 100) * slope) + y_int, zorder = 1)

    colors = ['red', 'gold', 'limegreen', 'royalblue']
    color_indicies = [2, 1, 3, 0, 2, 0]
    colormap = matplotlib.colors.ListedColormap(colors)
    plt.scatter(energies, bins, c = color_indicies, cmap = colormap, zorder = 3)
    plt.errorbar(energies[5], bins[5], bin_error[5], energy_error[5], ecolor = 'black', elinewidth = 1, capsize = 2, capthick = 1, zorder = 2)
    
    plt.title('SiPM-3000 Gain Calibration')
    plt.xlabel('Emission Line Energy (keV)')
    plt.ylabel('Histogram Bin Number (bin number)')
    plt.axis([0, 100, 0, 4096])
    plt.text(5, 3700, 'Linear fit slope (bins/keV): {:.2f} ± {:.2f}'.format(slope, slope_error))
    plt.text(5, 3400, 'Linear fit intercept (bins): {:.2f} ± {:.2f}'.format(y_int, y_int_error))
    plt.show()

def main():
    x_values, x_errors, y_values, y_errors = get_input()
    S_x, S_y, S_xx, S_xy, S = calc_sums(x_values, y_values, y_errors)
    delta = calc_delta(S_xx, S, S_x)
    y_int = calc_y_int(delta, S_xx, S_y, S_x, S_xy)
    slope = calc_slope(delta, S, S_xy, S_x, S_y)
    y_int_error = math.sqrt(calc_y_int_error(delta, S_xx))
    slope_error = math.sqrt(calc_slope_error(delta, S))
    print('The linear fit is: y = ({:.4f} ± {:.4f})x + ({:.4f} ± {:.4f})'.format(slope, slope_error, y_int, y_int_error))
    plot_data(x_values, x_errors, y_values, y_errors, slope, slope_error, y_int, y_int_error)


if __name__ == '__main__':
    main()
