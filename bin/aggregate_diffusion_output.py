#!/usr/bin/env -S python -B

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2022 All Rights Reserved

import argparse
import os
import shutil
import tarfile

# Required parameters
parser = argparse.ArgumentParser(description='Aggregating Diffusion Coefficients output to' +
                                             ' compressed file from a given CIF.')
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

print(f'Aggregating Diffusion Coefficients json files from {0}, {1}'.format(arg.FrameworkName,
                                                                            arg.OutputFolders))

# Copy diffusion.json from all given Output Folders to AggregateDiffusionCoefficients folder
for i in range(len(arg.OutputFolders)):
    src = os.path.join(arg.OutputFolders[i], 'diffusion.json')
    shutil.copyfile(src, f'{arg.FrameworkName[i]}-diffusion.json')

# Compress to create isotherms.tgz
with tarfile.open('diffusion.tgz', 'w') as tar:
    for file in os.listdir():
        if file.endswith('.json'):
            tar.add(file)
