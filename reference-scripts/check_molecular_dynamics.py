#!/usr/bin/env -S python -B

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2023 All Rights Reserved

import glob
import os
import sys

PROPERTY_NAN_SEARCH = 'Conserved energy'

raspa_out_file = glob.glob(os.path.join('Output', 'System_0', 'output_*_0.data'))[0]

with open(raspa_out_file, 'r') as f:
    raspa_string = f.read()

raspa_out = raspa_string.split('\n')

# Find the last block on RASPA output
n = [i for i, line in enumerate(raspa_out) if '=' in line][-1]
last_block = raspa_out[n:]

# Check if the simulation finished without warnings
warnings = [line for line in last_block if 'WARNING' in line]

# Check if the simulation finished without errors
errors = [line for line in last_block if 'ERROR' in line]

# Check if the simulation finished successfully
success_finished = any(['Simulation finished' in line for line in last_block])

# Check if the simulation produced nan values
conserved_energy_lines = [line for line in raspa_out if PROPERTY_NAN_SEARCH in line]
nan_found = any(['nan' in line for line in conserved_energy_lines])

if nan_found:
    errors.append('NaN values found.')

if not success_finished or nan_found:
    ErrorMessage = 'Simulation failed!\n' + '\n'.join(errors)
    sys.exit(ErrorMessage)

if len(warnings) > 0:
    WarningMessage = f'Simulation finished with {len(warnings)} \
warnings!\n' + '\n'.join(warnings)
    print(WarningMessage)
else:
    print('Simulation finished successfully!')
