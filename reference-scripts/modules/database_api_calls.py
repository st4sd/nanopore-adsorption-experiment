# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2021 All Rights Reserved

import os

import requests


def _url(path: str) -> str:
    """
    Returns the full endpoint URL by composing it with the base API URL.
    """
    return f'http://database-api.{os.environ["INGRESS_SUBDOMAIN"]}' + path


def get_objectID(materialName: str, materialSource: str) -> str:
    """
    Retrieves the unique ObjectID of a material using a GET call.
    """
    url = _url(f'/materials?name={materialName}&source={materialSource}')
    response = requests.get(url).json()
    materials = response['materials']
    objectID = materials[0]['_id']
    return objectID


def post_tDependentProp(id: str,
                        name: str,
                        provenance: str,
                        temperature: float,
                        composition: list[dict],
                        data: list[dict]) -> requests.models.Response:
    """
    Inserts a t-dependent property for a given material ID using a POST call.
    """
    url = _url(f'/materials/{id}/thermodynamic-properties/t-dependent')
    thermoProp = {'name': str(name),
                  'provenance': str(provenance),
                  'temperature': float(temperature),
                  'composition': composition,
                  'data': data}
    return requests.post(url, json=thermoProp)


def post_pDependentProp(id: str,
                        name: str,
                        provenance: str,
                        pressure: float,
                        composition: list[dict],
                        data: list[dict]) -> requests.models.Response:
    """
    Inserts a p-dependent property for a given material ID using a POST call.
    """
    url = _url(f'/materials/{id}/thermodynamic-properties/p-dependent')
    thermoProp = {'name': str(name),
                  'provenance': str(provenance),
                  'pressure': float(pressure),
                  'composition': composition,
                  'data': data}
    return requests.post(url, json=thermoProp)


def post_constantProp(id: str,
                      name: str,
                      RMSE: float,
                      provenance: str,
                      data: list[dict],
                      pressures: float,
                      temperatures: float,
                      composition: list[dict]) -> requests.models.Response:
    """
    Inserts a constant property for a given material ID using a POST call.
    """
    url = _url(f'/materials/{id}/thermodynamic-properties/constant')
    thermoProp = {'name': str(name),
                  'provenance': str(provenance),
                  'pressures': float(pressures),
                  'temperatures': float(temperatures),
                  'data': data,
                  'RMSE': float(RMSE),
                  'composition': composition}
    return requests.post(url, json=thermoProp)
