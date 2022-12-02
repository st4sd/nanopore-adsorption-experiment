#!/bin/bash

# © Copyright IBM Corp. 2021 All Rights Reserved

# Parse input parameters
while getopts o:n:s:p:c:t: flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        s) FrameworkSource=${OPTARG};;
        p) ExternalPressure=${OPTARG};;
        c) FlueGasComposition=${OPTARG};;
        t) ExternalTemperature=${OPTARG};;
    esac
done

echo -e "\nDecompressing statistics CSV files..."
tar --no-overwrite-dir -xvzf timeseries_csv.tgz -C ${OutputFolder}

echo -e "\nParse statistics CSV files and write to database..."
write_adsorption_to_database.py --FrameworkName ${FrameworkName} \
                                --FrameworkSource ${FrameworkSource} \
                                --ExternalPressure ${ExternalPressure} \
                                --FlueGasComposition ${FlueGasComposition} \
                                --ExternalTemperature ${ExternalTemperature} \
                                ${OutputFolder};
