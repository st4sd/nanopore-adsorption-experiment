#!/usr/bin/env -S python -B

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2022 All Rights Reserved

import argparse
import glob
import json
import os

import numpy as np
from modules.calculate_properties import (calculate_directional_self_diffusivity,
                                          calculate_NumberOfMolecules, calculate_UnitCells)
from modules.InChIKey import InChIKey
from RASPA2 import parse

# Required parameters
parser = argparse.ArgumentParser(description='Parse the MSD output of RASPA simulation.')
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
parser.add_argument('--ExternalTemperature',
                    type=float,
                    default=300.0,
                    action='store',
                    required=False,
                    metavar='EXTERNAL_TEMPERATURE',
                    help='External temperature [Kelvin].')
parser.add_argument('--FlueGasComposition',
                    action='store',
                    required=False,
                    type=json.loads,
                    default={'CO2': 1.0},
                    metavar='FLUE_GAS_COMPOSITION',
                    help='Dictionary containing flue gas component names and fractions.')
parser.add_argument('--NumberOfMolecules',
                    type=int,
                    default=None,
                    action='store',
                    required=False,
                    metavar='TOTAL_NUMBER_OF_MOLECULES',
                    help='Total number of molecules created inside the supercell.')
parser.add_argument('--LargestCutoff',
                    type=float,
                    default=12.8,
                    action='store',
                    required=False,
                    metavar='LARGEST_CUTOFF',
                    help='Largest cutoff radius [Angstrom].')
arg = parser.parse_args()

# Check if the simulation finished successfully and without warnings

# Get the raspa out file name
raspa_out_filename = glob.glob('output_{0}_*_{1:.6f}_0.data'.format(arg.FrameworkName,
                                                                    arg.ExternalTemperature))[0]

# Automatically calculate the number of molecules in the supercell
cif_filename = os.path.join(arg.output_folder, arg.FrameworkName + '.cif')

# Calculate number of unit cell repetitions in the supercell
arg.UnitCells = calculate_UnitCells(cif_filename, arg.LargestCutoff)

if arg.NumberOfMolecules is None:
    arg.NumberOfMolecules = calculate_NumberOfMolecules(cif_filename,
                                                        arg.LargestCutoff,
                                                        arg.UnitCells)

# Read the raspa output file
with open(os.path.join(arg.output_folder, raspa_out_filename), 'r') as f:
    raspa_string = f.read()

raspa_out = raspa_string.split('\n')

# Calculate mol -> mol/kg conversion factor for the supercell
raspa_dict = parse(raspa_string)
to_mol_kg = raspa_dict['MoleculeDefinitions']['Conversion factor molecules/unit cell -> mol/kg'][0]

# Extract number of unit cells in the supercell
unit_cells = [int(line.split(':')[1]) for line in raspa_out if 'Number of unitcells' in line]

# Calculate the conversion factor
to_mol_kg /= np.prod(unit_cells)

# Get provenance from environment variable
provenance = os.getenv('INSTANCE_DIR').split('/')[-1]

results = {
    "name": "diffusion",
    "temperature": arg.ExternalTemperature,
    "provenance": provenance,
    "composition": [],
    "data": [
        {"number_of_molecules": arg.NumberOfMolecules,
         "loading": [],
         "diffusion_coefficient_x": [],
         "diffusion_coefficient_y": [],
         "diffusion_coefficient_z": [],
         "diffusion_coefficient_mean": []}
    ]
}

for i, gas in enumerate(arg.FlueGasComposition):

    # Add the gas to composition list
    results["composition"].append({"fraction": arg.FlueGasComposition[gas],
                                   "InChIKey": InChIKey[gas]})

    # Calculate the loading
    loading = int(arg.NumberOfMolecules * arg.FlueGasComposition[gas]) * to_mol_kg

    # Add the loading to results
    results["data"][0]["loading"].append({"value": loading,
                                          "uncertainty": 0.0,
                                          "InChIKey": InChIKey[gas]})

    # Get the msd file name
    msd_filename = os.path.join(arg.output_folder, f'msd_self_{gas}_{i}.dat')

    # Read the diffusion files
    time, msd_t, msd_x, msd_y, msd_z, _, _ = np.genfromtxt(msd_filename,
                                                           skip_header=6,
                                                           delimiter=' ').T

    # Calculate the self-diffusivity
    Dx, Dx_SD = calculate_directional_self_diffusivity(time, msd_x, arg.FrameworkName + '.cif')
    Dy, Dy_SD = calculate_directional_self_diffusivity(time, msd_y, arg.FrameworkName + '.cif')
    Dz, Dz_SD = calculate_directional_self_diffusivity(time, msd_z, arg.FrameworkName + '.cif')
    Ds, Ds_SD = calculate_directional_self_diffusivity(time, msd_t, arg.FrameworkName + '.cif')

    # Divide Ds and Ds_SD by 3 to account to the fact that the simulation is in 3D
    if not isinstance(Ds, type(None)):
        Ds /= 3
        Ds_SD /= 3

    results['data'][0]['diffusion_coefficient_x'].append({"value": Dx,
                                                          "uncertainty": Dx_SD,
                                                          "InChIKey": InChIKey[gas]})
    results['data'][0]['diffusion_coefficient_y'].append({"value": Dy,
                                                          "uncertainty": Dy_SD,
                                                          "InChIKey": InChIKey[gas]})
    results['data'][0]['diffusion_coefficient_z'].append({"value": Dz,
                                                          "uncertainty": Dz_SD,
                                                          "InChIKey": InChIKey[gas]})
    results['data'][0]['diffusion_coefficient_mean'].append({"value": Ds,
                                                             "uncertainty": Ds_SD,
                                                             "InChIKey": InChIKey[gas]})

# Write string into file
with open(os.path.join(arg.output_folder, 'diffusion.json'), 'w') as f:
    json.dump(results, f, indent=2)
