#!/usr/bin/env -S python -B

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2021 All Rights Reserved

import argparse
import io
import json
import os

import pandas as pd

from modules.copy_files import save_to_disk
from modules.database_api_calls import get_objectID, post_tDependentProp

from modules.InChIKey import InChIKey

if (os.environ.get("INGRESS_SUBDOMAIN") is None or os.environ.get("INGRESS_SUBDOMAIN") == ""
        or os.environ.get("INGRESS_SUBDOMAIN") == "${INGRESS}"):
    ingress_subdomain = False
else:
    ingress_subdomain = True

# Required parameters
parser = argparse.ArgumentParser(description='Write adsorption figures-of-merit to database.')
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
parser.add_argument('--FrameworkSource',
                    type=str,
                    required=True,
                    action='store',
                    metavar='FRAMEWORK_SOURCE',
                    choices=['local',
                             'CSD',
                             'hMOF',
                             'BWDB',
                             'BW20K',
                             'ABC-6',
                             'ARABG',
                             'ARC-MOF',
                             'DEEM2011',
                             'CoRE2019',
                             'CoRE_DDEC',
                             'generated',
                             'CURATED-COF',
                             'baburin_2008',
                             'simperler_2005',
                             'database_zeolite_structures'],
                    help='Source of the CIF file describing the nanoporous material structure.')

# Optional parameters
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
parser.add_argument('--FlueGasComposition',
                    action='store',
                    required=False,
                    type=json.loads,
                    default={'CO2': 1.0},
                    metavar='FLUE_GAS_COMPOSITION',
                    help='Dictionary containing flue gas component names and fractions.')
arg = parser.parse_args()

if ingress_subdomain:
    # Get MongoDB objectIDs for the material
    objectID = get_objectID(arg.FrameworkName, arg.FrameworkSource)

    print(f'Name: {arg.FrameworkName}, Source: {arg.FrameworkSource}, ObjectID: {objectID}')

# Manipulate ExternalPressure string
externalPressures = list(map(float, arg.ExternalPressure.split(',')))
print(f'T={arg.ExternalTemperature} K, P={externalPressures} Pa')

# Assume name is isotherm and get provenance from environment variable
name = 'isotherm'
provenance = os.getenv('INSTANCE_DIR').split('/')[-1]
print(f'Provenance: {provenance}')

# Populate composition array
print(f'FlueGasComposition: {arg.FlueGasComposition}')
composition = [{'fraction': fraction,
                'InChIKey': InChIKey[name]} for name, fraction in arg.FlueGasComposition.items()]
print(f'InChIKey Composition: {composition}')

# Read CSV files as Pandas DataFrame
data = []
for pressure in externalPressures:
    csv_filename = f'stats_{arg.ExternalTemperature:.6f}_{pressure:.0f}.csv'
    if os.path.exists(os.path.join(arg.output_folder, csv_filename)):
        transpose_csv = pd.read_csv(os.path.join(arg.output_folder, csv_filename),
                                    skipinitialspace=True,
                                    dtype=str).T.to_csv(header=0)
        csv = pd.read_csv(io.StringIO(transpose_csv), index_col=0)

        # Populate data array
        adsorptions = []
        for column_name in csv.columns:
            if 'mol/kg' in column_name:
                value = csv[column_name]['mean']
                uncertainty = csv[column_name]['mean-error']
                adsorption = {'value': value,
                              'uncertainty': uncertainty,
                              'InChIKey': InChIKey[column_name.split('_')[0]]}
                adsorptions.append(adsorption)

        # Convert pressure values to bar units
        dataElement = {'pressure': pressure / 100000, 'adsorption': adsorptions}
        data.append(dataElement)

print(f'data: {data}\n')

if ingress_subdomain:
    # Issue POST call
    response = post_tDependentProp(objectID,
                                   name,
                                   provenance,
                                   arg.ExternalTemperature,
                                   composition,
                                   data)

    print(f'response: {response.json()}')

save_to_disk(name,
             'isotherm.json',
             arg.output_folder,
             provenance,
             arg.ExternalTemperature,
             data,
             composition)
