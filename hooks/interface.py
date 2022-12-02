# © Copyright IBM Corp. 2022 All Rights Reserved

import json
import tarfile
import typing

import pandas


def get_input_ids(input_id_file: str, variables: typing.Dict[str, str]) -> typing.List[str]:
    """Extracts input ids from input_id_file
       Args:
          input_id_file: A path to the file containing the input ids.
            The value of the field interface.inputSpec.source.file
          variables: The global variables of the virtual experiment instance.
       Returns:
          Returns a list of the ids of the inputs in the naming specification defined by interface
    """

    with open(input_id_file, "r+") as cifs:
        materials = cifs.read()

    return materials.splitlines()


def get_properties(property_name: str, property_output_file: str, input_id_file: str) -> pandas.DataFrame:
    """This hook discovers the values of a property for all measured input ids.
       Args:
          property_output_file: A file path. The value of interface.propertiesSpec.name.source.output
            for the given property name (see next field)
          property_name: The value of interface.propertiesSpec.name.
          input_id_file: A file path. The path to the input id file.
       Returns:
          Returns a DataFrame with two columns (input-id, $PropertyName). Each row correspond to an input.
    """

    file = tarfile.open(property_output_file)
    file.extractall()
    file.close()

    with open(input_id_file, "r+") as cifs:
        materials = cifs.read()

    result = pandas.DataFrame()
    for material in materials.splitlines():
        material_name = material.split("/")[1]
        with open(f'{material_name}-isotherm.json', 'r') as j:
            contents = json.loads(j.read())
        concat_result = pandas.DataFrame([[material, contents]],
                                         columns=['input-id', property_name])
        result = pandas.concat([result, concat_result], ignore_index=True)

    return result
