from datetime import datetime
from typing import Dict
import requests
import json
import pandas as pd
from requests.exceptions import RequestException

from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_environment_variable,
)

API_URI = (
    get_environment_variable("FAST_API_HOST")
    + ":"
    + get_environment_variable("FAST_API_PORT")
)


def get_json(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response json as dict
    """
    try:
        resp_dict = requests.get(API_URI + relative_path, params=kwargs).json()

        if isinstance(resp_dict, str):
            # Sometimes, the json is still represented as string instead of dict
            resp_dict = json.loads(resp_dict)

        return resp_dict
    except RequestException as err:
        print("API not availlable!")
        return ""


def get_dataframe(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint. Deserializes to dataframe
    :param relative_path:
    :return:
    """
    df_dict = get_json(relative_path, **kwargs)

    df = pd.DataFrame.from_dict(df_dict)

    # Convert string timestamp to actual tz data type
    df["time"] = df["time"].map(
        lambda t_string: datetime.strptime(t_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    )
    # Set UTC timezone (trans)
    df["time"] = df["time"].map(lambda t: t.tz_localize("UTC"))

    df["time"] = df["time"].map(
        lambda t: t.tz_convert(
            get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
        )
    )

    return df


def get_raw(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the raw response
    """
    try:
        return requests.get(API_URI + relative_path, params=kwargs).content
    except RequestException as err:
        print("API not availlable!")
        return None


def get_str(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as string
    """
    try:
        return requests.get(API_URI + relative_path, params=kwargs).text
    except RequestException as err:
        print("API not availlable!")
        return ""


def get_int(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as int number
    """
    try:
        return int(requests.get(API_URI + relative_path, params=kwargs).text)
    except RequestException as err:
        print("API not availlable!")
        return None


def get_float(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as float number
    """
    try:
        return float(requests.get(API_URI + relative_path, params=kwargs).text)
    except RequestException as err:
        print("API not availlable!")
        return None


def patch(relative_path: str, **kwargs):
    try:
        requests.patch(API_URI + relative_path, params=kwargs)
    except RequestException as err:
        print("API not availlable!")


def post(relative_path: str, data: Dict = None, json: Dict = None, **kwargs):
    try:
        requests.post(API_URI + relative_path, params=kwargs, data=data, json=json)
    except RequestException as err:
        print("API not availlable!")
