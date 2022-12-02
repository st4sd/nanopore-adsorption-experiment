#!/bin/bash

# © Copyright IBM Corp. 2020 All Rights Reserved

# Parse input parameters
while getopts o:n:c: flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        c) FlueGasComposition=${OPTARG};;
    esac
done

echo -e "\nDecompressing CIF files..."
tar --no-overwrite-dir -xvzf eqeq_cif.tgz -C ${OutputFolder}

echo -e "\nCreating MakeGrid input file..."
make_grid.py --FrameworkName ${FrameworkName} \
             --FlueGasComposition ${FlueGasComposition} \
             ${OutputFolder}

echo -e "\nRunning MakeGrid simulation..."
cd ${OutputFolder} && simulate -i simulation-MakeGrid.input

echo -e "\nCompressing MakeGrid output from ${RASPA_DIR}/share/raspa/grids/..."
tar -cvzf grids.tgz ${RASPA_DIR}/share/raspa/grids/Local/${FrameworkName}/
