#!/usr/bin/env -S python -B

# © Copyright IBM Corp. 2020 All Rights Reserved
# SPDX-License-Identifier: Apache2.0

import argparse
import os
from textwrap import dedent

from modules.calculate_properties import calculate_UnitCells
from modules.copy_files import copy_cif_file

# Required parameters
parser = argparse.ArgumentParser(description='Create P1-symmetry supercell.')
parser.add_argument('output_folder',
                    type=str,
                    action='store',
                    metavar='OUTPUT_FOLDER',
                    help='Directory for storing output files.')
parser.add_argument('--FrameworkName',
                    type=str,
                    required=True,
                    action='store',
                    metavar='FRAMEWORK_NAME',
                    help='Name of the CIF file describing the nanoporous material structure.')
parser.add_argument('--FrameworkSource',
                    type=str,
                    required=True,
                    action='store',
                    metavar='FRAMEWORK_SOURCE',
                    choices=['local',
                             'CSD',
                             'hMOF',
                             'BWDB',
                             'BW20K',
                             'ARABG',
                             'CoRE2019',
                             'CoRE_DDEC',
                             'CURATED-COF',
                             'baburin_2008',
                             'simperler_2005',
                             'database_zeolite_structures'],
                    help='Source of the CIF file describing the nanoporous material structure.')
parser.add_argument('--FrameworkFolder',
                    type=str,
                    action='store',
                    required=True,
                    metavar='FRAMEWORK_FOLDER',
                    help='Location of the framework <source>/<name>.cif files.')

# Optional parameters
parser.add_argument('--RemoveAtomNumberCodeFromLabel',
                    const='yes',
                    default='no',
                    required=False,
                    action='store_const',
                    help='Reading CIF files, the number is removed from the framework atom labels.')
parser.add_argument('--CutOffVDW',
                    type=float,
                    default=12.8,
                    action='store',
                    required=False,
                    metavar='CUTOFF_VDW',
                    help='The cutoff of the Van der Waals potential [Angstrom].')
parser.add_argument('--CutOffChargeCharge',
                    type=float,
                    default=12.8,
                    action='store',
                    required=False,
                    metavar='CUTOFF_CHARGE_CHARGE',
                    help='The cutoff of the charge-charge potential [Angstrom].')
parser.add_argument('--CutOffChargeBondDipole',
                    type=float,
                    default=12.8,
                    action='store',
                    required=False,
                    metavar='CUTOFF_CHARGE_BONDDIPOLE',
                    help='The cutoff of the charge-bonddipole potential [Angstrom].')
parser.add_argument('--CutOffBondDipoleBondDipole',
                    type=float,
                    default=12.8,
                    action='store',
                    required=False,
                    metavar='CUTOFF_BONDDIPOLE_BONDDIPOLE',
                    help='The cutoff of the bonddipole-bonddipole potential [Angstrom].')
parser.add_argument('--UnitCells',
                    type=str,
                    default=None,
                    metavar='X,Y,Z',
                    required=False,
                    action='store',
                    help='Number of unit cell replications in the supercell (comma-separated).')
arg = parser.parse_args()

# Copy files to output directory
copy_cif_file(arg.FrameworkFolder, arg.FrameworkSource, arg.FrameworkName, arg.output_folder)

# Calculate self-consistent properties
cif_filename = os.path.join(arg.output_folder, arg.FrameworkName + '.cif')

# Calculate which cutoff radius is the largest
largest_cutoff = max(arg.CutOffVDW,
                     arg.CutOffChargeCharge,
                     arg.CutOffChargeBondDipole,
                     arg.CutOffBondDipoleBondDipole)

# Calculate number of unit cell repetitions in the supercell
if arg.UnitCells:
    try:
        arg.UnitCells = arg.UnitCells.replace(',', ' ')
    except Exception:
        raise ValueError('Error parsing unit cell: {0}'.format(arg.UnitCells))
else:
    arg.UnitCells = calculate_UnitCells(cif_filename, largest_cutoff)

# Create input file as string
inputfile = dedent("""\
SimulationType                  MonteCarlo
NumberOfCycles                  0                               # int

CutOffVDW                       {CutOffVDW}                     # float
CutOffChargeCharge              {CutOffChargeCharge}            # float
CutOffChargeBondDipole          {CutOffChargeBondDipole}        # float
CutOffBondDipoleBondDipole      {CutOffBondDipoleBondDipole}    # float

Framework                       0                               # int
FrameworkName                   {FrameworkName}                 # string
UseChargesFromCIFFile           yes                             # yes / no
RemoveAtomNumberCodeFromLabel   {RemoveAtomNumberCodeFromLabel} # yes / no
UnitCells                       {UnitCells}                     # int int int
""").format(**arg.__dict__)

# Write string to file
with open(os.path.join(arg.output_folder, 'simulation-CreateSupercell.input'), 'w') as f:
    f.write(inputfile)
