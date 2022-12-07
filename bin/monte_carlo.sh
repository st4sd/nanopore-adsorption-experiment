#!/bin/bash

# © Copyright IBM Corp. 2020 All Rights Reserved
# SPDX-License-Identifier: Apache2.0

# Parse input parameters
while getopts o:n:p:c:t:g flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        p) ExternalPressure=${OPTARG};;
        c) FlueGasComposition=${OPTARG};;
        t) ExternalTemperature=${OPTARG};;
        g) UseTabularGrid="--UseTabularGrid";;
    esac
done

echo -e "\nDecompressing CIF files from ChargeEquilibration component..."
tar --no-overwrite-dir -xvzf eqeq_cif.tgz -C ${OutputFolder}

# Only decompress grid files if flag is present
if [[ -n "${UseTabularGrid}" ]]; then
    echo -e "\nDecompressing MakeGrid output to ${RASPA_DIR}/share/raspa/grids/..."
    tar --no-overwrite-dir -xvzf grids.tgz -C /
    rm -vf grids.tgz
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
