#!/bin/bash

# © Copyright IBM Corp. 2020 All Rights Reserved

# Parse input parameters
while getopts o:n: flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
    esac
done

echo -e "\nDecompressing CIF files..."
tar --no-overwrite-dir -xvzf cif.tgz -C ${OutputFolder}

echo -e "\nRunning EQeq calculation..."
cd ${OutputFolder}
eqeq ${FrameworkName}.cif -o ${FrameworkName}_EQeq.cif

echo -e "\nCompressing CIF files..."
tar -cvzf eqeq_cif.tgz *.cif
