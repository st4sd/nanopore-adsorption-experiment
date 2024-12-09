#!/usr/bin/env -S python -B

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2022 All Rights Reserved

import argparse
import os
import json

from modules.database_api_calls import (get_objectID, post_tDependentProp)

# Required parameters
parser = argparse.ArgumentParser(description='Write diffusion figures-of-merit to database.')
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
arg = parser.parse_args()

# Get MongoDB objectIDs for the material
objectID = get_objectID(arg.FrameworkName, arg.FrameworkSource)
print(f'Name: {arg.FrameworkName}, Source: {arg.FrameworkSource}, ObjectID: {objectID}')

# Read the results from the json file
with open(os.path.join(arg.output_folder, 'diffusion.json'), 'r') as f:
    results = json.load(f)

# Issue POST call
response = post_tDependentProp(objectID,
                               results['name'],
                               results['provenance'],
                               results['temperature'],
                               results['composition'],
                               results['data'])

print(f'response: {response.json()}')
