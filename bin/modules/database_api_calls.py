# © Copyright IBM Corp. 2021 All Rights Reserved
# SPDX-License-Identifier: Apache2.0

import os

import requests


def _url(path):
    """
    Returns the full endpoint URL by composing it with the base API URL.
    """
    return f'http://database-api.{os.environ["INGRESS_SUBDOMAIN"]}' + path


def get_objectID(materialName, materialSource):
    """
    Retrieves the unique ObjectID of a material using a GET call.
    """
    url = _url(f'/materials?name={materialName}&source={materialSource}')
    response = requests.get(url).json()
    materials = response['materials']
    objectID = materials[0]['_id']
    return objectID


def post_tDependentProp(id, name, provenance, temperature, composition, data):
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


def post_pDependentProp(id, name, provenance, pressure, composition, data):
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


def post_constantProp(id, name, provenance, pressures, temperatures, data, RMSE, composition):
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
