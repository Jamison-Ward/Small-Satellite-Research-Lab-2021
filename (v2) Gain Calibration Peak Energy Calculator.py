# This program assigns an energy to a histogram data peak by accounting
# for the relative intensities of overlapped emission lines and 
# attenuation of x-ray intensity due to the detector housing

import math
import numpy
from scipy import interpolate

def getInput(materials):
    '''Stores user energy-intensity data pairs as dictionary
       key-value pairs and gets housing thickness'''
    print('\nNOTE: Please enter all input pairs as comma-seperated vales.'
          '\n      Enter "n" or "N" at any point to stop inputting data pairs.')
    line_dict = {}
    emisn_line = ''
    while emisn_line not in ('n', 'N'):
        try:
            emisn_line = input('\nEnter an emission line energy (keV) and relative intensity (%): ')
            if emisn_line not in ('n', 'N'):
                emisn_line = emisn_line.split(',')
                line_dict[float(emisn_line[0].strip())] = float(emisn_line[1].strip())
        except:
            print('Error: Invalid input.\nPlease enter a comma-seperated data pair or "n"/"N" to finish data input.')

    hous_dict = {}
    hous_layer = ''
    while hous_layer not in ('n', 'N'):
        try:
            hous_layer = input('\nEnter a layer of housing material (elemental symbol) and thickness (mm): ')
            if hous_layer not in ('n', 'N'):
                hous_layer = hous_layer.split(',')
                hous_layer[0] = hous_layer[0].strip().lower()
                if hous_layer[0] in materials.keys():  # Retrieve material density
                    if hous_layer[0] not in hous_dict:  # Account for multiple layers of same material
                        hous_dict[hous_layer[0]] = [float(hous_layer[1].strip())]
                    else:
                        hous_dict[hous_layer[0]].append(float(hous_layer[1].strip()))
                else:
                    raise ValueError
        except:
            print('Error: Invalid input.\nPlease enter a comma-seperated data pair or "n"/"N" to finish data input.')
    return line_dict, hous_dict


def getAttenCoeff(photon_energy, hous_material):
    '''Uses data read from input file to interpolate the mass
       attenuation coefficient based on the emission line energy'''
    energy_data_points = []
    atten_data_points = []
    data_file = open('{}_atten_data_NIST.txt'.format(hous_material.capitalize()), 'r')  # Read desired raw data file from which to interpolate
    for line in data_file:
        data_list = line.split()
        energy_data_points.append(float(data_list[0]) * 1000)  # Convert raw data energies from MeV to keV
        atten_data_points.append(float(data_list[1]))
    data_file.close()
    
    log_energy, log_atten = numpy.log(energy_data_points), numpy.log(atten_data_points)
    interp_func = interpolate.interp1d(log_energy, log_atten, fill_value='extrapolate')
    new_log_atten = interp_func(numpy.log(photon_energy))
    new_atten = numpy.exp(new_log_atten)
    # print(new_atten)
    return new_atten


def adjustIntens(line_dict, hous_dict, dens_dict):
    '''Adjusts the emission line's relative intensity based on
       the attenuation coefficient and housing thickness'''
    for energy, intens_0 in line_dict.items():
        intens_factor = 1
        for material, thick_list in hous_dict.items():
            atten_coeff = getAttenCoeff(energy, material)
            for thick in thick_list:
                intens_factor *= (math.e) ** (-(atten_coeff) * dens_dict[material] * (thick / 10))  # Attenuation formula, convert housing thickness from mm to cm
        intens = intens_0 * intens_factor
        line_dict[energy] = intens
    return line_dict
        

def weightedAverage(line_dict):
    '''Performs weighted average calculation of all emission line
       energies based on their adjusted relative intensities'''
    numer_sum = 0
    denom_sum = 0
    for energy, intens in line_dict.items():
        numer_sum += (energy * intens)
        denom_sum += intens
    peak_energy = numer_sum / denom_sum
    return peak_energy


def main():
    '''Retrieves material densities, implements
       continuation loop, and calls relevant functions'''
    dens_dict = {}  # g/cm^3
    elem_file = open('elem_densities_NIST.txt', 'r')
    for line in elem_file:
        data_list = line.split()
        dens_dict[data_list[1].strip().lower()] = float(data_list[5].strip())
    elem_file.close()
    comp_mix_file = open('comp_mix_densities_NIST.txt', 'r')
    for line in comp_mix_file:
        data_list = line.split()
        dens_dict[data_list[0].strip().lower()] = float(data_list[3].strip())
    comp_mix_file.close()
    #print(dens_dict)
    
    user_response = 'y'
    while user_response in ('y', 'Y'):
        emisn_lines, hous_layers = getInput(dens_dict)
        #print(emisn_lines)
        #print(hous_layers)
        emisn_lines_adj = adjustIntens(emisn_lines, hous_layers, dens_dict)
        #print(emisn_lines_adj)
        weighted_peak_energy = weightedAverage(emisn_lines_adj)
        print('\nThe weighted peak energy is {:.3f} keV.'.format(weighted_peak_energy))
        user_response = input('\nWould you like to calculate another weighted peak? ("y" or "Y" to continue): ')
    print('\nGoodbye')


if __name__ == '__main__':
    main()
