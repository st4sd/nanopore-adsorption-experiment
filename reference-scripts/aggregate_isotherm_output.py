#!/usr/bin/env -S python -B

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2022 All Rights Reserved

import argparse
import os
import shutil
import tarfile

# Required parameters
parser = argparse.ArgumentParser(description='Aggregating isotherm output to compressed file' +
                                             'from a given CIF.')
parser.add_argument('--FrameworkName',
                    type=str,
                    required=True,
                    action='store',
                    nargs='+',
                    metavar='FRAMEWORK_NAME',
                    help='Name of the CIF file describing the nanoporous material structure.')
parser.add_argument('--OutputFolders',
                    type=str,
                    required=True,
                    action='store',
                    nargs='+',
                    metavar='OUTPUT_FOLDERS',
                    help='Directory for storing JSON output files.')
arg = parser.parse_args()

print(f'Aggregating isotherm output json files from {arg.FrameworkName}, {arg.OutputFolders}.')

# Copy isothermProperties.json from all given Output Folders to AggregateIsotherms folder
for i in range(len(arg.OutputFolders)):
    src = os.path.join(arg.OutputFolders[i], 'isotherm.json')
    shutil.copyfile(src, f'{arg.FrameworkName[i]}-isotherm.json')

# Compress to create isotherms.tgz
with tarfile.open('isotherms.tgz', 'w') as tar:
    for file in os.listdir():
        if file.endswith('.json'):
            tar.add(file)
