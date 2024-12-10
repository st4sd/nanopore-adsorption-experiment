#!/bin/bash

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2022 All Rights Reserved

# Parse input parameters
while getopts o:n:s: flag
do
    case "${flag}" in
        o) OutputFolder=${OPTARG};;
        n) FrameworkName=${OPTARG};;
        s) FrameworkSource=${OPTARG};;
    esac
done

echo -e "\nWrite diffusion coefficient to database..."
write_diffusion_to_database.py --FrameworkName ${FrameworkName} \
                               --FrameworkSource ${FrameworkSource} \
                               ${OutputFolder};
