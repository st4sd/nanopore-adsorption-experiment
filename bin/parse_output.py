#!/usr/bin/env -S python -B

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2021 All Rights Reserved

import argparse
import glob
import json
import math
import os

from RASPA2 import parse

# Required parameters
parser = argparse.ArgumentParser(description='Parse output of RASPA simulation.')
parser.add_argument('output_folder',
                    type=str,
                    action='store',
                    metavar='OUTPUT_FOLDER',
                    help='Directory for storing output files.')
parser.add_argument('--FrameworkName',
                    type=str,
                    required=True,
                    action='store',
                    metavar='FRAMEWORK_NAME',
                    help='Name of the CIF file describing the nanoporous material structure.')

# Optional parameters
parser.add_argument('--FlueGasComposition',
                    action='store',
                    required=False,
                    type=json.loads,
                    default={'CO2': 1.0},
                    metavar='FLUE_GAS_COMPOSITION',
                    help='Dictionary containing flue gas component names and fractions.')
parser.add_argument('--NumberOfCycles',
                    type=int,
                    default=10000,
                    action='store',
                    required=False,
                    metavar='NUMBER_OF_CYCLES',
                    help='Total number of Monte Carlo cycles executed in the simulation.')
parser.add_argument('--PrintEvery',
                    type=int,
                    default=1,
                    action='store',
                    required=False,
                    metavar='PRINT_EVERY',
                    help='Print the loadings and energies every \'PRINT_EVERY\' cycles.')
parser.add_argument('--ExternalTemperature',
                    type=float,
                    default=300.0,
                    action='store',
                    required=False,
                    metavar='EXTERNAL_TEMPERATURE',
                    help='External temperature [Kelvin].')
parser.add_argument('--ExternalPressure',
                    type=int,
                    action='store',
                    required=False,
                    default=101325,
                    metavar='EXTERNAL_PRESSURE',
                    help='External pressure [Pascal].')
arg = parser.parse_args()

# Read file into string
input_file_name = glob.glob('{0}/output_{1}_*_{2:.6f}_{3:g}.data'.format(arg.output_folder,
                                                                         arg.FrameworkName,
                                                                         arg.ExternalTemperature,
                                                                         arg.ExternalPressure))[0]
with open(os.path.join(arg.output_folder, input_file_name), 'r') as f:
    raspa_string = f.read()

# Parse string into dictionary and list
raspa_dict = parse(raspa_string)
raspa_list = raspa_string.split('\n')

# Extract number of unit cells in the supercell
unit_cells = [int(line.split(':')[1]) for line in raspa_list if 'Number of unitcells' in line]

# Calculate mol/kg conversion factor for the supercell
to_mol_kg = raspa_dict['MoleculeDefinitions']['Conversion factor molecules/unit cell -> mol/kg'][0]
to_mol_kg /= math.prod(unit_cells)

# Build header string
header = 'cycle,\tstep,\tN_ads'
for component in range(len(arg.FlueGasComposition)):
    cycle_key = f'Current cycle: 0 out of {arg.NumberOfCycles}'
    component_key = f'Component {component}'
    molecule_name = raspa_dict[cycle_key][component_key][0]
    header += (
        f',\t{molecule_name}_[molecules/uc]'
        f',\t{molecule_name}_[mol/kg]'
    )
csv_output = header + '\n'

# For each cycle
steps = 0
for cycle in range(0, arg.NumberOfCycles, arg.PrintEvery):
    cycle_key = f'Current cycle: {cycle} out of {arg.NumberOfCycles}'
    number_of_adsorbates = int(raspa_dict[cycle_key]['Number of Adsorbates'][0])
    steps += max(20, number_of_adsorbates)
    line = (
        f'{cycle},\t'
        f'{steps},\t'
        f'{number_of_adsorbates}'
    )

    # For each component
    for component in range(len(arg.FlueGasComposition)):
        component_key = f'Component {component}'
        number_of_molecules = int(raspa_dict[cycle_key][component_key][2].split('/')[0])
        line += (
            f',\t{number_of_molecules:7}'
            f',\t{number_of_molecules * to_mol_kg:.7f}'
        )
    csv_output += line + '\n'

# Write string into file
output_file_name = f'raspa_{arg.ExternalTemperature:.6f}_{arg.ExternalPressure}.csv'
with open(os.path.join(arg.output_folder, output_file_name), 'w') as f:
    f.write(csv_output)
