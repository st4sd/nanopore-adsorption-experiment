#!/bin/bash

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2022 All Rights Reserved

# Parse input parameters
while getopts u:o:n:c:t: flag
do
    case "${flag}" in
        u) UseGrid=${OPTARG};;
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
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

    # Define --UseTabularGrid environment variable
    UseTabularGrid="--UseTabularGrid"
fi

echo -e "\nCreating Molecular Dynamics input file..."
molecular_dynamics.py ${UseTabularGrid} \
                      --FrameworkName ${FrameworkName} \
                      --FlueGasComposition ${FlueGasComposition} \
                      --ExternalTemperature ${ExternalTemperature} \
                      ${OutputFolder}

echo -e "\nRunning Molecular Dynamics simulation..."
cd ${OutputFolder} && $RASPA_DIR/bin/simulate -i simulation-MolecularDynamics.input

echo -e "\nCompressing RASPA output and MSD files..."
tar -cvzf molecular_dynamics.tgz -C Output/System_0/ .
tar -cvzf mean_squared_displacement.tgz -C MSDOrderN/System_0/ .

echo -e "\nChecking simulation output..."
check_molecular_dynamics.py
