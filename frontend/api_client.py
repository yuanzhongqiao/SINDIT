from datetime import datetime
from typing import Dict
import json
from util.log import logger
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

RETRY_COUNT = 5


def _handle_request_exception():
    logger.info("API not available!")
    logger.info(f"Tried to connect to {API_URI}")
    logger.info("Retrying in 5 seconds...")
    time.sleep(5)


def get_json(relative_path: str, endless_scan: bool = True, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response json as dict
    """
    range_limit = RETRY_COUNT if not endless_scan else 999999999999999999999999
    for i in range(range_limit):
        try:
            resp_dict = requests.get(
                API_URI + relative_path, params=kwargs, timeout=30
            ).json()

            if isinstance(resp_dict, str):
                # Sometimes, the json is still represented as string instead of dict
                resp_dict = json.loads(resp_dict)

            return resp_dict
        except ReqExc:
            _handle_request_exception()


def get_dataframe(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint. Deserializes to dataframe
    :param relative_path:
    :return:
    """
    df_dict = get_json(relative_path, endless_scan=False, **kwargs)

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


def get_raw(relative_path: str, endless_scan: bool = True, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the raw response
    """
    range_limit = RETRY_COUNT if not endless_scan else 999999999999999999999999
    for i in range(range_limit):
        try:
            return requests.get(
                API_URI + relative_path, params=kwargs, timeout=300
            ).content
        except ReqExc:
            _handle_request_exception()


def get_str(relative_path: str, endless_scan: bool = True, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as string
    """
    range_limit = RETRY_COUNT if not endless_scan else 999999999999999999999999
    for i in range(range_limit):
        try:
            return requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
        except ReqExc:
            _handle_request_exception()


def get_int(relative_path: str, endless_scan: bool = True, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as int number
    """
    range_limit = RETRY_COUNT if not endless_scan else 999999999999999999999999
    for i in range(range_limit):
        try:
            return int(
                requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
            )
        except ReqExc:
            _handle_request_exception()


def get_float(relative_path: str, endless_scan: bool = True, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as float number
    """
    range_limit = RETRY_COUNT if not endless_scan else 999999999999999999999999
    for i in range(range_limit):
        try:
            return float(
                requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
            )
        except ReqExc:
            _handle_request_exception()


def patch(relative_path: str, endless_scan: bool = True, **kwargs):
    range_limit = RETRY_COUNT if not endless_scan else 999999999999999999999999
    for i in range(range_limit):
        try:
            requests.patch(API_URI + relative_path, params=kwargs)
        except ReqExc:
            _handle_request_exception()


def post(
    relative_path: str,
    data: Dict = None,
    json: Dict = None,
    endless_scan: bool = True,
    **kwargs,
):
    """Post request. Returns the response body text

    Args:
        relative_path (str): _description_
        data (Dict, optional): _description_. Defaults to None.
        json (Dict, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    range_limit = RETRY_COUNT if not endless_scan else 999999999999999999999999
    for i in range(range_limit):
        try:
            response = requests.post(
                API_URI + relative_path, params=kwargs, data=data, json=json
            )
            text = response.text
            if text[0] == '"' and text[-1] == '"':
                text = text[1:-1]
            return text
        except ReqExc:
            _handle_request_exception()


def delete(relative_path: str, endless_scan: bool = True, **kwargs):
    """Delete request. Returns the response body text

    Args:
        relative_path (str): _description_


    Returns:
        _type_: _description_
    """
    range_limit = RETRY_COUNT if not endless_scan else 999999999999999999999999
    for i in range(range_limit):
        try:
            response = requests.delete(API_URI + relative_path, params=kwargs)
            text = response.text
            if text[0] == '"' and text[-1] == '"':
                text = text[1:-1]
            return text
        except ReqExc:
            _handle_request_exception()
