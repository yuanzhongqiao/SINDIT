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


def _handle_request_exception(retry_number: int = 0):
    logger.info("API not available!")
    logger.info(f"Tried to connect to {API_URI}")

    sleep_time = 5 * (2**retry_number)

    logger.info(f"Retrying in {sleep_time} seconds...")
    time.sleep(sleep_time)


def get_json(relative_path: str, retries: int = -1, timeout: int = 30, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :param retries: how often to retry if the call failed. Negative numbners mean (about) unlimited.
    :return: the response json as dict
    """
    range_limit = retries + 1 if retries >= 0 else 999999999999999999999999
    for i in range(range_limit):
        try:
            resp_dict = requests.get(
                API_URI + relative_path, params=kwargs, timeout=timeout
            ).json()

            if isinstance(resp_dict, str):
                # Sometimes, the json is still represented as string instead of dict
                resp_dict = json.loads(resp_dict)

            return resp_dict
        except ReqExc:
            if i < retries:
                _handle_request_exception(i)


def get_dataframe(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint. Deserializes to dataframe
    :param relative_path:
    :param retries: how often to retry if the call failed. Negative numbners mean (about) unlimited.
    :return:
    """
    df_dict = get_json(relative_path=relative_path, **kwargs)

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


def get_raw(relative_path: str, retries: int = -1, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :param retries: how often to retry if the call failed. Negative numbners mean (about) unlimited.
    :return: the raw response
    """
    range_limit = retries + 1 if retries >= 0 else 999999999999999999999999
    for i in range(range_limit):
        try:
            return requests.get(
                API_URI + relative_path, params=kwargs, timeout=300
            ).content
        except ReqExc:
            _handle_request_exception(i)


def get_str(relative_path: str, retries: int = -1, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response as string
    """
    range_limit = retries + 1 if retries >= 0 else 999999999999999999999999
    for i in range(range_limit):
        try:
            return requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
        except ReqExc:
            _handle_request_exception(i)


def get_int(relative_path: str, retries: int = -1, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :param retries: how often to retry if the call failed. Negative numbners mean (about) unlimited.
    :return: the response as int number
    """
    range_limit = retries + 1 if retries >= 0 else 999999999999999999999999
    for i in range(range_limit):
        try:
            return int(
                requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
            )
        except ReqExc:
            _handle_request_exception(i)


def get_float(relative_path: str, retries: int = -1, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :param retries: how often to retry if the call failed. Negative numbners mean (about) unlimited.
    :return: the response as float number
    """
    range_limit = retries + 1 if retries >= 0 else 999999999999999999999999
    for i in range(range_limit):
        try:
            return float(
                requests.get(API_URI + relative_path, params=kwargs, timeout=30).text
            )
        except ReqExc:
            _handle_request_exception(i)


def patch(relative_path: str, retries: int = -1, **kwargs):
    range_limit = retries + 1 if retries >= 0 else 999999999999999999999999
    for i in range(range_limit):
        try:
            return requests.patch(API_URI + relative_path, params=kwargs)
        except ReqExc:
            _handle_request_exception(i)


def post(
    relative_path: str,
    data: Dict = None,
    json: Dict = None,
    retries: int = -1,
    **kwargs,
):
    """Post request. Returns the response body text

    Args:
    relative_path (str): _description_
    retries: how often to retry if the call failed. Negative numbners mean (about) unlimited.
        data (Dict, optional): _description_. Defaults to None.
        json (Dict, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    range_limit = retries + 1 if retries >= 0 else 999999999999999999999999
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
            _handle_request_exception(i)


def delete(relative_path: str, retries: int = -1, **kwargs):
    """Delete request. Returns the response body text

    Args:
    relative_path (str): _description_
    retries: how often to retry if the call failed. Negative numbners mean (about) unlimited.


    Returns:
        _type_: _description_
    """
    range_limit = retries + 1 if retries >= 0 else 999999999999999999999999
    for i in range(range_limit):
        try:
            response = requests.delete(API_URI + relative_path, params=kwargs)
            text = response.text
            if text[0] == '"' and text[-1] == '"':
                text = text[1:-1]
            return text
        except ReqExc:
            _handle_request_exception(i)
