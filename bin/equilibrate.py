#!/usr/bin/env -S python -B

# © Copyright IBM Corp. 2022 All Rights Reserved

import argparse
import itertools
import json
import os

import numpy as np
import pandas as pd
import pymser

# Required parameters
parser = argparse.ArgumentParser(description='Parse output of RASPA simulation.')
parser.add_argument('output_folder',
                    type=str,
                    action='store',
                    metavar='OUTPUT_FOLDER',
                    help='Directory for storing output files.')

# Optional parameters
parser.add_argument('--FlueGasComposition',
                    action='store',
                    required=False,
                    type=json.loads,
                    default={'CO2': 1.0},
                    metavar='FLUE_GAS_COMPOSITION',
                    help='Dictionary containing flue gas component names and fractions.')
parser.add_argument('--ExternalTemperature',
                    type=float,
                    default=298.0,
                    action='store',
                    required=False,
                    metavar='EXTERNAL_TEMPERATURE',
                    help='External temperature [Kelvin].')
parser.add_argument('--ExternalPressure',
                    type=str,
                    action='store',
                    required=False,
                    default="101325",
                    metavar='EXTERNAL_PRESSURE(S)',
                    help='External pressure [Pascal]. Accepts a comma-separated list of values.')
parser.add_argument('--Uncertainty',
                    type=str,
                    default='uSD',
                    action='store',
                    required=False,
                    metavar='UNCERTAINTY',
                    choices=['SD', 'SE', 'uSD', 'uSE'],
                    help='Select the version of desired uncertainty.')
parser.add_argument('--EquilibrationRule',
                    type=str,
                    default='global',
                    action='store',
                    required=False,
                    metavar='EQUILIBRATION_RULE',
                    choices=['global', 'individual'],
                    help='Select between global or individual equilibration for each component.')
parser.add_argument('--BatchSize',
                    type=int,
                    default=5,
                    action='store',
                    required=False,
                    metavar='BATCH_SIZE',
                    help='Size of batch to take the average.')
parser.add_argument('--LLM',
                    default=False,
                    required=False,
                    action='store_true',
                    help='Use the LLM version of MSER.')
parser.add_argument('--PrintResults',
                    default=True,
                    required=False,
                    action='store_true',
                    help='Print the results of MSER and ADF test.')
arg = parser.parse_args()

# Manipulate ExternalPressure string
externalPressures = list(map(float, arg.ExternalPressure.split(',')))

# Iterate over the parsed raspa files on output folder
for pressure in externalPressures:

    # Reads the parsed result with pandas
    csv_filename = f'raspa_{arg.ExternalTemperature:.6f}_{pressure:.0f}.csv'
    data = pd.read_csv(os.path.join(arg.output_folder, csv_filename),
                       sep=',\t',
                       index_col=0,
                       engine='python',
                       usecols=lambda x: x != 'step')
    NCycles = len(data)

    # Dictionary containg the results
    results = {}

    # If EquilibrationRule is 'global' only analyse the total number of molecules 'N_ads'
    if arg.EquilibrationRule == 'global':
        # Apply the MSER to get the index of the start of equilibrated data
        results_global = pymser.equilibrate(input_data=data['N_ads'].to_numpy(),
                                            LLM=arg.LLM,
                                            batch_size=arg.BatchSize,
                                            ADF_test=True,
                                            uncertainty=arg.Uncertainty,
                                            print_results=arg.PrintResults)

        for key in data.keys():
            # Calculate autocorrelation time and the number of uncorrelated samples
            equilibrated = data[key][results_global['t0']:]
            ac_time, uncorr_samples = pymser.calc_autocorrelation_time(equilibrated)

            # Get the equilibrated averages and standard deviation
            average, uncertainty = pymser.calc_equilibrated_average(data=data[key].to_numpy(),
                                                                    eq_index=results_global['t0'],
                                                                    uncertainty=arg.Uncertainty,
                                                                    ac_time=ac_time)

            # Adds the results on the resuts dictionary to output file
            results[key] = {'average': average,
                            'uncertainty': uncertainty,
                            't0': results_global['t0'],
                            'ac_time': ac_time,
                            'uncorrelated_samples': uncorr_samples}

    # If EquilibrationRule is 'individual' apply MSER to each gas component individually
    if arg.EquilibrationRule == 'individual':

        for key in data.keys():
            # Apply the MSER to get the index of the start of equilibrated data
            results[key] = pymser.equilibrate(input_data=data[key].to_numpy(),
                                              LLM=arg.LLM,
                                              batch_size=arg.BatchSize,
                                              ADF_test=True,
                                              uncertainty=arg.Uncertainty,
                                              print_results=arg.PrintResults)

    # Calculate selectivity for multi-component adsorbate gas
    if len(arg.FlueGasComposition) > 1:
        component_list = list(arg.FlueGasComposition)

        # Treat CO2 specially by making it the default numerator
        if 'CO2' in component_list:
            component_list.remove('CO2')
            pairs = list(zip(['CO2'] * len(component_list), component_list))
            # Example: pairs = [('CO2', 'N2'), ('CO2', 'H2O'), ('CO2', 'O2')]

        # List all non-repeating pairs of components
        else:
            pairs = list(itertools.combinations(component_list, 2))
            # Example: pairs = [('N2', 'H2O'), ('N2', 'O2'), ('H2O', 'O2')]

        # Calculate selectivity for all pairs of gas components
        for numerator, denominator in pairs:

            # Get the molar fraction of the components
            frac_1 = arg.FlueGasComposition[numerator]
            frac_2 = arg.FlueGasComposition[denominator]

            # Get the adsorbed amount of the components
            ads_1 = results[numerator + '_[mol/kg]']['average']
            ads_2 = results[denominator + '_[mol/kg]']['average']

            # Get the standard deviation of adsorption
            unc_1 = results[numerator + '_[mol/kg]']['uncertainty']
            unc_2 = results[denominator + '_[mol/kg]']['uncertainty']

            # Calculates selectivity
            selectivity = (ads_1 / ads_2) / (frac_1 / frac_2)
            select_uncert = selectivity * (np.sqrt((unc_1/ads_1)**2 + (unc_2/ads_2)**2))

            results[f'{numerator}/{denominator}_selectivity'] = {'average': selectivity,
                                                                 'uncertainty': select_uncert,
                                                                 't0': np.NaN,
                                                                 'ac_time': np.NaN,
                                                                 'uncorrelated_samples': np.NaN}

    # Starts the output file
    csv_out = "observable, mean, mean-error, number-equilibrated-frames, correlation-time, ratio\n"

    # Write the data in results dictionary to output file
    for key in results.keys():
        avg = results[key]['average']
        uncertainty = results[key]['uncertainty']
        n_eq_frames = NCycles - results[key]['t0']
        ac_time = results[key]['ac_time']
        uncorr = results[key]['uncorrelated_samples']

        csv_out += f"{key}, {avg:.7f}, {uncertainty:.7f}, {n_eq_frames}, {ac_time}, {uncorr}\n"

    # Write string into file
    output_file_name = f'stats_{arg.ExternalTemperature:.6f}_{pressure:.0f}.csv'
    with open(os.path.join(arg.output_folder, output_file_name), 'w') as f:
        f.write(csv_out)
