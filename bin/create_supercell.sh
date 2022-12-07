#!/bin/bash

# © Copyright IBM Corp. 2020 All Rights Reserved
# SPDX-License-Identifier: Apache2.0

# Parse input parameters
while getopts u:o:n:s:f: flag
do
    case "${flag}" in
        u) UnitCells=${OPTARG};;
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        s) FrameworkSource=${OPTARG};;
        f) FrameworkFolder=${OPTARG};;
    esac
done

echo -e "\nCreating RASPA input file with a ${UnitCells} supercell..."
if [[ -n "${UnitCells}" ]]; then
	create_supercell.py --FrameworkFolder ${FrameworkFolder} --FrameworkSource ${FrameworkSource} --FrameworkName ${FrameworkName} --UnitCells ${UnitCells} ${OutputFolder}
else
	create_supercell.py --FrameworkFolder ${FrameworkFolder} --FrameworkSource ${FrameworkSource} --FrameworkName ${FrameworkName} ${OutputFolder}
fi

echo -e "\nRunning 0-step MonteCarlo simulation..."
cd ${OutputFolder} && simulate -i simulation-CreateSupercell.input

echo -e "\nCopying P1-symmetry CIF file..."
cp -v Movies/System_0/Framework_0_final_*_P1.cif ${FrameworkName}_P1.cif

echo -e "\nCompressing CIF files..."
tar -cvzf cif.tgz *.cif
