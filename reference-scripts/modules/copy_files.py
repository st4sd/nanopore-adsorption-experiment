# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2020 All Rights Reserved

import glob
import json
import os
import shutil


def copy_def_files(output_folder: str, forcefield_folder: str) -> None:
    """
    Copy all '*.def' files of the appropriate force field to the output folder.
    """
    def_files = glob.glob(forcefield_folder + '/*.def')

    # Return an error if there are no *.def files in the folder
    if def_files:
        for f in def_files:
            print(f'Copying {f} to {output_folder}')
            shutil.copy(f, os.path.join(output_folder, f.split('/')[-1]))
    else:
        print(f'Warning! Force field *.def files not found in {forcefield_folder}.')
        exit(1)


def copy_cif_file(output_folder: str,
                  framework_name: str,
                  framework_source: str,
                  framework_folder: str) -> None:
    """
    Copy the 'framework_name.cif' file from the 'framework_source' folder to the output folder.
    """
    if framework_source != 'local':
        cif_file = os.path.join(framework_folder, framework_source, framework_name + '.cif')
        shutil.copy(cif_file, os.path.join(output_folder, cif_file.split('/')[-1]))
        print(f'Copying {cif_file} to {output_folder}')
    else:
        print(f'Assuming the CIF file is already inside {output_folder}')


def save_to_disk(name: str,
                 filename: str,
                 directory: str,
                 provenance: str,
                 temperature: float,
                 data: list[dict],
                 composition: list[dict]) -> None:
    """
    Save a JSON file to disk with the same content as the database records.
    """
    thermoProp = {'name': str(name),
                  'provenance': str(provenance),
                  'temperature': float(temperature),
                  'composition': composition,
                  'data': data}

    with open(os.path.join(directory, filename), 'w') as f:
        f.write(json.dumps(thermoProp))
