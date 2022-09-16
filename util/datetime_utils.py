from datetime import datetime


def neo4j_str_to_datetime(string: str) -> datetime:
    return datetime.fromisoformat(string.replace('"', "")[:-3])


def datetime_to_neo4j_str(dt: datetime) -> str:
    iso_str = dt.isoformat()
    with_padding = iso_str + "000"
    with_surroundings = '"' + with_padding + '"'

    return with_surroundings


def neo4j_str_or_datetime_to_datetime(date_time: str | datetime) -> datetime:
    if isinstance(date_time, datetime):
        return date_time
    else:
        return neo4j_str_to_datetime(date_time)
