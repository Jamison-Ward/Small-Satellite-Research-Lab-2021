# This program assigns an energy to a histogram data peak by accounting
# for the relative intensities of overlapped emission lines and 
# attenuation of x-ray intensity due to the detector housing

import math
import numpy
from scipy import interpolate

Al_density = 2.6989 # g/cm^3

def getInput():
    '''Stores user energy-intensity data pairs as dictionary
       key-value pairs and gets housing thickness'''
    print('\nNOTE: Please enter all input pairs as comma-seperated decimal numbers.'
          '\n      Enter "n" or "N" at any point to stop inputting data pairs.')
    line_dict = {}
    emisn_line = ''
    while emisn_line not in ('n', 'N'):
        try:
            emisn_line = input('\nEnter an emission line energy (keV) and relative intensity (%): ')
            if emisn_line in ('n', 'N'):  # Exit energy-intensity input loop
                continue
            emisn_line = emisn_line.split(',')
            line_dict[float(emisn_line[0].strip())] = float(emisn_line[1].strip())
        except:
            print('Error: Invalid input.\nPlease enter a comma-seperated data pair or "n"/"N" to finish data input.')
            
    good_value = False
    while good_value == False:
        try:
            hous_thick = float(input('\nEnter the housing thickness (mm): '))
            good_value = True
        except ValueError as error:
            print(error, 'Please enter a valid number.')
    return line_dict, hous_thick


def getAttenCoeff(photon_energy, energy_data, atten_data):
    '''Uses data read from input file to interpolate the mass
       attenuation coefficient based on the emission line energy'''
    log_energy, log_atten = numpy.log(energy_data), numpy.log(atten_data)
    interp_func = interpolate.interp1d(log_energy, log_atten, fill_value='extrapolate')
    new_log_atten = interp_func(numpy.log(photon_energy))
    new_atten = numpy.exp(new_log_atten)
    return new_atten
    

def adjustIntens(line_dict, hous_thick, energy_data, atten_data):
    '''Adjusts the emission line's relative intensity based on
       the attenuation coefficient and housing thickness'''
    for energy, intens_0 in line_dict.items():
        mass_atten_coeff = getAttenCoeff(energy, energy_data, atten_data)
        intens = intens_0 * ((math.e)**(-(mass_atten_coeff) * Al_density * (hous_thick / 10)))  # Attenuation formula, convert housing thickness from mm to cm
        line_dict[energy] = intens
    return line_dict
        

def weightedAverage(line_dict):
    '''Performs weighted average calculation of all emission line
       energies based on their adjusted relative intensities'''
    num_sum = 0
    den_sum = 0
    for energy, intens in line_dict.items():
        num_sum += (energy * intens)
        den_sum += intens
    peak_energy = num_sum / den_sum
    return peak_energy


def main():
    '''Opens raw attenuation data file, implements
       continuation loop, and calls relevant functions'''
    energy_data_points = []
    atten_data_points = []
    data_file = open('Al_attn_data_NIST.txt', 'r')  # Enter desired raw data file from which to interpolate
    for line in data_file:
        data_list = line.split()
        energy_data_points.append(float(data_list[0]) * 1000)  # Convert raw data energies from MeV to keV
        atten_data_points.append(float(data_list[1]))
    data_file.close()
    
    user_response = 'y'
    while user_response in ('y', 'Y'):
        emisn_lines, hous_thick = getInput()
        emisn_lines_adj = adjustIntens(emisn_lines, hous_thick, energy_data_points, atten_data_points)
        weighted_peak_energy = weightedAverage(emisn_lines_adj)
        print('\nThe weighted peak energy is {:.3f} keV.'.format(weighted_peak_energy))
        user_response = input('\nWould you like to calculate another weighted peak? ("y" or "Y" to continue): ')
    print('\nGoodbye')


if __name__ == '__main__':
    main()
