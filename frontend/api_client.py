from datetime import datetime
from typing import Dict
import json
import time
import requests
import pandas as pd
from requests.exceptions import RequestException as ReqExc

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
    while True:
        try:
            resp_dict = requests.get(
                API_URI + relative_path, params=kwargs, timeout=30
            ).json()

            if isinstance(resp_dict, str):
                # Sometimes, the json is still represented as string instead of dict
                resp_dict = json.loads(resp_dict)

            return resp_dict
        except ReqExc:
            print("API not availlable! Retrying in 5 seconds...")
            time.sleep(5)


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
    while True:
        try:
            return requests.get(
                API_URI + relative_path, params=kwargs, timeout=300
            ).content
        except ReqExc:
            print("API not availlable! Retrying in 5 seconds...")
            time.sleep(5)


def get_str(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as string
    """
    while True:
        try:
            return requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
        except ReqExc:
            print("API not availlable! Retrying in 5 seconds...")
            time.sleep(5)


def get_int(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as int number
    """
    while True:
        try:
            return int(
                requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
            )
        except ReqExc:
            print("API not availlable! Retrying in 5 seconds...")
            time.sleep(5)


def get_float(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as float number
    """
    while True:
        try:
            return float(
                requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
            )
        except ReqExc:
            print("API not availlable! Retrying in 5 seconds...")
            time.sleep(5)


def patch(relative_path: str, **kwargs):
    while True:
        try:
            requests.patch(API_URI + relative_path, params=kwargs)
        except ReqExc:
            print("API not availlable! Retrying in 5 seconds...")
            time.sleep(5)


def post(relative_path: str, data: Dict = None, json: Dict = None, **kwargs):
    """Post request. Returns the response body text

    Args:
        relative_path (str): _description_
        data (Dict, optional): _description_. Defaults to None.
        json (Dict, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    while True:
        try:
            response = requests.post(
                API_URI + relative_path, params=kwargs, data=data, json=json
            )
            text = response.text
            if text[0] == '"' and text[-1] == '"':
                text = text[1:-1]
            return text
        except ReqExc:
            print("API not availlable! Retrying in 5 seconds...")
            time.sleep(5)


def delete(relative_path: str, **kwargs):
    """Delete request. Returns the response body text

    Args:
        relative_path (str): _description_


    Returns:
        _type_: _description_
    """
    while True:
        try:
            response = requests.delete(API_URI + relative_path, params=kwargs)
            text = response.text
            if text[0] == '"' and text[-1] == '"':
                text = text[1:-1]
            return text
        except ReqExc:
            print("API not availlable! Retrying in 5 seconds...")
            time.sleep(5)
