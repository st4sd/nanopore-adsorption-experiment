#!/bin/bash

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2022 All Rights Reserved

# Parse input parameters
while getopts o:n:c:t: flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        c) FlueGasComposition=${OPTARG};;
        t) ExternalTemperature=${OPTARG};;
    esac
done

echo -e "\nDecompressing RASPA output files..."
tar --no-overwrite-dir -xvzf molecular_dynamics.tgz -C ${OutputFolder}
tar --no-overwrite-dir -xvzf mean_squared_displacement.tgz -C ${OutputFolder}
tar --no-overwrite-dir -xvzf charged_cif.tgz -C ${OutputFolder}

echo -e "\nParse RASPA data files into CSV files..."
parse_msd.py --FrameworkName ${FrameworkName} \
             --FlueGasComposition ${FlueGasComposition} \
             --ExternalTemperature ${ExternalTemperature} \
             ${OutputFolder}
