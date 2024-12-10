#!/bin/bash

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2020 All Rights Reserved

# Parse input parameters
while getopts o:n:s:f: flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        s) FrameworkSource=${OPTARG};;
        f) FrameworkFolder=${OPTARG};;
    esac
done

echo -e "\nCreating a primitive cell from the original CIF file..."
cp -v ${FrameworkFolder}/${FrameworkSource}/${FrameworkName}.cif ${OutputFolder}/${FrameworkName}.cif
pmg structure --convert --filename ${FrameworkName}.cif ${FrameworkName}_prim.cif

echo -e "\nCopying P1-symmetry CIF file..."
mv -v ${FrameworkName}_prim.cif ${OutputFolder}/${FrameworkName}_P1.cif
cd ${OutputFolder}

echo -e "\nCompressing CIF files..."
tar -cvzf cif.tgz *.cif
