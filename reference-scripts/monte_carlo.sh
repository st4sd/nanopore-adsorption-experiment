#!/bin/bash

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2020 All Rights Reserved

# Parse input parameters
while getopts u:o:n:p:c:t: flag
do
    case "${flag}" in
        u) UseGrid=${OPTARG};;
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        p) ExternalPressure=${OPTARG};;
        c) FlueGasComposition=${OPTARG};;
        t) ExternalTemperature=${OPTARG};;
    esac
done

echo -e "\nDecompressing CIF files from ChargeAssignment component..."
tar --no-overwrite-dir -xvzf charged_cif.tgz -C ${OutputFolder}

# Only decompress grid files if UseGrid is true
if [[ "${UseGrid}" -eq 1 ]]; then
    echo -e "\nDecompressing MakeGrid output to ${RASPA_DIR}/share/raspa/grids/..."
    tar --no-overwrite-dir -xvzf grids.tgz -C /
    rm -vf grids.tgz

    # Define --UseTabularGrid environment variable
    UseTabularGrid="--UseTabularGrid"
fi

echo -e "\nCreating MonteCarlo input file..."
monte_carlo.py ${UseTabularGrid} \
               --FrameworkName ${FrameworkName} \
               --ExternalPressure ${ExternalPressure} \
               --FlueGasComposition ${FlueGasComposition} \
               --ExternalTemperature ${ExternalTemperature} \
               ${OutputFolder}

echo -e "\nRunning MonteCarlo simulation..."
cd ${OutputFolder} && simulate -i simulation-MonteCarlo.input

echo -e "\nCompressing RASPA output files..."
tar -cvzf output_data.tgz -C Output/System_0/ .
