#!/bin/bash

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2022 All Rights Reserved

# Parse input parameters
while getopts o:p:c:t:l flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        p) ExternalPressure=${OPTARG};;
        c) FlueGasComposition=${OPTARG};;
        t) ExternalTemperature=${OPTARG};;
        l) LLM="--LLM";;
    esac
done

echo -e "\nDecompressing RASPA CSV files..."
tar --no-overwrite-dir -xvzf raspa_csv.tgz -C ${OutputFolder}

echo -e "\nApply MSER to determine the start of equilibrated data..."
equilibrate.py --ExternalPressure ${ExternalPressure} \
               --ExternalTemperature ${ExternalTemperature} \
               --FlueGasComposition ${FlueGasComposition} \
               ${LLM} \
               ${OutputFolder}

echo -e "\nCompressing equilibrated CSV files..."
tar -cvzf timeseries_csv.tgz -C ${OutputFolder} stats_*.csv
