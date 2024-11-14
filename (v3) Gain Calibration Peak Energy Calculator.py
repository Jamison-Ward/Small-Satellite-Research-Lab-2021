# This program assigns an energy to a histogram data peak by accounting
# for the relative intensities of overlapped emission lines and 
# attenuation of x-ray intensity due to the detector housing

import math
import numpy
from scipy import interpolate

def getInput(materials):
    '''Stores user energy-intensity-intensity error data triples  
       as dictionary key-value pairs and gets housing thickness'''
    print('\nNOTE: Please enter all input triples as comma-seperated vales.'
          '\n      Enter "n" or "N" at any point to stop inputting data triples.')
    line_dict = {}
    emisn_line = ''
    while emisn_line not in ('n', 'N'):
        try:
            emisn_line = input('\nEnter an emission line energy (keV), relative intensity (%), and relative intensity error (%): ')
            if emisn_line not in ('n', 'N'):
                emisn_line = emisn_line.split(',')
                line_dict[float(emisn_line[0].strip())] = {float(emisn_line[1].strip()): float(emisn_line[2].strip())}
        except:
            print('Error: Invalid input.\nPlease enter a comma-seperated data triple or "n"/"N" to finish data input.')

    hous_dict = {}
    hous_layer = ''
    while hous_layer not in ('n', 'N'):
        try:
            hous_layer = input('\nEnter a layer of housing material (elemental symbol), thickness (mm), and thickness error (mm): ')
            if hous_layer not in ('n', 'N'):
                hous_layer = hous_layer.split(',')
                hous_layer[0] = hous_layer[0].strip().lower()
                if hous_layer[0] in materials.keys():  # Retrieve material density
                    if hous_layer[0] not in hous_dict:  # Account for multiple layers of same material
                        hous_dict[hous_layer[0]] = [{float(hous_layer[1].strip()): float(hous_layer[2].strip())}]
                    else:
                        hous_dict[hous_layer[0]].append({float(hous_layer[1].strip()): float(hous_layer[2].strip())})
                else:
                    raise ValueError
        except:
            print('Error: Invalid input.\nPlease enter a comma-seperated data triple or "n"/"N" to finish data input.')
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
    # print('New atten:', new_atten)
    return new_atten


def adjustIntens(line_dict, hous_dict, dens_dict):
    '''Adjusts the emission line's relative intensity based on
       the attenuation coefficient and housing thickness'''
    for energy, intens_data in line_dict.items():
        for intens_0, intens_0_error in intens_data.items():
            # print('Incident intensity:', intens_0)
            # print('Error:', intens_0_error)
            intens_factor = 1
            quad_sum = 0
            for material, thick_list in hous_dict.items():
                atten_coeff = getAttenCoeff(energy, material)
                for thick_data in thick_list:
                    for thick, thick_error in thick_data.items():
                        # print('Thickness:', thick)
                        # print('Error:', thick_error)
                        intens_factor *= (math.e) ** (-(atten_coeff) * dens_dict[material] * (thick / 10))  # Attenuation formula, convert housing thickness from mm to cm
                        quad_sum += (thick_error / 10) ** 2  # Convert housing thickness error from mm to cm
            # print('Final intensity factor:', intens_factor)
            intens = intens_0 * intens_factor
            thick_error_tot = math.sqrt(quad_sum)
            # print('Total thickness error:', thick_error_tot)
            intens_error = math.sqrt((intens_factor * intens_0_error) ** 2 + (intens_0 * -(atten_coeff * dens_dict[material]) * intens_factor * thick_error_tot) ** 2)
            # print('Overall intensity error:', intens_error)
            line_dict[energy] = {intens: intens_error}
    return line_dict
        

def weightedAverage(line_dict):
    '''Performs weighted average calculation of all emission line
       energies based on their adjusted relative intensities'''
    numer_sum = 0
    denom_sum = 0
    energy_list = []
    intens_list = []
    intens_error_list = []
    for energy, intens_data in line_dict.items():
        for intens, intens_error in intens_data.items():
            numer_sum += (energy * intens)
            denom_sum += intens
            energy_list.append(energy)
            intens_list.append(intens)
            intens_error_list.append(intens_error)
    peak_energy = numer_sum / denom_sum
    # print(energy_list)
    # print(intens_list)
    # print(intens_error_list)
    sub_factor = 0
    for i in range(len(energy_list)):
        sub_factor += energy_list[i] * intens_list[i]
    # print(sub_factor)
    quad_sum = 0
    for i in range(len(energy_list)):
        part_deriv = ((sum(intens_list) * energy_list[i]) - sub_factor)/ ((sum(intens_list)) ** 2)
        quad_sum += (intens_error_list[i] * part_deriv) ** 2
    # print(quad_sum)
    peak_energy_error = math.sqrt(quad_sum)
    return peak_energy, peak_energy_error


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
        # print(emisn_lines)
        # print(hous_layers)
        emisn_lines_adj = adjustIntens(emisn_lines, hous_layers, dens_dict)
        # print(emisn_lines_adj)
        weighted_peak_energy, weighted_peak_energy_error = weightedAverage(emisn_lines_adj)
        print('\nThe weighted peak energy is {:.3f} ± {:.3f} keV.'.format(weighted_peak_energy, weighted_peak_energy_error))
        user_response = input('\nWould you like to calculate another weighted peak? ("y" or "Y" to continue): ')
    print('\nGoodbye')


if __name__ == '__main__':
    main()
