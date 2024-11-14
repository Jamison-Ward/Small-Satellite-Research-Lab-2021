# This program plots the raw source data and performs a linear fit of the data

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def get_input():
    '''Obtains raw bin number and peak energy data
       and can be set to accept user input file name'''
    good_data = False
    while good_data == False:
        try:
            #input_name = input('Enter data file name with extension (e.g. .txt): ')
            input_ref = open('source_data.txt', 'r')
            input_contents = []
            for line in input_ref:
                line = line.strip()
                data_list = line.split(',')
                for i in range(len(data_list)):
                    data_list[i] = float(data_list[i])
                input_contents.append(data_list)
            input_ref.close()
            good_data = True
        except FileNotFoundError:
            print('File not found.\nPlease enter a valid file name.')
    return input_contents

def format_data(data_list):
    '''Organizes raw bin and energy data into lists for plotting'''
    bin_list = []
    energy_list = []
    for data_pair in data_list:
        bin_list.append(data_pair[0])
        energy_list.append(data_pair[1])
    return bin_list, energy_list

def lin_fit(x, m, b):
    '''Performs a linear fit of the data'''
    return m * np.array(x, dtype=np.float64) + b

def plot_data(bins, energies):
    '''Plots the raw data and the linear fit on a graph'''
    opt_parameters, covar = curve_fit(lin_fit, bins, energies)
    print('Optimized parameters:', opt_parameters)
    errors = np.sqrt(np.diag(covar))
    print('Associated errors:', errors)
    plt.scatter(bins, energies)
    plt.plot(np.linspace(0,4096), lin_fit(np.linspace(0,4096), *opt_parameters))
    plt.title('SiPM-3000 Third Gain Calibration')
    plt.xlabel('ADC Bin Number')
    plt.ylabel('Photon Energy (keV)')
    plt.axis([0, 4096, 0, 100])
    plt.text(100, 90, 'Linear fit slope (keV/bin): {:.5f} ± {:.5f}'.format(opt_parameters[0], errors[0]))
    plt.text(100, 83, 'Linear fit intercept (keV): {:.2f} ± {:.2f}'.format(opt_parameters[1], errors[1]))
    plt.show()

def main():
    '''Manages function calls'''
    line_data = get_input()
    #print(line_data)
    bin_data, energy_data = format_data(line_data)
    #print(bin_data)
    #print(energy_data)
    plot_data(bin_data, energy_data)


if __name__ == '__main__':
    main()
                
