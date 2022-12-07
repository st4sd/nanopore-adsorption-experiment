#!/usr/bin/env -S python -B

# © Copyright IBM Corp. 2020 All Rights Reserved
# SPDX-License-Identifier: Apache2.0

import argparse
import json
import os
from textwrap import dedent

from modules.calculate_properties import calculate_grid, calculate_UnitCells
from modules.copy_files import copy_def_files

# Required parameters
parser = argparse.ArgumentParser(description='Create Ewald Sum grid for RASPA simulations.')
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

# Optional parameters
parser.add_argument('--ForcefieldFolder',
                    type=str,
                    action='store',
                    required=False,
                    metavar='FORCEFIELD_FOLDER',
                    default=os.getenv('FORCEFIELD_DIR'),
                    help='Location of the force field *.def files.')
parser.add_argument('--FlueGasComposition',
                    action='store',
                    required=False,
                    type=json.loads,
                    default={'CO2': 1.0},
                    metavar='FLUE_GAS_COMPOSITION',
                    help='Dictionary containing flue gas component names and fractions.')
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
parser.add_argument('--EwaldPrecision',
                    type=float,
                    default=1.0e-6,
                    action='store',
                    required=False,
                    metavar='EWALD_PRECISION',
                    help='Ewald sum precision used to calculate the amount of wave vectors.')
parser.add_argument('--SpacingVDWGrid',
                    type=float,
                    default=0.1,
                    action='store',
                    required=False,
                    metavar='SPACING_VDW_GRID',
                    help='The grid spacing of the Van der Waals potentials [Angstrom].')
parser.add_argument('--SpacingCoulombGrid',
                    type=float,
                    default=0.1,
                    action='store',
                    required=False,
                    metavar='SPACING_COULOMB_GRID',
                    help='The grid spacing of the Coulomb potential [Angstrom].')
arg = parser.parse_args()

# Copy files to output directory
copy_def_files(arg.output_folder, arg.ForcefieldFolder)

# Calculate grid types and number of grids
arg.GridTypes, arg.NumberOfGrids = calculate_grid(arg.FlueGasComposition)

# Calculate self-consistent properties
cif_filename = os.path.join(arg.output_folder, arg.FrameworkName + '.cif')

# Calculate which cutoff radius is the largest
largest_cutoff = max(arg.CutOffVDW,
                     arg.CutOffChargeCharge,
                     arg.CutOffChargeBondDipole,
                     arg.CutOffBondDipoleBondDipole)

# Calculate number of unit cell repetitions in the supercell
arg.UnitCells = calculate_UnitCells(cif_filename, largest_cutoff)

# Create input file as string
inputfile = dedent("""\
SimulationType                  MakeGrid

Forcefield                      Local                           # string
CutOffVDW                       {CutOffVDW}                     # float
CutOffChargeCharge              {CutOffChargeCharge}            # float
CutOffChargeBondDipole          {CutOffChargeBondDipole}        # float
CutOffBondDipoleBondDipole      {CutOffBondDipoleBondDipole}    # float
ChargeMethod                    Ewald                           # string
EwaldPrecision                  {EwaldPrecision}                # float

Framework                       0                               # int
FrameworkName                   {FrameworkName}                 # string
UseChargesFromCIFFile           yes                             # yes / no
UnitCells                       {UnitCells}                     # int int int

NumberOfGrids                   {NumberOfGrids}                 # int
GridTypes                       {GridTypes}                     # string
SpacingVDWGrid                  {SpacingVDWGrid}                # float
SpacingCoulombGrid              {SpacingCoulombGrid}            # float
""").format(**arg.__dict__)

# Write string to file
with open(os.path.join(arg.output_folder, 'simulation-MakeGrid.input'), 'w') as f:
    f.write(inputfile)
