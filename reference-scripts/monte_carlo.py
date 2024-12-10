#!/usr/bin/env -S python -B

# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2020 All Rights Reserved

import argparse
import json
import os
from textwrap import dedent

from modules.calculate_properties import calculate_grid, calculate_UnitCells
from modules.copy_files import copy_def_files

# Required parameters
parser = argparse.ArgumentParser(description='Run RASPA GCMC simulation.')
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
parser.add_argument('--NumberOfInitializationCycles',
                    type=int,
                    default=0,
                    action='store',
                    required=False,
                    metavar='NUMBER_OF_INITIALIZATION_CYCLES',
                    help='Number of Monte Carlo initialization cycles.')
parser.add_argument('--NumberOfCycles',
                    type=int,
                    default=10000,
                    action='store',
                    required=False,
                    metavar='NUMBER_OF_CYCLES',
                    help='Total number of Monte Carlo simulation cycles.')
parser.add_argument('--PrintEvery',
                    type=int,
                    default=1,
                    action='store',
                    required=False,
                    metavar='PRINT_EVERY',
                    help='Print the loadings and energies every \'PRINT_EVERY\' cycles.')
parser.add_argument('--WriteBinaryRestartFileEvery',
                    type=int,
                    default=1000,
                    action='store',
                    required=False,
                    metavar='WRITE_BINARY_RESTART_FILE_EVERY',
                    help='Write restart file every \'WRITE_BINARY_RESTART_FILE_EVERY\' cycles.')
parser.add_argument('--ForcefieldFolder',
                    type=str,
                    action='store',
                    required=False,
                    metavar='FORCEFIELD_FOLDER',
                    default=os.getenv('FORCEFIELD_DIR'),
                    help='Location of the force field *.def files.')
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
parser.add_argument('--IgnoreChargesFromCIFFile',
                    required=False,
                    action='store_true',
                    help='Whether to consider the partial atomic charges already in the CIF file.')
parser.add_argument('--HeliumVoidFraction',
                    type=float,
                    default=0.0,
                    action='store',
                    required=False,
                    metavar='HELIUM_VOID_FRACTION',
                    help='The void fraction measured by probing the structure with He at 300 K.')
parser.add_argument('--ExternalTemperature',
                    type=float,
                    default=300.0,
                    action='store',
                    required=False,
                    metavar='EXTERNAL_TEMPERATURE',
                    help='External temperature [Kelvin].')
parser.add_argument('--ExternalPressure',
                    type=str,
                    action='store',
                    required=False,
                    default="101325",
                    metavar='EXTERNAL_PRESSURE(S)',
                    help='External pressure [Pascal]. Accepts a comma-separated list of values.')
parser.add_argument('--FlueGasComposition',
                    action='store',
                    required=False,
                    type=json.loads,
                    default={'CO2': 1.0},
                    metavar='FLUE_GAS_COMPOSITION',
                    help='Dictionary containing flue gas component names and fractions.')
parser.add_argument('--UseTabularGrid',
                    const='yes',
                    default='no',
                    required=False,
                    action='store_const',
                    help='Use a pre-calculated grid for the energy and forces.')
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
parser.add_argument('--WriteMoviesEvery',
                    type=int,
                    default=0,
                    action='store',
                    required=False,
                    metavar='WRITE_MOVIES_EVERY',
                    help='Write snapshots of the simulation every \'WRITE_MOVIES_EVERY\' cycles.')
arg = parser.parse_args()

# Manipulate ExternalPressure string
arg.ExternalPressure = arg.ExternalPressure.replace(',', ' ')

# Copy files to output directory
copy_def_files(arg.output_folder, arg.ForcefieldFolder)

# Calculate self-consistent properties
cif_filename = os.path.join(arg.output_folder, arg.FrameworkName + '.cif')

# Calculate which cutoff radius is the largest
largest_cutoff = max(arg.CutOffVDW,
                     arg.CutOffChargeCharge,
                     arg.CutOffChargeBondDipole,
                     arg.CutOffBondDipoleBondDipole)

# Calculate number of unit cell repetitions in the supercell
arg.UnitCells = calculate_UnitCells(cif_filename, largest_cutoff)

# Calculate grid types and number of grids
arg.GridTypes, arg.NumberOfGrids = calculate_grid(arg.FlueGasComposition)

# Determine whether movies snapshots should be saved
arg.Movies = 'yes' if arg.WriteMoviesEvery else 'no'

# Determine whether existing partial atomic charges are considered or not
arg.UseChargesFromCIFFile = 'no' if arg.IgnoreChargesFromCIFFile else 'yes'

# Create file header as string
inputfile = dedent("""\
SimulationType                      MonteCarlo
NumberOfCycles                      {NumberOfCycles}                        # int
NumberOfInitializationCycles        {NumberOfInitializationCycles}          # int
PrintEvery                          {PrintEvery}                            # int

ContinueAfterCrash                  yes                                     # yes / no
Movies                              {Movies}                                # yes / no
WriteMoviesEvery                    {WriteMoviesEvery}                      # int
WriteBinaryRestartFileEvery         {WriteBinaryRestartFileEvery}           # int

ForceField                          Local                                   # string
CutOffVDW                           {CutOffVDW}                             # float
CutOffChargeCharge                  {CutOffChargeCharge}                    # float
CutOffChargeBondDipole              {CutOffChargeBondDipole}                # float
CutOffBondDipoleBondDipole          {CutOffBondDipoleBondDipole}            # float
ChargeMethod                        Ewald                                   # string
EwaldPrecision                      {EwaldPrecision}                        # float

Framework                           0                                       # int
FrameworkName                       {FrameworkName}                         # string
HeliumVoidFraction                  {HeliumVoidFraction}                    # float
ExternalTemperature                 {ExternalTemperature}                   # float
ExternalPressure                    {ExternalPressure}                      # float
UseChargesFromCIFFile               {UseChargesFromCIFFile}                 # yes / no
UnitCells                           {UnitCells}                             # int int int

NumberOfGrids                       {NumberOfGrids}                         # int
GridTypes                           {GridTypes}                             # string
SpacingVDWGrid                      {SpacingVDWGrid}                        # float
SpacingCoulombGrid                  {SpacingCoulombGrid}                    # float
UseTabularGrid                      {UseTabularGrid}                        # yes / no

""").format(**arg.__dict__)

# Create component list as string
for name, fraction in arg.FlueGasComposition.items():
    number_of_components = len(arg.FlueGasComposition)
    index_of_component = list(arg.FlueGasComposition).index(name)

    # Append component string block to input file
    if (number_of_components > 1):
        # Remove one's own component index from identity change list
        identity_change_list = list(range(number_of_components))
        identity_change_list.remove(index_of_component)

        inputfile += dedent(f"""\
        Component {index_of_component} MoleculeName                  {name}
                    MolFraction                   {fraction}
                    MoleculeDefinition            Local
                    SwapProbability               0.5
                    TranslationProbability        0.2
                    RotationProbability           0.1
                    ReinsertionProbability        0.1
                    IdentityChangeProbability     0.1
                        NumberOfIdentityChanges   {number_of_components - 1}
                        IdentityChangesList       {' '.join(map(str, identity_change_list))}
                    CreateNumberOfMolecules       0

        """)
    else:
        inputfile += dedent(f"""\
        Component {index_of_component} MoleculeName                  {name}
                    MolFraction                   {fraction}
                    MoleculeDefinition            Local
                    SwapProbability               0.5
                    TranslationProbability        0.3
                    RotationProbability           0.1
                    ReinsertionProbability        0.1
                    CreateNumberOfMolecules       0

        """)

# Write string to file
with open(os.path.join(arg.output_folder, 'simulation-MonteCarlo.input'), 'w') as f:
    f.write(inputfile)
