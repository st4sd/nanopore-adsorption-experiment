# © Copyright IBM Corp. 2020 All Rights Reserved
# SPDX-License-Identifier: Apache2.0

import gemmi
import numpy as np


def calculate_UnitCells(cif_filename, cutoff):
    """
    Calculate the number of unit cell repetitions so that all supercell lengths are larger than
    twice the interaction potential cut-off radius.
    RASPA considers the perpendicular directions as the directions perpendicular to the `ab`,
    `bc`, and `ca` planes. Thus, the directions depend on the crystallographic vectors `a`, `b`,
    and `c`.
    The length in the perpendicular directions are the projections of the crystallographic vectors
    on the vectors `a x b`, `b x c`, and `c x a`. (here `x` means cross product)
    """
    # Read data from CIF file
    cif = gemmi.cif.read_file(cif_filename).sole_block()
    a = float(cif.find_value('_cell_length_a').split('(')[0])
    b = float(cif.find_value('_cell_length_b').split('(')[0])
    c = float(cif.find_value('_cell_length_c').split('(')[0])
    beta = float(cif.find_value('_cell_angle_beta').split('(')[0]) * np.pi / 180.0
    gamma = float(cif.find_value('_cell_angle_gamma').split('(')[0]) * np.pi / 180.0
    alpha = float(cif.find_value('_cell_angle_alpha').split('(')[0]) * np.pi / 180.0

    # Calculate the nu value
    nu = np.cos(alpha) - np.cos(gamma) * np.cos(beta) / np.sin(gamma)

    # Build the transformation matrix as a numpy array
    CellBox = np.array([[a, 0.0, 0.0],
                        [b * np.cos(gamma), b * np.sin(gamma), 0.0],
                        [c * np.cos(beta), c * nu, c * np.sqrt(1.0 - np.cos(beta)**2 - nu**2)]])

    # Calculate the cross products
    axb = np.cross(CellBox[0], CellBox[1])
    bxc = np.cross(CellBox[1], CellBox[2])
    cxa = np.cross(CellBox[2], CellBox[0])

    # Calculates the volume of the unit cell
    V = np.dot(np.cross(CellBox[0], CellBox[1]), CellBox[2])

    # Calculate perpendicular widths
    p_width_1 = V / np.linalg.norm(bxc)
    p_width_2 = V / np.linalg.norm(cxa)
    p_width_3 = V / np.linalg.norm(axb)

    # Calculate UnitCells string
    uc_array = np.ceil(2.0 * cutoff / np.array([p_width_1, p_width_2, p_width_3])).astype(int)
    unit_cells = ' '.join(map(str, uc_array))

    return unit_cells


def calculate_grid(composition):
    """
    Calculate the number and types of energy grids.
    """
    # Initialise grid variables
    grid_types = ''
    number_of_grids = 0

    # Read composition dictionary
    for molecule in composition:
        if molecule == 'CO2':
            atoms = 'C_co2 O_co2 '
        elif molecule == 'N2':
            atoms = 'N_n2 '
        elif molecule == 'O2':
            atoms = 'O_o2 '
        elif molecule == 'H2O':
            atoms = 'Ow Hw Lw'
        else:
            print(f'Error! {molecule} is not defined as a valid flue gas component.')
            exit(1)

        # Update grid variables
        grid_types += atoms
        number_of_grids += len(atoms.split())

    return grid_types, number_of_grids
