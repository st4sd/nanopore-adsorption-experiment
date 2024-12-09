#!/bin/bash

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2020 All Rights Reserved

# Parse input parameters
while getopts u:o:n:c: flag
do
    case "${flag}" in
        u) UseGrid=${OPTARG};;
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        c) FlueGasComposition=${OPTARG};;
    esac
done

if [[ "${UseGrid}" -eq 1 ]]; then
    echo -e "\nDecompressing CIF files..."
    tar --no-overwrite-dir -xvzf charged_cif.tgz -C ${OutputFolder}

    echo -e "\nCreating MakeGrid input file..."
    make_grid.py --FrameworkName ${FrameworkName} \
                 --FlueGasComposition ${FlueGasComposition} \
                 ${OutputFolder}

    echo -e "\nRunning MakeGrid simulation..."
    cd ${OutputFolder} && simulate -i simulation-MakeGrid.input

    echo -e "\nCompressing MakeGrid output from ${RASPA_DIR}/share/raspa/grids/..."
    tar -cvzf grids.tgz ${RASPA_DIR}/share/raspa/grids/Local/${FrameworkName}/
else
    echo -e "\nSkipping MakeGrid component..."
    tar -cvzf grids.tgz -T /dev/null
fi;
