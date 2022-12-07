#!/bin/bash

# © Copyright IBM Corp. 2021 All Rights Reserved
# SPDX-License-Identifier: Apache2.0

# Parse input parameters
while getopts o:n:p:c:t: flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        p) ExternalPressures=${OPTARG};;
        c) FlueGasComposition=${OPTARG};;
        t) ExternalTemperature=${OPTARG};;
    esac
done

echo -e "\nDecompressing RASPA output files..."
tar --no-overwrite-dir -xvzf output_data.tgz -C ${OutputFolder}

echo -e "\nParse RASPA data files into CSV files..."
for ExternalPressure in $(echo $ExternalPressures | sed 's/,/ /g'); do
    parse_output.py --FrameworkName ${FrameworkName} \
                    --ExternalPressure ${ExternalPressure} \
                    --FlueGasComposition ${FlueGasComposition} \
                    --ExternalTemperature ${ExternalTemperature} \
                    ${OutputFolder};
done

echo -e "\nCompressing RASPA CSV files..."
tar -cvzf raspa_csv.tgz -C ${OutputFolder} raspa_*.csv
