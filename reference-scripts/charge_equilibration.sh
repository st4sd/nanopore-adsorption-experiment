#!/bin/bash

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2020 All Rights Reserved

# Parse input parameters
while getopts o:n:m: flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        m) AtomicChargesMethod=${OPTARG};;
    esac
done

echo -e "\nDecompressing CIF files..."
tar --no-overwrite-dir -xvzf cif.tgz -C ${OutputFolder}
cd ${OutputFolder}

if [[ "${AtomicChargesMethod}" = "existing" ]]; then
    echo -e "\nKeeping existing atomic charges in the provided CIF file..."
    cp -v ${FrameworkName}.cif ${FrameworkName}_charged.cif

elif [[ "${AtomicChargesMethod}" = "eqeq" ]]; then
    echo -e "\nRunning EQeq calculation..."
    eqeq ${FrameworkName}.cif -o ${FrameworkName}_charged.cif

else
    echo -e "Invalid method: ${AtomicChargesMethod}"
    exit 1
fi;

echo -e "\nCompressing CIF files..."
tar -cvzf charged_cif.tgz *.cif
