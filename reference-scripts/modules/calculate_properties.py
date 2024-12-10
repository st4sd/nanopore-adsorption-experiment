# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2020 All Rights Reserved

import gemmi
import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import typing


def calculate_perpendicular_widths(cif_filename: str) -> typing.Tuple[float, float, float]:

    """
    This finction calculate the perpendicular widths of the unit cell.

    RASPA considers the perpendicular directions as the directions perpendicular to the `ab`,
    `bc`, and `ca` planes. Thus, the directions depend on the crystallographic vectors `a`, `b`,
    and `c`. The length in the perpendicular directions are the projections of the
    crystallographic vectors on the vectors `a x b`, `b x c`, and `c x a`. (here `x` means
    cross product).

    The perpendicular widths are calculated as the volume of the unit cell divided by the length.

    Parameters
    ----------
    cif_filename : string
        Name of the cif file.

    Returns
    -------
    p_width_1: float
      Perpendicular width in the direction of `a x b`.
    p_width_2: float
        Perpendicular width in the direction of `b x c`.
    p_width_3: float
        Perpendicular width in the direction of `c x a`.
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
    nu = (np.cos(alpha) - np.cos(gamma) * np.cos(beta)) / np.sin(gamma)

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

    return p_width_1, p_width_2, p_width_3


def calculate_UnitCells(cif_filename: str, cutoff: float) -> str:
    """
    Calculate the number of unit cell repetitions so that all supercell lengths are larger than
    twice the interaction potential cut-off radius.

    Parameters
    ----------
    cif_filename : string
        Name of the cif file.
    cutoff : float
        Cut-off radius.

    Returns
    -------
    unit_cells : string
        String with the number of unit cells in each direction.
    """

    # Calculate the perpendicular widths
    p_width_1, p_width_2, p_width_3 = calculate_perpendicular_widths(cif_filename)

    # Calculate UnitCells string
    uc_array = np.ceil(2.0 * cutoff / np.array([p_width_1, p_width_2, p_width_3])).astype(int)
    unit_cells = ' '.join(map(str, uc_array))

    return unit_cells


def calculate_NumberOfMolecules(cif_filename: str, cutoff: float, unitcells: str) -> int:
    """
    Calculate the number of molecules in the simulation box to ensure that
    there is at least `UnitCell` / `CutOff**3` molecules per unit cell.
    This will ensure that on average there is at least eight molecules
    inside the simulation box.

    Parameters
    ----------
    cif_filename : string
        Name of the cif file.
    cutoff : float
        Cut-off radius.
    unitcells : str
        Cut-off radius.

    Returns
    -------
    number_of_molecules : int
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
    nu = (np.cos(alpha) - np.cos(gamma) * np.cos(beta)) / np.sin(gamma)

    # Build the transformation matrix as a numpy array
    CellBox = np.array([[a, 0.0, 0.0],
                        [b * np.cos(gamma), b * np.sin(gamma), 0.0],
                        [c * np.cos(beta), c * nu, c * np.sqrt(1.0 - np.cos(beta)**2 - nu**2)]])

    # Calculates the volume of the unit cell
    V = np.dot(np.cross(CellBox[0], CellBox[1]), CellBox[2])

    # Get the mumber of unit cells
    unitcells_array = np.array(unitcells.split(' ')).astype(int)

    # Calculate the number of molecules
    NumberOfMolecules = int(np.round(np.prod(unitcells_array) * V / (cutoff)**3))

    return NumberOfMolecules


def calculate_grid(composition: dict) -> typing.Tuple[str, int]:
    """
    Calculate the number and types of energy grids.

    Parameters
    ----------
    composition : dict
        Dictionary with the composition of the flue gas.

    Returns
    -------
    grid_types : string
        String with the types of energy grids.
    number_of_grids : int
        Number of energy grids.
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
        elif molecule == 'SO2':
            atoms = 'S_so2 O_so2 '
        elif molecule == 'H2O':
            atoms = 'Ow Hw Lw '
        elif molecule == 'Ar':
            atoms = 'Ar '
        elif molecule == 'CF4':
            atoms = 'C_cf4 F_cf4 '
        elif molecule == 'C2H2':
            atoms = 'H_c2h2 C_c2h2 '
        else:
            print(f'Error! {molecule} is not defined as a valid flue gas component.')
            exit(1)

        # Update grid variables
        grid_types += atoms
        number_of_grids += len(atoms.split())

    return grid_types, number_of_grids


def linear(x, slope, intercept):
    '''
    Linear Equation
    '''
    return slope * x + intercept


def find_diffusion_regime(time,
                          msd,
                          slope_target=1.0,
                          pore_limiting_diameter=0.0) -> typing.Tuple[int, int, float]:
    '''
    This function search the region on the MSD data where the Einstein model
    for diffusion can be applied.

    Parameters
    ----------
    time : array
        Time array.
    msd : array
        Mean Squared Displacement array.
    slope_target : float, optional
        Slope of the linear fit to the MSD data. The default is 1.0.
    pore_limiting_diameter : float, optional
        Pore limiting diameter. The default is 0.0.

    Returns
    -------
    diffusion_start : float
        Start position of the diffusion regime.
    diffusion_end : float
        End position of the diffusion regime.
    block_slope : float
        Slope of the linear fit to the log(MSD) data.
    '''

    # Convert the MSD data to log scale
    time_log = np.log10(time)
    msd_log = np.log10(msd)

    # compute second derivative of MSD
    second_d = np.gradient(np.gradient(msd_log))

    # Find the peaks in the second derivate
    peaks, _ = find_peaks(second_d, distance=15)

    # Add the last point on the list if it generates a block with more than 15 points
    if len(msd_log[peaks[-1]:]) > 15:
        peaks = np.append(peaks, [len(msd_log)], axis=0)

    # Split the data into blocks
    block_dict = {}

    start = 0
    for i, peak in enumerate(peaks):

        # Calculate the inclination in the block data
        slope, intercept = np.polyfit(time_log[start:peak], msd_log[start:peak], 1)

        # Store the block data
        block_dict[i] = {'time': time_log[start:peak],
                         'msd': msd_log[start:peak],
                         'start': start,
                         'end': peak,
                         'is_valid': max(msd[start:peak]) > pore_limiting_diameter**2,
                         'slope': slope,
                         'intercept': intercept}

        # Update the start position
        start = peak

    # Find the block with the slope closest to slope_target
    block_index = np.argmin([abs(block_dict[i]['slope'] - slope_target) for i in block_dict])

    diffusion_start = block_dict[block_index]['start']
    diffusion_end = block_dict[block_index]['end']
    block_slope = block_dict[block_index]['slope']

    return diffusion_start, diffusion_end, block_slope


def calculate_directional_self_diffusivity(time, msd, cif_filename) -> typing.Tuple[float, float]:
    '''
    Calculates the self-diffusivity (D) in a specific direction in space using the
    least-squares regression on the MSD curve.

    MSD(t) = a * t + b

    D = a / 2

    Parameters
    ----------
    time : array
        Array containing the simulation time in ps
    msd : array
        Array containing the Mean Squared Distance on a specific direction in Å^2
    cif_filename : string
        Name of the cif file.

    Returns
    -------
    D: float
        Self diffusivity in units of m^2/s
    D_sd : float
        Error of the self-diffusivity fit in units of m^2/s
    '''

    # Calculate the maximum perpendicular width of unit cell (in Angstrom)
    pld = max(calculate_perpendicular_widths(cif_filename))

    # Check if the maximum value of MSD indicates diffusion
    if max(msd) > pld**2:
        # Find the correct region to fit the Einstein equation
        start, end, slope = find_diffusion_regime(time,
                                                  msd,
                                                  pore_limiting_diameter=pld)

        if abs(slope - 1) < 0.4:
            # Fit a linear function to the msd data
            [slope, _], pcov = curve_fit(linear, time[start:end], msd[start:end])
            perr = np.sqrt(np.diag(pcov))

            # Convert to units of m^2/s
            D = slope / 2 * 1e-8
            D_sd = perr[0] * 1e-8

            return D, D_sd

        else:
            print('Failed to find a region with normal diffusive regime!')
            print(f'Closest slope to 1 is {slope}. You may need to increase the NumberOfCycles.')
            return None, None

    else:
        print(f'Max MSD is {max(msd)}, shoud be greater the {pld**2}.')
        # Fit a linear function to the msd data
        start, end, slope = find_diffusion_regime(time,
                                                  msd,
                                                  slope_target=0.0,
                                                  pore_limiting_diameter=pld)

        if abs(slope - 0.0) < 0.4:
            print('Molecule is in confined diffusion regime! Ds = Dc')
            # Calculate the assintotic value of Dc and convert to units of m^2/s
            D = np.mean(msd[start:end]) * 1e-20
            D_sd = np.std(msd[start:end]) * 1e-20

            return D, D_sd

        else:
            print('Failed to find a region with confined diffusive regime!')
            print(f'Closest slope to 0 is {slope}. You may need to increase the NumberOfCycles.')
            return None, None
